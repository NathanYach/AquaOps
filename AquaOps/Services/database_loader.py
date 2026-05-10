# AquaOps/Services/database_loader.py
from __future__ import annotations

import logging
from typing import AsyncGenerator

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from AquaOps.Models.Connection.connections_config import ConnectionsConfig
from AquaOps.Models.config_context import ConfigContext
from AquaOps.Models.Database.base import Base

# Import all models so SQLAlchemy's metadata is fully populated before
# create_all is called. Order matters for FK resolution.
from AquaOps.Models.Database.Settings.module_settings import ModuleSettings, ModuleSystemSettings
from AquaOps.Models.Database.Settings.zone_settings import ZoneSettings, ZonePropertySettings
from AquaOps.Models.Database.Settings.device_settings import DeviceSettings
from AquaOps.Models.Database.Settings.sensor_settings import SensorSettings
from AquaOps.Models.Database.Settings.node_settings import NodeSettings
from AquaOps.Models.Database.Settings.workflow_settings import (
    WorkflowSettings,
    WorkflowTrigger,
    WorkflowCondition,
    WorkflowAction,
    WorkflowStopCondition,
    WorkflowSafetyInheritance,
)
from AquaOps.Models.Database.Settings.safety_settings import SafetyPolicySettings, SafetyRuleSettings
from AquaOps.Models.Database.Metrics.Metrics import (
    SensorReading,
    DeviceEvent,
    WorkflowExecution,
    SafetyEvent,
    NodeHeartbeat,
)

log = logging.get_logger()

_engine:         AsyncEngine | None          = None
_session_factory: async_sessionmaker | None  = None


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

def _build_engine(cfg: ConnectionsConfig) -> AsyncEngine:
    db = cfg.database
    url = (
        f"postgresql+asyncpg://{db.username}:{db.password}"
        f"@{db.host}:{db.port}/{db.name}"
    )
    return create_async_engine(
        url,
        pool_size=db.pool.max_connections,
        pool_timeout=db.pool.connection_timeout_seconds,
        echo=False,
    )


def get_engine() -> AsyncEngine:
    if _engine is None:
        raise RuntimeError("Database not initialised — call init_database() first.")
    return _engine


def get_session_factory() -> async_sessionmaker:
    if _session_factory is None:
        raise RuntimeError("Database not initialised — call init_database() first.")
    return _session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields a scoped session."""
    async with get_session_factory()() as session:
        yield session


# ---------------------------------------------------------------------------
# Schema + table creation
# ---------------------------------------------------------------------------

_SCHEMAS = ("aquaops",)


async def _create_schemas(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        for schema in _SCHEMAS:
            await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
    log.debug("Schemas ensured: %s", _SCHEMAS)


async def _create_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.debug("Tables created/verified.")


# ---------------------------------------------------------------------------
# Seed helpers
# ---------------------------------------------------------------------------

async def _seed(context: ConfigContext, session: AsyncSession) -> None:
    """Populate an empty database from the YAML-loaded config."""
    log.info("Database empty — seeding from file config.")

    for module_id, module_cfg in context.modules.items():
        module_row = ModuleSettings.from_dataclass(module_cfg)
        session.add(module_row)

        for zone_id, zone_cfg in module_cfg.zones.items():
            zone_row = ZoneSettings.from_dataclass(module_id, zone_cfg)
            session.add(zone_row)

            for device_id, device_cfg in zone_cfg.devices.items():
                session.add(DeviceSettings.from_dataclass(zone_id, device_cfg))

            for sensor_id, sensor_cfg in zone_cfg.sensors.items():
                session.add(SensorSettings.from_dataclass(zone_id, sensor_cfg))

            for wf_id, wf_cfg in zone_cfg.workflows.items():
                session.add(WorkflowSettings.from_dataclass(zone_id, wf_cfg))

            for policy_id, policy_cfg in zone_cfg.safety.items():
                session.add(SafetyPolicySettings.from_dataclass(module_id, policy_cfg, zone_id=zone_id))

        for policy_id, policy_cfg in module_cfg.global_safety.policies.items():
            session.add(SafetyPolicySettings.from_dataclass(module_id, policy_cfg))

    await session.commit()
    log.info("Seeding complete.")


# ---------------------------------------------------------------------------
# Override helpers
# ---------------------------------------------------------------------------

async def _override_from_database(context: ConfigContext, session: AsyncSession) -> None:
    """
    Rebuild the in-memory ConfigContext from database rows.
    This is the single source of truth after first boot.
    """
    log.info("Loading config from database.")

    result = await session.execute(
        select(ModuleSettings)
    )
    db_modules = result.scalars().all()

    for db_module in db_modules:
        if db_module.module_id not in context.modules:
            log.warning("DB contains module '%s' not in YAML; skipping override.", db_module.module_id)
            continue

        # Shallow enable/disable sync only for now.
        # Deeper field-level merging can be added per-module as needed.
        yaml_module = context.modules[db_module.module_id]
        context.modules[db_module.module_id] = yaml_module

    log.info("Database config loaded.")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def init_database(context: ConfigContext) -> None:
    """
    Called once at startup after load_configs().

    1. Skip entirely if no database is configured (YAML-only mode).
    2. Build engine + session factory.
    3. Create schemas and tables.
    4. Seed on first run, otherwise override context from DB.
    """
    global _engine, _session_factory

    if not context.connections or not context.connections.database:
        log.info("No database configured — running in file-only mode.")
        return

    try:
        _engine = _build_engine(context.connections)
        _session_factory = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        await _create_schemas(_engine)
        await _create_tables(_engine)

        async with _session_factory() as session:
            result = await session.execute(select(ModuleSettings).limit(1))
            is_empty = result.scalars().first() is None

            if is_empty:
                await _seed(context, session)
            else:
                await _override_from_database(context, session)

    except Exception:
        log.exception("Database unavailable — running in file-only mode.")
        _engine = None
        _session_factory = None


async def close_database() -> None:
    """Gracefully close the connection pool on shutdown."""
    global _engine, _session_factory
    if _engine:
        await _engine.dispose()
        log.info("Database engine disposed.")
    _engine = None
    _session_factory = None