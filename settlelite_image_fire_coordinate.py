import os
import pandas as pd
import requests
from dotenv import load_dotenv
import geopandas
import folium
from ultralytics import YOLO
from pathlib import Path

# load env
load_dotenv()
MAP_KEY = os.getenv("MAP_KEY")

if not MAP_KEY:
    raise ValueError(
        "MAP_KEY not found in .env file. Get one from https://firms.modaps.eosdis.nasa.gov/api/"
    )

# load model ONCE
model = YOLO("models/fire_detector.pt")

base_url = "https://firms.modaps.eosdis.nasa.gov"

REGION_BBOX = {
    "india": {
        "up": "77.1,23.5,84.5,31.5",
        "mp": "74.0,21.0,82.0,26.0",
        "maharashtra": "72.5,17.0,80.0,22.0",
    },
}


# ---------------- FIRMS DATA ----------------
async def fetch_firms_data(country, state, source="VIIRS_SNPP_NRT", day_range=3):
    country = country.lower()
    state = state.lower()

    if country not in REGION_BBOX or state not in REGION_BBOX[country]:
        raise ValueError(f"Bounding box not found for {country} - {state}")

    area = REGION_BBOX[country][state]
    url = f"{base_url}/api/area/csv/{MAP_KEY}/{source}/{area}/{day_range}"

    response = requests.get(url)
    if response.status_code != 200:
        raise ConnectionError(response.text)

    temp_file = "firms_temp.csv"
    with open(temp_file, "wb") as f:
        f.write(response.content)

    df = pd.read_csv(temp_file)

    df = df[
        ["latitude", "longitude", "acq_date", "acq_time", "confidence"]
    ]

    df = geopandas.GeoDataFrame(
        df,
        geometry=geopandas.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326",
    )

    return df, temp_file


# ---------------- MAP GENERATION ----------------
async def generate_map(data: pd.DataFrame):
    center_lat = data["latitude"].mean()
    center_lon = data["longitude"].mean()

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles="OpenStreetMap",
    )

    colors = {"h": "red", "n": "orange", "l": "yellow"}

    for _, row in data.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=4,
            color=colors.get(row["confidence"], "yellow"),
            fill=True,
            fill_opacity=0.7,
            popup=f"{row['acq_date']} {row['acq_time']}",
        ).add_to(m)

    file_name = "firms_map.html"
    m.save(file_name)

    with open(file_name, "r", encoding="utf-8") as f:
        html = f.read()

    return html, file_name


# ---------------- YOLO FIRE DETECTION ----------------
async def draw_boxes(image_path, save_dir="outputs"):
    results = model(
        image_path,
        conf=0.25,
        save=True,
        project=save_dir,
        name="fires",
    )

    r = results[0]
    save_path = Path(r.save_dir)

    images = list(save_path.glob("*.jpg")) + list(save_path.glob("*.png"))
    if not images:
        raise FileNotFoundError("YOLO output image not found")

    return str(images[0])
