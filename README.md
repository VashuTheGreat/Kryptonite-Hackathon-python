# FireWatch Pro – API Documentation

## Local Setup

### Steps

1. **Create & activate virtual environment**

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1   # PowerShell
```

2. **Environment variables**

* Copy `.env.example` to `.env`
* Fill required keys (AI keys, DB config, etc.)

3. **Install dependencies**

```bash
uv pip compile pyproject.toml -o requirements.txt 
pip install -r requirements.txt
```

4. **Run locally**

```bash
uvicorn index:app --reload
```

Server will start at:

```
http://127.0.0.1:8000
```

---

## API Endpoints

### Home

`GET /`

* **Description:** Base route to verify API is active
* **Response**

```json
{
  "message": "FireWatch Pro Active"
}
```

---

### Health Check

`GET /health`

* **Description:** Check system health
* **Response**

```json
{
  "message": "success"
}
```

---

## AI Chat Endpoints

### Chat with FireWatch AI

`POST /chat`

* **Description:** Send a message to the AI assistant
* **Request Body**

```json
{
  "user_id": "string",
  "message": "string"
}
```

* **Response**

```json
{
  "response": "AI generated reply"
}
```

> `user_id` is used to maintain conversation memory per user.

---

### Get Chat History

`GET /chat/history/{user_id}`

* **Description:** Fetch complete chat history for a user
* **Response**

```json
{
  "history": [
    {
      "role": "user",
      "content": "Hello"
    },
    {
      "role": "ai",
      "content": "Hi! How can I help?"
    }
  ]
}
```

---

## Fire Intelligence Endpoints

### Get Fire Locations Map

`POST /get_locations`

* **Description:** Fetch FIRMS satellite fire data and return interactive map HTML

* **Parameters (query/form):**

  * `country` (string, default: `india`)
  * `state` (string, default: `up`)
  * `source` (string, default: `VIIRS_SNPP_NRT`)
  * `day_range` (integer, default: `3`)

* **Response**

```json
{
  "html": "<html>...</html>"
}
```

---

### Get High-Confidence Fire Regions

`POST /get_hight_regions_area`

* **Description:** Returns only high-confidence (`h`) fire points

* **Parameters (query/form):**

  * `country` (string)
  * `state` (string)
  * `source` (string)
  * `day_range` (integer)

* **Response**

```json
{
  "data": "[{...}]"
}
```

> Data is returned as a JSON string for frontend compatibility.

---

### Detect Fire Bounding Boxes (YOLO)

`POST /draw_boxes_fire`

* **Description:** Upload satellite image and detect fire regions using YOLO

* **Request Type:** `multipart/form-data`

* **Body:**

  * `file` (image file)

* **Response**

```json
{
  "data": "<base64_encoded_image>"
}
```

> Decode base64 on the client side to display the processed image.

---

## System Notes

* CORS enabled for all origins
* AI system initializes on startup using FastAPI lifespan
* Memory-based conversation handling via `user_id`
* Supports near real-time fire monitoring

---

## Developer Tools

* Swagger UI: `http://127.0.0.1:8000/docs`

---

## Status

🔥 **FireWatch Pro is production-ready for hackathons and demos**
