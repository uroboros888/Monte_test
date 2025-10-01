from monte.cli import main


def test_results_output_directory_created(tmp_path):
    dsl_path = tmp_path / "scenario.dsl"
    dsl_path.write_text(
        'scenario "cli" {\n'
        '  dataset "local" from "data/market.csv"\n'
        '  parameter horizon = 2\n'
        '  task simulate {\n'
        '    engine = "monte"\n'
        '  }\n'
        '  metric "mean" using aggregator.mean\n'
        '}\n'
    )

    results_output = tmp_path / "nested" / "output.json"

    exit_code = main(["run", str(dsl_path), "--results-output", str(results_output)])

    assert exit_code == 0
    assert results_output.exists()
    assert results_output.read_text(encoding="utf-8").strip().startswith("{")
