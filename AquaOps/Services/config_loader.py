# AquaOps/Services/config_loader.py
from pathlib import Path
import yaml

from AquaOps.Models.config_context import ConfigContext
from AquaOps.Models.Connection.connections_config import ConnectionsConfig
from AquaOps.Models.Modules.module_config import ModuleConfig
from AquaOps.Services.aqua_ops_logger import Logger

logger = Logger().get_logger()


def load_configs(config_dir: Path) -> ConfigContext:
    context = ConfigContext()

    if not config_dir.exists():
        logger.error(f"Config path does not exist: {config_dir}")
        raise FileNotFoundError(f"Config directory not found: {config_dir}")

    yaml_files = list(config_dir.glob("*.yaml"))
    modules_dir = config_dir / "modules"
    if modules_dir.exists():
        yaml_files += list(modules_dir.glob("*.yaml"))

    if not yaml_files:
        logger.warning(f"No YAML files found in '{config_dir}'.")
        return context

    for file in yaml_files:
        with open(file) as f:
            data = yaml.safe_load(f)

        if not data:
            continue

        modules = data.get("modules", {})

        if "connections" in modules:
            context.connections = ConnectionsConfig.from_dict(modules["connections"])
            logger.info("Connections config loaded.")

        for module_id, module_data in modules.items():
            if module_id == "connections" or not isinstance(module_data, dict):
                continue
            context.modules[module_id] = ModuleConfig.from_dict(module_id, module_data)
            logger.info(f"Module loaded: '{module_id}'.")

    logger.info(f"Config loaded: {len(context.modules)} module(s) — {list(context.modules.keys())}")
    return context