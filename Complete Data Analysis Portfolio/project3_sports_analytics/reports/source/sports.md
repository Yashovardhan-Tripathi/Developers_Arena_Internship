# Sports analysis — source narrative

## Executive summary

The non-copy NBA Elo archive contains 63,157 team-games (1947–2015); on the final three seasons, source forecast accuracy was 66.4% with Brier score 0.208.

## Questions and sources

The team analysis uses one non-copy team perspective per NBA game from the FiveThirtyEight Elo archive (1947–2015). The player analysis uses the historical RAPTOR player-season file (1977–2022). The sources have different grains and are reported separately.

## Statistical and predictive assessment

The source's pregame Elo probability is evaluated on the final three archive seasons (2013–2015), chronologically held out: accuracy 66.4%, Brier score 0.2082, mean predicted win chance 0.622, observed win fraction 0.590. This is a historical assessment of the published forecast, not a newly trained predictive model. RAPTOR rankings require caution because methodology varies across eras.

## Recommendation

Use the source probabilities as a historical calibration reference only. Before applying forecasting to current games, retrain or validate on current data and a strictly chronological holdout, then compare calibration and Brier score with a simple baseline.

## Limitations

- The NBA Elo file ends in 2015; it is a historical archive, not current NBA coverage.
- Only one non-copy team-game perspective is used per game; win rates use team-game rows and games are not independent for inference.
- The Elo probability is the source's pregame estimate; forecast evaluation is descriptive and uses the final three seasons as a chronological holdout.
- RAPTOR player ratings are publisher-defined estimates whose methodology varies across historical eras; cross-era rankings should be treated cautiously.
- Team and player analyses use different source grains and cannot be combined into one performance score.

## Figures

See `visualizations/sports/` and `visualizations/sports/manifest.csv`.
