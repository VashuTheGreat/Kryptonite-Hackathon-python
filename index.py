from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
import uvicorn as uv
import os
import shutil
import base64

from fastapi.middleware.cors import CORSMiddleware

from settlelite_image_fire_coordinate import (
    fetch_firms_data,
    generate_map,
    draw_boxes,   # ✅ IMPORTED, NOT REDEFINED
)

app = FastAPI(description="Fire Detector")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return {"message": "hello World"}


@app.get("/health")
async def health():
    return JSONResponse(
        status_code=200,
        content={"message": "success"}
    )


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

    # cleanup temp files
    if map_file and os.path.exists(map_file):
        os.remove(map_file)
    if temp_file and os.path.exists(temp_file):
        os.remove(temp_file)

    return {"html": html}


@app.post("/draw_boxes_fire")
async def draw_yolo_boxes(file: UploadFile):
    os.makedirs("public", exist_ok=True)

    if not file:
        return JSONResponse(status_code=400, content={"error": "File is required"})

    file_path = f"public/{file.filename}"

    # save uploaded file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # run YOLO inference
    output_image_path = await draw_boxes(image_path=file_path)

    # read output image
    with open(output_image_path, "rb") as f:
        image_bytes = f.read()

    # cleanup
    os.remove(file_path)
    shutil.rmtree(os.path.dirname(output_image_path), ignore_errors=True)

    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    return {"data": encoded_image}


if __name__ == "__main__":
    uv.run("index:app", host="127.0.0.1", port=8000, reload=True)
