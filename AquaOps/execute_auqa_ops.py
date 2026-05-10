import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from AquaOps.config_loader import load_configs
from AquaOps.Database.database_loader import sync_database
from AquaOps.Utils.aqua_ops_logger import Logger

logger = Logger().get_logger()


async def main():
    logger.info("=== AquaOps Starting ===")

    # 1. Load config from YAML files
    config_dir = Path("AquaOps/config")
    context = load_configs(config_dir)

    # 2. Sync with database — seeds on first run, overrides from DB on subsequent runs
    await sync_database(context)

    # 3. context.irrigation and context.connections are now fully loaded
    #    and ready to pass into managers
    logger.info("=== Config ready ===")
    logger.info(f"  Irrigation zones: {list(context.irrigation.zones.keys()) if context.irrigation else 'None'}")
    logger.info(f"  Database:         {'connected' if context.connections and context.connections.database else 'not configured'}")
    #logger.info(f"  MQTT:             {'configured' if context.connections and context.connections.mqtt else 'not configured'}")

    # TODO: initialise AquaOps orchestrator here
    # aqua_ops = AquaOps(context)
    # await aqua_ops.run()


if __name__ == "__main__":
    asyncio.run(main())