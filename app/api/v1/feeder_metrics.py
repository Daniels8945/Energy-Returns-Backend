from fastapi import APIRouter, Depends, Query, Path
from sqlmodel import Session, select
from db import get_session
from services.feeder_metrics_service import get_and_save_feeder_metrics_from_api, insert_new_feeder_data
from models import FeederMetrics
from datetime import datetime
from services.zone_mapping import get_feeder_snapshot
from datetime import datetime, date
from services.get_feeder_history import get_feeder_history


router = APIRouter(prefix="/v1/metrics", tags=["Feeder Metrics"])


# THIS ENDPOINT TRIGGERS DATA FETCHING FROM EXTERNAL API AND SAVES TO DB
# END POINT TO GET LATEST FEEDER METRICS FROM EXTERNAL API AND SAVE TO DB

@router.get("/get_latest_feeders_data_from_api")
def get_latest_metrics(session: Session = Depends(get_session)):
    count = get_and_save_feeder_metrics_from_api(session)
    return {"status": "ok", "records_saved": count}


# ENDPOINT TO LIST ALL FEEDER METRICS FROM DB To FRONTEND TABLE
@router.get("/feeder_metrics")
def list_feeder_metrics(session: Session = Depends(get_session)):
    return session.exec(
        select(FeederMetrics).order_by(FeederMetrics.recorded_at.desc())).all()


@router.get("/ingest_feeder_update")
def ingest_feeder_update(session: Session = Depends(get_session)):
    update = insert_new_feeder_data(session)
    return {"status": "New feeder data inserted", "update_saved": update}


# This end point gets all the feeders by zone and trading point 

@router.get("/snapshot")
def get_feeder_snapshot_route(
    snapshot_time: datetime | None = Query(
        default=None,
        description="Exact snapshot time (UTC). If omitted, latest snapshot is returned."
    ),
    session: Session = Depends(get_session)
):
    data = get_feeder_snapshot(
        session=session,
        snapshot_time=snapshot_time
    )

    return {
        "status": "ok",
        "data": data
    }



@router.get("/{feeder_id}/history")
def feeder_history(
    feeder_id: int = Path(..., description="External feeder ID"),
    from_date: date | None = Query(default = None, alias="from", description="Start date (YYYY-MM-DD)"),
    to_date: date | None = Query(default = None, alias="to", description="End date (YYYY-MM-DD)"),
    session: Session = Depends(get_session)
):
    data = get_feeder_history(
        session=session,
        feeder_id=feeder_id,
        from_date=from_date,
        to_date=to_date
    )

    return {
        "status": "ok",
        "feeder_id": feeder_id,
        "from": from_date,
        "to": to_date,
        "count": len(data),
        "data": data
    }