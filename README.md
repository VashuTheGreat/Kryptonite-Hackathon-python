# Satellite & Drone Fire Detection System (Backend)

This project is the Python backend for an advanced fire detection and response system. It leverages satellite data to identify potential fire hotspots and processes drone imagery to verify and pinpoint fires using AI.

## 🚀 Overview

The system operates in a multi-stage process:

1.  **Satellite Detection**: The system queries NASA's FIRMS (Fire Information for Resource Management System) to detect thermal anomalies and potential fires over a large area (e.g., a state or country).
2.  **Drone Verification**: Once a location is identified, a drone is dispatched to the coordinates.
3.  **AI Analysis**: The drone captures images, which are sent to this backend. A YOLOv8 AI model analyzes the images to confirm the presence of fire.
4.  **Response**: Upon confirmation, the system is designed to trigger alarms (FireKit) and coordinate fire suppression efforts (e.g., spreading water).

## ✨ Features

- **Real-time Satellite Monitoring**: Fetches active fire data from NASA FIRMS.
- **Interactive Mapping**: Generates HTML maps visualizing fire locations with confidence levels.
- **AI Fire Detection**: Uses a custom YOLOv8 model to detect fire in aerial images.
- **High-Confidence Filtering**: API endpoint to filter and retrieve only high-confidence fire alerts.
- **FastAPI Backend**: High-performance, asynchronous API for seamless integration with frontend or drone hardware.

## 🛠️ Tech Stack

- **Language**: Python
- **Framework**: FastAPI
- **AI/ML**: Ultralytics YOLOv8
- **Geospatial**: Geopandas, Folium, Pandas
- **Data Source**: NASA FIRMS API

## 📂 Project Structure

- `index.py`: Main entry point for the FastAPI application.
- `settlelite_image_fire_coordinate.py`: Core logic for fetching satellite data and running AI inference.
- `models/`: Contains the trained YOLO model (`fire_detector.pt`).
- `requirements.txt`: Project dependencies.

## ⚙️ Installation & Setup

1.  **Clone the Repository**

    ```bash
    git clone <repository-url>
    cd SettliteFireDetector
    ```

2.  **Create a Virtual Environment**

    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Linux/Mac
    source .venv/bin/activate
    ```

3.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**
    Create a `.env` file in the root directory and add your NASA FIRMS Map Key:
    ```env
    MAP_KEY=your_nasa_firms_map_key_here
    ```
    > You can obtain a Map Key from [NASA FIRMS API](https://firms.modaps.eosdis.nasa.gov/api/).

## 🚀 Usage

1.  **Start the Server**

    ```bash
    python index.py
    # OR
    uvicorn index:app --reload
    ```

2.  **API Endpoints**
    - `POST /get_locations`: Get fire locations and map for a specific region.
    - `POST /get_hight_regions_area`: Get high-confidence fire data.
    - `POST /draw_boxes_fire`: Upload an image to detect fire.

3.  **Access Documentation**
    Once the server is running, visit `http://127.0.0.1:8000/docs` for the interactive Swagger UI.
