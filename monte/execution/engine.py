"""Minimal execution engine for Monte scenarios."""
from __future__ import annotations

import math
import random
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List

from ..dsl.model import Metric, Scenario, Task


@dataclass
class ExecutionResult:
    """Represents the output of a pipeline run."""

    raw_results: Dict[str, List[float]]
    metrics: Dict[str, float]


class ExecutionEngine:
    """Evaluate tasks defined in a :class:`Scenario`.

    The implementation is intentionally lightweight: it focuses on determinism
    and reproducibility so that early design experiments can be automated.
    """

    def __init__(self, *, base_seed: int | None = None) -> None:
        self._base_seed = base_seed

    def run(self, scenario: Scenario) -> ExecutionResult:
        raw_results: Dict[str, List[float]] = {}

        for index, task in enumerate(scenario.tasks):
            seed = self._calculate_seed(scenario, task, index)
            samples = self._execute_task(task, seed=seed, horizon=scenario.parameters.get("horizon", 1))
            raw_results[task.name] = samples

        metrics = ResultAggregator().aggregate(scenario.metrics, raw_results)
        return ExecutionResult(raw_results=raw_results, metrics=metrics)

    def _calculate_seed(self, scenario: Scenario, task: Task, index: int) -> int:
        seed_components: List[int] = [index]
        if self._base_seed is not None:
            seed_components.append(self._base_seed)
        if "seed" in scenario.parameters:
            seed_components.append(int(scenario.parameters["seed"]))
        if "seed" in task.options:
            seed_components.append(int(task.options["seed"]))
        seed = 0
        for component in seed_components:
            seed = (seed * 31 + component) % (2**32)
        return seed

    def _execute_task(self, task: Task, *, seed: int, horizon: int) -> List[float]:
        if task.engine != "monte":
            raise ValueError(f"Unsupported engine '{task.engine}'")

        rng = random.Random(seed)
        mean = float(task.options.get("mean", 0.0))
        stddev = float(task.options.get("stddev", 1.0))
        samples = [rng.gauss(mean, stddev) for _ in range(max(1, int(horizon)))]
        return samples


class ResultAggregator:
    """Aggregate metric declarations against raw task outputs."""

    def aggregate(self, metrics: Iterable[Metric], raw_results: Dict[str, List[float]]) -> Dict[str, float]:
        aggregated: Dict[str, float] = {}
        for metric in metrics:
            aggregated[metric.name] = self._evaluate(metric, raw_results)
        return aggregated

    def _evaluate(self, metric: Metric, raw_results: Dict[str, List[float]]) -> float:
        if metric.aggregator.startswith("aggregator.percentile"):
            percentile = self._parse_percentile(metric.aggregator)
            samples = self._flatten(raw_results.values())
            if not samples:
                raise ValueError("Cannot compute percentile without samples")
            samples = sorted(samples)
            index = (len(samples) - 1) * percentile
            lower = math.floor(index)
            upper = math.ceil(index)
            if lower == upper:
                return samples[int(index)]
            return samples[lower] * (upper - index) + samples[upper] * (index - lower)
        if metric.aggregator == "aggregator.mean":
            samples = self._flatten(raw_results.values())
            if not samples:
                raise ValueError("Cannot compute mean without samples")
            return sum(samples) / len(samples)
        raise ValueError(f"Unsupported aggregator '{metric.aggregator}'")

    @staticmethod
    def _flatten(sample_groups: Iterable[List[float]]) -> List[float]:
        flattened: List[float] = []
        for samples in sample_groups:
            flattened.extend(samples)
        return flattened

    @staticmethod
    def _parse_percentile(expression: str) -> float:
        match = re.match(r"aggregator\.percentile\((?P<value>[0-1]?\.?\d+)\)", expression)
        if not match:
            raise ValueError(f"Invalid percentile aggregator '{expression}'")
        percentile = float(match.group("value"))
        if not 0 <= percentile <= 1:
            raise ValueError("Percentile must be within [0, 1]")
        return percentile


__all__ = ["ExecutionEngine", "ExecutionResult", "ResultAggregator"]
