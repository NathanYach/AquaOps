from __future__ import annotations
from sqlalchemy import Float, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from AquaOps.Database.Models.base import Base
from AquaOps.Irrigation.Config.zone_config import ZoneConfig


class ZoneSoilSettings(Base):
    __tablename__ = "zone_soil_settings"
    __table_args__ = {"schema": "irrigation"}

    id:                        Mapped[int]   = mapped_column(Integer, primary_key=True, autoincrement=True)
    zone_id:                   Mapped[str]   = mapped_column(String(50), ForeignKey("irrigation.zone_settings.zone_id"), unique=True)
    target_moisture_percent:   Mapped[float] = mapped_column(Float, default=0.0)
    moisture_tolerance_percent: Mapped[float] = mapped_column(Float, default=0.0)

    zone: Mapped["ZoneSettings"] = relationship(back_populates="soil")

    @staticmethod
    def from_dataclass(cfg: ZoneConfig) -> ZoneSoilSettings:
        return ZoneSoilSettings(
            target_moisture_percent=cfg.soil.target_moisture_percent,
            moisture_tolerance_percent=cfg.soil.moisture_tolerance_percent,
        )