"""High level orchestration utilities."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..dsl.parser import parse_scenario
from ..execution.engine import ExecutionEngine, ExecutionResult
from ..generator.json_generator import scenario_to_json, write_json_config


@dataclass
class PipelineArtifacts:
    """Group the different outputs produced during a run."""

    scenario_json: dict
    execution: ExecutionResult


class PipelineOrchestrator:
    """Glue component combining parsing, generation and execution."""

    def __init__(self, *, engine: Optional[ExecutionEngine] = None) -> None:
        self._engine = engine or ExecutionEngine()

    def run(self, dsl_source: str, *, json_output: Path | None = None) -> PipelineArtifacts:
        scenario = parse_scenario(dsl_source)
        if json_output is not None:
            config = write_json_config(scenario, json_output)
        else:
            config = scenario_to_json(scenario)
        execution = self._engine.run(scenario)
        return PipelineArtifacts(scenario_json=config, execution=execution)


def run_from_file(path: Path, *, json_output: Path | None = None) -> PipelineArtifacts:
    try:
        source = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:  # pragma: no cover - simple passthrough
        raise FileNotFoundError(f"DSL file '{path}' not found") from exc
    orchestrator = PipelineOrchestrator()
    return orchestrator.run(source, json_output=json_output)


__all__ = ["PipelineOrchestrator", "PipelineArtifacts", "run_from_file"]
