"""Non-clinical encounter analysis for the UCI diabetes hospital source."""

from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.domains.common import PALETTE, add_metric, apply_style, chart, finish_domain, save_chart, write_processed_table, write_table
from src.data_io import load_raw


DOMAIN = "healthcare"
DATASET_IDS = ["healthcare_diabetes_130"]
SOURCE = "UCI Diabetes 130-US Hospitals, 1999–2008"
LIMITATIONS = [
    "Rows are hospital encounters, not unique people; patients can contribute multiple encounters.",
    "The source is observational, historical, and limited to 130 US hospitals; differences are not causal effects or clinical guidance.",
    "A 30-day readmission label is analyzed descriptively; discharge destinations, death, and transfer pathways can affect eligibility.",
    "Patient and encounter identifiers are removed from all exported analysis tables and charts.",
    "Age is supplied in grouped bands and missing or unknown race/lab values are retained as explicit unknown categories where shown.",
]


def _cluster_bootstrap_rate(frame: pd.DataFrame, resamples: int = 1000, seed: int = 42) -> tuple[float, float]:
    grouped = frame.groupby("patient_nbr", sort=False)["readmit_30d"].agg(["sum", "count"])
    sums, counts = grouped["sum"].to_numpy(), grouped["count"].to_numpy()
    rng = np.random.default_rng(seed)
    rates = np.empty(resamples)
    for i in range(resamples):
        selected = rng.integers(0, len(grouped), size=len(grouped))
        rates[i] = sums[selected].sum() / counts[selected].sum()
    return tuple(float(v) for v in np.quantile(rates, [.025, .975]))


def build() -> dict[str, object]:
    apply_style()
    raw = load_raw(DOMAIN, "diabetic_data.csv", low_memory=False)
    data = raw.copy()
    data.replace("?", pd.NA, inplace=True)
    for col in ("encounter_id", "patient_nbr", "admission_type_id", "discharge_disposition_id", "admission_source_id"):
        data[col] = pd.to_numeric(data[col], errors="coerce")
    for col in ("time_in_hospital", "num_lab_procedures", "num_procedures", "num_medications", "number_diagnoses", "number_inpatient"):
        data[col] = pd.to_numeric(data[col], errors="coerce")
    data["readmit_30d"] = data["readmitted"].eq("<30").astype("int8")
    # Exclude documented in-hospital deaths from the discharge readmission denominator.
    eligible = data.loc[data["discharge_disposition_id"].ne(11)].copy()
    eligible["age"] = eligible["age"].fillna("Unknown")
    age_order = ["[0-10)","[10-20)","[20-30)","[30-40)","[40-50)","[50-60)","[60-70)","[70-80)","[80-90)","[90-100)","Unknown"]
    eligible["age"] = pd.Categorical(eligible["age"], categories=age_order, ordered=True)
    eligible["a1c_status"] = eligible["A1Cresult"].fillna("Not recorded")
    eligible["med_change"] = eligible["change"].map({"Ch": "Changed", "No": "No change"}).fillna("Unknown")
    overall_rate = float(eligible["readmit_30d"].mean())
    ci = _cluster_bootstrap_rate(eligible)
    age_rates = eligible.groupby("age", observed=False, as_index=False).agg(encounters=("readmit_30d","size"), readmit_30d_rate=("readmit_30d","mean"))
    age_rates = age_rates.loc[age_rates["encounters"].gt(0)]
    a1c = eligible.groupby("a1c_status", as_index=False).agg(encounters=("readmit_30d","size"), readmit_30d_rate=("readmit_30d","mean"))
    med = eligible.groupby("med_change", as_index=False).agg(encounters=("readmit_30d","size"), readmit_30d_rate=("readmit_30d","mean"))
    inpatient = eligible.groupby("number_inpatient", as_index=False).agg(encounters=("readmit_30d","size"), readmit_30d_rate=("readmit_30d","mean"))
    inpatient = inpatient.loc[inpatient["number_inpatient"].le(10)]
    summary = eligible.groupby("age", observed=False, as_index=False).agg(median_stay_days=("time_in_hospital","median"), encounters=("encounter_id","size"))
    summary = summary.loc[summary["encounters"].gt(0)]
    n_patients = int(eligible["patient_nbr"].nunique())
    n_encounters = int(len(eligible))
    repeated_share = float(eligible["patient_nbr"].duplicated(keep=False).mean())
    stay_median = float(eligible["time_in_hospital"].median())
    a1c_recorded_share = float(eligible["A1Cresult"].notna().mean())

    export_cols = ["race","gender","age","time_in_hospital","num_lab_procedures","num_procedures","num_medications","number_inpatient","number_diagnoses","A1Cresult","readmitted","readmit_30d"]
    write_processed_table(eligible[export_cols], DOMAIN, "eligible_encounters_deidentified.csv")
    write_table(age_rates, DOMAIN, "readmission_by_age.csv")
    write_table(a1c, DOMAIN, "readmission_by_a1c_status.csv")
    write_table(med, DOMAIN, "readmission_by_medication_change.csv")
    write_table(inpatient, DOMAIN, "readmission_by_prior_inpatient_visits.csv")
    write_table(summary, DOMAIN, "stay_by_age.csv")

    rows=[]
    fig, ax=plt.subplots(figsize=(9,5)); ax.bar(age_rates["age"].astype(str),age_rates["readmit_30d_rate"]*100,color=PALETTE[0]); ax.set(title="Readmission within 30 days by age band",xlabel="Age band",ylabel="Encounters readmitted within 30 days (%)"); ax.tick_params(axis="x",rotation=35)
    save_chart(DOMAIN,fig,"readmission_by_age.png"); rows.append(chart(DOMAIN,"health_readmission_age","30-day readmission by age","How does the observed 30-day encounter readmission rate vary by age band?","Describes encounter-level outcome rates with encounter counts in the companion table.","bar","outputs/healthcare/tables/readmission_by_age.csv","readmission_by_age.png","1999–2008","percent of eligible encounters","Age-band bars show encounter-level 30-day readmission percent; grouped ages are source-defined."))

    fig, ax=plt.subplots(figsize=(8,4.8)); stay=eligible["time_in_hospital"].dropna(); ax.hist(stay,bins=np.arange(0.5,15.5,1),color=PALETTE[1]); ax.set(title="Hospital stay length by encounter",xlabel="Days in hospital",ylabel="Encounters")
    save_chart(DOMAIN,fig,"length_of_stay.png"); rows.append(chart(DOMAIN,"health_length_of_stay","Length of stay","What is the distribution of recorded hospital stay length?","Shows encounter counts by recorded length of stay.","histogram","datasets/raw/healthcare/diabetic_data.csv","length_of_stay.png","1999–2008","days","Histogram counts encounters by days in hospital."))

    fig, ax=plt.subplots(figsize=(8,4.8)); p=a1c.sort_values("readmit_30d_rate"); ax.barh(p["a1c_status"],p["readmit_30d_rate"]*100,color=PALETTE[2]); ax.set(title="Readmission by recorded A1C test result",xlabel="Encounters readmitted within 30 days (%)",ylabel="A1C result / not recorded")
    save_chart(DOMAIN,fig,"readmission_by_a1c.png"); rows.append(chart(DOMAIN,"health_readmission_a1c","Readmission by A1C recording","How do observed readmission rates differ by A1C result recording category?","Compares groups while preserving 'Not recorded' as a separate category.","horizontal_bar","outputs/healthcare/tables/readmission_by_a1c_status.csv","readmission_by_a1c.png","1999–2008","percent of encounters","Horizontal bars compare A1C categories; not recorded is shown explicitly."))

    fig, ax=plt.subplots(figsize=(8,4.8)); p=med.sort_values("readmit_30d_rate"); ax.bar(p["med_change"],p["readmit_30d_rate"]*100,color=PALETTE[3]); ax.set(title="Readmission by medication-change status",xlabel="Medication change recorded during encounter",ylabel="Encounters readmitted within 30 days (%)")
    save_chart(DOMAIN,fig,"readmission_by_med_change.png"); rows.append(chart(DOMAIN,"health_readmission_med_change","Readmission by medication change","How do observed readmission rates compare by medication-change status?","Displays descriptive outcome rates across the source change flag.","bar","outputs/healthcare/tables/readmission_by_medication_change.csv","readmission_by_med_change.png","1999–2008","percent of encounters","Bars compare medication change categories; differences are not causal."))

    fig, ax=plt.subplots(figsize=(8,4.8)); ax.plot(inpatient["number_inpatient"],inpatient["readmit_30d_rate"]*100,marker="o",color=PALETTE[4]); ax.set(title="Readmission by prior inpatient encounter count",xlabel="Prior inpatient encounters recorded",ylabel="Encounters readmitted within 30 days (%)")
    save_chart(DOMAIN,fig,"readmission_by_prior_visits.png"); rows.append(chart(DOMAIN,"health_readmission_prior_visits","Readmission and prior inpatient visits","How does observed readmission vary with recorded prior inpatient visits?","Shows the relationship between utilization count and outcome; counts above ten are omitted from this chart only.","line","outputs/healthcare/tables/readmission_by_prior_inpatient_visits.csv","readmission_by_prior_visits.png","1999–2008","percent of encounters","Line shows outcome rates by count with the count value on the horizontal axis."))

    metrics=[
        add_metric("eligible_encounters",n_encounters,"encounters","Encounters excluding discharge disposition ID 11 (expired)."),
        add_metric("unique_patients",n_patients,"patients","Distinct patient identifiers among eligible encounters; IDs are not exported."),
        add_metric("readmission_within_30d_rate",round(overall_rate,4),"proportion","Eligible encounters labeled '<30' divided by eligible encounters.","Eligible encounters excluding disposition 11"),
        add_metric("readmission_30d_ci95_lower",round(ci[0],4),"proportion","Lower cluster-bootstrap percentile bound, resampling patient clusters 1,000 times with seed 42.","Eligible encounters, patient-cluster resampling"),
        add_metric("readmission_30d_ci95_upper",round(ci[1],4),"proportion","Upper cluster-bootstrap percentile bound, resampling patient clusters 1,000 times with seed 42.","Eligible encounters, patient-cluster resampling"),
        add_metric("median_stay_days",stay_median,"days","Median recorded time_in_hospital among eligible encounters.","Eligible encounters"),
        add_metric("a1c_recorded_share",round(a1c_recorded_share,4),"proportion","Share of eligible encounters with any A1Cresult category recorded.","Eligible encounters"),
    ]
    high=age_rates.sort_values("readmit_30d_rate",ascending=False).iloc[0]
    headline=f"Among {n_encounters:,} eligible encounters from {n_patients:,} patients, {overall_rate:.1%} were labeled readmitted within 30 days; median stay was {stay_median:.0f} days."
    recommendation="Use the descriptive groups to prioritize a data-quality and care-transition review, then validate current local data and confounders before designing interventions; these historical associations do not establish causes."
    report=f"""# Healthcare analysis — source narrative

## Executive summary

{headline}

## Question and source

This analysis describes encounters in the UCI Diabetes 130-US Hospitals dataset (1999–2008). The unit is an encounter; repeat encounters for the same patient are retained. Readmission within 30 days is defined by the source label `<30`. Encounters with discharge disposition 11 (expired) are excluded from the eligible denominator.

## Methods and statistical interpretation

The 95% interval for the overall rate is a percentile bootstrap resampling patient clusters (1,000 resamples, seed 42), preserving multiple encounters within selected patients. Group rates are descriptive. No causal or clinical claims are made. The highest observed age-band rate is {float(high['readmit_30d_rate']):.1%} for {str(high['age'])} (n={int(high['encounters']):,}); small group counts should be considered.

## Recommendation

{recommendation}

## Limitations

"""+"\n".join(f"- {x}" for x in LIMITATIONS)+"\n\n## Figures\n\nSee `visualizations/healthcare/` and `visualizations/healthcare/manifest.csv`.\n"
    from pathlib import Path
    (Path("reports/source")).mkdir(parents=True,exist_ok=True); Path("reports/source/healthcare.md").write_text(report,encoding="utf-8")
    Path("recommendations").mkdir(exist_ok=True); Path("recommendations/healthcare.md").write_text(f"# Healthcare recommendations\n\n## Finding\n\n{headline}\n\n## Action\n\n{recommendation}\n\n## Limitation\n\nThe 1999–2008 hospital sample is historical and observational.\n\n## Monitor\n\nCurrent eligible encounter readmission rate, patient-cluster confidence interval, and discharge follow-up completion in a locally governed dataset.\n",encoding="utf-8")
    result=finish_domain(DOMAIN,DATASET_IDS,{"start":"1999","end":"2008","unit_of_analysis":"eligible hospital encounter","eligible_population":"discharge disposition ID != 11"},metrics,LIMITATIONS,rows)
    result.update({"headline":headline,"recommendation":recommendation})
    return result
