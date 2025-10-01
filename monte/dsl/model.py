"""Domain models for the Monte simulation DSL."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Dataset:
    """Represents a dataset declaration within a scenario."""

    name: str
    path: str


@dataclass
class Task:
    """Represents an execution task defined in the DSL."""

    name: str
    engine: str
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Metric:
    """Represents an aggregated metric request."""

    name: str
    aggregator: str


@dataclass
class Scenario:
    """The root object that groups datasets, tasks and metrics."""

    name: str
    datasets: List[Dataset] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    tasks: List[Task] = field(default_factory=list)
    metrics: List[Metric] = field(default_factory=list)


__all__ = ["Dataset", "Task", "Metric", "Scenario"]
