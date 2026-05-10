
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from AquaOps.Database.Config.database_config import DatabaseConfig
from AquaOps.Database.Config.database_pool_config import DatabasePoolConfig

@dataclass(frozen=True)
class ConnectionsConfig:
    #mqtt:     Optional[MqttConfig]          = None
    database: Optional[DatabaseConfig]      = None
    #nodes:    dict[str, NodeConfig]         = field(default_factory=dict)

    @staticmethod
    def from_dict(data: Optional[dict]) -> ConnectionsConfig:
        data = data or {}
        return ConnectionsConfig(
            #mqtt=MqttConfig.from_dict(data.get("mqtt"))         if data.get("mqtt")     else None,
            database=DatabaseConfig.from_dict(data.get("database")) if data.get("database") else None,
            #nodes={
            #    node_id: NodeConfig.from_dict(node_data)
            #    for node_id, node_data in data.get("nodes", {}).items()
            #},
        )