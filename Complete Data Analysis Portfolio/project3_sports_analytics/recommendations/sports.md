# Sports recommendations

## Finding

The non-copy NBA Elo archive contains 63,157 team-games (1947–2015); on the final three seasons, source forecast accuracy was 66.4% with Brier score 0.208.

## Action

Use the source probabilities as a historical calibration reference only. Before applying forecasting to current games, retrain or validate on current data and a strictly chronological holdout, then compare calibration and Brier score with a simple baseline.

## Limitation

The Elo file ends in 2015; RAPTOR's methods differ by era.

## Monitor

Prospective Brier score, calibration curve, and accuracy by season after comparison to a base-rate forecast.
