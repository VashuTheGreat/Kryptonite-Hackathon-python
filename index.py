from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import uvicorn as uv
import os
import shutil
import base64
import json

# --- 1. Import Your Existing Logic ---
from settlelite_image_fire_coordinate import (
    fetch_firms_data,
    generate_map,
    draw_boxes,  
)

# --- 2. Import Bot Logic ---
from bot import get_graph_app, SYSTEM_PROMPT
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# --- 3. Global State ---
bot_app = None
bot_db_conn = None

# --- 4. Lifespan Manager (Startup/Shutdown) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot_app, bot_db_conn
    print("🔥 FireWatch AI: Initializing System...")
    try:
        # Initialize Graph and "Connection" (RAM or DB)
        bot_app, bot_db_conn = await get_graph_app()
        
        # Enter the async context (required for the connection manager)
        await bot_db_conn.__aenter__()
        print("✅ FireWatch AI: Online and Ready.")
        yield
    except Exception as e:
        print(f"❌ Startup Error: {e}")
        yield
    finally:
        print("🧯 FireWatch AI: Shutting down...")
        if bot_db_conn:
            await bot_db_conn.__aexit__(None, None, None)

app = FastAPI(description="FireWatch Pro API", lifespan=lifespan)

# --- 5. CORS Setup ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 6. Data Models ---
class ChatRequest(BaseModel):
    user_id: str
    message: str

# --- 7. Chat Endpoints ---

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint. Sends message to AI and returns response.
    """
    if not bot_app:
        raise HTTPException(status_code=503, detail="AI System is initializing")
    
    # Config uses user_id to maintain separate conversation threads
    config = {"configurable": {"thread_id": request.user_id}}
    
    # Input: We pass the new HumanMessage. LangGraph handles the history appending.
    inputs = {"messages": [HumanMessage(content=request.message)]}
    
    try:
        # Run the graph
        final_state = await bot_app.ainvoke(inputs, config=config)
        
        # Get the very last message (the AI's response)
        ai_response = final_state["messages"][-1].text
        return {"response": ai_response}
        
    except Exception as e:
        print(f"Chat Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/chat/history/{user_id}")
async def get_chat_history(user_id: str):
    """
    New Endpoint: Fetches all previous messages for a specific user.
    Useful for reloading the chat window on the frontend.
    """
    if not bot_app:
        raise HTTPException(status_code=503, detail="AI System is initializing")

    config = {"configurable": {"thread_id": user_id}}
    
    try:
        # Fetch the current state of the conversation from Memory
        state_snapshot = await bot_app.get_state(config)
        
        # If no history exists, return empty list
        if not state_snapshot.values:
            return {"history": []}

        messages = state_snapshot.values.get("messages", [])
        
        # Convert complex objects to simple JSON
        formatted_history = []
        for msg in messages:
            role = "unknown"
            if isinstance(msg, HumanMessage):
                role = "user"
            elif isinstance(msg, AIMessage):
                role = "ai"
            elif isinstance(msg, SystemMessage):
                continue # Skip system prompt in history display
            
            # Skip ToolCalls/ToolMessages for cleaner UI (optional)
            if role != "unknown":
                formatted_history.append({
                    "role": role,
                    "content": msg.content
                })

        return {"history": formatted_history}

    except Exception as e:
        print(f"History Error: {e}")
        return {"history": []} # Return empty on error to prevent UI crash

# --- 8. Existing Fire Endpoints ---

@app.get("/")
async def home():
    return {"message": "FireWatch Pro Active"}

@app.get("/health")
async def health():
    return JSONResponse(status_code=200, content={"message": "success"})

@app.post("/get_locations")
async def map_locations(
    country: str = "india",
    state: str = "up",
    source: str = "VIIRS_SNPP_NRT",
    day_range: int = 3
):
    data, temp_file = await fetch_firms_data(
        country=country,
        state=state,
        source=source,
        day_range=day_range
    )

    html, map_file = await generate_map(data=data)

    if map_file and os.path.exists(map_file):
        os.remove(map_file)
        
    if temp_file and os.path.exists(temp_file):
        os.remove(temp_file)

    return {"html": html}

@app.post("/get_hight_regions_area")
async def high_regions(
    country: str = "india",
    state: str = "up",
    source: str = "VIIRS_SNPP_NRT",
    day_range: int = 3
):
    data, temp_file = await fetch_firms_data(
        country=country,
        state=state,
        source=source,
        day_range=day_range
    )
    
    if hasattr(data, 'empty') and data.empty:
        return {"data": "[]"}
        
    data = data[data['confidence'] == 'h']
    if 'geometry' in data.columns:
        data = data.drop(columns=['geometry'])

    result = json.dumps(data.to_dict(orient='records'))    
    if temp_file and os.path.exists(temp_file):
        os.remove(temp_file)

    return {"data": result}

@app.post("/draw_boxes_fire")
async def draw_yolo_boxes(file: UploadFile):
    os.makedirs("public", exist_ok=True)
    if not file:
        return JSONResponse(status_code=400, content={"error": "File is required"})

    file_path = f"public/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    output_image_path = await draw_boxes(image_path=file_path)

    with open(output_image_path, "rb") as f:
        image_bytes = f.read()

    os.remove(file_path)
    shutil.rmtree(os.path.dirname(output_image_path), ignore_errors=True)

    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    return {"data": encoded_image}

if __name__ == "__main__":
    # Ensure this matches the filename 'index.py'
    uv.run("index:app", host="127.0.0.1", port=8000, reload=True)