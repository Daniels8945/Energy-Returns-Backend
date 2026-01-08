from datetime import datetime
from sqlmodel import Session
from database.db import engine
from modules.feeders import LoadFeeders

def run_feeder_snapshot():
    """
    Runs feeder snapshot ingestion safely
    """
    service = LoadFeeders()

    with Session(engine) as session:
        result = service.map_zones_with_live_data(session)

        print(
            f"[APSCHEDULER] Snapshot completed | "
            f"Inserted: {result['inserted']} | "
            f"Updated: {result['updates']} | "
            f"Time: {datetime.utcnow()}"
        )