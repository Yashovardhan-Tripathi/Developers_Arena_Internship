"""NBA team-game and player-season analysis using FiveThirtyEight sources."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.data_io import load_raw
from src.domains.common import PALETTE, add_metric, apply_style, chart, finish_domain, save_chart, write_processed_table, write_table


DOMAIN="sports"
DATASET_IDS=["sports_nba_elo","sports_historical_raptor_player"]
LIMITATIONS=[
    "The NBA Elo file ends in 2015; it is a historical archive, not current NBA coverage.",
    "Only one non-copy team-game perspective is used per game; win rates use team-game rows and games are not independent for inference.",
    "The Elo probability is the source's pregame estimate; forecast evaluation is descriptive and uses the final three seasons as a chronological holdout.",
    "RAPTOR player ratings are publisher-defined estimates whose methodology varies across historical eras; cross-era rankings should be treated cautiously.",
    "Team and player analyses use different source grains and cannot be combined into one performance score.",
]


def build()->dict[str,object]:
    apply_style()
    games=load_raw(DOMAIN,"nbaallelo.csv",low_memory=False)
    games["year_id"]=pd.to_numeric(games["year_id"],errors="coerce")
    games["forecast"]=pd.to_numeric(games["forecast"],errors="coerce")
    games["pts"]=pd.to_numeric(games["pts"],errors="coerce");games["opp_pts"]=pd.to_numeric(games["opp_pts"],errors="coerce")
    copy=games["_iscopy"].astype(str).str.strip().str.lower().isin(["true","1","yes"])
    one=games.loc[~copy].dropna(subset=["year_id","forecast","game_result","team_id","fran_id"]).copy()
    one["win"]=one["game_result"].eq("W").astype("int8")
    one["margin"]=one["pts"]-one["opp_pts"]
    one["forecast_decile"]=pd.cut(one["forecast"],bins=np.linspace(0,1,11),include_lowest=True,duplicates="drop")
    team=one.groupby("fran_id",as_index=False).agg(games=("win","size"),wins=("win","sum"),win_rate=("win","mean"),mean_end_elo=("elo_n","mean"),mean_margin=("margin","mean"))
    team=team.loc[team["games"].ge(200)].sort_values("win_rate",ascending=False)
    season=one.groupby("year_id",as_index=False).agg(games=("win","size"),mean_margin=("margin","mean"),team_game_win_rate=("win","mean"))
    calibration=one.groupby("forecast_decile",observed=False,as_index=False).agg(games=("win","size"),mean_forecast=("forecast","mean"),observed_win_rate=("win","mean")).dropna()
    last_season=int(one["year_id"].max()); holdout=one.loc[one["year_id"].ge(last_season-2)]
    brier=float(np.mean((holdout["forecast"]-holdout["win"])**2))
    acc=float(((holdout["forecast"].ge(.5)).astype(int)==holdout["win"]).mean())
    z=1.959963984540054; accuracy_den=1+z*z/len(holdout); accuracy_center=(acc+z*z/(2*len(holdout)))/accuracy_den; accuracy_half=z*((acc*(1-acc)/len(holdout)+z*z/(4*len(holdout)**2))**.5)/accuracy_den
    rap=load_raw(DOMAIN,"historical_RAPTOR_by_player.csv",low_memory=False)
    for col in ["season","poss","mp","raptor_total","raptor_offense","raptor_defense","war_total"]:
        rap[col]=pd.to_numeric(rap[col],errors="coerce")
    qualified=rap.loc[rap["poss"].ge(1000)].copy()
    best_seasons=qualified.sort_values("war_total",ascending=False).head(15)
    career=qualified.groupby(["player_id","player_name"],as_index=False).agg(seasons=("season","nunique"),career_war=("war_total","sum"),mean_raptor=("raptor_total","mean"),total_possessions=("poss","sum")).sort_values("career_war",ascending=False).head(15)
    recent=rap.loc[rap["season"].eq(2022)].nlargest(15,"raptor_total")
    games_n=len(one);win_rate=float(one["win"].mean());forecast_mean=float(holdout["forecast"].mean());obs_holdout=float(holdout["win"].mean())
    start=int(one["year_id"].min());end=int(one["year_id"].max())

    # Public output tables contain franchise/player labels only, never source IDs.
    write_processed_table(one[["date_game","year_id","fran_id","opp_fran","pts","opp_pts","forecast","win","margin","is_playoffs"]],DOMAIN,"team_games.csv")
    write_processed_table(rap[["player_name","season","poss","mp","raptor_total","raptor_offense","raptor_defense","war_total"]],DOMAIN,"player_seasons.csv")
    write_table(team.head(20),DOMAIN,"team_records.csv");write_table(season,DOMAIN,"season_summary.csv");write_table(calibration,DOMAIN,"elo_calibration.csv");write_table(best_seasons,DOMAIN,"top_player_seasons.csv");write_table(career,DOMAIN,"career_war_leaders.csv");write_table(recent,DOMAIN,"raptor_2022_leaders.csv")
    rows=[]
    fig,ax=plt.subplots(figsize=(9,5.4));t=team.head(15).sort_values("win_rate");ax.barh(t["fran_id"],t["win_rate"]*100,color=PALETTE[0]);ax.set(title="Highest historical franchise win rates (minimum 200 games)",xlabel="Team-game win rate (%)",ylabel="Franchise")
    save_chart(DOMAIN,fig,"team_win_rates.png");rows.append(chart(DOMAIN,"sports_franchise_win_rates","Franchise win rates","Which franchises had the highest win rates in the covered archive?","Ranks franchises with at least 200 non-copy team-game records.","horizontal_bar","outputs/sports/tables/team_records.csv","team_win_rates.png",f"{start}–{end}","percent of team games","Horizontal bars compare franchise win percentages; the minimum game threshold is stated."))

    fig,ax=plt.subplots(figsize=(8,5));ax.plot(calibration["mean_forecast"],calibration["observed_win_rate"],marker="o",color=PALETTE[1]);ax.plot([0,1],[0,1],linestyle="--",color="#64748B",label="Perfect calibration");ax.set(title="Pregame Elo forecast calibration",xlabel="Mean predicted win probability",ylabel="Observed win fraction",xlim=(0,1),ylim=(0,1));ax.legend()
    save_chart(DOMAIN,fig,"elo_calibration.png");rows.append(chart(DOMAIN,"sports_elo_calibration","Elo probability calibration","Do historical Elo probabilities align with observed win fractions?","Groups source pregame forecasts into probability deciles and compares observed outcomes.","reliability_diagram","outputs/sports/tables/elo_calibration.csv","elo_calibration.png",f"holdout {last_season-2}–{last_season}","probability / fraction","Reliability plot compares observed win fraction to predicted probability with a diagonal reference."))

    fig,ax=plt.subplots(figsize=(9,4.8));ax.plot(season["year_id"],season["mean_margin"],marker="o",color=PALETTE[2]);ax.axhline(0,color="#64748B",lw=1);ax.set(title="Mean team-game scoring margin by season",xlabel="Season year",ylabel="Points scored minus opponent points")
    save_chart(DOMAIN,fig,"season_margin.png");rows.append(chart(DOMAIN,"sports_season_margin","Season scoring margin","How did average team-game scoring margin change by season?","Describes scoring balance across the historical archive.","line","outputs/sports/tables/season_summary.csv","season_margin.png",f"{start}–{end}","points per team game","Season line uses points minus opponent points; zero indicates even average margin."))

    fig,ax=plt.subplots(figsize=(10,5.5));p=best_seasons.sort_values("war_total");labels=p["player_name"].astype(str)+" ("+p["season"].astype(int).astype(str)+")";ax.barh(labels,p["war_total"],color=PALETTE[3]);ax.set(title="Highest single-season total WAR (minimum 1,000 possessions)",xlabel="Publisher-defined total WAR",ylabel="Player and season")
    save_chart(DOMAIN,fig,"top_player_seasons.png");rows.append(chart(DOMAIN,"sports_top_player_seasons","Top RAPTOR player seasons","Which qualified player-seasons have the highest source WAR totals?","Ranks seasons with at least 1,000 possessions using the source's total WAR estimate.","horizontal_bar","outputs/sports/tables/top_player_seasons.csv","top_player_seasons.png","1977–2022","publisher-defined WAR","Bars rank player-seasons and label the season; this source estimate varies by era."))

    fig,ax=plt.subplots(figsize=(9,5.2));recent=recent.sort_values("raptor_total");ax.barh(recent["player_name"],recent["raptor_total"],color=PALETTE[4]);ax.set(title="Top 2022 RAPTOR total ratings",xlabel="Publisher-defined RAPTOR total",ylabel="Player")
    save_chart(DOMAIN,fig,"raptor_2022.png");rows.append(chart(DOMAIN,"sports_raptor_2022","2022 RAPTOR leaders","Which players led the 2022 source season on RAPTOR total?","Ranks players in the last RAPTOR season available in the selected snapshot.","horizontal_bar","outputs/sports/tables/raptor_2022_leaders.csv","raptor_2022.png","2022 season","publisher-defined rating","Bars rank 2022 player ratings; values are source-defined estimates."))

    metrics=[
        add_metric("team_game_records",games_n,"team games","Count of non-copy team-game rows with available outcome and forecast."),
        add_metric("team_game_win_rate",round(win_rate,4),"proportion","Wins divided by non-copy team-game records."),
        add_metric("elo_holdout_brier_score",round(brier,4),"squared probability error","Mean squared error of source pregame Elo probabilities on the final three seasons."),
        add_metric("elo_holdout_accuracy",round(acc,4),"proportion correct","Share of final-three-season team-game forecasts correctly classified at probability 0.5."),
        add_metric("elo_holdout_accuracy_ci95_lower",round(accuracy_center-accuracy_half,4),"proportion correct","Lower Wilson interval bound for holdout classification accuracy."),
        add_metric("elo_holdout_accuracy_ci95_upper",round(accuracy_center+accuracy_half,4),"proportion correct","Upper Wilson interval bound for holdout classification accuracy."),
        add_metric("elo_holdout_observed_win_rate",round(obs_holdout,4),"proportion","Observed team-game win fraction in the final three archive seasons."),
        add_metric("qualified_raptor_player_seasons",int(len(qualified)),"player-seasons","Player-season records with at least 1,000 possessions."),
        add_metric("raptor_players_2022",int(rap.loc[rap["season"].eq(2022),"player_id"].nunique()),"players","Distinct player IDs in the 2022 RAPTOR source season."),
    ]
    headline=f"The non-copy NBA Elo archive contains {games_n:,} team-games ({start}–{end}); on the final three seasons, source forecast accuracy was {acc:.1%} with Brier score {brier:.3f}."
    recommendation="Use the source probabilities as a historical calibration reference only. Before applying forecasting to current games, retrain or validate on current data and a strictly chronological holdout, then compare calibration and Brier score with a simple baseline."
    report=f"""# Sports analysis — source narrative

## Executive summary

{headline}

## Questions and sources

The team analysis uses one non-copy team perspective per NBA game from the FiveThirtyEight Elo archive ({start}–{end}). The player analysis uses the historical RAPTOR player-season file (1977–2022). The sources have different grains and are reported separately.

## Statistical and predictive assessment

The source's pregame Elo probability is evaluated on the final three archive seasons ({last_season-2}–{last_season}), chronologically held out: accuracy {acc:.1%}, Brier score {brier:.4f}, mean predicted win chance {forecast_mean:.3f}, observed win fraction {obs_holdout:.3f}. This is a historical assessment of the published forecast, not a newly trained predictive model. RAPTOR rankings require caution because methodology varies across eras.

## Recommendation

{recommendation}

## Limitations

"""+"\n".join(f"- {x}" for x in LIMITATIONS)+"\n\n## Figures\n\nSee `visualizations/sports/` and `visualizations/sports/manifest.csv`.\n"
    Path("reports/source").mkdir(parents=True,exist_ok=True);Path("reports/source/sports.md").write_text(report,encoding="utf-8")
    Path("recommendations").mkdir(exist_ok=True);Path("recommendations/sports.md").write_text(f"# Sports recommendations\n\n## Finding\n\n{headline}\n\n## Action\n\n{recommendation}\n\n## Limitation\n\nThe Elo file ends in 2015; RAPTOR's methods differ by era.\n\n## Monitor\n\nProspective Brier score, calibration curve, and accuracy by season after comparison to a base-rate forecast.\n",encoding="utf-8")
    result=finish_domain(DOMAIN,DATASET_IDS,{"team_game_start_year":str(start),"team_game_end_year":str(end),"player_season_start":"1977","player_season_end":"2022","unit_of_analysis":"team-game and player-season (separate)"},metrics,LIMITATIONS,rows)
    result.update({"headline":headline,"recommendation":recommendation})
    return result
