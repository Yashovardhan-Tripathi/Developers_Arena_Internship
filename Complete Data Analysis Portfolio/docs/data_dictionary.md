# Data dictionary and preparation contracts

The source snapshots were retrieved and profiled on 2026-11-04. Raw files remain unchanged under `datasets/raw/`; hashes and licensing are in [`datasets/catalog.csv`](../datasets/catalog.csv). These profiles describe inputs only; analysis-specific exclusions and transformations will be recorded in each domain project.

## Required snapshot profile

`python scripts/prepare_data.py --domain <domain> --check-only` reports raw-file SHA-256, bytes, row count, column names, full blank/null counts, and literal `?` counts. No rows are modified. The following are the observed profiles.

| Domain/source | Grain and coverage | Observed fields | Missingness and cautions |
| --- | --- | --- | --- |
| Sales: Online Retail II (1,067,371 rows) | One invoice line; UCI reports 2009-12-01 to 2011-12-09, UK retailer; `Price` is GBP | `Invoice`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `Price`, `Customer ID`, `Country` | Blank `Description`: 4,382; blank `Customer ID`: 243,007; literal `?` in `Description`: 92. Invoice IDs beginning with C indicate cancellations per UCI. Do not treat gross line totals as profit. |
| Healthcare: Diabetes 130-US Hospitals (101,766 rows) | One hospital encounter, 130 US hospitals, 1999–2008; repeated encounters per `patient_nbr` | 50 columns: `encounter_id`, `patient_nbr`, race/gender/age/weight, admission/discharge/source IDs, utilization and diagnoses, lab indicators, medication indicators, `readmitted` | Blank `max_glu_serum`: 96,420; blank `A1Cresult`: 84,748. Literal `?`: race 2,273; weight 98,569; payer_code 40,256; medical_specialty 49,949; diag_1 21; diag_2 358; diag_3 1,423. The raw IDs must not appear in public output. `IDS_mapping.csv` has 67 rows, 2 blank IDs and 5 blank descriptions; verify mapping sections before joining. |
| Sports: NBA Elo (126,314 rows) | One team-game row; two team rows can describe one game. File seasons run through 2015. | `gameorder`, `game_id`, `lg_id`, `_iscopy`, `year_id`, `date_game`, `seasongame`, `is_playoffs`, `team_id`, `fran_id`, `pts`, `elo_i`, `elo_n`, `win_equiv`, `opp_id`, `opp_fran`, `opp_pts`, `opp_elo_i`, `opp_elo_n`, `game_location`, `game_result`, `forecast`, `notes` | `notes` blank in 120,890 rows. `forecast` is an Elo chance, not observed outcome. Game information attribution in source README: Basketball-Reference. |
| Sports: historical RAPTOR player file (19,159 rows) | Player-season rating records; seasons 1977–2022; 3,591 player IDs | `player_name`, `player_id`, `season`, `poss`, `mp`, `raptor_offense`, `raptor_defense`, `raptor_total`, `war_total`, `war_reg_season`, `war_playoffs`, `predator_offense`, `predator_defense`, `predator_total`, `pace_impact` | One blank `pace_impact`. RAPTOR methodology varies by era, as documented in the source README; label ratings as publisher-defined estimates. |
| Finance: split-adjusted NYSE snapshot (851,264 rows) | One security-date row; 501 symbols; 1,762 unique dates from 2010-01-04 to 2016-12-30 | `date`, `symbol`, `open`, `close`, `low`, `high`, `volume` | No pandas blank values or `?` markers. 467 symbols have all 1,762 dates; 34 have incomplete coverage. Prices are split-adjusted, with dividend adjustment not stated. Dataset selection/survivorship bias and mirror provenance must be disclosed. |
| E-commerce: Online Shoppers (12,330 rows) | One session; source states each user appears once within its one-year sample | `Administrative`, `Administrative_Duration`, `Informational`, `Informational_Duration`, `ProductRelated`, `ProductRelated_Duration`, `BounceRates`, `ExitRates`, `PageValues`, `SpecialDay`, `Month`, `OperatingSystems`, `Browser`, `Region`, `TrafficType`, `VisitorType`, `Weekend`, `Revenue` | No blank values or `?` markers in the downloaded file. `PageValues` is tied to pages visited before purchase, so check temporal availability before using it as a predictor. It cannot support repeat-purchase or basket metrics. |

The full profile command does not calculate duplicate business keys, invalid domain constraints, or clinical privacy transformations. Those checks belong to the domain preparation steps, where key definitions and exclusions can be defended.

## Shared metric record

Each exported metric must include a stable metric ID, domain, value, unit, denominator/grain where applicable, data version/hash, coverage window, filters, and definition. Missing or unsupported metrics are represented as unavailable with a reason, never as zero.

## Chart inventory record

Each chart entry must contain a unique chart ID, domain, title/question, purpose, source output, artifact path, coverage/filters, units, and accessibility summary. Re-exporting a chart is not a distinct visualization.

## Domain output boundary

Domain outputs live in `outputs/<domain>/`; raw and processed data remain separate. The dashboard consumes validated derived output tables and metadata only. Shared schema changes require coordination through the integrator described in the Blueprint.
