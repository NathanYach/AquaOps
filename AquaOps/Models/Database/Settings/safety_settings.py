# AquaOps/Database/Models/safety_settings.py
from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, ForeignKeyConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from AquaOps.Models.Database.base import Base
from AquaOps.Models.Safety.safety_config import SafetyPolicy, SafetyRule


class SafetyPolicySettings(Base):
    """
    A named safety policy scoped to a module or zone.
    zone_id = None  →  module-level (global) policy
    zone_id = set   →  zone-level policy

    PK is (policy_id, module_id) — both columns needed because the same
    policy_id name could appear in different modules.
    """
    __tablename__ = "safety_policy_settings"
    __table_args__ = (
        ForeignKeyConstraint(["module_id"], ["aquaops.module_settings.module_id"]),
        ForeignKeyConstraint(["zone_id"],   ["aquaops.zone_settings.zone_id"]),
        {"schema": "aquaops"},
    )

    policy_id: Mapped[str]        = mapped_column(String(100), primary_key=True)
    module_id: Mapped[str]        = mapped_column(String(100), primary_key=True)
    zone_id:   Mapped[str | None] = mapped_column(String(100), nullable=True)
    enabled:   Mapped[bool]       = mapped_column(Boolean, default=True)

    module: Mapped["ModuleSettings"]           = relationship(back_populates="safety_policies")
    zone:   Mapped["ZoneSettings | None"]      = relationship(back_populates="safety_policies")
    rules:  Mapped[list["SafetyRuleSettings"]] = relationship(
        back_populates="policy",
        foreign_keys="[SafetyRuleSettings.policy_id, SafetyRuleSettings.module_id]",
        cascade="all, delete-orphan",
    )

    @staticmethod
    def from_dataclass(
        module_id: str,
        cfg: SafetyPolicy,
        zone_id: str | None = None,
    ) -> SafetyPolicySettings:
        return SafetyPolicySettings(
            policy_id=cfg.policy_id,
            module_id=module_id,
            zone_id=zone_id,
            enabled=cfg.enabled,
            rules=[
                SafetyRuleSettings.from_dataclass(
                    rule_id=rule_id,
                    cfg=rule,
                    policy_id=cfg.policy_id,
                    module_id=module_id,
                )
                for rule_id, rule in cfg.rules.items()
            ],
        )


class SafetyRuleSettings(Base):
    """
    A single safety rule belonging to either a policy or a workflow.
    Exactly one of (policy_id+module_id) or (workflow_id+zone_id) should be set.

    FKs use composite references to match the composite PKs of their
    parent tables — required by PostgreSQL.
    """
    __tablename__ = "safety_rule_settings"
    __table_args__ = (
        # FK → safety_policy_settings (composite PK: policy_id + module_id)
        ForeignKeyConstraint(
            ["policy_id", "module_id"],
            ["aquaops.safety_policy_settings.policy_id", "aquaops.safety_policy_settings.module_id"],
            ondelete="CASCADE",
        ),
        # FK → workflow_settings (composite PK: workflow_id + zone_id)
        ForeignKeyConstraint(
            ["workflow_id", "zone_id"],
            ["aquaops.workflow_settings.workflow_id", "aquaops.workflow_settings.zone_id"],
            ondelete="CASCADE",
        ),
        {"schema": "aquaops"},
    )

    rule_id:     Mapped[str]        = mapped_column(String(100), primary_key=True)
    # Policy scope (nullable when attached to a workflow instead)
    policy_id:   Mapped[str | None] = mapped_column(String(100), nullable=True)
    module_id:   Mapped[str | None] = mapped_column(String(100), nullable=True)
    # Workflow scope (nullable when attached to a policy instead)
    workflow_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    zone_id:     Mapped[str | None] = mapped_column(String(100), nullable=True)

    type:     Mapped[str]          = mapped_column(String(100), default="")
    enabled:  Mapped[bool]         = mapped_column(Boolean,     default=True)
    action:   Mapped[str]          = mapped_column(String(50),  default="shutdown")
    limit:    Mapped[int | None]   = mapped_column(Integer,     nullable=True)
    sensor:   Mapped[str]          = mapped_column(String(100), default="")
    operator: Mapped[str]          = mapped_column(String(10),  default="")
    value:    Mapped[str | None]   = mapped_column(String(100), nullable=True)

    policy:   Mapped["SafetyPolicySettings | None"] = relationship(
        back_populates="rules",
        foreign_keys="[SafetyRuleSettings.policy_id, SafetyRuleSettings.module_id]",
    )
    workflow: Mapped["WorkflowSettings | None"] = relationship(
        back_populates="safety_rules",
        foreign_keys="[SafetyRuleSettings.workflow_id, SafetyRuleSettings.zone_id]",
    )

    @staticmethod
    def from_dataclass(
        rule_id:     str,
        cfg:         SafetyRule,
        policy_id:   str | None = None,
        module_id:   str | None = None,
        workflow_id: str | None = None,
        zone_id:     str | None = None,
    ) -> SafetyRuleSettings:
        return SafetyRuleSettings(
            rule_id=rule_id,
            policy_id=policy_id,
            module_id=module_id,
            workflow_id=workflow_id,
            zone_id=zone_id,
            type=cfg.type,
            enabled=cfg.enabled,
            action=cfg.action,
            limit=cfg.limit,
            sensor=cfg.sensor,
            operator=cfg.operator,
            value=str(cfg.value) if cfg.value is not None else None,
        )