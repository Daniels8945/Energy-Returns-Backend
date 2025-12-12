from pydantic import BaseModel
from typing import Optional

class FeederCreate(BaseModel):
    name: str
    voltage_level: Optional[str] = "11kV"
    note: Optional[str] = None

class MonthlyReadingCreate(BaseModel):
    feeder_id: int
    month: str
    delivered_kwh: float
    consumption_kwh: float
    # delivered_kwh: Optional[float] = None 
    estimated: Optional[bool] = False

class InterfaceReadingCreate(BaseModel):
    interface_point: str
    month: str
    delivered_kwh: float


class FeederRead(FeederCreate):
    id: int

class MonthlyReadingRead(MonthlyReadingCreate):
    id: int

class InterfaceReadingRead(InterfaceReadingCreate):
    id: int
