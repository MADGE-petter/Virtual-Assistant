"""
Alert Types - Định nghĩa Enums và Dataclasses
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class AlertLevel(Enum):
    """Mức độ cảnh báo"""
    WARNING = "warning"      # Vàng
    CRITICAL = "critical"    # Đỏ
    DANGER = "danger"        # Đỏ đậm
    INFO = "info"           # Xanh


@dataclass
class AlertThreshold:
    """Ngưỡng cảnh báo"""
    metric: str           # cpu, ram, disk, battery
    warning: float        # Ngưỡng warning
    critical: float       # Ngưỡng critical
    danger: Optional[float] = None  # Ngưỡng danger (optional)


@dataclass
class Alert:
    """Đối tượng cảnh báo"""
    id: str
    level: AlertLevel
    metric: str
    message: str
    value: float
    timestamp: datetime
    acknowledged: bool = False
