from typing import List, Dict

def calculate_totals(feeder_readings: List, interface_readings: List):
    total_consumption = sum(r.consumption_kwh for r in feeder_readings)
    total_interface = sum(r.delivered_kwh for r in interface_readings)
    energy_return = total_interface - total_consumption
    return {
        "total_consumption": total_consumption,
        "total_interface": total_interface,
        "energy_return": energy_return,
        "return_pct": (energy_return / total_interface * 100) if total_interface else None
    }

def build_interface_allocations(interface_readings: List) -> Dict[str, float]:
    allocations = {}
    for ir in interface_readings:
        allocations[ir.interface_point] = allocations.get(ir.interface_point, 0) + ir.delivered_kwh
    return allocations

def feeder_returns(feeder_readings: List, interface_allocations: Dict[str, float], feeders_meta: List):
    rows = []
    feeder_map = {f.id: f.name for f in feeders_meta}
    for r in feeder_readings:
        feeder_name = feeder_map.get(r.feeder_id, None)
        delivered = interface_allocations.get(feeder_name, r.delivered_kwh)
        ret = delivered - r.consumption_kwh
        pct = (ret / delivered * 100) if delivered else None
        rows.append({
            "feeder_id": r.feeder_id,
            "feeder_name": feeder_name,
            "consumption_kwh": r.consumption_kwh,
            "delivered_kwh": delivered,
            "return_kwh": ret,
            "return_pct": pct,
            "estimated": r.estimated
        })
    return rows