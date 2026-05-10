from __future__ import annotations
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from AquaOps.Database.Models.base import Base
from AquaOps.Irrigation.Config.zone_config import ZoneConfig


class ZoneHardwareSettings(Base):
    __tablename__ = "zone_hardware_settings"
    __table_args__ = {"schema": "irrigation"}

    id:                    Mapped[int]        = mapped_column(Integer, primary_key=True, autoincrement=True)
    zone_id:               Mapped[str]        = mapped_column(String(50), ForeignKey("irrigation.zone_settings.zone_id"), unique=True)
    valve_id:              Mapped[str | None] = mapped_column(String(50), nullable=True)
    moisture_sensor_id:    Mapped[str | None] = mapped_column(String(50), nullable=True)
    temperature_sensor_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    grow_light_id:         Mapped[str | None] = mapped_column(String(50), nullable=True)

    zone: Mapped["ZoneSettings"] = relationship(back_populates="hardware")

    @staticmethod
    def from_dataclass(cfg: ZoneConfig) -> ZoneHardwareSettings:
        return ZoneHardwareSettings(
            valve_id=cfg.hardware.valve_id,
            moisture_sensor_id=cfg.hardware.moisture_sensor_id,
            temperature_sensor_id=cfg.hardware.temperature_sensor_id,
            grow_light_id=cfg.hardware.grow_light_id,
        )