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
        result = service.ingest_all_feeders(session)

        print(
            f"[APSCHEDULER] Snapshot completed | "
            f"Inserted: {result['inserted']} | "
            f"Updated: {result['updated']} | "
            f"Time: {datetime.utcnow()}"
        )