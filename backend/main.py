import os
import socketio
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, Dict
import uvicorn
from datetime import datetime
from session_manager import RideSession
import database

load_dotenv()

API_KEY = os.getenv("API_KEY", "change_me_to_a_secure_random_key")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

class Location(BaseModel):
    lat: float
    lon: float

class StartRideRequest(BaseModel):
    startLocation: Location
    endLocation: Location

class EndRideRequest(BaseModel):
    sessionId: str

class TelemetryRequest(BaseModel):
    sessionId: str
    location: Location
    speed: float
    deviation: Optional[float] = 0.0
    accuracy: Optional[float] = 0.0
    timestamp: Optional[int] = None

app = FastAPI()

database.init_db()

sessions: Dict[str, RideSession] = {}

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key or api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return api_key

def cleanup_stale_sessions():
    cutoff = datetime.now().timestamp() - 7200
    active_sids = list(sessions.keys())
    count = 0
    
    for sid in active_sids:
        session = sessions[sid]
        last_ts = getattr(session, 'last_timestamp', 0) / 1000.0
        if last_ts == 0: last_ts = session.start_time.timestamp()
        
        if last_ts < cutoff:
            print(f"CLEANUP: Closing stale session {sid}")
            session.status = "ABANDONED"
            database.update_ride_status(sid, "ABANDONED")
            del sessions[sid]
            count += 1
            
    if count > 0:
        print(f"Cleanup: Removed {count} stale sessions.")

def load_active_rides():
    cleanup_stale_sessions()
    
    active_rows = database.get_active_rides()
    count = 0
    for row in active_rows:
        s_id = row['ride_session_id']
        start_loc = Location(lat=row['start_lat'], lon=row['start_lon'])
        end_loc = Location(lat=row['end_lat'], lon=row['end_lon'])
        
        session = RideSession(s_id, start_loc, end_loc)
        sessions[s_id] = session
        count += 1
    print(f"Global State Recovery: Rehydrated {count} active rides.")

load_active_rides()

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=CORS_ORIGINS)
socket_app = socketio.ASGIApp(sio, app)

@app.get("/")
def read_root():
    return {"message": "SafeCorridor Backend Running"}

@app.post("/api/ride/start")
async def start_ride(req: StartRideRequest, api_key: str = Security(verify_api_key)):
    session_id = str(int(datetime.now().timestamp() * 1000))
    database.create_ride(session_id, req.startLocation.model_dump(), req.endLocation.model_dump())
    new_session = RideSession(session_id, req.startLocation, req.endLocation)
    sessions[session_id] = new_session
    print(f"Ride started: {session_id}")
    await sio.emit('ride_started', {
        "sessionId": session_id,
        "startLocation": req.startLocation.model_dump(),
        "endLocation": req.endLocation.model_dump()
    })
    return {"sessionId": session_id, "status": "STARTED"}

@app.post("/api/ride/telemetry")
async def ride_telemetry(req: TelemetryRequest, api_key: str = Security(verify_api_key)):
    session = sessions.get(req.sessionId)
    if not session:
        print(f"Auto-creating session for {req.sessionId}")
        start_loc = req.location
        end_loc = req.location
        database.create_ride(req.sessionId, start_loc.model_dump(), end_loc.model_dump())
        session = RideSession(req.sessionId, start_loc, end_loc)
        sessions[req.sessionId] = session
        await sio.emit('ride_started', {
            "sessionId": req.sessionId,
            "startLocation": start_loc.model_dump(),
            "endLocation": end_loc.model_dump()
        })

    result = session.update_telemetry(req)
    result['location'] = req.location.model_dump()
    await sio.emit('ride_update', result)
    return result

@app.post("/api/ride/end")
async def end_ride(req: EndRideRequest, api_key: str = Security(verify_api_key)):
    session = sessions.get(req.sessionId)
    if session:
        print(f"Ride ended: {req.sessionId}")
        session.end_ride()
        await sio.emit('ride_ended', {"sessionId": req.sessionId})
        del sessions[req.sessionId]
    return {"status": "ENDED"}

@sio.event
async def connect(sid, environ):
    print("Dashboard connected", sid)

@sio.event
async def disconnect(sid):
    print("Dashboard disconnected", sid)

if __name__ == "__main__":
    uvicorn.run("main:socket_app", host="0.0.0.0", port=3000, reload=True)
