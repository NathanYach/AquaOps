from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Device
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DeviceConfig:
    device_id:   str          = ""
    type:        str          = ""
    pin:         Optional[int] = None
    description: str          = ""

    @staticmethod
    def from_dict(device_id: str, data: Optional[dict]) -> DeviceConfig:
        data = data or {}
        return DeviceConfig(
            device_id=device_id,
            type=data.get("type",               ""),
            pin=data.get("pin"),
            description=data.get("description", ""),
        )


# ---------------------------------------------------------------------------
# Sensor
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SensorConfig:
    sensor_id:   str          = ""
    type:        str          = ""
    pin:         Optional[int] = None
    description: str          = ""

    @staticmethod
    def from_dict(sensor_id: str, data: Optional[dict]) -> SensorConfig:
        data = data or {}
        return SensorConfig(
            sensor_id=sensor_id,
            type=data.get("type",               ""),
            pin=data.get("pin"),
            description=data.get("description", ""),
        )


# ---------------------------------------------------------------------------
# Node
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class NodeConfig:
    node_id:     str                      = ""
    description: str                      = ""
    devices:     dict[str, DeviceConfig]  = field(default_factory=dict)
    sensors:     dict[str, SensorConfig]  = field(default_factory=dict)

    @staticmethod
    def from_dict(node_id: str, data: Optional[dict]) -> NodeConfig:
        data = data or {}
        return NodeConfig(
            node_id=data.get("node_id", node_id),
            description=data.get("description", ""),
            devices={
                device_id: DeviceConfig.from_dict(device_id, d)
                for device_id, d in data.get("devices", {}).items()
            },
            sensors={
                sensor_id: SensorConfig.from_dict(sensor_id, s)
                for sensor_id, s in data.get("sensors", {}).items()
            },
        )