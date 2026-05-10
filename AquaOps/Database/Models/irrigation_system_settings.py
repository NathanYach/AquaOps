from __future__ import annotations
from sqlalchemy import Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

from AquaOps.Database.Models.base import Base
from AquaOps.Irrigation.Config.irrigation_config import IrrigationConfig


class IrrigationSystemSettings(Base):
    __tablename__ = "system_settings"
    __table_args__ = {"schema": "irrigation"}

    id:                         Mapped[int]  = mapped_column(Integer, primary_key=True, autoincrement=True)
    enabled:                    Mapped[bool] = mapped_column(Boolean, default=False)
    telemetry_interval_seconds: Mapped[int]  = mapped_column(Integer, default=30)

    @staticmethod
    def from_dataclass(cfg: IrrigationConfig) -> IrrigationSystemSettings:
        return IrrigationSystemSettings(
            enabled=cfg.system.enabled,
            telemetry_interval_seconds=cfg.system.telemetry_interval_seconds,
        )