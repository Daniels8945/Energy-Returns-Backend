from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional

class Feeder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    voltage_level: str = "11kV"
    note: Optional[str] = None

class MonthlyReading(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    feeder_id: int = Field(foreign_key="feeder.id")
    month: str
    consumption_kwh: float
    delivered_kwh: float
    estimated: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class InterfaceReading(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    interface_point: str
    month: str
    delivered_kwh: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
