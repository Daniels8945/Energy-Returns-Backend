from modules.feeders import LoadFeeders
from sqlmodel import select, Session
from models import Feeder

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