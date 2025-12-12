from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from db import get_session
from crud import (
    create_interface_reading,
    get_interface_reading,
    get_interface_readings_for_month,
    update_interface_reading,
    delete_interface_reading,
)
from schemas import InterfaceReadingCreate, InterfaceReadingRead
from models import InterfaceReading

router = APIRouter(prefix="/v1/interface", tags=["interface"])

@router.post("/", response_model=InterfaceReadingRead)
def create(reading: InterfaceReadingCreate, session: Session = Depends(get_session)):
    ir = InterfaceReading(interface_point=reading.interface_point, month=reading.month, delivered_kwh=reading.delivered_kwh)
    created = create_interface_reading(session, ir)
    return created

@router.get("/month/{month}", response_model=list[InterfaceReadingRead])
def list_by_month(month: str, session: Session = Depends(get_session)):
    return get_interface_readings_for_month(session, month)

@router.get("/{reading_id}", response_model=InterfaceReadingRead)
def retrieve(reading_id: int, session: Session = Depends(get_session)):
    r = get_interface_reading(session, reading_id)
    if not r:
        raise HTTPException(status_code=404, detail="Interface reading not found")
    return r

@router.put("/{reading_id}", response_model=InterfaceReadingRead)
def update(reading_id: int, payload: InterfaceReadingCreate, session: Session = Depends(get_session)):
    data = payload.dict()
    updated = update_interface_reading(session, reading_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Interface reading not found")
    return updated

@router.delete("/{reading_id}")
def delete(reading_id: int, session: Session = Depends(get_session)):
    ok = delete_interface_reading(session, reading_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Interface reading not found")
    return {"ok": True}