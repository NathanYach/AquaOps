from __future__ import annotations
from sqlalchemy import Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

from AquaOps.Database.Models.base import Base
from AquaOps.Irrigation.Config.irrigation_config import IrrigationConfig


class IrrigationSafetySettings(Base):
    __tablename__ = "safety_settings"
    __table_args__ = {"schema": "irrigation"}

    id:      Mapped[int]  = mapped_column(Integer, primary_key=True, autoincrement=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # Leak Detection
    leak_detection_enabled:             Mapped[bool] = mapped_column(Boolean, default=True)
    leak_shutdown_all_zones:            Mapped[bool] = mapped_column(Boolean, default=True)
    leak_alert_on_detection:            Mapped[bool] = mapped_column(Boolean, default=True)

    # Emergency Shutdown
    emergency_shutdown_enabled:         Mapped[bool] = mapped_column(Boolean, default=True)
    emergency_disable_all_valves:       Mapped[bool] = mapped_column(Boolean, default=True)
    emergency_disable_all_pumps:        Mapped[bool] = mapped_column(Boolean, default=True)

    # Runtime Limits
    global_max_continuous_runtime_seconds: Mapped[int] = mapped_column(Integer, default=300)
    global_max_daily_delivery_ml:          Mapped[int] = mapped_column(Integer, default=0)

    # Sensor Validation
    shutdown_on_sensor_failure:           Mapped[bool] = mapped_column(Boolean, default=True)
    ignore_invalid_readings:              Mapped[bool] = mapped_column(Boolean, default=False)
    max_invalid_readings_before_shutdown: Mapped[int]  = mapped_column(Integer, default=5)

    @staticmethod
    def from_dataclass(cfg: IrrigationConfig) -> IrrigationSafetySettings:
        gs = cfg.global_safety
        return IrrigationSafetySettings(
            enabled=gs.enabled,
            leak_detection_enabled=gs.leak_detection.enabled,
            leak_shutdown_all_zones=gs.leak_detection.shutdown_all_zones_on_leak,
            leak_alert_on_detection=gs.leak_detection.alert_on_detection,
            emergency_shutdown_enabled=gs.emergency_shutdown.enabled,
            emergency_disable_all_valves=gs.emergency_shutdown.disable_all_valves,
            emergency_disable_all_pumps=gs.emergency_shutdown.disable_all_pumps,
            global_max_continuous_runtime_seconds=gs.runtime_limits.global_max_continuous_runtime_seconds,
            global_max_daily_delivery_ml=gs.runtime_limits.global_max_daily_delivery_ml,
            shutdown_on_sensor_failure=gs.sensor_validation.shutdown_on_sensor_failure,
            ignore_invalid_readings=gs.sensor_validation.ignore_invalid_readings,
            max_invalid_readings_before_shutdown=gs.sensor_validation.max_invalid_readings_before_shutdown,
        )