from modules.feeders import LoadFeeders
from models import Feeder
from sqlmodel import Session, select
from models import FeederMetrics
from collections import defaultdict
from datetime import datetime
from typing import Optional


def get_feeder_snapshot(
    session: Session,
    snapshot_time: Optional[datetime] = None
):
    """
    Fetch feeder metrics grouped by:
    Zone → Trading Point → Feeders
    """

    stmt = select(FeederMetrics)

    if snapshot_time:
        stmt = stmt.where(FeederMetrics.snapshot_time == snapshot_time)
    else:
        # Default: latest snapshot
        latest_stmt = select(FeederMetrics.snapshot_time).order_by(
            FeederMetrics.snapshot_time.desc()
        )
        snapshot_time = session.exec(latest_stmt).first()
        stmt = stmt.where(FeederMetrics.snapshot_time == snapshot_time)

    records = session.exec(stmt).all()

    zones_map = defaultdict(lambda: defaultdict(list))

    for r in records:
        zones_map[r.zone][r.trading_point].append({
            "feeder_id": r.feeder_external_id,
            "name": r.feeder_name,
            "consumption_kwh": r.consumption_kwh,
            "uptime_hours": r.uptime_hours,
            "voltage_class": r.voltage_class,
            "station": r.station,
            "status": r.status
        })

    response = []

    for zone_name, trading_points in zones_map.items():
        zone_obj = {
            "zone": zone_name,
            "trading_points": []
        }

        for tp_name, feeders in trading_points.items():
            zone_obj["trading_points"].append({
                "name": tp_name,
                "feeders": feeders
            })

        response.append(zone_obj)

    return {
        "snapshot_time": snapshot_time,
        "Zone": response
    }









# Synchronizes feeders from external API into local database
def sync_feeders_from_api(
    session: Session,
    feeders: list,
    ) -> int:
    """ Sync feeders from external API into local database."""
    feeder_zone_map = LoadFeeders().build_feeder_zone_map()

    created = 0

    for f in feeders:
        external_id = f["external_feeder_id"]

        if external_id not in feeder_zone_map:
            continue  # outside trading scope

        exists = session.exec(
            select(Feeder).where(Feeder.external_feeder_id == external_id)
        ).first()

        if exists:
            continue

        feeder = Feeder(
            external_feeder_id=external_id,
            device_uid=f["device_uid"],
            name=f["name"],
            zone=feeder_zone_map[external_id]["zone"],
            trading_point=feeder_zone_map[external_id]["trading_point"],
            station=f["station"],
            voltage_level=f["voltage_level"],
            category=f["category"],
            disco=f["disco"],
            state=f["state"]
        )

        session.add(feeder)
        created += 1

    session.commit()
    return created