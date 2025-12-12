from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from db import get_session
from crud import (
    create_monthly_reading,
    get_monthly_reading,
    get_monthly_readings_for_month,
    get_monthly_readings_for_feeder,
    update_monthly_reading,
    delete_monthly_reading,
)
from schemas import MonthlyReadingCreate, MonthlyReadingRead
from models import MonthlyReading

router = APIRouter(prefix="/v1/monthly", tags=["monthly"])

@router.post("/", response_model=MonthlyReadingRead)
def create(reading: MonthlyReadingCreate, session: Session = Depends(get_session)):
    mr = MonthlyReading(feeder_id=reading.feeder_id, month=reading.month, consumption_kwh=reading.consumption_kwh, delivered_kwh=reading.delivered_kwh, estimated=reading.estimated)
    created = create_monthly_reading(session, mr)
    return created

@router.get("/month/{month}", response_model=list[MonthlyReadingRead])
def list_by_month(month: str, session: Session = Depends(get_session)):
    return get_monthly_readings_for_month(session, month)

@router.get("/feeder/{feeder_id}", response_model=list[MonthlyReadingRead])
def list_by_feeder(feeder_id: int, session: Session = Depends(get_session)):
    return get_monthly_readings_for_feeder(session, feeder_id)

@router.get("/{reading_id}", response_model=MonthlyReadingRead)
def retrieve(reading_id: int, session: Session = Depends(get_session)):
    r = get_monthly_reading(session, reading_id)
    if not r:
        raise HTTPException(status_code=404, detail="Reading not found")
    return r

@router.put("/{reading_id}", response_model=MonthlyReadingRead)
def update(reading_id: int, payload: MonthlyReadingCreate, session: Session = Depends(get_session)):
    data = payload.dict()
    updated = update_monthly_reading(session, reading_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Reading not found")
    return updated

@router.delete("/{reading_id}")
def delete(reading_id: int, session: Session = Depends(get_session)):
    ok = delete_monthly_reading(session, reading_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Reading not found")
    return {"ok": True}