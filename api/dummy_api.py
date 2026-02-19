from __future__ import annotations

from datetime import date
from fastapi import FastAPI

app = FastAPI(title="Dummy Retail Tools API", version="0.1")

STORE_HOURS = {
    "ST-CHI-01": {"store_id": "ST-CHI-01", "city": "Chicago", "hours": "10:00 AM – 8:00 PM"},
    "ST-AUS-02": {"store_id": "ST-AUS-02", "city": "Austin", "hours": "10:00 AM – 9:00 PM"},
}

INVENTORY = {
    ("ST-CHI-01", "SKU-HEADPHONES-01"): {"available": True, "qty": 7, "pickup_eta": "Today"},
    ("ST-CHI-01", "SKU-LAPTOP-13"): {"available": False, "qty": 0, "pickup_eta": "3–5 days"},
}

@app.get("/store_hours")
def store_hours(store_id: str):
    return STORE_HOURS.get(store_id, {"store_id": store_id, "hours": "Unknown (store not found)"})

@app.get("/inventory")
def inventory(store_id: str, sku: str):
    data = INVENTORY.get((store_id, sku), {"available": False, "qty": 0, "pickup_eta": "Unknown"})
    return {"store_id": store_id, "sku": sku, **data}

@app.get("/appointment_slots")
def appointment_slots(store_id: str, service: str):
    slots = [
        {"date": str(date.today()), "time": "11:00", "service": service},
        {"date": str(date.today()), "time": "15:30", "service": service},
        {"date": str(date.today()), "time": "18:10", "service": service},
    ]
    return {"store_id": store_id, "service": service, "slots": slots}
