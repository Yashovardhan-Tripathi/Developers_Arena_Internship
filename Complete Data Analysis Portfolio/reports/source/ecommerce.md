# E-commerce session analysis — source narrative

## Executive summary

1,908 of 12,330 sampled sessions resulted in a purchase (15.5%; 95% Wilson interval 14.8%–16.1%).

## Question and source

Which session groups and browsing behaviors are associated with purchase sessions? The UCI Online Shoppers dataset contains 12,330 sessions in a one-year sample; each user appears once in that sample. This is session conversion analysis, not repeat-purchase or basket analysis.

## Methods and statistics

The conversion proportion uses purchase sessions divided by all sessions. Its 95% Wilson interval is 14.8%–16.1%. Visitor type and purchase outcome show a Pearson chi-square association test (p=4.27e-30, df=2); the test is associational and the sample may not represent present-day traffic. PageValues is excluded from prediction because it can encode post-engagement information.

## Recommendation

Prioritize a controlled review of the observed visitor-type and engagement differences, and validate them on current session data before changing acquisition or checkout flows. Do not use PageValues in a pre-session purchase prediction because it may include information available only after navigation.

## Limitations

- Each row is a session in a one-year sample; the source does not support repeat-purchase or basket-level analysis.
- PageValues is derived from pages visited before purchase and may encode post-engagement information; it is excluded from predictive features.
- Sessions are observational; group differences do not show that a browsing behavior causes conversion.
- The source is a historical sample and includes grouped traffic/device fields whose coding may not reflect current systems.

## Figures

See `visualizations/ecommerce/` and `visualizations/ecommerce/manifest.csv`.
