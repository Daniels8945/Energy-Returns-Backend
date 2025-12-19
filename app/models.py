from datetime import datetime
from sqlmodel import SQLModel, Field, UniqueConstraint
from typing import Optional

class Feeder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    note: Optional[str] = None

    # External identity
    external_feeder_id: int = Field(index=True, unique=True)
    device_uid: Optional[str]

    # Business identity
    name: str
    voltage_level: str
    zone: str
    trading_point: str
    station: str

    # Technical metadata
    category: Optional[str]
    disco: str
    state: str

    created_at: datetime = Field(default_factory=datetime.utcnow)

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


class FeederMetrics(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    feeder_external_id: int = Field(index=True)
    feeder_name: str


    consumption_kwh: float
    uptime_hours: float
    voltage_class: str

    station: str
    zone: str
    trading_point: str
    status: int  # 1 = online, 0 = offline

    # snapshot_time: datetime = Field(index=True)
    recorded_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        # prevents duplicates for same feeder + time
        UniqueConstraint("feeder_external_id", "recorded_at"),
    )