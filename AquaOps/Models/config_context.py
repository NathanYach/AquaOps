from __future__ import annotations
from typing import Optional

from AquaOps.Models.Modules.module_config import ModuleConfig
from AquaOps.Models.Connection.connections_config import ConnectionsConfig


class ConfigContext:
    """
    Top-level runtime config container.
    Holds all loaded modules and connection settings.
    """
    def __init__(self):
        self.modules:     dict[str, ModuleConfig] = {}
        self.connections: Optional[ConnectionsConfig] = None

    def get_module(self, module_id: str) -> Optional[ModuleConfig]:
        return self.modules.get(module_id)