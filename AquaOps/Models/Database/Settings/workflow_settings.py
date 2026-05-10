# AquaOps/Database/Models/workflow_settings.py
from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, ForeignKeyConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from AquaOps.Database.base import Base
from AquaOps.Models.Modules.workflow_config import (
    ActionConfig,
    ConditionConfig,
    StopConditionConfig,
    TriggerConfig,
    WorkflowConfig,
)


class WorkflowSettings(Base):
    __tablename__ = "workflow_settings"
    __table_args__ = {"schema": "aquaops"}

    workflow_id: Mapped[str]  = mapped_column(String(100), primary_key=True)
    zone_id:     Mapped[str]  = mapped_column(String(100), primary_key=True)
    enabled:     Mapped[bool] = mapped_column(Boolean, default=False)

    # zone_id → zone_settings FK is a simple single-column ref (zone_id is PK there)
    __table_args__ = (
        ForeignKeyConstraint(["zone_id"], ["aquaops.zone_settings.zone_id"]),
        {"schema": "aquaops"},
    )

    zone:            Mapped["ZoneSettings"]                    = relationship(back_populates="workflows")
    trigger:         Mapped["WorkflowTrigger"]                 = relationship(back_populates="workflow", uselist=False, cascade="all, delete-orphan")
    conditions:      Mapped[list["WorkflowCondition"]]         = relationship(back_populates="workflow", cascade="all, delete-orphan")
    actions:         Mapped[list["WorkflowAction"]]            = relationship(back_populates="workflow", cascade="all, delete-orphan")
    stop_conditions: Mapped[list["WorkflowStopCondition"]]     = relationship(back_populates="workflow", cascade="all, delete-orphan")
    safety_policies: Mapped[list["WorkflowSafetyInheritance"]] = relationship(back_populates="workflow", cascade="all, delete-orphan")
    safety_rules:    Mapped[list["SafetyRuleSettings"]]        = relationship(back_populates="workflow", cascade="all, delete-orphan")

    @staticmethod
    def from_dataclass(zone_id: str, cfg: WorkflowConfig) -> WorkflowSettings:
        from AquaOps.Models.Database.Settings.safety_settings import SafetyRuleSettings
        return WorkflowSettings(
            workflow_id=cfg.workflow_id,
            zone_id=zone_id,
            enabled=cfg.enabled,
            trigger=WorkflowTrigger.from_dataclass(cfg.workflow_id, zone_id, cfg.trigger),
            conditions=[
                WorkflowCondition.from_dataclass(cfg.workflow_id, zone_id, i, c)
                for i, c in enumerate(cfg.conditions)
            ],
            actions=[
                WorkflowAction.from_dataclass(cfg.workflow_id, zone_id, i, a)
                for i, a in enumerate(cfg.actions)
            ],
            stop_conditions=[
                WorkflowStopCondition.from_dataclass(cfg.workflow_id, zone_id, i, s)
                for i, s in enumerate(cfg.stop_conditions)
            ],
            safety_policies=[
                WorkflowSafetyInheritance(
                    workflow_id=cfg.workflow_id,
                    zone_id=zone_id,
                    policy_id=p,
                )
                for p in cfg.safety.inherit_policies
            ],
            safety_rules=[
                SafetyRuleSettings.from_dataclass(
                    rule_id=rule_id, cfg=rule,
                    workflow_id=cfg.workflow_id, zone_id=zone_id,
                )
                for rule_id, rule in cfg.safety.rules.items()
            ],
        )


class WorkflowTrigger(Base):
    __tablename__ = "workflow_trigger"
    __table_args__ = (
        # FK must match the composite PK of workflow_settings
        ForeignKeyConstraint(
            ["workflow_id", "zone_id"],
            ["aquaops.workflow_settings.workflow_id", "aquaops.workflow_settings.zone_id"],
            ondelete="CASCADE",
        ),
        {"schema": "aquaops"},
    )

    workflow_id: Mapped[str]           = mapped_column(String(100), primary_key=True)
    zone_id:     Mapped[str]           = mapped_column(String(100), primary_key=True)
    type:        Mapped[str]           = mapped_column(String(100), default="")
    sensor:      Mapped[str]           = mapped_column(String(100), default="")
    operator:    Mapped[str]           = mapped_column(String(10),  default="")
    value:       Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    workflow: Mapped["WorkflowSettings"] = relationship(back_populates="trigger")

    @staticmethod
    def from_dataclass(workflow_id: str, zone_id: str, cfg: TriggerConfig) -> WorkflowTrigger:
        return WorkflowTrigger(
            workflow_id=workflow_id,
            zone_id=zone_id,
            type=cfg.type,
            sensor=cfg.sensor,
            operator=cfg.operator,
            value=str(cfg.value) if cfg.value is not None else None,
        )


class WorkflowCondition(Base):
    __tablename__ = "workflow_condition"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workflow_id", "zone_id"],
            ["aquaops.workflow_settings.workflow_id", "aquaops.workflow_settings.zone_id"],
            ondelete="CASCADE",
        ),
        {"schema": "aquaops"},
    )

    id:            Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    workflow_id:   Mapped[str]           = mapped_column(String(100))
    zone_id:       Mapped[str]           = mapped_column(String(100))
    sequence:      Mapped[int]           = mapped_column(Integer, default=0)
    type:          Mapped[str]           = mapped_column(String(100), default="")
    sensor:        Mapped[str]           = mapped_column(String(100), default="")
    device:        Mapped[str]           = mapped_column(String(100), default="")
    property:      Mapped[str]           = mapped_column(String(100), default="")
    operator:      Mapped[str]           = mapped_column(String(10),  default="")
    value:         Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    value_minutes: Mapped[Optional[int]] = mapped_column(Integer,     nullable=True)

    workflow: Mapped["WorkflowSettings"] = relationship(back_populates="conditions")

    @staticmethod
    def from_dataclass(workflow_id: str, zone_id: str, seq: int, cfg: ConditionConfig) -> WorkflowCondition:
        return WorkflowCondition(
            workflow_id=workflow_id, zone_id=zone_id, sequence=seq,
            type=cfg.type, sensor=cfg.sensor, device=cfg.device,
            property=cfg.property, operator=cfg.operator,
            value=str(cfg.value) if cfg.value is not None else None,
            value_minutes=cfg.value_minutes,
        )


class WorkflowAction(Base):
    __tablename__ = "workflow_action"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workflow_id", "zone_id"],
            ["aquaops.workflow_settings.workflow_id", "aquaops.workflow_settings.zone_id"],
            ondelete="CASCADE",
        ),
        {"schema": "aquaops"},
    )

    id:          Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workflow_id: Mapped[str] = mapped_column(String(100))
    zone_id:     Mapped[str] = mapped_column(String(100))
    sequence:    Mapped[int] = mapped_column(Integer, default=0)
    type:        Mapped[str] = mapped_column(String(100), default="")
    device:      Mapped[str] = mapped_column(String(100), default="")
    command:     Mapped[str] = mapped_column(String(100), default="")

    workflow: Mapped["WorkflowSettings"] = relationship(back_populates="actions")

    @staticmethod
    def from_dataclass(workflow_id: str, zone_id: str, seq: int, cfg: ActionConfig) -> WorkflowAction:
        return WorkflowAction(
            workflow_id=workflow_id, zone_id=zone_id, sequence=seq,
            type=cfg.type, device=cfg.device, command=cfg.command,
        )


class WorkflowStopCondition(Base):
    __tablename__ = "workflow_stop_condition"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workflow_id", "zone_id"],
            ["aquaops.workflow_settings.workflow_id", "aquaops.workflow_settings.zone_id"],
            ondelete="CASCADE",
        ),
        {"schema": "aquaops"},
    )

    id:          Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    workflow_id: Mapped[str]           = mapped_column(String(100))
    zone_id:     Mapped[str]           = mapped_column(String(100))
    sequence:    Mapped[int]           = mapped_column(Integer, default=0)
    type:        Mapped[str]           = mapped_column(String(100), default="")
    sensor:      Mapped[str]           = mapped_column(String(100), default="")
    operator:    Mapped[str]           = mapped_column(String(10),  default="")
    value:       Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    workflow: Mapped["WorkflowSettings"] = relationship(back_populates="stop_conditions")

    @staticmethod
    def from_dataclass(workflow_id: str, zone_id: str, seq: int, cfg: StopConditionConfig) -> WorkflowStopCondition:
        return WorkflowStopCondition(
            workflow_id=workflow_id, zone_id=zone_id, sequence=seq,
            type=cfg.type, sensor=cfg.sensor, operator=cfg.operator,
            value=str(cfg.value) if cfg.value is not None else None,
        )


class WorkflowSafetyInheritance(Base):
    """Junction table linking a workflow to global safety policies it inherits."""
    __tablename__ = "workflow_safety_inheritance"
    __table_args__ = (
        ForeignKeyConstraint(
            ["workflow_id", "zone_id"],
            ["aquaops.workflow_settings.workflow_id", "aquaops.workflow_settings.zone_id"],
            ondelete="CASCADE",
        ),
        {"schema": "aquaops"},
    )

    workflow_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    zone_id:     Mapped[str] = mapped_column(String(100), primary_key=True)
    policy_id:   Mapped[str] = mapped_column(String(100), primary_key=True)

    workflow: Mapped["WorkflowSettings"] = relationship(back_populates="safety_policies")