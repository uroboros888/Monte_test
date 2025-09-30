"""Utilities to convert DSL objects into JSON compatible structures."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from ..dsl.model import Scenario


def scenario_to_json(scenario: Scenario) -> Dict[str, Any]:
    """Convert a :class:`Scenario` into a JSON serialisable dictionary."""

    metadata = {
        "schema_version": "0.1",
        "run_id": datetime.now(timezone.utc).isoformat(),
        "initiator": "local-dev",
    }

    inputs = {
        "datasets": [dataset.path for dataset in scenario.datasets],
        "parameters": scenario.parameters,
    }

    pipeline = [task.name for task in scenario.tasks]

    return {
        "metadata": metadata,
        "inputs": inputs,
        "pipeline": pipeline,
        "results": {},
        "artifacts": [],
        "extensions": {},
    }


def write_json_config(scenario: Scenario, destination: Path) -> Dict[str, Any]:
    """Generate and persist a JSON configuration file."""

    config = scenario_to_json(scenario)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return config


__all__ = ["scenario_to_json", "write_json_config"]
