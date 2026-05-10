from __future__ import annotations
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from AquaOps.Models.Database.base import Base
from AquaOps.Models.Hardware.hardware_config import NodeConfig


class NodeSettings(Base):
    __tablename__ = "node_settings"
    __table_args__ = {"schema": "aquaops"}

    node_id:     Mapped[str] = mapped_column(String(100), primary_key=True)
    description: Mapped[str] = mapped_column(String(255), default="")

    devices: Mapped[list["DeviceSettings"]] = relationship(back_populates="node", cascade="all, delete-orphan")
    sensors: Mapped[list["SensorSettings"]] = relationship(back_populates="node", cascade="all, delete-orphan")

    @staticmethod
    def from_dataclass(cfg: NodeConfig) -> NodeSettings:
        return NodeSettings(
            node_id=cfg.node_id,
            description=cfg.description,
        )