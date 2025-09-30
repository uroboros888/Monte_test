from pathlib import Path

from monte.pipeline.orchestrator import run_from_file


def test_run_from_file(tmp_path):
    dsl_path = tmp_path / "scenario.dsl"
    dsl_path.write_text(
        """
        scenario "baseline" {
          dataset "market" from "data/market.csv"
          parameter horizon = 3
          task simulate {
            engine = "monte"
            seed = 99
          }
          metric "roi" using aggregator.mean
        }
        """,
        encoding="utf-8",
    )

    artifacts = run_from_file(dsl_path)

    assert artifacts.scenario_json["pipeline"] == ["simulate"]
    assert "roi" in artifacts.execution.metrics
    assert len(artifacts.execution.raw_results["simulate"]) == 3
