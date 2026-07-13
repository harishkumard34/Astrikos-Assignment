from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models, database
from typing import List, Dict
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

device_history = {}
active_alerts = []

def analyze_reading(reading: models.ReadingCreate):
    device_id = reading.device_id
    metric = reading.metric
    val = reading.value
    
    if val == 0.0:
        active_alerts.insert(0, {
            "device_id": device_id,
            "metric": metric,
            "type": "SENSOR_FAULT",
            "message": f"Value dropped to exactly 0.0. Possible sensor failure.",
            "timestamp": reading.timestamp.isoformat()
        })
        return "SENSOR_FAULT"
        
    if device_id not in device_history:
        device_history[device_id] = {}
    if metric not in device_history[device_id]:
        device_history[device_id][metric] = []
        
    history = device_history[device_id][metric]
    history.append(val)
    
    if len(history) > 5:
        history.pop(0)
        
    if len(history) == 5:
        avg = sum(history) / len(history)
        
        # Noise/Spike check
        if val > avg * 1.5 and history[-2] <= avg * 1.2:
            return "NOISE_IGNORED"
            
        # Gradual failure check
        is_increasing = all(history[i] <= history[i+1] for i in range(len(history)-1))
        diff = history[-1] - history[0]
        if is_increasing and diff > 1.5:
            active_alerts.insert(0, {
                "device_id": device_id,
                "metric": metric,
                "type": "GRADUAL_FAILURE",
                "message": f"Gradual increase detected over last 5 readings (+{diff:.1f}).",
                "timestamp": reading.timestamp.isoformat()
            })
            return "GRADUAL_WARNING"
            
    return "NORMAL"

@app.post("/ingest")
def ingest_data(reading: models.ReadingCreate, db: Session = Depends(database.get_db)):
    db_reading = models.ReadingDB(
        device_id=reading.device_id,
        metric=reading.metric,
        value=reading.value,
        timestamp=reading.timestamp.replace(tzinfo=None)
    )
    db.add(db_reading)
    db.commit()
    
    analyze_reading(reading)
    
    if len(active_alerts) > 50:
        active_alerts.pop()
        
    return {"status": "success"}

@app.get("/status")
def get_status():
    latest_state = {}
    for device, metrics in device_history.items():
        latest_state[device] = {}
        for metric, history in metrics.items():
            if history:
                latest_state[device][metric] = history[-1]
                
    return {
        "devices": latest_state,
        "alerts": active_alerts
    }
