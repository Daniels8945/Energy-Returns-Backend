from sqlmodel import select, Session
from models import Feeder, MonthlyReading, InterfaceReading
from typing import Optional, List


def create_feeder(session: Session, feeder: Feeder):
    session.add(feeder)
    session.commit()
    session.refresh(feeder)
    return feeder

def create_monthly_reading(session: Session, reading: MonthlyReading):
    session.add(reading)
    session.commit()
    session.refresh(reading)
    return reading

def create_interface_reading(session: Session, reading: InterfaceReading):
    session.add(reading)
    session.commit()
    session.refresh(reading)
    return reading

def get_feeder_readings_for_month(session: Session, month: str):
    stmt = select(MonthlyReading).where(MonthlyReading.month==month)
    return session.exec(stmt).all()

def get_interface_readings_for_month(session: Session, month: str):
    stmt = select(InterfaceReading).where(InterfaceReading.month==month)
    return session.exec(stmt).all()

def get_monthly_readings_for_feeder(session: Session, feeder_id: int) -> List[MonthlyReading]:
    stmt = select(MonthlyReading).where(MonthlyReading.feeder_id == feeder_id)
    return session.exec(stmt).all()

def get_feeders(session: Session):
    stmt = select(Feeder)
    return session.exec(stmt).all()

def get_feeder(session: Session, feeder_id: int) -> Optional[Feeder]:
    return session.get(Feeder, feeder_id)


def update_feeder(session: Session, feeder_id: int, data: dict) -> Optional[Feeder]:
    f = session.get(Feeder, feeder_id)
    if not f:
        return None
    for k, v in data.items():
        setattr(f, k, v)
    session.add(f)
    session.commit()
    session.refresh(f)
    return f

def delete_feeder(session: Session, feeder_id: int) -> bool:
    f = session.get(Feeder, feeder_id)
    if not f:
        return False
    session.delete(f)
    session.commit()
    return True



# INTERFACE READINGS
def create_interface_reading(session: Session, reading: InterfaceReading) -> InterfaceReading:
    session.add(reading)
    session.commit()
    session.refresh(reading)
    return reading

def get_interface_reading(session: Session, reading_id: int) -> Optional[InterfaceReading]:
    return session.get(InterfaceReading, reading_id)

def get_interface_readings_for_month(session: Session, month: str) -> List[InterfaceReading]:
    stmt = select(InterfaceReading).where(InterfaceReading.month == month)
    return session.exec(stmt).all()

def update_interface_reading(session: Session, reading_id: int, data: dict) -> Optional[InterfaceReading]:
    r = session.get(InterfaceReading, reading_id)
    if not r:
        return None
    for k, v in data.items():
        setattr(r, k, v)
    session.add(r)
    session.commit()
    session.refresh(r)
    return r

def delete_interface_reading(session: Session, reading_id: int) -> bool:
    r = session.get(InterfaceReading, reading_id)
    if not r:
        return False
    session.delete(r)
    session.commit()
    return True


# MONTHLY READINGS
def create_monthly_reading(session: Session, reading: MonthlyReading) -> MonthlyReading:
    session.add(reading)
    session.commit()
    session.refresh(reading)
    return reading 

def get_monthly_reading(session: Session, reading_id: int) -> Optional[MonthlyReading]:
    return session.get(MonthlyReading, reading_id)


def get_monthly_readings_for_month(session: Session, month: str) -> List[MonthlyReading]:
    stmt = select(MonthlyReading).where(MonthlyReading.month == month)
    return session.exec(stmt).all()

def update_monthly_reading(session: Session, reading_id: int, data: dict) -> Optional[MonthlyReading]:
    r = session.get(MonthlyReading, reading_id)
    if not r:
        return None
    for k, v in data.items():
        setattr(r, k, v)
    session.add(r)
    session.commit()
    session.refresh(r)
    return r

def delete_monthly_reading(session: Session, reading_id: int) -> bool:
    r = session.get(MonthlyReading, reading_id)
    if not r:
        return False
    session.delete(r)
    session.commit()
    return True