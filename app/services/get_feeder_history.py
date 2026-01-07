from sqlmodel import Session, select
from datetime import datetime, date
from models import FeederMetrics

def get_feeder_history(
    session: Session,
    feeder_id: int,
    from_date: date | None = None,
    to_date: date | None = None
):
    """
    Fetch historical readings for a feeder
    """

    stmt = select(FeederMetrics).where(
        FeederMetrics.feeder_external_id == feeder_id
    )

    if from_date:
        stmt = stmt.where(
            FeederMetrics.snapshot_time >= datetime.combine(
                from_date, datetime.min.time()
            )
        )

    if to_date:
        stmt = stmt.where(
            FeederMetrics.snapshot_time <= datetime.combine(
                to_date, datetime.max.time()
            )
        )

    stmt = stmt.order_by(FeederMetrics.snapshot_time.asc())

    records = session.exec(stmt).all()

    return [
        {
            "snapshot_time": r.snapshot_time,
            "consumption_kwh": r.consumption_kwh,
            "uptime_hours": r.uptime_hours,
            "status": r.status,
            "station": r.station,
            "voltage_class": r.voltage_class,
            "zone": r.zone,
            "trading_point": r.trading_point
        }
        for r in records
    ]

# def get_feeder_history(
#     session: Session,
#     feeder_id: int,
#     from_date: date,
#     to_date: date
# ):
#     """
#     Fetch historical readings for a feeder between two dates
#     """

#     if from_date and to_date:
#         stmt = (
#             select(FeederMetrics)
#             .where(FeederMetrics.feeder_external_id == feeder_id)
#             .where(FeederMetrics.snapshot_time >= datetime.combine(from_date, datetime.min.time()))
#             .where(FeederMetrics.snapshot_time <= datetime.combine(to_date, datetime.max.time()))
#             .order_by(FeederMetrics.snapshot_time.asc())
#         )
#     else:
#         feeder_data = (select(FeederMetrics)
#         .where(FeederMetrics.feeder_external_id == feeder_id))
#     records = session.exec(stmt).all()

#     return [
#         {
#             "snapshot_time": r.snapshot_time,
#             "consumption_kwh": r.consumption_kwh,
#             "uptime_hours": r.uptime_hours,
#             "status": r.status,
#             "station": r.station,
#             "voltage_class": r.voltage_class,
#             "zone": r.zone,
#             "trading_point": r.trading_point
#         }
#         for r in records
#     ]
