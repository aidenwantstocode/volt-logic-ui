from sqlalchemy import Column, Integer, Text, Numeric, DateTime, Index, CheckConstraint
from sqlalchemy.sql import func
try:
    from backend.database import Base
except ImportError:
    from database import Base

class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vehicle_id = Column(Text, nullable=False)
    company = Column(Text, nullable=False)
    battery_type = Column(Text, nullable=False)
    capacity = Column(Numeric(precision=10, scale=4), nullable=True)
    re = Column(Numeric(precision=10, scale=4), nullable=True)
    rct = Column(Numeric(precision=10, scale=4), nullable=True)
    ambient_temperature = Column(Numeric(precision=10, scale=2), nullable=True)
    voltage = Column(Numeric(precision=10, scale=3), nullable=True)
    current = Column(Numeric(precision=10, scale=3), nullable=True)
    temperature = Column(Numeric(precision=10, scale=3), nullable=True)
    resistance = Column(Numeric(precision=10, scale=4), nullable=True)
    status = Column(Text, nullable=False)
    confidence = Column(Text, nullable=True)
    model_version = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("status IN ('HEALTHY', 'WARNING', 'CRITICAL')", name="check_inspection_status"),
        Index("ix_inspections_company_battery_type", "company", "battery_type"),
    )
