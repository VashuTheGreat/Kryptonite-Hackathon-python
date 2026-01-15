from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
import uvicorn as uv
from settlelite_image_fire_coordinate import fetch_firms_data, generate_map, draw_boxes
import os
import shutil
import base64
import vconsoleprint
app = FastAPI(description="Fire Detector")

@app.get("/")
async def home():
    "Home route just gives hello world"
    return {"message": "hello World"}

@app.get("/health")
async def health():
    """Health route"""
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
    """Returuns html code for rendering yellow red regions"""
    data,file_pa = await fetch_firms_data(
        country=country, state=state, source=source, day_range=day_range
    )

   
    html_,file_p = await generate_map(data=data)
    if file_p:
        os.remove(file_p)
    if file_pa:
        os.remove(file_pa)

    # data_for_csv = data.drop(columns=['geometry']) if 'geometry' in data.columns else data
    # data=data_for_csv.to_dict()

    return {"html":html_}

@app.post("/draw_boxes_fire")
async def draw_yolo_boxes(file: UploadFile):
    """Upload a file and get boxes drawned on it to represent fire it returns incoded string"""
    os.makedirs("public", exist_ok=True)
    if not file:
        return "Uploading file is mandatory"
    file_path = f"public/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    img_path_folder = await draw_boxes(image_path=file_path) 
    img_path=img_path_folder+f"/{file.filename}"
    with open(img_path, "rb") as f:
        image_byte = f.read()

    if file_path and img_path_folder:
        os.remove(file_path)
        shutil.rmtree(img_path_folder)   
    encoded_image = base64.b64encode(image_byte).decode("utf-8")
    return {"data": encoded_image}   


# @app.middleware("/")
# async def middleware():
#     return {"404"}
if __name__ == "__main__":
    uv.run("index:app", host="127.0.0.1", port=8000, reload=True)