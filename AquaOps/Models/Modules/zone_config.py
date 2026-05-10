from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from AquaOps.Models.Modules.workflow_config import WorkflowConfig
from AquaOps.Models.Safety.safety_config import SafetyPolicy


# ---------------------------------------------------------------------------
# Zone Device Reference
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ZoneDeviceConfig:
    """Reference to a logical device assigned to this zone."""
    device_id: str = ""
    node:      str = ""
    type:      str = ""

    @staticmethod
    def from_dict(device_id: str, data: Optional[dict]) -> ZoneDeviceConfig:
        data = data or {}
        return ZoneDeviceConfig(
            device_id=device_id,
            node=data.get("node", ""),
            type=data.get("type", ""),
        )


# ---------------------------------------------------------------------------
# Zone Sensor Reference
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ZoneSensorConfig:
    """Reference to a logical sensor assigned to this zone."""
    sensor_id: str = ""
    node:      str = ""
    type:      str = ""

    @staticmethod
    def from_dict(sensor_id: str, data: Optional[dict]) -> ZoneSensorConfig:
        data = data or {}
        return ZoneSensorConfig(
            sensor_id=sensor_id,
            node=data.get("node", ""),
            type=data.get("type", ""),
        )


# ---------------------------------------------------------------------------
# Zone Config
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ZoneConfig:
    zone_id:      str                          = ""
    display_name: str                          = ""
    enabled:      bool                         = False
    devices:      dict[str, ZoneDeviceConfig]  = field(default_factory=dict)
    sensors:      dict[str, ZoneSensorConfig]  = field(default_factory=dict)
    workflows:    dict[str, WorkflowConfig]    = field(default_factory=dict)
    safety:       dict[str, SafetyPolicy]      = field(default_factory=dict)
    properties:   dict                         = field(default_factory=dict)  # module-specific metadata (e.g. soil, environment)

    @staticmethod
    def from_dict(zone_id: str, data: Optional[dict]) -> ZoneConfig:
        data = data or {}
        return ZoneConfig(
            zone_id=zone_id,
            display_name=data.get("display_name", zone_id),
            enabled=data.get("enabled",           False),
            devices={
                device_id: ZoneDeviceConfig.from_dict(device_id, d)
                for device_id, d in data.get("devices", {}).items()
            },
            sensors={
                sensor_id: ZoneSensorConfig.from_dict(sensor_id, s)
                for sensor_id, s in data.get("sensors", {}).items()
            },
            workflows={
                workflow_id: WorkflowConfig.from_dict(workflow_id, w)
                for workflow_id, w in data.get("workflows", {}).items()
            },
            safety={
                policy_id: SafetyPolicy.from_dict(policy_id, p)
                for policy_id, p in data.get("safety", {}).items()
            },
            properties=data.get("properties", {}),
        )