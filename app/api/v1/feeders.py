from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from db import get_session
from crud import create_feeder, get_feeder, get_feeders, update_feeder, delete_feeder
from schemas import FeederCreate, FeederRead
from models import Feeder

router = APIRouter(prefix="/v1/feeders", tags=["feeders"])

@router.post("/", response_model=FeederRead)
def create(f_payload: FeederCreate, session: Session = Depends(get_session)):
    f = Feeder(name=f_payload.name, voltage_level=f_payload.voltage_level, note=f_payload.note)
    created = create_feeder(session, f)
    return created

@router.get("/", response_model=list[FeederRead])
def list_feed(session: Session = Depends(get_session)):
    return get_feeders(session)

@router.get("/{feeder_id}", response_model=FeederRead)
def retrieve(feeder_id: int, session: Session = Depends(get_session)):
    f = get_feeder(session, feeder_id)
    if not f:
        raise HTTPException(status_code=404, detail="Feeder not found")
    return f

@router.put("/{feeder_id}", response_model=FeederRead)
def update(feeder_id: int, payload: FeederCreate, session: Session = Depends(get_session)):
    data = payload.dict()
    updated = update_feeder(session, feeder_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Feeder not found")
    return updated

@router.delete("/{feeder_id}")
def remove(feeder_id: int, session: Session = Depends(get_session)):
    ok = delete_feeder(session, feeder_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Feeder not found")
    return {"ok": True}