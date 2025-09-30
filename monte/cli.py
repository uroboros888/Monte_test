"""Command line interface for the Monte prototype."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .pipeline.orchestrator import run_from_file


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Monte DSL scenarios")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Execute a scenario from a DSL file")
    run_parser.add_argument("dsl_path", type=Path, help="Path to the DSL file")
    run_parser.add_argument(
        "--json-output",
        type=Path,
        dest="json_output",
        default=None,
        help="Optional path where the generated JSON configuration will be written",
    )
    run_parser.add_argument(
        "--results-output",
        type=Path,
        dest="results_output",
        default=None,
        help="Optional path where aggregated metrics will be stored as JSON",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command != "run":
        parser.print_help()
        return 1

    artifacts = run_from_file(args.dsl_path, json_output=args.json_output)
    metrics_json: dict[str, Any] = {
        "metrics": artifacts.execution.metrics,
        "raw_results": artifacts.execution.raw_results,
    }

    if args.results_output is not None:
        args.results_output.parent.mkdir(parents=True, exist_ok=True)
        args.results_output.write_text(json.dumps(metrics_json, indent=2), encoding="utf-8")
    else:
        print(json.dumps(metrics_json, indent=2))

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
