"""Garmin Pulse dashboard: reads the dbt marts layer from Postgres."""
import os

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

st.set_page_config(page_title="Garmin Pulse", page_icon="⌚", layout="wide")


@st.cache_resource
def get_engine():
    url = URL.create(
        "postgresql+psycopg2",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=5432,
        database=os.environ["POSTGRES_DB"],
    )
    return create_engine(url)


@st.cache_data(ttl=300)
def load(query: str) -> pd.DataFrame:
    return pd.read_sql(query, get_engine())


daily = load("select * from marts.fct_daily_health order by calendar_date")
weekly = load("select * from marts.fct_weekly_summary order by week_start")
workouts = load("select * from marts.fct_workouts order by start_time_local desc")

st.title("⌚ Garmin Pulse")
st.caption("Personal health analytics: Garmin Connect → Postgres → dbt → Streamlit")

# Date filter
min_d, max_d = daily["calendar_date"].min(), daily["calendar_date"].max()
start, end = st.sidebar.date_input("Date range", (min_d, max_d), min_value=min_d, max_value=max_d)
d = daily[(daily["calendar_date"] >= start) & (daily["calendar_date"] <= end)]
w = workouts[(workouts["calendar_date"] >= start) & (workouts["calendar_date"] <= end)]

# KPIs
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Avg steps / day", f"{d['total_steps'].mean():,.0f}")
c2.metric("Avg sleep (h)", f"{d['sleep_hours'].mean():.1f}")
c3.metric("Avg sleep score", f"{d['sleep_score'].mean():.0f}")
c4.metric("Avg resting HR", f"{d['resting_hr'].mean():.0f}")
c5.metric("Workouts", f"{len(w)}")

left, right = st.columns(2)
left.plotly_chart(px.bar(d, x="calendar_date", y="total_steps", title="Daily steps"), use_container_width=True)
right.plotly_chart(
    px.line(d, x="calendar_date", y=["sleep_hours", "deep_hours", "rem_hours"], title="Sleep (hours)"),
    use_container_width=True,
)

left, right = st.columns(2)
left.plotly_chart(
    px.line(d, x="calendar_date", y=["resting_hr", "avg_overnight_hrv"], title="Resting HR and overnight HRV"),
    use_container_width=True,
)
right.plotly_chart(
    px.line(d, x="calendar_date", y=["body_battery_high", "body_battery_low", "avg_stress"], title="Body battery and stress"),
    use_container_width=True,
)

st.subheader("Weekly summary")
st.dataframe(weekly.sort_values("week_start", ascending=False), use_container_width=True, hide_index=True)

st.subheader("Workouts")
st.dataframe(w, use_container_width=True, hide_index=True)
