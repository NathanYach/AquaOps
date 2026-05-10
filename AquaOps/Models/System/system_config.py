from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SystemConfig:
    enabled:                    bool = True
    telemetry_interval_seconds: int  = 30
    log_level:                  str  = "INFO"
    log_to_file:                bool = False
    log_to_database:            bool = False

    @staticmethod
    def from_dict(data: Optional[dict]) -> SystemConfig:
        data = data or {}
        return SystemConfig(
            enabled=data.get("enabled",                         True),
            telemetry_interval_seconds=data.get("telemetry_interval_seconds", 30),
            log_level=data.get("log_level",                     "INFO"),
            log_to_file=data.get("log_to_file",                 False),
            log_to_database=data.get("log_to_database",         False),
        )