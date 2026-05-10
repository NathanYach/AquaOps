from __future__ import annotations
from sqlalchemy import Boolean, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from AquaOps.Models.Database.base import Base
from AquaOps.Models.Modules.zone_config import ZoneConfig


class ZoneSettings(Base):
    __tablename__ = "zone_settings"
    __table_args__ = {"schema": "aquaops"}

    zone_id:      Mapped[str]  = mapped_column(String(100), primary_key=True)
    module_id:    Mapped[str]  = mapped_column(String(100), ForeignKey("aquaops.module_settings.module_id"))
    display_name: Mapped[str]  = mapped_column(String(200), default="")
    enabled:      Mapped[bool] = mapped_column(Boolean, default=False)

    module:          Mapped["ModuleSettings"]             = relationship(back_populates="zones")
    properties:      Mapped[list["ZonePropertySettings"]] = relationship(back_populates="zone", cascade="all, delete-orphan")
    devices:         Mapped[list["DeviceSettings"]]       = relationship(back_populates="zone", cascade="all, delete-orphan")
    sensors:         Mapped[list["SensorSettings"]]       = relationship(back_populates="zone", cascade="all, delete-orphan")
    workflows:       Mapped[list["WorkflowSettings"]]     = relationship(back_populates="zone", cascade="all, delete-orphan")
    safety_policies: Mapped[list["SafetyPolicySettings"]] = relationship(back_populates="zone", cascade="all, delete-orphan")

    @staticmethod
    def from_dataclass(module_id: str, cfg: ZoneConfig) -> ZoneSettings:
        return ZoneSettings(
            zone_id=cfg.zone_id,
            module_id=module_id,
            display_name=cfg.display_name,
            enabled=cfg.enabled,
            properties=[
                ZonePropertySettings(zone_id=cfg.zone_id, key=k, value=str(v))
                for k, v in cfg.properties.items()
            ],
        )


class ZonePropertySettings(Base):
    """
    Generic key-value store for module-specific zone metadata.
    Keeps zone_settings fully normalized — no domain-specific columns.
    """
    __tablename__ = "zone_property_settings"
    __table_args__ = {"schema": "aquaops"}

    zone_id: Mapped[str] = mapped_column(String(100), ForeignKey("aquaops.zone_settings.zone_id"), primary_key=True)
    key:     Mapped[str] = mapped_column(String(100), primary_key=True)
    value:   Mapped[str] = mapped_column(String(500), default="")

    zone: Mapped["ZoneSettings"] = relationship(back_populates="properties")