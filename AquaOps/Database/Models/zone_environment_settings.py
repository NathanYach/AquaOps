from __future__ import annotations
from sqlalchemy import Float, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from AquaOps.Database.Models.base import Base
from AquaOps.Irrigation.Config.zone_config import ZoneConfig


class ZoneEnvironmentSettings(Base):
    __tablename__ = "zone_environment_settings"
    __table_args__ = {"schema": "irrigation"}

    id:                      Mapped[int]   = mapped_column(Integer, primary_key=True, autoincrement=True)
    zone_id:                 Mapped[str]   = mapped_column(String(50), ForeignKey("irrigation.zone_settings.zone_id"), unique=True)
    target_air_temp_c:       Mapped[float] = mapped_column(Float, default=0.0)
    target_humidity_percent: Mapped[float] = mapped_column(Float, default=0.0)
    light_duration_hours:    Mapped[float] = mapped_column(Float, default=0.0)

    zone: Mapped["ZoneSettings"] = relationship(back_populates="environment")

    @staticmethod
    def from_dataclass(cfg: ZoneConfig) -> ZoneEnvironmentSettings:
        return ZoneEnvironmentSettings(
            target_air_temp_c=cfg.environment.target_air_temp_c,
            target_humidity_percent=cfg.environment.target_humidity_percent,
            light_duration_hours=cfg.environment.light_duration_hours,
        )