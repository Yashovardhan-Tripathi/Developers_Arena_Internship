"""Unified, local dashboard for the five portfolio analyses."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

st.set_page_config(page_title="Complete Data Analysis Portfolio",page_icon="📊",layout="wide",initial_sidebar_state="expanded")

DOMAINS={
    "Business sales":"sales",
    "Healthcare encounters":"healthcare",
    "Sports analytics":"sports",
    "Financial risk":"finance",
    "E-commerce sessions":"ecommerce",
}
TITLES={"sales":"Business sales","healthcare":"Healthcare encounters","sports":"Sports analytics","finance":"Financial risk","ecommerce":"E-commerce sessions"}

@st.cache_data(show_spinner="Loading the selected analysis…")
def load_metrics(domain:str)->dict:
    path=ROOT/"outputs"/domain/"metrics.json"
    if not path.is_file(): raise FileNotFoundError(f"Required metrics are missing: {path.relative_to(ROOT)}")
    doc=json.loads(path.read_text(encoding="utf-8"))
    if doc.get("schema_version")!="1.0" or doc.get("domain")!=domain or not isinstance(doc.get("metrics"),list):
        raise ValueError("The metrics file has an unsupported schema or domain.")
    return doc

@st.cache_data(show_spinner="Loading analysis data…")
def load_table(relative_path:str,parse_dates:tuple[str,...]=())->pd.DataFrame:
    path=(ROOT/relative_path).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file(): raise FileNotFoundError(f"Required analysis table is missing: {relative_path}")
    return pd.read_csv(path,parse_dates=list(parse_dates),low_memory=False)

def metric_lookup(domain:str)->dict[str,dict]:
    return {x["metric_id"]:x for x in load_metrics(domain)["metrics"]}

def metric_row(items:list[tuple[str,str,str]],domain:str)->None:
    metrics=metric_lookup(domain);cols=st.columns(len(items))
    for col,(key,label,fmt) in zip(cols,items):
        item=metrics.get(key)
        if not item or not item.get("available",False):
            col.metric(label,"Not available",help=(item or {}).get("unavailable_reason","No validated metric is available."));continue
        value=item.get("value")
        if value is None: display="Not available"
        elif fmt=="currency": display=f"£{value:,.0f}"
        elif fmt=="percent": display=f"{value:.1%}"
        elif fmt=="number": display=f"{value:,.0f}"
        elif fmt=="decimal": display=f"{value:.3f}"
        else: display=str(value)
        col.metric(label,display,help=item.get("definition",""))

def source_note(domain:str)->None:
    doc=load_metrics(domain)
    coverage=" · ".join(f"{key.replace('_',' ').title()}: {value}" for key,value in doc.get("coverage",{}).items() if value is not None)
    st.caption(f"Data snapshot: {', '.join(doc.get('dataset_snapshots',{}).keys())} · {coverage}")
    limitations=doc.get("limitations",[])
    if limitations:
        with st.expander("Sources, methods, and limitations"):
            st.markdown("\n".join(f"- {item}" for item in limitations))
            st.caption(f"Source details: datasets/README.md · Metrics schema {doc.get('schema_version')}")

def static_figures(domain:str)->None:
    path=ROOT/"visualizations"/domain/"manifest.csv"
    if not path.is_file():
        st.info("Charts have not been generated yet. Run the documented domain build command.")
        return
    manifest=pd.read_csv(path)
    if manifest.empty or not {"output_path","title","accessibility_summary"}.issubset(manifest.columns):
        st.warning("The chart manifest is empty or does not match the expected schema.")
        return
    st.subheader("Analysis figures")
    for left in range(0,len(manifest),2):
        cols=st.columns(2)
        for offset,col in enumerate(cols):
            index=left+offset
            if index>=len(manifest): break
            row=manifest.iloc[index]
            path=(ROOT/str(row["output_path"])).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file():
                col.warning(f"Figure is unavailable: {row['title']}");continue
            col.image(str(path),caption=f"{row['title']} — {row['accessibility_summary']}",width="stretch")

def overview()->None:
    st.title("Complete Data Analysis Portfolio")
    st.write("Five reproducible analyses across business sales, healthcare, sports, finance, and e-commerce.")
    st.info("Findings use historical source snapshots. Each project page shows its coverage, definitions, and limitations.")
    ready=[]
    for domain in DOMAINS.values():
        try: ready.append(load_metrics(domain))
        except Exception: pass
    charts=sum(len(pd.read_csv(ROOT/"visualizations"/d/"manifest.csv")) for d in DOMAINS.values() if (ROOT/"visualizations"/d/"manifest.csv").is_file())
    cols=st.columns(3);cols[0].metric("Completed domain analyses",len(ready));cols[1].metric("Source snapshots",sum(len(x.get("dataset_snapshots",{})) for x in ready));cols[2].metric("Distinct charts",charts)
    st.subheader("Explore the portfolio")
    cards=st.columns(2)
    for i,(label,domain) in enumerate(DOMAINS.items()):
        with cards[i%2]:
            st.markdown(f"### {label}")
            try:
                doc=load_metrics(domain);items=doc["metrics"]
                focus=next((m for m in items if m["metric_id"] in {"completed_orders","readmission_within_30d_rate","elo_holdout_accuracy","equal_weight_annualized_price_return","session_conversion_rate"}),items[0] if items else None)
                if focus:
                    val=focus["value"]
                    unit=focus.get("unit","")
                    if isinstance(val,(int,float)) and ("proportion" in unit or "rate" in focus["metric_id"] or "accuracy" in focus["metric_id"]): display=f"{val:.1%}"
                    elif isinstance(val,(int,float)) and unit=="GBP": display=f"£{val:,.0f}"
                    elif isinstance(val,int): display=f"{val:,}"
                    elif isinstance(val,float): display=f"{val:,.2f}"
                    else: display=str(val)
                    st.write(f"**Reference metric:** {focus['metric_id'].replace('_',' ').title()} — {display} {focus['unit']}")
                st.write(f"**Coverage:** {', '.join(str(v) for v in doc['coverage'].values() if v)}")
            except Exception as exc: st.warning(f"Analysis unavailable: {exc}")
            st.caption(f"Use the sidebar to open {label}.")
    st.subheader("Portfolio files")
    downloads=[("README","README.md"),("Setup guide","docs/setup.md"),("Data dictionary","docs/data_dictionary.md"),("Validation log","docs/validation.md"),("Executive summary","executive_summary.pdf")]
    for start in range(0,len(downloads),3):
        cols=st.columns(3)
        for col,(label,relative) in zip(cols,downloads[start:start+3]):
            path=ROOT/relative
            if path.is_file():col.download_button(f"Download {label}",path.read_bytes(),file_name=path.name,mime="application/pdf" if path.suffix==".pdf" else "text/markdown")

def sales_page()->None:
    domain="sales";st.title("Business sales");source_note(domain)
    try: df=load_table("datasets/processed/sales/sales_lines.csv",("InvoiceDate",))
    except Exception as exc: st.error(str(exc));return
    st.sidebar.subheader("Sales filters")
    years=sorted(df["year"].dropna().astype(int).unique())
    yr=st.sidebar.selectbox("Invoice year",years,index=len(years)-1)
    countries=sorted(df["Country"].dropna().astype(str).unique())
    chosen=st.sidebar.multiselect("Countries",countries,default=countries[:min(8,len(countries))],help="Choose countries; clear the selection to include all countries.")
    data=df.loc[df["year"].eq(yr)]
    if chosen: data=data.loc[data["Country"].isin(chosen)]
    if data.empty: st.warning("No sales lines match these filters. Reset or widen the selection.");return
    orders=data.groupby("Invoice")["gross_line_sales_gbp"].sum()
    c=st.columns(3);c[0].metric("Gross line sales",f"£{data['gross_line_sales_gbp'].sum():,.0f}");c[1].metric("Eligible invoices",f"{data['Invoice'].nunique():,}");c[2].metric("Mean invoice value",f"£{orders.mean():,.2f}")
    monthly=data.assign(month=data["InvoiceDate"].dt.to_period("M").dt.to_timestamp()).groupby("month",as_index=False)["gross_line_sales_gbp"].sum()
    fig=px.line(monthly,x="month",y="gross_line_sales_gbp",markers=True,title="Gross sales by month",labels={"month":"Invoice month","gross_line_sales_gbp":"Gross sales (GBP)"});st.plotly_chart(fig,width="stretch")
    product=data.assign(product=data["Description"].fillna(data["StockCode"]).astype(str)).groupby("product",as_index=False)["gross_line_sales_gbp"].sum().nlargest(12,"gross_line_sales_gbp")
    st.plotly_chart(px.bar(product.sort_values("gross_line_sales_gbp"),x="gross_line_sales_gbp",y="product",orientation="h",title="Top products in selected scope",labels={"gross_line_sales_gbp":"GBP","product":"Product"}),width="stretch")
    st.caption("Gross positive line sales are not profit. Cancellation rows were excluded during preparation.")
    st.download_button("Download filtered monthly summary",monthly.to_csv(index=False),file_name="sales_monthly_filtered.csv",mime="text/csv")
    static_figures(domain)

def healthcare_page()->None:
    domain="healthcare";st.title("Healthcare encounters");source_note(domain)
    try: df=load_table("datasets/processed/healthcare/eligible_encounters_deidentified.csv")
    except Exception as exc: st.error(str(exc));return
    st.sidebar.subheader("Encounter filters")
    ages=sorted(df["age"].dropna().astype(str).unique())
    selected_age=st.sidebar.multiselect("Age bands",ages,default=ages)
    genders=sorted(df["gender"].dropna().astype(str).unique())
    selected_gender=st.sidebar.multiselect("Gender categories",genders,default=genders)
    data=df.loc[df["age"].astype(str).isin(selected_age)&df["gender"].astype(str).isin(selected_gender)]
    if data.empty: st.warning("No encounters match these filters. Reset or widen the selection.");return
    c=st.columns(4);c[0].metric("Eligible encounters",f"{len(data):,}");c[1].metric("30-day readmission",f"{data['readmit_30d'].mean():.1%}");c[2].metric("Median stay",f"{data['time_in_hospital'].median():.0f} days");c[3].metric("A1C recorded",f"{data['A1Cresult'].notna().mean():.1%}")
    age=data.groupby("age",observed=True,as_index=False).agg(encounters=("readmit_30d","size"),rate=("readmit_30d","mean"))
    st.plotly_chart(px.bar(age,x="age",y="rate",hover_data=["encounters"],title="30-day readmission by age band",labels={"age":"Source age band","rate":"Readmission share"}),width="stretch")
    st.plotly_chart(px.histogram(data,x="time_in_hospital",color="readmitted",barmode="overlay",opacity=.72,title="Stay length by source readmission label",labels={"time_in_hospital":"Days in hospital","readmitted":"Readmission label"}),width="stretch")
    st.caption("Encounter-level, historical descriptive results; repeated patients remain and no patient or encounter IDs are exported. This is not clinical guidance.")
    st.download_button("Download filtered de-identified encounters",data.to_csv(index=False),file_name="healthcare_encounters_filtered.csv",mime="text/csv")
    static_figures(domain)

def sports_page()->None:
    domain="sports";st.title("Sports analytics");source_note(domain)
    try: games=load_table("datasets/processed/sports/team_games.csv");players=load_table("datasets/processed/sports/player_seasons.csv")
    except Exception as exc: st.error(str(exc));return
    st.sidebar.subheader("Team and season filters")
    years=sorted(games["year_id"].dropna().astype(int).unique())
    season=st.sidebar.select_slider("Season range",options=years,value=(years[0],years[-1]))
    franchises=sorted(games["fran_id"].dropna().unique().tolist());franchise=st.sidebar.selectbox("Franchise",["All franchises"]+franchises)
    selected=games.loc[games["year_id"].between(*season)]
    if franchise!="All franchises": selected=selected.loc[selected["fran_id"].eq(franchise)]
    if selected.empty: st.warning("No team-games match these filters. Reset or widen the season range.");return
    c=st.columns(3);c[0].metric("Team-game records",f"{len(selected):,}");c[1].metric("Win rate",f"{selected['win'].mean():.1%}");c[2].metric("Mean point margin",f"{selected['margin'].mean():.2f}")
    annual=selected.groupby("year_id",as_index=False).agg(games=("win","size"),win_rate=("win","mean"),mean_margin=("margin","mean"))
    st.plotly_chart(px.line(annual,x="year_id",y="win_rate",markers=True,title="Win rate over selected seasons",labels={"year_id":"Season","win_rate":"Team-game win rate"}),width="stretch")
    st.subheader("Player-season ratings (separate source and grain)")
    player_years=sorted(players["season"].dropna().astype(int).unique());player_season=st.selectbox("Player rating season",player_years,index=len(player_years)-1)
    top=players.loc[players["season"].eq(player_season)].nlargest(15,"raptor_total")
    st.plotly_chart(px.bar(top.sort_values("raptor_total"),x="raptor_total",y="player_name",orientation="h",title=f"Top RAPTOR total ratings: {player_season}",labels={"raptor_total":"Publisher-defined estimate","player_name":"Player"}),width="stretch")
    st.caption("Team-game win rates and player-season ratings are reported separately. The Elo source ends in 2015; RAPTOR methods vary by era.")
    st.download_button("Download filtered team-game summary",annual.to_csv(index=False),file_name="sports_team_games_filtered.csv",mime="text/csv")
    static_figures(domain)

def finance_page()->None:
    domain="finance";st.title("Financial risk");source_note(domain)
    try: df=load_table("datasets/processed/finance/daily_prices_and_returns.csv",("date",))
    except Exception as exc: st.error(str(exc));return
    st.sidebar.subheader("Price history filters")
    symbols=sorted(df["symbol"].dropna().astype(str).unique().tolist())
    default=symbols[:min(8,len(symbols))]
    selected=st.sidebar.multiselect("Symbols",symbols,default=default)
    start,end=df["date"].min().date(),df["date"].max().date()
    dates=st.sidebar.date_input("Date range",value=(start,end),min_value=start,max_value=end)
    if len(dates)!=2: st.info("Choose a start and end date.");return
    data=df.loc[df["symbol"].isin(selected)&df["date"].between(pd.Timestamp(dates[0]),pd.Timestamp(dates[1]))]
    if data.empty: st.warning("No prices match these filters. Reset or widen the selection.");return
    pivot=data.pivot(index="date",columns="symbol",values="close").sort_index();indexed=pivot/pivot.iloc[0]*100
    returns=pivot.pct_change().dropna(how="all");vol=returns.std()*252**.5
    c=st.columns(3);c[0].metric("Symbols selected",f"{len(selected):,}");c[1].metric("Observed trading dates",f"{len(pivot):,}");c[2].metric("Median annualized volatility",f"{vol.median():.1%}" if len(vol) else "Not available")
    st.plotly_chart(px.line(indexed,title="Indexed split-adjusted close (base 100)",labels={"date":"Date","value":"Index","variable":"Symbol"}),width="stretch")
    portfolio=returns.mean(axis=1,skipna=True).dropna();growth=(1+portfolio).cumprod().rename("growth_of_1").reset_index()
    st.plotly_chart(px.line(growth,x="date",y="growth_of_1",title="Equal-weight selected-symbol price-return illustration",labels={"date":"Date","growth_of_1":"Growth of 1"}),width="stretch")
    st.caption("Split-adjusted close price returns; dividend adjustment is undocumented. Selected-symbol equal weighting is a historical illustration, not investment advice.")
    st.download_button("Download filtered indexed prices",indexed.reset_index().to_csv(index=False),file_name="finance_indexed_prices.csv",mime="text/csv")
    static_figures(domain)

def ecommerce_page()->None:
    domain="ecommerce";st.title("E-commerce sessions");source_note(domain)
    try: df=load_table("datasets/processed/ecommerce/sessions.csv")
    except Exception as exc: st.error(str(exc));return
    st.sidebar.subheader("Session filters")
    month_order={"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"June":6,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
    months=sorted(df["Month"].dropna().unique().tolist(),key=lambda x:month_order.get(x,99))
    selected_month=st.sidebar.multiselect("Sample months",months,default=months)
    visitor=st.sidebar.multiselect("Visitor type",sorted(df["VisitorType"].dropna().unique()),default=sorted(df["VisitorType"].dropna().unique()))
    weekend=st.sidebar.selectbox("Timing",["All","Weekday","Weekend"])
    data=df.loc[df["Month"].isin(selected_month)&df["VisitorType"].isin(visitor)]
    if weekend!="All": data=data.loc[data["Weekend"].eq(weekend=="Weekend")]
    if data.empty: st.warning("No sessions match these filters. Reset or widen the selection.");return
    c=st.columns(4);c[0].metric("Sessions",f"{len(data):,}");c[1].metric("Purchase sessions",f"{int(data['Revenue'].sum()):,}");c[2].metric("Conversion",f"{data['Revenue'].mean():.1%}");c[3].metric("Median product-page views",f"{data['ProductRelated'].median():.0f}")
    chart=data.groupby("Month",as_index=False).agg(sessions=("Revenue","size"),conversion=("Revenue","mean"))
    st.plotly_chart(px.line(chart,x="Month",y="conversion",markers=True,title="Session conversion in selected months",labels={"Month":"Sample month","conversion":"Purchase-session share"}),width="stretch")
    st.plotly_chart(px.box(data,x="Revenue",y="ProductRelated",points=False,title="Product-related page views by session outcome",labels={"Revenue":"Purchase session","ProductRelated":"Product-related page views"}),width="stretch")
    st.caption("One-year session sample; it cannot support repeat-purchase or basket metrics. PageValues is not used to predict purchases.")
    st.download_button("Download filtered session summary",chart.to_csv(index=False),file_name="ecommerce_conversion_filtered.csv",mime="text/csv")
    static_figures(domain)

st.markdown("""<style>
:root { color-scheme: light; }
section[data-testid="stSidebar"] { border-right: 1px solid #CBD5E1; }
div[data-testid="stMetric"] { background:#F8FAFC; border:1px solid #CBD5E1; padding:1rem; border-radius:.55rem; }
:focus-visible { outline: 3px solid #1D4ED8 !important; outline-offset:2px !important; }
</style>""",unsafe_allow_html=True)
st.sidebar.title("Portfolio")
page=st.sidebar.radio("Navigate",["Overview",*DOMAINS.keys()],label_visibility="visible")
if page=="Overview": overview()
else:
    domain=DOMAINS[page]
    try:
        {"sales":sales_page,"healthcare":healthcare_page,"sports":sports_page,"finance":finance_page,"ecommerce":ecommerce_page}[domain]()
    except (FileNotFoundError,ValueError,json.JSONDecodeError) as exc:
        st.error(f"This view could not load a required validated output: {exc}")
        st.markdown("Follow [setup and build instructions](../docs/setup.md) from the project root.")
