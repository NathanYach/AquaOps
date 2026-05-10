import unittest
import argparse
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from AquaOps.Services.config_loader import load_configs


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_dir", help="Path to the directory containing *.yaml config files.")
    args, remaining = parser.parse_known_args()
    return args, remaining


args, remaining_argv = parse_args()
CONFIG_DIR = Path(args.config_dir)


def setUpModule():
    global cfg
    context = load_configs(CONFIG_DIR)
    cfg = context.irrigation






class TestIrrigationConfigLoaded(unittest.TestCase):
    def test_irrigation_config_is_not_none(self):
        self.assertIsNotNone(cfg, "IrrigationConfig was not loaded (returned None)")






class TestSystemConfig(unittest.TestCase):
    def test_system_enabled(self):
        self.assertTrue(cfg.system.enabled)

    def test_system_telemetry_interval(self):
        self.assertEqual(cfg.system.telemetry_interval_seconds, 30)






class TestGlobalSafetyConfig(unittest.TestCase):
    def test_global_safety_enabled(self):
        self.assertTrue(cfg.global_safety.enabled)


    def test_leak_detection_enabled(self):
        self.assertTrue(cfg.global_safety.leak_detection.enabled)

    def test_leak_detection_shutdown_all_zones(self):
        self.assertTrue(cfg.global_safety.leak_detection.shutdown_all_zones_on_leak)

    def test_leak_detection_alert(self):
        self.assertTrue(cfg.global_safety.leak_detection.alert_on_detection)


    def test_emergency_shutdown_enabled(self):
        self.assertTrue(cfg.global_safety.emergency_shutdown.enabled)

    def test_emergency_shutdown_valves(self):
        self.assertTrue(cfg.global_safety.emergency_shutdown.disable_all_valves)

    def test_emergency_shutdown_pumps(self):
        self.assertTrue(cfg.global_safety.emergency_shutdown.disable_all_pumps)


    def test_runtime_limits_max_continuous(self):
        self.assertEqual(cfg.global_safety.runtime_limits.global_max_continuous_runtime_seconds, 300)

    def test_runtime_limits_max_daily_delivery(self):
        self.assertEqual(cfg.global_safety.runtime_limits.global_max_daily_delivery_ml, 20000)


    def test_sensor_validation_shutdown_on_failure(self):
        self.assertTrue(cfg.global_safety.sensor_validation.shutdown_on_sensor_failure)

    def test_sensor_validation_ignore_invalid(self):
        self.assertFalse(cfg.global_safety.sensor_validation.ignore_invalid_readings)

    def test_sensor_validation_max_invalid_readings(self):
        self.assertEqual(cfg.global_safety.sensor_validation.max_invalid_readings_before_shutdown, 5)






class TestZonesLoaded(unittest.TestCase):
    def test_zones_not_empty(self):
        self.assertGreater(len(cfg.zones), 0, "No zones were loaded")

    def test_herbs_zone_exists(self):
        self.assertIn("herbs", cfg.zones)

    def test_tropicals_zone_exists(self):
        self.assertIn("tropicals", cfg.zones)






class TestHerbsZone(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.z = cfg.zones["herbs"]

    def test_zone_id(self):
        self.assertEqual(self.z.zone_id, "herbs")

    def test_display_name(self):
        self.assertEqual(self.z.display_name, "Herb Garden")

    def test_enabled(self):
        self.assertTrue(self.z.enabled)


    def test_target_air_temp(self):
        self.assertEqual(self.z.environment.target_air_temp_c, 22)

    def test_target_humidity(self):
        self.assertEqual(self.z.environment.target_humidity_percent, 55)

    def test_light_duration(self):
        self.assertEqual(self.z.environment.light_duration_hours, 14)


    def test_target_moisture(self):
        self.assertEqual(self.z.soil.target_moisture_percent, 45)

    def test_moisture_tolerance(self):
        self.assertEqual(self.z.soil.moisture_tolerance_percent, 5)


    def test_preferred_water_source(self):
        self.assertEqual(self.z.watering.preferred_water_source, "aquarium")

    def test_fallback_water_source(self):
        self.assertEqual(self.z.watering.fallback_water_source, "conditioned")

    def test_trigger_below_moisture(self):
        self.assertEqual(self.z.watering.trigger_below_moisture_percent, 40)

    def test_target_delivery_ml(self):
        self.assertEqual(self.z.watering.target_delivery_ml, 500)

    def test_max_delivery_ml(self):
        self.assertEqual(self.z.watering.max_delivery_ml, 1000)

    def test_flow_rate(self):
        self.assertEqual(self.z.watering.estimated_flow_rate_ml_per_second, 25)

    def test_minimum_interval(self):
        self.assertEqual(self.z.watering.minimum_interval_minutes, 120)

    def test_max_watering_duration(self):
        self.assertEqual(self.z.watering.max_watering_duration_seconds, 90)


    def test_safety_leak_detection(self):
        self.assertTrue(self.z.watering.safety.leak_detection_enabled)

    def test_safety_auto_shutdown(self):
        self.assertTrue(self.z.watering.safety.auto_shutdown_on_sensor_failure)

    def test_safety_max_daily_delivery(self):
        self.assertEqual(self.z.watering.safety.max_daily_delivery_ml, 3000)

    def test_safety_max_continuous_runtime(self):
        self.assertEqual(self.z.watering.safety.max_continuous_runtime_seconds, 120)


    def test_valve_id(self):
        self.assertEqual(self.z.hardware.valve_id, "valve_1")

    def test_moisture_sensor_id(self):
        self.assertEqual(self.z.hardware.moisture_sensor_id, "soil_1")

    def test_temperature_sensor_id(self):
        self.assertEqual(self.z.hardware.temperature_sensor_id, "temp_1")

    def test_grow_light_id(self):
        self.assertEqual(self.z.hardware.grow_light_id, "light_1")






class TestTropicalsZone(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.z = cfg.zones["tropicals"]

    def test_zone_id(self):
        self.assertEqual(self.z.zone_id, "tropicals")

    def test_display_name(self):
        self.assertEqual(self.z.display_name, "Tropical Plants")

    def test_enabled(self):
        self.assertTrue(self.z.enabled)


    def test_target_air_temp(self):
        self.assertEqual(self.z.environment.target_air_temp_c, 26)

    def test_target_humidity(self):
        self.assertEqual(self.z.environment.target_humidity_percent, 75)

    def test_light_duration(self):
        self.assertEqual(self.z.environment.light_duration_hours, 12)


    def test_target_moisture(self):
        self.assertEqual(self.z.soil.target_moisture_percent, 70)

    def test_moisture_tolerance(self):
        self.assertEqual(self.z.soil.moisture_tolerance_percent, 4)


    def test_preferred_water_source(self):
        self.assertEqual(self.z.watering.preferred_water_source, "aquarium")

    def test_fallback_water_source(self):
        self.assertEqual(self.z.watering.fallback_water_source, "conditioned")

    def test_trigger_below_moisture(self):
        self.assertEqual(self.z.watering.trigger_below_moisture_percent, 65)

    def test_target_delivery_ml(self):
        self.assertEqual(self.z.watering.target_delivery_ml, 1200)

    def test_max_delivery_ml(self):
        self.assertEqual(self.z.watering.max_delivery_ml, 2000)

    def test_flow_rate(self):
        self.assertEqual(self.z.watering.estimated_flow_rate_ml_per_second, 40)

    def test_minimum_interval(self):
        self.assertEqual(self.z.watering.minimum_interval_minutes, 90)

    def test_max_watering_duration(self):
        self.assertEqual(self.z.watering.max_watering_duration_seconds, 180)


    def test_safety_leak_detection(self):
        self.assertTrue(self.z.watering.safety.leak_detection_enabled)

    def test_safety_auto_shutdown(self):
        self.assertTrue(self.z.watering.safety.auto_shutdown_on_sensor_failure)

    def test_safety_max_daily_delivery(self):
        self.assertEqual(self.z.watering.safety.max_daily_delivery_ml, 8000)

    def test_safety_max_continuous_runtime(self):
        self.assertEqual(self.z.watering.safety.max_continuous_runtime_seconds, 240)


    def test_valve_id(self):
        self.assertEqual(self.z.hardware.valve_id, "valve_2")

    def test_moisture_sensor_id(self):
        self.assertEqual(self.z.hardware.moisture_sensor_id, "soil_2")

    def test_temperature_sensor_id(self):
        self.assertEqual(self.z.hardware.temperature_sensor_id, "temp_2")

    def test_grow_light_id(self):
        self.assertEqual(self.z.hardware.grow_light_id, "light_2")


if __name__ == "__main__":
    import sys
    unittest.main(argv=[sys.argv[0]] + remaining_argv)