# AquaOps/Database/Models/module_settings.py
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from AquaOps.Models.Database.base import Base
from AquaOps.Models.Modules.module_config import ModuleConfig


class ModuleSettings(Base):
    __tablename__ = "module_settings"
    __table_args__ = {"schema": "aquaops"}

    module_id: Mapped[str]  = mapped_column(String(100), primary_key=True)
    enabled:   Mapped[bool] = mapped_column(Boolean, default=False)

    system:          Mapped["ModuleSystemSettings"]       = relationship(back_populates="module", uselist=False, cascade="all, delete-orphan")
    zones:           Mapped[list["ZoneSettings"]]         = relationship(back_populates="module", cascade="all, delete-orphan")
    safety_policies: Mapped[list["SafetyPolicySettings"]] = relationship(back_populates="module", cascade="all, delete-orphan")

    @staticmethod
    def from_dataclass(cfg: ModuleConfig) -> ModuleSettings:
        return ModuleSettings(
            module_id=cfg.module_id,
            enabled=cfg.enabled,
            system=ModuleSystemSettings.from_dataclass(cfg),
        )


class ModuleSystemSettings(Base):
    __tablename__ = "module_system_settings"
    __table_args__ = {"schema": "aquaops"}

    # Single-column PK that is also the FK — standard one-to-one pattern
    module_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("aquaops.module_settings.module_id", ondelete="CASCADE"),
        primary_key=True,
    )
    telemetry_interval_seconds: Mapped[int]  = mapped_column(Integer, default=30)
    log_level:                  Mapped[str]  = mapped_column(String(20), default="INFO")
    log_to_file:                Mapped[bool] = mapped_column(Boolean, default=False)
    log_to_database:            Mapped[bool] = mapped_column(Boolean, default=False)

    module: Mapped["ModuleSettings"] = relationship(back_populates="system")

    @staticmethod
    def from_dataclass(cfg: ModuleConfig) -> ModuleSystemSettings:
        return ModuleSystemSettings(
            module_id=cfg.module_id,
            telemetry_interval_seconds=cfg.system.telemetry_interval_seconds,
            log_level=cfg.system.log_level,
            log_to_file=cfg.system.log_to_file,
            log_to_database=cfg.system.log_to_database,
        )