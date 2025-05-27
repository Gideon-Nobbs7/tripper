import requests
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

user_loc = APIRouter()


class LocationData(BaseModel):
    latitude: float
    longitude: float


@user_loc.post("/api/set-user-location")
async def set_user_location(request: Request):
    data = await request.json()
    lat = data.get("latitude")
    lng = data.get("longitude")

    print(f"Received from browser: {lat}, {lng}")
    return JSONResponse(content={"status": "success", "latitude": lat, "longitude": lng})


@user_loc.get("/", response_class=HTMLResponse)
def serve_frontend():
    with open("index.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)