from __future__ import annotations

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine

from AquaOps.config_context import ConfigContext
from AquaOps.Database.Config.database_config import DatabaseConfig
from AquaOps.Database.Models.base import Base

from AquaOps.Database.Models.irrigation_safety_settings import IrrigationSafetySettings
from AquaOps.Database.Models.irrigation_system_settings import IrrigationSystemSettings
from AquaOps.Database.Models.zone_settings import ZoneSettings
from AquaOps.Database.Models.zone_environment_settings import ZoneEnvironmentSettings
from AquaOps.Database.Models.zone_soil_settings import ZoneSoilSettings
from AquaOps.Database.Models.zone_hardware_settings import ZoneHardwareSettings
from AquaOps.Database.Models.zone_watering_settings import ZoneWateringSettings

from AquaOps.Irrigation.Config.irrigation_config import IrrigationConfig
from AquaOps.Irrigation.Config.zone_config import ZoneConfig
from AquaOps.Irrigation.Config.system_config import SystemConfig
from AquaOps.Irrigation.Config.global_safety_config import (
    GlobalSafetyConfig,
    LeakDetectionConfig,
    EmergencyShutdownConfig,
    RuntimeLimitsConfig,
    SensorValidationConfig,
)
from AquaOps.Irrigation.Config.environment_config import EnvironmentConfig
from AquaOps.Irrigation.Config.soil_config import SoilConfig
from AquaOps.Irrigation.Config.hardware_config import HardwareConfig
from AquaOps.Irrigation.Config.watering_config import WateringConfig, WateringSafetyConfig


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

def build_engine(cfg: DatabaseConfig) -> AsyncEngine:
    url = (
        f"postgresql+asyncpg://{cfg.username}:{cfg.password}"
        f"@{cfg.host}:{cfg.port}/{cfg.name}"
    )
    return create_async_engine(
        url,
        pool_size=cfg.pool.max_connections,
        pool_timeout=cfg.pool.connection_timeout_seconds,
    )


# ---------------------------------------------------------------------------
# Schema + Table creation
# ---------------------------------------------------------------------------

async def init_database(engine: AsyncEngine):
    """Create schemas and all tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS irrigation"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS aquarium"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS telemetry"))
        await conn.run_sync(Base.metadata.create_all)


# ---------------------------------------------------------------------------
# Seed
# ---------------------------------------------------------------------------

async def _seed(context: ConfigContext, session: AsyncSession):
    """Populate an empty database from the file-loaded config."""
    print("[database_loader] Database empty — seeding from file config...")

    if context.irrigation:
        cfg = context.irrigation
        session.add(IrrigationSystemSettings.from_dataclass(cfg))
        session.add(IrrigationSafetySettings.from_dataclass(cfg))
        for zone in cfg.zones.values():
            session.add(ZoneSettings.from_dataclass(zone))

    await session.commit()
    print("[database_loader] Seeding complete.")


# ---------------------------------------------------------------------------
# to_dataclass helpers
# ---------------------------------------------------------------------------

def _zone_to_dataclass(
    zone:        ZoneSettings,
    environment: ZoneEnvironmentSettings,
    soil:        ZoneSoilSettings,
    hardware:    ZoneHardwareSettings,
    watering:    ZoneWateringSettings,
) -> ZoneConfig:
    return ZoneConfig(
        zone_id=zone.zone_id,
        display_name=zone.display_name,
        enabled=zone.enabled,
        environment=EnvironmentConfig(
            target_air_temp_c=environment.target_air_temp_c,
            target_humidity_percent=environment.target_humidity_percent,
            light_duration_hours=environment.light_duration_hours,
        ),
        soil=SoilConfig(
            target_moisture_percent=soil.target_moisture_percent,
            moisture_tolerance_percent=soil.moisture_tolerance_percent,
        ),
        hardware=HardwareConfig(
            valve_id=hardware.valve_id,
            moisture_sensor_id=hardware.moisture_sensor_id,
            temperature_sensor_id=hardware.temperature_sensor_id,
            grow_light_id=hardware.grow_light_id,
        ),
        watering=WateringConfig(
            preferred_water_source=watering.preferred_water_source,
            fallback_water_source=watering.fallback_water_source,
            trigger_below_moisture_percent=watering.trigger_below_moisture_percent,
            target_delivery_ml=watering.target_delivery_ml,
            max_delivery_ml=watering.max_delivery_ml,
            estimated_flow_rate_ml_per_second=watering.estimated_flow_rate_ml_per_second,
            minimum_interval_minutes=watering.minimum_interval_minutes,
            max_watering_duration_seconds=watering.max_watering_duration_seconds,
            safety=WateringSafetyConfig(
                leak_detection_enabled=watering.safety_leak_detection_enabled,
                auto_shutdown_on_sensor_failure=watering.safety_auto_shutdown_on_sensor_failure,
                max_daily_delivery_ml=watering.safety_max_daily_delivery_ml,
                max_continuous_runtime_seconds=watering.safety_max_continuous_runtime_seconds,
            ),
        ),
    )


def _irrigation_to_dataclass(
    system:  IrrigationSystemSettings,
    safety:  IrrigationSafetySettings,
    zones:   dict[str, ZoneConfig],
) -> IrrigationConfig:
    return IrrigationConfig(
        system=SystemConfig(
            enabled=system.enabled,
            telemetry_interval_seconds=system.telemetry_interval_seconds,
        ),
        global_safety=GlobalSafetyConfig(
            enabled=safety.enabled,
            leak_detection=LeakDetectionConfig(
                enabled=safety.leak_detection_enabled,
                shutdown_all_zones_on_leak=safety.leak_shutdown_all_zones,
                alert_on_detection=safety.leak_alert_on_detection,
            ),
            emergency_shutdown=EmergencyShutdownConfig(
                enabled=safety.emergency_shutdown_enabled,
                disable_all_valves=safety.emergency_disable_all_valves,
                disable_all_pumps=safety.emergency_disable_all_pumps,
            ),
            runtime_limits=RuntimeLimitsConfig(
                global_max_continuous_runtime_seconds=safety.global_max_continuous_runtime_seconds,
                global_max_daily_delivery_ml=safety.global_max_daily_delivery_ml,
            ),
            sensor_validation=SensorValidationConfig(
                shutdown_on_sensor_failure=safety.shutdown_on_sensor_failure,
                ignore_invalid_readings=safety.ignore_invalid_readings,
                max_invalid_readings_before_shutdown=safety.max_invalid_readings_before_shutdown,
            ),
        ),
        zones=zones,
    )


# ---------------------------------------------------------------------------
# Override
# ---------------------------------------------------------------------------

async def _override_from_database(context: ConfigContext, session: AsyncSession):
    """Overwrite the file-loaded config with settings from the database."""
    print("[database_loader] Loading config from database...")

    if context.irrigation:

        # System
        system_result = await session.execute(select(IrrigationSystemSettings))
        system = system_result.scalars().first()

        # Safety
        safety_result = await session.execute(select(IrrigationSafetySettings))
        safety = safety_result.scalars().first()

        # Zones + children
        zones: dict[str, ZoneConfig] = {}

        zone_result = await session.execute(select(ZoneSettings))
        db_zones = zone_result.scalars().all()

        for zone in db_zones:
            env_result  = await session.execute(select(ZoneEnvironmentSettings).where(ZoneEnvironmentSettings.zone_id == zone.zone_id))
            soil_result = await session.execute(select(ZoneSoilSettings).where(ZoneSoilSettings.zone_id == zone.zone_id))
            hw_result   = await session.execute(select(ZoneHardwareSettings).where(ZoneHardwareSettings.zone_id == zone.zone_id))
            wat_result  = await session.execute(select(ZoneWateringSettings).where(ZoneWateringSettings.zone_id == zone.zone_id))

            environment = env_result.scalars().first()
            soil        = soil_result.scalars().first()
            hardware    = hw_result.scalars().first()
            watering    = wat_result.scalars().first()

            if all([environment, soil, hardware, watering]):
                zones[zone.zone_id] = _zone_to_dataclass(zone, environment, soil, hardware, watering)

        if system and safety and zones:
            context.irrigation = _irrigation_to_dataclass(system, safety, zones)

    print("[database_loader] Database config loaded.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def sync_database(context: ConfigContext):
    """
    Called at startup after load_configs().
    - Connects to the database if configured.
    - Creates schemas and tables if they don't exist.
    - Seeds from file config on first run.
    - Overwrites context from database on subsequent runs.
    """
    if not context.connections or not context.connections.database:
        print("[database_loader] No database configured — using file config.")
        return

    try:
        engine = build_engine(context.connections.database)
        await init_database(engine)

        async with AsyncSession(engine) as session:
            result = await session.execute(select(ZoneSettings))
            existing = result.scalars().first()

            if existing is None:
                await _seed(context, session)
            else:
                await _override_from_database(context, session)

    except Exception as e:
        print(f"[database_loader] Database unavailable — using file config. ({e})")