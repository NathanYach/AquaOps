from pathlib import Path
import sys
import yaml

from AquaOps.config_context import ConfigContext
from AquaOps.connections_config import ConnectionsConfig
from AquaOps.Irrigation.Config.irrigation_config import IrrigationConfig
from AquaOps.Utils.aqua_ops_logger import Logger

logger = Logger().get_logger()


def load_configs(config_dir: Path) -> ConfigContext:
    context = ConfigContext()

    try:
        config_dir = Path(sys.argv[1]).expanduser().resolve()

        if not config_dir.exists():
            logger.error(f"Config path does not exist: {config_dir}")
            sys.exit(1)

    except IndexError:
        logger.error("No configuration path provided in arguments.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

    logger.info("Reading configs from file...")

    for file in config_dir.glob("*.yaml"):
        with open(file) as f:
            data = yaml.safe_load(f)

        modules = data.get("modules", {})

        if "connections" in modules:
            context.connections = ConnectionsConfig.from_dict(modules["connections"])
            logger.info("Connections config loaded.")

        if "irrigation-config" in modules:
            context.irrigation = IrrigationConfig.from_dict(modules["irrigation-config"])
            logger.info("Irrigation config loaded.")

        if "aquarium-config" in modules:
            # context.aquarium = AquariumConfig.from_dict(modules["aquarium-config"])
            logger.info("Aquarium config found (not yet implemented).")

    return context