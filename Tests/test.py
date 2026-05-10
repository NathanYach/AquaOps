import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from AquaOps.Models_loader import load_configs


def indent(level: int) -> str:
    return "  " * level


def print_section(title: str, level: int = 0):
    print(f"{indent(level)}[{title}]")


def print_field(key: str, value, level: int = 1):
    print(f"{indent(level)}{key}: {value}")


def print_config(config_dir: Path):
    context = load_configs(config_dir)
    cfg = context.irrigation

    if cfg is None:
        print("No irrigation config loaded.")
        return

    print(f"\n{'='*60}")
    print(f"  Irrigation Config: {config_dir}")
    print(f"{'='*60}\n")




    print_section("System")
    print_field("enabled",                    cfg.system.enabled)
    print_field("telemetry_interval_seconds", cfg.system.telemetry_interval_seconds)




    print()
    print_section("Global Safety")
    print_field("enabled", cfg.global_safety.enabled)

    print_section("Leak Detection", level=1)
    print_field("enabled",                    cfg.global_safety.leak_detection.enabled,                  level=2)
    print_field("shutdown_all_zones_on_leak", cfg.global_safety.leak_detection.shutdown_all_zones_on_leak, level=2)
    print_field("alert_on_detection",         cfg.global_safety.leak_detection.alert_on_detection,        level=2)

    print_section("Emergency Shutdown", level=1)
    print_field("enabled",             cfg.global_safety.emergency_shutdown.enabled,          level=2)
    print_field("disable_all_valves",  cfg.global_safety.emergency_shutdown.disable_all_valves, level=2)
    print_field("disable_all_pumps",   cfg.global_safety.emergency_shutdown.disable_all_pumps,  level=2)

    print_section("Runtime Limits", level=1)
    print_field("global_max_continuous_runtime_seconds", cfg.global_safety.runtime_limits.global_max_continuous_runtime_seconds, level=2)
    print_field("global_max_daily_delivery_ml",          cfg.global_safety.runtime_limits.global_max_daily_delivery_ml,          level=2)

    print_section("Sensor Validation", level=1)
    print_field("shutdown_on_sensor_failure",         cfg.global_safety.sensor_validation.shutdown_on_sensor_failure,          level=2)
    print_field("ignore_invalid_readings",            cfg.global_safety.sensor_validation.ignore_invalid_readings,             level=2)
    print_field("max_invalid_readings_before_shutdown", cfg.global_safety.sensor_validation.max_invalid_readings_before_shutdown, level=2)




    print()
    print_section(f"Zones ({len(cfg.zones)} loaded)")

    for zone_id, z in cfg.zones.items():
        print()
        print_section(f"Zone: {zone_id}", level=1)
        print_field("zone_id",      z.zone_id,      level=2)
        print_field("display_name", z.display_name, level=2)
        print_field("enabled",      z.enabled,      level=2)

        print_section("Environment", level=2)
        print_field("target_air_temp_c",       z.environment.target_air_temp_c,       level=3)
        print_field("target_humidity_percent", z.environment.target_humidity_percent, level=3)
        print_field("light_duration_hours",    z.environment.light_duration_hours,    level=3)

        print_section("Soil", level=2)
        print_field("target_moisture_percent",   z.soil.target_moisture_percent,   level=3)
        print_field("moisture_tolerance_percent", z.soil.moisture_tolerance_percent, level=3)

        print_section("Watering", level=2)
        print_field("preferred_water_source",          z.watering.preferred_water_source,          level=3)
        print_field("fallback_water_source",           z.watering.fallback_water_source,           level=3)
        print_field("trigger_below_moisture_percent",  z.watering.trigger_below_moisture_percent,  level=3)
        print_field("target_delivery_ml",              z.watering.target_delivery_ml,              level=3)
        print_field("max_delivery_ml",                 z.watering.max_delivery_ml,                 level=3)
        print_field("estimated_flow_rate_ml_per_second", z.watering.estimated_flow_rate_ml_per_second, level=3)
        print_field("minimum_interval_minutes",        z.watering.minimum_interval_minutes,        level=3)
        print_field("max_watering_duration_seconds",   z.watering.max_watering_duration_seconds,   level=3)

        print_section("Safety", level=3)
        print_field("leak_detection_enabled",          z.watering.safety.leak_detection_enabled,          level=4)
        print_field("auto_shutdown_on_sensor_failure", z.watering.safety.auto_shutdown_on_sensor_failure, level=4)
        print_field("max_daily_delivery_ml",           z.watering.safety.max_daily_delivery_ml,           level=4)
        print_field("max_continuous_runtime_seconds",  z.watering.safety.max_continuous_runtime_seconds,  level=4)

        print_section("Hardware", level=2)
        print_field("valve_id",             z.hardware.valve_id,             level=3)
        print_field("moisture_sensor_id",   z.hardware.moisture_sensor_id,   level=3)
        print_field("temperature_sensor_id", z.hardware.temperature_sensor_id, level=3)
        print_field("grow_light_id",        z.hardware.grow_light_id,        level=3)

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python print_config.py <config_dir>")
        sys.exit(1)

    print_config(Path(sys.argv[1]))