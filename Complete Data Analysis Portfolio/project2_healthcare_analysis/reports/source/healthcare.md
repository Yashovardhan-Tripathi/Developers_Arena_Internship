# Healthcare analysis — source narrative

## Executive summary

Among 100,124 eligible encounters from 70,446 patients, 11.3% were labeled readmitted within 30 days; median stay was 4 days.

## Question and source

This analysis describes encounters in the UCI Diabetes 130-US Hospitals dataset (1999–2008). The unit is an encounter; repeat encounters for the same patient are retained. Readmission within 30 days is defined by the source label `<30`. Encounters with discharge disposition 11 (expired) are excluded from the eligible denominator.

## Methods and statistical interpretation

The 95% interval for the overall rate is a percentile bootstrap resampling patient clusters (1,000 resamples, seed 42), preserving multiple encounters within selected patients. Group rates are descriptive. No causal or clinical claims are made. The highest observed age-band rate is 14.3% for [20-30) (n=1,650); small group counts should be considered.

## Recommendation

Use the descriptive groups to prioritize a data-quality and care-transition review, then validate current local data and confounders before designing interventions; these historical associations do not establish causes.

## Limitations

- Rows are hospital encounters, not unique people; patients can contribute multiple encounters.
- The source is observational, historical, and limited to 130 US hospitals; differences are not causal effects or clinical guidance.
- A 30-day readmission label is analyzed descriptively; discharge destinations, death, and transfer pathways can affect eligibility.
- Patient and encounter identifiers are removed from all exported analysis tables and charts.
- Age is supplied in grouped bands and missing or unknown race/lab values are retained as explicit unknown categories where shown.

## Figures

See `visualizations/healthcare/` and `visualizations/healthcare/manifest.csv`.
