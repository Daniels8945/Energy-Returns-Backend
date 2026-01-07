from datetime import datetime
from dotenv import load_dotenv
import os
import requests
from fastapi import status
import json
from sqlmodel import Session, select
from models import FeederMetrics


load_dotenv()


with open(os.path.join(os.path.dirname(__file__), 'zones.json')) as f:
    zones = json.load(f)
    
class LoadFeeders():

    url = f"https://feedercomplianceprodapi.azurewebsites.net/api/v1/Energy/feeder-online-data?apiKey="

    def __init__(self):
        self.api_key = os.getenv("API_KEY")


# Fetch raw feeder data from external API
    def fetch(self):
        response  = requests.get(
            self.url + self.api_key)
        if response.status_code == status.HTTP_200_OK:
            return response.json()["data"]
        else:
            return []
        
        
# Normalize raw feeder data into structured format
    def normalize(self):
        raw = self.fetch()
        feeders = []
        for f in raw:
            feeders.append({
                "external_feeder_id": f["feederId"],
                "device_uid": f.get("deviceUID"),
                "name": f["name"],
                "station": f["station"],
                "voltage_level": f["voltageClass"],
                "category": f.get("feederCategory"),
                "consumption_kwh": f["actualEnergyConsumption"],
                "uptime_hours": f["upTimeHours"],
                "status": f["status"],
                "interface": f.get("motherFeederName"),
                "disco": f["disco"],
                "state": f["state"],
            })
        return feeders


#  Saves feeder metrics to the database
#  Payload is expected to be a list of zones, each containing trading points and feeders with their metrics

    def save_feeder_metrics(
            self,
            session: Session,
            snapshot_time: datetime,
            feeder_data: dict,
            zone_name: str,
            trading_point_name: str
    ) -> bool:
        """ 
            Save feeder metrics to the database.
            Idempotently save feeder metrics.
            Returns True if inserted, False if updated.
        """

        stmt = select(FeederMetrics).where(
            FeederMetrics.feeder_external_id == feeder_data["feederId"],
            FeederMetrics.snapshot_time == snapshot_time
        )
        existing = session.exec(stmt).first()

        if existing:
            existing.consumption_kwh = feeder_data["actualEnergyConsumption"]
            existing.uptime_hours = feeder_data["upTimeHours"]
            existing.status = feeder_data["status"]
            return False
        # else:
        record = FeederMetrics(
            feeder_external_id=feeder_data["feederId"],
            feeder_name=feeder_data["name"],
            consumption_kwh=feeder_data["actualEnergyConsumption"],
            uptime_hours=feeder_data["upTimeHours"],
            voltage_class=feeder_data["voltageClass"],
            station=feeder_data["station"],
            status=feeder_data["status"],
            snapshot_time=snapshot_time,
            zone=zone_name,
            trading_point=trading_point_name,
        )
        session.add(record)
        return True


# Create an index of feeders by their external IDs
    def index_feeders(self):    
        return {f["feederId"]: f for f in self.fetch()}
    
# This function gets the api data then pull out zones and map with live feeder data
# Map zones with live feeder data

    def  map_zones_with_live_data(self, session: Session):
        feeder_index = self.index_feeders()
        output = []
        inserts = 0
        updates = 0

        snapshot_time = datetime.utcnow().replace(minute=0, second=0, microsecond=0)


        for zone in zones:
            zone_obj = {
                "zone": zone["name"],
                "trading_points": []
            }

            for tp in zone["trading_points"]:

                feeders = []

                for feeder_id in tp["feeder_ids"]:
                    feeder_data = feeder_index.get(feeder_id)

                    # Skip if feeder data not found
                    if not feeder_data:
                        continue

                    inserted = self.save_feeder_metrics(
                        session=session,
                        feeder_data=feeder_data,
                        zone_name=zone["name"],
                        trading_point_name=tp["name"],
                        snapshot_time=snapshot_time
                    )
                    inserts += int(inserted)
                    updates += int(not inserted)
         
                    feeders.append({
                        "feeder_id": feeder_id,
                        "name": feeder_data["name"],
                        "consumption_kwh": feeder_data["actualEnergyConsumption"],
                        "uptime_hours": feeder_data["upTimeHours"],
                        "voltage_class": feeder_data["voltageClass"],
                        "station": feeder_data["station"],
                        "status": feeder_data["status"]
                    })

                if feeders:
                    zone_obj["trading_points"].append({
                        "name": tp["name"],
                        "feeders": feeders
                    })

            if zone_obj["trading_points"]:
                output.append(zone_obj)
                
        session.commit()

        return {
            "Zone": output,
            "inserted": inserts,
            "updates": updates,
            # "snapshot_time": snapshot_time
        }


# save all feeder data into a new row from the API

    def ingest_all_feeders(self, 
                           session: Session,
            ):
        
        def set_snapshot_time():
            now = datetime.utcnow()
            minute = (now.minute // 5) * 5
            return now.replace(minute= minute, second=0, microsecond=0)
        
        snapshot_time = set_snapshot_time()

        feeder_index = self.index_feeders()

        inserted = 0
        updated = 0

        for zone in zones:
            zone_name = zone["name"]

            # location = feeder_zone_map.get(feeder_id)
            for trading_point in zone["trading_points"]:
                tp_name = trading_point["name"]

                for feeder_id in trading_point["feeder_ids"]:
                    feeder = feeder_index.get(feeder_id)

                    if not feeder: # if feeder not mapped in zone.json file
                        continue

                    feeder_payload = {
                        "feederId": feeder_id,
                        "name": feeder["name"],
                        "actualEnergyConsumption": feeder["actualEnergyConsumption"],
                        "upTimeHours": feeder["upTimeHours"],
                        "voltageClass": feeder["voltageClass"],
                        "station": feeder["station"],
                        "status": feeder["status"],
                    }

                    inserted_flag = self.save_feeder_metrics(
                        session=session,
                        feeder_data=feeder_payload,
                        zone_name=zone_name,
                        trading_point_name=tp_name,
                        snapshot_time=snapshot_time
                    )
                    inserted += int(inserted_flag)
                    updated += int(not inserted_flag)

        session.commit()

        return {
            # "trading_points": location["trading_points"],
            "snapshot_time": snapshot_time,
            "inserted": inserted,
            "updated": updated
        }



# Build a mapping of feeder IDs to their respective zones and trading points
    def build_feeder_zone_map(self) -> dict:

        mapping = {}

        for zone in zones:
            zone_name = zone["name"]
            for tp in zone["trading_points"]:
                tp_name = tp["name"]
                for feeder_id in tp["feeder_ids"]:
                    mapping[feeder_id] = {
                        "zone": zone_name,
                        "trading_point": tp_name
                    }
        return mapping









# snapshot_time = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
# feeders = self.fetch()

# feeder_zone_map = self.build_feeder_zone_map()
# live_feeders = self.fetch()




# stmt = select(FeederMetrics).where(
#     FeederMetrics.feeder_external_id == feeder["feederId"],
#     FeederMetrics.recorded_at == snapshot_time
# )

# existing = session.exec(stmt).first()

# if existing:
#     existing.consumption_kwh = feeder["actualEnergyConsumption"]
#     existing.uptime_hours = feeder["upTimeHours"]
#     existing.status = feeder["status"]
#     updated += 1
#     continue

# record = FeederMetrics(
#     feeder_external_id=feeder["feederId"],
#     feeder_name=feeder["name"],
#     station=feeder["station"],
#     voltage_class=feeder["voltageClass"],
#     consumption_kwh=feeder["actualEnergyConsumption"],
#     uptime_hours=feeder["upTimeHours"],
#     status=feeder["status"],
#     snapshot_time=snapshot_time
# )

# session.add(record)
# inserted += 1


# Example fields from external API:

# "external_feeder_id": f["feederId"],
# "upTimeHours": f["upTimeHours"],
# "voltageUptimeHours": f["voltageUptimeHours"],
# "voltageStatus": f["voltageStatus"],
# "status": f["status"],
# "status_text": "Online" if f["status"] == 1 else "Offline",
# "station": f["station"],
# "feeder_id": f["feederId"],
# "feeder_name": f["name"],
# "station": f["station"],
# "interface": f["motherFeederName"],
# "voltage_level": f["voltageClass"],
# "category": f["feederCategory"],
# "consumption_kwh": f["actualEnergyConsumption"],
# "disco": f["disco"],
# "state": f["state"]