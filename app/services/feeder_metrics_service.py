from datetime import datetime
from sqlmodel import Session
from modules.feeders import LoadFeeders


# Fetches live feeder data from external API, maps zones, and saves metrics to DB
def get_and_save_feeder_metrics_from_api(session: Session):
    snapshot_time = datetime.now().replace(minute=0, second=0, microsecond=0)
    result = LoadFeeders().map_zones_with_live_data(
        session,
        # snapshot_time
    )
    return result


#  Example payload structure:
#  []
#    {
#      "zone": "Zone A",
#      "trading_points": [
#        {
#          "name": "TP1",
#          "feeders": [
#            {
#              "feeder_id": "F1",
#              "name": "Feeder 1",
#              "station": "Station A",
#              "voltage_class": 11,
#              "consumption_kwh": 1200,
#              "uptime_hours": 24,
#              "status": "active"
#            }
#          ]
#        }
#      ]
#    }
#  ]