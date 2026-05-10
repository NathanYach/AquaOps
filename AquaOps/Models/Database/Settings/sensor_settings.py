from __future__ import annotations
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from AquaOps.Models.Database.base import Base
from AquaOps.Models.Modules.zone_config import ZoneDeviceConfig, ZoneSensorConfig

class SensorSettings(Base):
    __tablename__ = "sensor_settings"
    __table_args__ = {"schema": "aquaops"}

    sensor_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    zone_id:   Mapped[str] = mapped_column(String(100), ForeignKey("aquaops.zone_settings.zone_id"), primary_key=True)
    node_id:   Mapped[str] = mapped_column(String(100), ForeignKey("aquaops.node_settings.node_id"))
    type:      Mapped[str] = mapped_column(String(100), default="")

    zone: Mapped["ZoneSettings"] = relationship(back_populates="sensors")
    node: Mapped["NodeSettings"] = relationship(back_populates="sensors")

    @staticmethod
    def from_dataclass(zone_id: str, cfg: ZoneSensorConfig) -> SensorSettings:
        return SensorSettings(
            sensor_id=cfg.sensor_id,
            zone_id=zone_id,
            node_id=cfg.node,
            type=cfg.type,
        )