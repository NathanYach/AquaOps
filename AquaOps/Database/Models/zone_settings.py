from __future__ import annotations
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from AquaOps.Database.Models.base import Base
from AquaOps.Irrigation.Config.zone_config import ZoneConfig


class ZoneSettings(Base):
    __tablename__ = "zone_settings"
    __table_args__ = {"schema": "irrigation"}

    zone_id:      Mapped[str]  = mapped_column(String(50),  primary_key=True)
    display_name: Mapped[str]  = mapped_column(String(100), default="")
    enabled:      Mapped[bool] = mapped_column(Boolean,     default=False)

    environment: Mapped["ZoneEnvironmentSettings"] = relationship(back_populates="zone", uselist=False, cascade="all, delete-orphan")
    soil:        Mapped["ZoneSoilSettings"]        = relationship(back_populates="zone", uselist=False, cascade="all, delete-orphan")
    hardware:    Mapped["ZoneHardwareSettings"]    = relationship(back_populates="zone", uselist=False, cascade="all, delete-orphan")
    watering:    Mapped["ZoneWateringSettings"]    = relationship(back_populates="zone", uselist=False, cascade="all, delete-orphan")

    @staticmethod
    def from_dataclass(cfg: ZoneConfig) -> ZoneSettings:
        from AquaOps.Database.Models.zone_environment_settings import ZoneEnvironmentSettings
        from AquaOps.Database.Models.zone_soil_settings import ZoneSoilSettings
        from AquaOps.Database.Models.zone_hardware_settings import ZoneHardwareSettings
        from AquaOps.Database.Models.zone_watering_settings import ZoneWateringSettings

        return ZoneSettings(
            zone_id=cfg.zone_id,
            display_name=cfg.display_name,
            enabled=cfg.enabled,
            environment=ZoneEnvironmentSettings.from_dataclass(cfg),
            soil=ZoneSoilSettings.from_dataclass(cfg),
            hardware=ZoneHardwareSettings.from_dataclass(cfg),
            watering=ZoneWateringSettings.from_dataclass(cfg),
        )

    def to_dataclass(self) -> ZoneConfig:
        return ZoneConfig(
            zone_id=self.zone_id,
            display_name=self.display_name,
            enabled=self.enabled,
        )