from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from db import get_session
from services.feeder_metrics_service import get_and_save_feeder_metrics_from_api
from models import FeederMetrics

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
