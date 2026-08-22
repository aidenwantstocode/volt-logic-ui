from typing import Optional, List, Literal, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class TelemetryIn(BaseModel):
    vehicle_id: str = Field(default="EV-402", max_length=32, min_length=1, description="Unique vehicle or battery pack ID")
    company: Optional[str] = Field(default="PT. Logistik Nusantara Express", max_length=128, description="Operating company name")
    battery_type: Optional[str] = Field(default="Lithium-Ion 400V (NMC)", max_length=128, description="Battery pack chemistry & specification")

    # 4 Key Features from Kata_Mamah_WIN_AIC.ipynb
    capacity: float = Field(..., ge=0.0, le=10.0, description="Battery capacity (Ah or normalized ratio)")
    re: float = Field(..., ge=0.0, le=5.0, description="Electrolyte / Ohmic internal resistance Re (Ω)")
    rct: float = Field(..., ge=0.0, le=5.0, description="Charge transfer resistance Rct (Ω)")
    ambient_temperature: float = Field(..., ge=-50.0, le=150.0, description="Ambient / operational temperature (°C)")

    # Optional auxiliary / legacy fields
    voltage: Optional[float] = Field(default=None, ge=0.0, le=1000.0)
    current: Optional[float] = Field(default=None, ge=-500.0, le=500.0)
    temperature: Optional[float] = Field(default=None)
    internal_resistance: Optional[float] = Field(default=None)

    model_config = ConfigDict(extra="ignore")

class PredictResponse(BaseModel):
    status: Literal["HEALTHY", "WARNING", "CRITICAL"]
    status_id: str = Field(..., description="Label dalam bahasa Indonesia ('aman', 'perlu di test lebih lanjut', 'tidak aman')")
    confidence: str
    route: str
    model_version: str
    features: Optional[Dict[str, float]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class HistoryCreateRequest(BaseModel):
    vehicle_id: str = Field(..., max_length=32, min_length=1)
    company: str = Field(..., max_length=128, min_length=1)
    battery_type: str = Field(..., max_length=128, min_length=1)
    capacity: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    re: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    rct: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    ambient_temperature: Optional[float] = Field(default=None, ge=-50.0, le=150.0)
    voltage: Optional[float] = Field(default=None, ge=0.0, le=1000.0)
    current: Optional[float] = Field(default=None, ge=-500.0, le=500.0)
    temperature: Optional[float] = Field(default=None, ge=-50.0, le=200.0)
    resistance: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    status: Literal["HEALTHY", "WARNING", "CRITICAL"]
    confidence: Optional[str] = Field(default=None, max_length=32)
    model_version: Optional[str] = Field(default=None, max_length=64)

    model_config = ConfigDict(extra="ignore")

class HistoryItem(BaseModel):
    id: int
    vehicle_id: str
    company: str
    battery_type: str
    capacity: Optional[float] = None
    re: Optional[float] = None
    rct: Optional[float] = None
    ambient_temperature: Optional[float] = None
    voltage: Optional[float] = None
    current: Optional[float] = None
    temperature: Optional[float] = None
    resistance: Optional[float] = None
    status: str
    confidence: Optional[str] = None
    model_version: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HealthResponse(BaseModel):
    ok: bool = True
    app: str = "VOLT-LOGIC Battery Telemetry API"
    version: str = "2.0.0"
