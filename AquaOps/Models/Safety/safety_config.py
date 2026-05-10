from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Any


# ---------------------------------------------------------------------------
# Safety Rule
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SafetyRule:
    """
    A single independently evaluated safety rule.

    Duration-based:
        type: max_runtime
        limit: 300
        action: shutdown

    Sensor-based:
        type: sensor_threshold
        sensor: leak_sensor
        operator: "=="
        value: true
        action: shutdown

    Volume-based:
        type: max_volume_ml
        limit: 5000
        action: shutdown

    Failure-based:
        type: sensor_failure
        action: alert
    """
    rule_id:  str           = ""
    type:     str           = ""
    enabled:  bool          = True
    action:   str           = "shutdown"    # shutdown | alert | pause

    # Duration / volume / count based
    limit:    Optional[int] = None

    # Sensor based
    sensor:   str           = ""
    operator: str           = ""
    value:    Any           = None

    @staticmethod
    def from_dict(rule_id: str, data: Optional[dict]) -> SafetyRule:
        data = data or {}
        return SafetyRule(
            rule_id=rule_id,
            type=data.get("type",         ""),
            enabled=data.get("enabled",   True),
            action=data.get("action",     "shutdown"),
            limit=data.get("limit"),
            sensor=data.get("sensor",     ""),
            operator=data.get("operator", ""),
            value=data.get("value"),
        )


# ---------------------------------------------------------------------------
# Safety Policy
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SafetyPolicy:
    """
    A named, reusable collection of safety rules.
    Can be applied globally, per module, per zone, or per workflow.
    """
    policy_id: str                   = ""
    enabled:   bool                  = True
    rules:     dict[str, SafetyRule] = field(default_factory=dict)

    @staticmethod
    def from_dict(policy_id: str, data: Optional[dict]) -> SafetyPolicy:
        data = data or {}
        return SafetyPolicy(
            policy_id=policy_id,
            enabled=data.get("enabled", True),
            rules={
                rule_id: SafetyRule.from_dict(rule_id, rule_data)
                for rule_id, rule_data in data.get("rules", {}).items()
            },
        )


# ---------------------------------------------------------------------------
# Global Safety Config
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GlobalSafetyConfig:
    """
    Platform-wide safety policies applied to all modules and zones
    unless overridden at a lower level.
    """
    enabled:  bool                    = True
    policies: dict[str, SafetyPolicy] = field(default_factory=dict)

    @staticmethod
    def from_dict(data: Optional[dict]) -> GlobalSafetyConfig:
        data = data or {}
        return GlobalSafetyConfig(
            enabled=data.get("enabled", True),
            policies={
                policy_id: SafetyPolicy.from_dict(policy_id, policy_data)
                for policy_id, policy_data in data.get("policies", {}).items()
            },
        )