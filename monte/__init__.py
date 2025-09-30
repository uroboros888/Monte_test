"""Monte simulation prototype package."""

from __future__ import annotations

import sys


if sys.version_info < (3, 11):  # pragma: no cover - exercised via dedicated test
    raise RuntimeError(
        "Monte requires Python 3.11 or newer. Please upgrade your interpreter before use."
    )


from .dsl.parser import parse_scenario
from .execution.engine import ExecutionEngine
from .pipeline.orchestrator import PipelineOrchestrator, run_from_file

__all__ = ["parse_scenario", "ExecutionEngine", "PipelineOrchestrator", "run_from_file"]
