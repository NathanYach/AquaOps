from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from AquaOps.Models.Modules.zone_config import ZoneConfig
from AquaOps.Models.Safety.safety_config import GlobalSafetyConfig
from AquaOps.Models.System.system_config import SystemConfig


@dataclass(frozen=True)
class ModuleConfig:
    """
    A generic module (e.g. irrigation, aquarium, hydroponics).
    Modules are defined entirely in YAML — no code changes needed to add one.
    """
    module_id:     str                      = ""
    enabled:       bool                     = False
    system:        SystemConfig             = field(default_factory=SystemConfig)
    global_safety: GlobalSafetyConfig       = field(default_factory=GlobalSafetyConfig)
    zones:         dict[str, ZoneConfig]    = field(default_factory=dict)

    @staticmethod
    def from_dict(module_id: str, data: Optional[dict]) -> ModuleConfig:
        data = data or {}
        return ModuleConfig(
            module_id=module_id,
            enabled=data.get("enabled", False),
            system=SystemConfig.from_dict(data.get("system")),
            global_safety=GlobalSafetyConfig.from_dict(data.get("global_safety")),
            zones={
                zone_id: ZoneConfig.from_dict(zone_id, z)
                for zone_id, z in data.get("zones", {}).items()
            },
        )