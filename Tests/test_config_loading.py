"""
Tests/test_config_loading.py
Usage: python run_tests.py <config_dir>
       python -m pytest Tests/ --config-dir=<config_dir>

Tests the generic ModuleConfig / ZoneConfig / WorkflowConfig layer.
No domain-specific (irrigation-only) assumptions — validates whatever
modules are declared in the YAML under config/modules/.
"""

import unittest
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from AquaOps.Services.config_loader import load_configs
from AquaOps.Models.config_context import ConfigContext


def _parse_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("config_dir", help="Path to config directory")
    args, remaining = parser.parse_known_args()
    return Path(args.config_dir), remaining


CONFIG_DIR, _remaining_argv = _parse_args()
context: ConfigContext


def setUpModule():
    global context
    context = load_configs(CONFIG_DIR)


class TestContextLoaded(unittest.TestCase):

    def test_context_is_not_none(self):
        self.assertIsNotNone(context)

    def test_at_least_one_module_loaded(self):
        self.assertGreater(len(context.modules), 0, "No modules were loaded from YAML")


class TestConnections(unittest.TestCase):

    def test_connections_attribute_exists(self):
        self.assertTrue(hasattr(context, "connections"))

    @unittest.skipIf(
        lambda: not (context.connections and context.connections.database),
        "No database configured — skipping DB connection tests"
    )
    def test_database_host_not_empty(self):
        self.assertTrue(context.connections.database.host)

    @unittest.skipIf(
        lambda: not (context.connections and context.connections.database),
        "No database configured"
    )
    def test_database_port_is_positive(self):
        self.assertGreater(context.connections.database.port, 0)


def _make_module_tests(module_id: str):
    """
    Dynamically generates a TestCase class for one module.
    This lets unittest discover and report each module independently.
    """

    class ModuleTests(unittest.TestCase):

        @classmethod
        def setUpClass(cls):
            cls.module = context.modules[module_id]

        def test_module_id_matches_key(self):
            self.assertEqual(self.module.module_id, module_id)

        def test_module_has_system_config(self):
            self.assertIsNotNone(self.module.system)

        def test_system_log_level_valid(self):
            valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
            self.assertIn(self.module.system.log_level.upper(), valid)

        def test_system_telemetry_interval_positive(self):
            self.assertGreater(self.module.system.telemetry_interval_seconds, 0)

        def test_module_has_global_safety(self):
            self.assertIsNotNone(self.module.global_safety)

        def test_zones_is_dict(self):
            self.assertIsInstance(self.module.zones, dict)

    ModuleTests.__name__ = f"TestModule_{module_id}"
    ModuleTests.__qualname__ = ModuleTests.__name__
    return ModuleTests

def _make_zone_tests(module_id: str, zone_id: str):

    class ZoneTests(unittest.TestCase):

        @classmethod
        def setUpClass(cls):
            cls.zone = context.modules[module_id].zones[zone_id]

        def test_zone_id_matches_key(self):
            self.assertEqual(self.zone.zone_id, zone_id)

        def test_display_name_is_string(self):
            self.assertIsInstance(self.zone.display_name, str)

        def test_enabled_is_bool(self):
            self.assertIsInstance(self.zone.enabled, bool)

        def test_devices_is_dict(self):
            self.assertIsInstance(self.zone.devices, dict)

        def test_sensors_is_dict(self):
            self.assertIsInstance(self.zone.sensors, dict)

        def test_workflows_is_dict(self):
            self.assertIsInstance(self.zone.workflows, dict)

        def test_safety_is_dict(self):
            self.assertIsInstance(self.zone.safety, dict)

        def test_properties_is_dict(self):
            self.assertIsInstance(self.zone.properties, dict)

        def test_device_nodes_not_empty_when_present(self):
            for dev_id, dev in self.zone.devices.items():
                with self.subTest(device=dev_id):
                    self.assertTrue(dev.type, f"Device '{dev_id}' has no type")

        def test_sensor_nodes_not_empty_when_present(self):
            for sen_id, sen in self.zone.sensors.items():
                with self.subTest(sensor=sen_id):
                    self.assertTrue(sen.type, f"Sensor '{sen_id}' has no type")

    ZoneTests.__name__ = f"TestZone_{module_id}_{zone_id}"
    ZoneTests.__qualname__ = ZoneTests.__name__
    return ZoneTests

def _make_workflow_tests(module_id: str, zone_id: str, wf_id: str):

    class WorkflowTests(unittest.TestCase):

        @classmethod
        def setUpClass(cls):
            cls.wf = context.modules[module_id].zones[zone_id].workflows[wf_id]

        def test_workflow_id_matches_key(self):
            self.assertEqual(self.wf.workflow_id, wf_id)

        def test_enabled_is_bool(self):
            self.assertIsInstance(self.wf.enabled, bool)

        def test_trigger_has_type(self):
            self.assertTrue(self.wf.trigger.type,
                            f"Workflow '{wf_id}' trigger has no type")

        def test_actions_not_empty(self):
            self.assertGreater(len(self.wf.actions), 0,
                               f"Workflow '{wf_id}' has no actions")

        def test_action_devices_not_empty(self):
            for i, action in enumerate(self.wf.actions):
                with self.subTest(action=i):
                    self.assertTrue(action.device or action.type,
                                    f"Action [{i}] in workflow '{wf_id}' has no device or type")

        def test_safety_inherit_policies_is_list(self):
            self.assertIsInstance(self.wf.safety.inherit_policies, list)

        def test_safety_rules_is_dict(self):
            self.assertIsInstance(self.wf.safety.rules, dict)

    WorkflowTests.__name__ = f"TestWorkflow_{module_id}_{zone_id}_{wf_id}"
    WorkflowTests.__qualname__ = WorkflowTests.__name__
    return WorkflowTests



def _make_safety_policy_tests(module_id: str, policy_id: str, zone_id: str | None = None):
    scope = f"{module_id}_zone_{zone_id}" if zone_id else f"{module_id}_global"

    class SafetyPolicyTests(unittest.TestCase):

        @classmethod
        def setUpClass(cls):
            mod = context.modules[module_id]
            if zone_id:
                cls.policy = mod.zones[zone_id].safety[policy_id]
            else:
                cls.policy = mod.global_safety.policies[policy_id]

        def test_policy_id_matches_key(self):
            self.assertEqual(self.policy.policy_id, policy_id)

        def test_enabled_is_bool(self):
            self.assertIsInstance(self.policy.enabled, bool)

        def test_rules_is_dict(self):
            self.assertIsInstance(self.policy.rules, dict)

        def test_each_rule_has_type(self):
            for rule_id, rule in self.policy.rules.items():
                with self.subTest(rule=rule_id):
                    self.assertTrue(rule.type, f"Rule '{rule_id}' has no type")

        def test_each_rule_action_valid(self):
            valid = {"shutdown", "alert", "pause"}
            for rule_id, rule in self.policy.rules.items():
                with self.subTest(rule=rule_id):
                    self.assertIn(rule.action, valid,
                                  f"Rule '{rule_id}' action '{rule.action}' not in {valid}")

    SafetyPolicyTests.__name__ = f"TestSafetyPolicy_{scope}_{policy_id}"
    SafetyPolicyTests.__qualname__ = SafetyPolicyTests.__name__
    return SafetyPolicyTests



def _register_dynamic_tests():
    g = globals()
    for module_id, module in context.modules.items():
        g[f"TestModule_{module_id}"] = _make_module_tests(module_id)

        for policy_id in module.global_safety.policies:
            g[f"TestSafetyPolicy_{module_id}_global_{policy_id}"] = \
                _make_safety_policy_tests(module_id, policy_id)

        for zone_id, zone in module.zones.items():
            g[f"TestZone_{module_id}_{zone_id}"] = _make_zone_tests(module_id, zone_id)

            for wf_id in zone.workflows:
                g[f"TestWorkflow_{module_id}_{zone_id}_{wf_id}"] = \
                    _make_workflow_tests(module_id, zone_id, wf_id)

            for policy_id in zone.safety:
                g[f"TestSafetyPolicy_{module_id}_zone_{zone_id}_{policy_id}"] = \
                    _make_safety_policy_tests(module_id, policy_id, zone_id=zone_id)


try:
    _register_dynamic_tests()
except Exception:
    pass 


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]] + _remaining_argv)