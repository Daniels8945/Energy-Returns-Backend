import datetime
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
#  Below is an example structure of the expected payload

    def save_feeder_metrics(
            self,
            session: Session,
            # snapshot_time: datetime,
            feeder_data: dict, zone_name: str,
            trading_point_name: str
    ) -> bool:
        """ 
            Save feeder metrics to the database.
            Idempotently save feeder metrics.
            Returns True if inserted, False if updated.
        """
        # records = []

        stmt = select(FeederMetrics).where(
            FeederMetrics.feeder_external_id == feeder_data["feederId"],
            # FeederMetrics.recorded_at == snapshot_time
        )
        existing = session.exec(stmt).first()

        if existing:
            existing.consumption_kwh = feeder_data["actualEnergyConsumption"]
            existing.uptime_hours = feeder_data["upTimeHours"]
            existing.status = feeder_data["status"]
            # session.add(existing) # Avoid duplicate entries for the same snapshot time
            return False
        else:
            record = FeederMetrics(
                feeder_external_id=feeder_data["feederId"],
                feeder_name=feeder_data["name"],
                consumption_kwh=feeder_data["actualEnergyConsumption"],
                uptime_hours=feeder_data["upTimeHours"],
                voltage_class=feeder_data["voltageClass"],
                station=feeder_data["station"],
                status=feeder_data["status"],
                # recorded_at=snapshot_time,
                zone=zone_name,
                trading_point=trading_point_name,
            )
            session.add(record)
            # records.append(record)
            # session.commit()
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
                        # feeder_data={
                        #     "id": feeder_id,
                        #     **feeder_data
                        # },
                        zone_name=zone["name"],
                        trading_point_name=tp["name"],
                        # snapshot_time=snapshot_time
                    )

                    if inserted:
                        inserts += 1
                    else:
                        updates += 1
         
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