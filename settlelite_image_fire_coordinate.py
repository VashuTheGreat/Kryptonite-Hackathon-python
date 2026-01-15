import os
import pandas as pd
import requests
from dotenv import load_dotenv
import geopandas
import folium
import json
import os
from ultralytics import YOLO
import vconsoleprint
model=YOLO("models/fire_detector.pt")

load_dotenv()
MAP_KEY = os.getenv('MAP_KEY') 

if not MAP_KEY:
    raise ValueError("MAP_KEY not found in .env file. Get one from https://firms.modaps.eosdis.nasa.gov/api/")


base_url = "https://firms.modaps.eosdis.nasa.gov"  


REGION_BBOX = {
    "india": {
        "up": "77.1,23.5,84.5,31.5",
        "mp": "74.0,21.0,82.0,26.0",
        "maharashtra": "72.5,17.0,80.0,22.0",
    },
}

# ------------- fetches data from NASA FIRMS -------------------
async def fetch_firms_data(country: str, state: str, source="VIIRS_SNPP_NRT", day_range=3):
    country = country.lower()
    state = state.lower()

    if country not in REGION_BBOX or state not in REGION_BBOX[country]:
        raise ValueError(f"Bounding box not found for {country} and {state}")

    area = REGION_BBOX[country][state]
    url = f"{base_url}/api/area/csv/{MAP_KEY}/{source}/{area}/{day_range}"

    print(f"Fetching FIRMS data from: {url}")

    response =  requests.get(url)
    if response.status_code != 200:
        raise ConnectionError(f"Error fetching data: {response.status_code} - {response.text}")

    temp_file = "firms_temp.txt"
    with open(temp_file, "wb") as f:
        f.write(response.content)

    try:
        df = pd.read_csv(temp_file, sep=",")
    except:
        df = pd.read_csv(temp_file, sep="\t")

    filter_cols = ["latitude", "longitude", "acq_date", "acq_time", "confidence"]
    df = df[filter_cols]

    df = geopandas.GeoDataFrame(
    df, geometry=geopandas.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326"
    )

    return df,"firms_temp.txt"



# ---------------- generates a map -----------------------
async def generate_map(data:pd.DataFrame):
    center_lat = data['latitude'].mean()
    center_lon = data['longitude'].mean()

    m = folium.Map(location=[center_lat, center_lon], zoom_start=6, tiles="OpenStreetMap")

    colors = {'h':'red', 'n':'orange', 'l':'yellow'}

    for idx, row in data.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=4,
            color=colors[row['confidence']],
            fill=True,
            fill_opacity=0.7,
            popup=f"Date: {row['acq_date']}, Time: {row['acq_time']}"
        ).add_to(m)
    try:
        m.save("firms_map.html")
        html_=None,None
        with open("firms_map.html","r",encoding="utf-8") as f:
            html_=f.read()
        
        return html_,"firms_map.html"
    except Exception as e:
        return None


# ------------------ Draw detected Fire labels ------------
async def draw_boxes(image_path, save_dir="outputs"):
    results = model(
        image_path,
        conf=0.25,
        save=True,
        project=save_dir,
        name="fires"
    )

    r = results[0]

    print("Saved directory:", r.save_dir)

    return str(r.save_dir)







