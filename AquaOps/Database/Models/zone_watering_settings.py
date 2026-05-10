from __future__ import annotations
from sqlalchemy import Boolean, Float, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from AquaOps.Database.Models.base import Base
from AquaOps.Irrigation.Config.zone_config import ZoneConfig


class ZoneWateringSettings(Base):
    __tablename__ = "zone_watering_settings"
    __table_args__ = {"schema": "irrigation"}

    id:                                Mapped[int]   = mapped_column(Integer, primary_key=True, autoincrement=True)
    zone_id:                           Mapped[str]   = mapped_column(String(50), ForeignKey("irrigation.zone_settings.zone_id"), unique=True)
    preferred_water_source:            Mapped[str]   = mapped_column(String(50), default="conditioned")
    fallback_water_source:             Mapped[str]   = mapped_column(String(50), default="conditioned")
    trigger_below_moisture_percent:    Mapped[float] = mapped_column(Float,   default=40.0)
    target_delivery_ml:                Mapped[int]   = mapped_column(Integer, default=0)
    max_delivery_ml:                   Mapped[int]   = mapped_column(Integer, default=0)
    estimated_flow_rate_ml_per_second: Mapped[float] = mapped_column(Float,   default=0.0)
    minimum_interval_minutes:          Mapped[int]   = mapped_column(Integer, default=0)
    max_watering_duration_seconds:     Mapped[int]   = mapped_column(Integer, default=0)

    # Watering Safety
    safety_leak_detection_enabled:          Mapped[bool] = mapped_column(Boolean, default=True)
    safety_auto_shutdown_on_sensor_failure: Mapped[bool] = mapped_column(Boolean, default=True)
    safety_max_daily_delivery_ml:           Mapped[int]  = mapped_column(Integer, default=0)
    safety_max_continuous_runtime_seconds:  Mapped[int]  = mapped_column(Integer, default=120)

    zone: Mapped["ZoneSettings"] = relationship(back_populates="watering")

    @staticmethod
    def from_dataclass(cfg: ZoneConfig) -> ZoneWateringSettings:
        w = cfg.watering
        return ZoneWateringSettings(
            preferred_water_source=w.preferred_water_source,
            fallback_water_source=w.fallback_water_source,
            trigger_below_moisture_percent=w.trigger_below_moisture_percent,
            target_delivery_ml=w.target_delivery_ml,
            max_delivery_ml=w.max_delivery_ml,
            estimated_flow_rate_ml_per_second=w.estimated_flow_rate_ml_per_second,
            minimum_interval_minutes=w.minimum_interval_minutes,
            max_watering_duration_seconds=w.max_watering_duration_seconds,
            safety_leak_detection_enabled=w.safety.leak_detection_enabled,
            safety_auto_shutdown_on_sensor_failure=w.safety.auto_shutdown_on_sensor_failure,
            safety_max_daily_delivery_ml=w.safety.max_daily_delivery_ml,
            safety_max_continuous_runtime_seconds=w.safety.max_continuous_runtime_seconds,
        )