# AquaOps/main.py
"""
AquaOps — entry point.

Startup order
─────────────
1. Logging
2. Load YAML config  (file-based source of truth)
3. Init database     (seed on first run, override from DB on subsequent runs)
4. Start controllers (module → workflow → safety → node)
5. Launch FastAPI     (optional — only if API is enabled in config)

All heavy lifting is async; asyncio.run() is the only blocking call.
"""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from AquaOps.Services.config_loader import load_configs
from AquaOps.Services.database_loader import init_database, close_database
from AquaOps.Models.config_context import ConfigContext

log = logging.getLogger("aquaops")


async def run() -> None:
    config_dir = Path(__file__).parent.parent / "config"

    # 1. Load YAML
    log.info("Loading configuration from '%s'.", config_dir)
    context = load_configs(config_dir)
    log.info(
        "Config loaded: %d module(s) — %s",
        len(context.modules),
        list(context.modules.keys()) or "none",
    )

    await init_database(context)


def main() -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


if __name__ == "__main__":
    main()