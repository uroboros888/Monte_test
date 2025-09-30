from monte.dsl.parser import parse_scenario


def test_parse_baseline(tmp_path):
    source = (
        'scenario "baseline" {\n'
        '  dataset "market" from "data/market.csv"\n'
        '  parameter horizon = 10\n'
        '  task simulate {\n'
        '    engine = "monte"\n'
        '  }\n'
        '  metric "roi" using aggregator.mean\n'
        '}\n'
    )

    scenario = parse_scenario(source)

    assert scenario.name == "baseline"
    assert scenario.datasets[0].name == "market"
    assert scenario.parameters["horizon"] == 10
    assert scenario.tasks[0].engine == "monte"
    assert scenario.metrics[0].aggregator == "aggregator.mean"
