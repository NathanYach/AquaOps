from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Any

from AquaOps.Models.Safety.safety_config import SafetyRule


# ---------------------------------------------------------------------------
# Trigger
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TriggerConfig:
    type:     str = ""
    sensor:   str = ""
    operator: str = ""
    value:    Any = None

    @staticmethod
    def from_dict(data: Optional[dict]) -> TriggerConfig:
        data = data or {}
        return TriggerConfig(
            type=data.get("type",         ""),
            sensor=data.get("sensor",     ""),
            operator=data.get("operator", ""),
            value=data.get("value"),
        )


# ---------------------------------------------------------------------------
# Condition
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ConditionConfig:
    type:          str           = ""
    sensor:        str           = ""
    device:        str           = ""
    property:      str           = ""
    operator:      str           = ""
    value:         Any           = None
    value_minutes: Optional[int] = None

    @staticmethod
    def from_dict(data: Optional[dict]) -> ConditionConfig:
        data = data or {}
        return ConditionConfig(
            type=data.get("type",             ""),
            sensor=data.get("sensor",         ""),
            device=data.get("device",         ""),
            property=data.get("property",     ""),
            operator=data.get("operator",     ""),
            value=data.get("value"),
            value_minutes=data.get("value_minutes"),
        )


# ---------------------------------------------------------------------------
# Action
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ActionConfig:
    type:    str = ""
    device:  str = ""
    command: str = ""

    @staticmethod
    def from_dict(data: Optional[dict]) -> ActionConfig:
        data = data or {}
        return ActionConfig(
            type=data.get("type",       ""),
            device=data.get("device",   ""),
            command=data.get("command", ""),
        )


# ---------------------------------------------------------------------------
# Stop Condition
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class StopConditionConfig:
    type:     str = ""
    sensor:   str = ""
    operator: str = ""
    value:    Any = None

    @staticmethod
    def from_dict(data: Optional[dict]) -> StopConditionConfig:
        data = data or {}
        return StopConditionConfig(
            type=data.get("type",         ""),
            sensor=data.get("sensor",     ""),
            operator=data.get("operator", ""),
            value=data.get("value"),
        )


# ---------------------------------------------------------------------------
# Workflow Safety
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WorkflowSafetyConfig:
    """
    Safety scoped to a single workflow.
    - inherit_policies: global policy IDs to apply to this workflow
    - rules: inline rules defined directly on this workflow
    Both sets are evaluated independently by the safety engine.
    """
    inherit_policies: list[str]              = field(default_factory=list)
    rules:            dict[str, SafetyRule]  = field(default_factory=dict)

    @staticmethod
    def from_dict(data: Optional[dict]) -> WorkflowSafetyConfig:
        data = data or {}
        return WorkflowSafetyConfig(
            inherit_policies=data.get("inherit_policies", []),
            rules={
                rule_id: SafetyRule.from_dict(rule_id, rule_data)
                for rule_id, rule_data in data.get("rules", {}).items()
            },
        )


# ---------------------------------------------------------------------------
# Workflow
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WorkflowConfig:
    workflow_id:     str                       = ""
    enabled:         bool                      = False
    trigger:         TriggerConfig             = field(default_factory=TriggerConfig)
    conditions:      list[ConditionConfig]     = field(default_factory=list)
    actions:         list[ActionConfig]        = field(default_factory=list)
    stop_conditions: list[StopConditionConfig] = field(default_factory=list)
    safety:          WorkflowSafetyConfig      = field(default_factory=WorkflowSafetyConfig)

    @staticmethod
    def from_dict(workflow_id: str, data: Optional[dict]) -> WorkflowConfig:
        data = data or {}
        return WorkflowConfig(
            workflow_id=workflow_id,
            enabled=data.get("enabled", False),
            trigger=TriggerConfig.from_dict(data.get("trigger")),
            conditions=[ConditionConfig.from_dict(c) for c in data.get("conditions", [])],
            actions=[ActionConfig.from_dict(a) for a in data.get("actions", [])],
            stop_conditions=[StopConditionConfig.from_dict(s) for s in data.get("stop_conditions", [])],
            safety=WorkflowSafetyConfig.from_dict(data.get("safety")),
        )