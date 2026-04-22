from dataclasses import dataclass
from datetime import datetime

@dataclass
class Device:
    id: str
    serial: str
    status: str = "active"

@dataclass
class Reading:
    id: str
    device_id: str
    value: float
    unit: str = "celsius"
    timestamp: datetime