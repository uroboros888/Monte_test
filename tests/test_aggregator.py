from monte.dsl.model import Metric, Scenario, Task
from monte.execution.engine import ExecutionEngine


def test_percentile_aggregator():
    scenario = Scenario(
        name="baseline",
        tasks=[Task(name="simulate", engine="monte", options={"seed": 1})],
        metrics=[Metric(name="p90", aggregator="aggregator.percentile(0.9)")],
        parameters={"horizon": 5},
    )

    engine = ExecutionEngine(base_seed=123)
    result = engine.run(scenario)

    assert "p90" in result.metrics
    assert isinstance(result.metrics["p90"], float)
    assert len(result.raw_results["simulate"]) == 5
