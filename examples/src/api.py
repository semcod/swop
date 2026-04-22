from fastapi import FastAPI
from src.models import Device, Reading

app = FastAPI()

@app.get("/devices")
def list_devices():
    return {"devices": []}

@app.post("/readings")
def create_reading(reading: Reading):
    return {"id": reading.id, "value": reading.value}