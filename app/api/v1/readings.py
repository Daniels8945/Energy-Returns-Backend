from fastapi import APIRouter, Depends
from sqlmodel import Session
from db import get_session
from crud import get_feeder_readings_for_month, get_interface_readings_for_month, get_feeders
from services.calculations import calculate_totals, build_interface_allocations, feeder_returns

router = APIRouter(prefix="/v1/readings")


@router.get('/summary/{month}')
def month_summary(month: str, session: Session = Depends(get_session)):

    feeders = get_feeder_readings_for_month(session, month)
    interfaces = get_interface_readings_for_month(session, month)
    feeders_meta = get_feeders(session)
    totals = calculate_totals(feeders, interfaces)
    allocations = build_interface_allocations(interfaces)
    feeder_rows = feeder_returns(feeders, allocations, feeders_meta)
    return {
        "month": month,
        "totals": totals,
        "feeder_returns": feeder_rows,
        "interface_readings": [{"interface_point": i.interface_point, "delivered_kwh": i.delivered_kwh, "month": i.month} for i in interfaces],
        "feeder_count": len(feeders)
    }