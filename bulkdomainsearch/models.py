"""
Data models and typed structures for domain scan results.
"""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional, Dict, Any


class DomainStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    TAKEN = "TAKEN"
    INVALID = "INVALID"
    RATE_LIMITED = "RATE_LIMITED"
    ERROR = "ERROR"


@dataclass(frozen=True)
class DomainResult:
    domain: str
    status: DomainStatus
    http_code: int
    details: str
    elapsed_ms: int
    length: int
    error: Optional[str] = None

    @property
    def is_available(self) -> bool:
        return self.status == DomainStatus.AVAILABLE

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass
class ScanSummary:
    total: int
    available_count: int
    taken_count: int
    invalid_count: int
    error_count: int
    total_time_seconds: float

    @property
    def speed_qps(self) -> float:
        if self.total_time_seconds <= 0:
            return 0.0
        return round(self.total / self.total_time_seconds, 2)
