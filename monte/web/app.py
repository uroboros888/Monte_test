"""Flask application exposing a browser UI for Monte simulations."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any, Dict

from flask import Flask, Response, jsonify, render_template, request

from ..pipeline.orchestrator import PipelineArtifacts, PipelineOrchestrator

DEFAULT_DSL = """scenario \"baseline\" {
  dataset \"market\" from \"data/market.csv\"
  dataset \"demand\" from \"data/demand.csv\"

  parameter horizon = 30
  parameter seed = 42

  task simulate {
    engine = \"monte\"
    seed = 11
    mean = 1.2
    stddev = 0.4
  }

  metric \"roi_p90\" using aggregator.percentile(0.9)
  metric \"roi_mean\" using aggregator.mean
}
"""
def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")
    app.config["JSON_SORT_KEYS"] = False
    orchestrator = PipelineOrchestrator()
    current_year = datetime.now(UTC).year

    @app.get("/")
    def index() -> str:
        return render_template(
            "index.html",
            dsl_input=DEFAULT_DSL,
            result=None,
            error=None,
            current_year=current_year,
        )

    @app.post("/")
    def run_form() -> tuple[str, int] | str:
        dsl_input = request.form.get("dsl", "")
        if not dsl_input.strip():
            return (
                render_template(
                    "index.html",
                    dsl_input=dsl_input,
                    result=None,
                    error="Введите описание сценария в формате Monte DSL.",
                    current_year=current_year,
                ),
                400,
            )
        try:
            artifacts = orchestrator.run(dsl_input)
        except Exception as exc:  # noqa: BLE001 - surface pipeline errors to user
            return (
                render_template(
                    "index.html",
                    dsl_input=dsl_input,
                    result=None,
                    error=str(exc),
                    current_year=current_year,
                ),
                400,
            )
        result = _serialize_artifacts(artifacts)
        return render_template(
            "index.html",
            dsl_input=dsl_input,
            result=result,
            error=None,
            current_year=current_year,
        )

    @app.post("/api/run")
    def run_api() -> tuple[Response, int]:
        payload = request.get_json(silent=True)
        if not payload or "dsl" not in payload:
            return jsonify({"error": "Missing 'dsl' field in payload"}), 400
        dsl_input = str(payload["dsl"]).strip()
        if not dsl_input:
            return jsonify({"error": "Scenario DSL cannot be empty"}), 400
        try:
            artifacts = orchestrator.run(dsl_input)
        except Exception as exc:  # noqa: BLE001 - expose pipeline error details in response
            return jsonify({"error": str(exc)}), 400
        return jsonify(_serialize_artifacts(artifacts))

    @app.get("/api/example")
    def api_example() -> Dict[str, str]:
        return {"dsl": DEFAULT_DSL}

    return app


def _serialize_artifacts(artifacts: PipelineArtifacts) -> Dict[str, Any]:
    execution = artifacts.execution
    return {
        "metrics": execution.metrics,
        "raw_results": execution.raw_results,
        "scenario": artifacts.scenario_json,
        "scenario_json_pretty": json.dumps(artifacts.scenario_json, ensure_ascii=False, indent=2),
    }


def main() -> None:  # pragma: no cover - console entry point
    create_app().run(debug=False, host="0.0.0.0")


if __name__ == "__main__":  # pragma: no cover - manual execution helper
    main()
