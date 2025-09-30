scenario "baseline" {
  dataset "market" from "data/market.csv"
  dataset "demand" from "data/demand.csv"

  parameter horizon = 30
  parameter seed = 42

  task simulate {
    engine = "monte"
    seed = 11
    mean = 1.2
    stddev = 0.4
  }

  metric "roi_p90" using aggregator.percentile(0.9)
  metric "roi_mean" using aggregator.mean
}
