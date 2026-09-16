"""Waste Analytics page."""
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

from utils import api, auth, helpers
from utils.config import REFRESH_SECONDS

st.set_page_config(page_title="Analytics · DrainBot", page_icon="📊", layout="wide")
st_autorefresh(interval=REFRESH_SECONDS * 3 * 1000, key="analytics_refresh")

auth.require_login()

helpers.page_header("Waste Analytics", "Insights from all collected data", "📊")

events = api.get_events(limit=1000)

if not isinstance(events, list) or not events:
    st.info("No data yet. Run scenarios to populate analytics.")
    st.stop()

df = pd.DataFrame(events)

c1, c2, c3, c4 = st.columns(4)
c1.metric("📋 Total Events", len(df))
c2.metric("🚨 Critical", len(df[df["severity"] == "critical"]))
c3.metric("⚠️ Warning", len(df[df["severity"] == "warning"]))
c4.metric("✔️ Resolved", len(df[df["status"] == "resolved"]))

st.divider()

st.subheader("📈 Events by type")
type_counts = df["event_type"].value_counts().reset_index()
type_counts.columns = ["Event Type", "Count"]
fig1 = px.bar(type_counts, x="Event Type", y="Count", color="Count",
              color_continuous_scale="Teal", text="Count")
fig1.update_layout(showlegend=False, height=400, margin=dict(t=20, b=20))
st.plotly_chart(fig1, use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    st.subheader("🥧 By severity")
    sev_counts = df["severity"].value_counts().reset_index()
    sev_counts.columns = ["Severity", "Count"]
    fig2 = px.pie(sev_counts, names="Severity", values="Count",
                  color="Severity",
                  color_discrete_map={"critical": "#f44336",
                                       "warning": "#ff9800",
                                       "info": "#2196f3"},
                  hole=0.4)
    fig2.update_layout(height=350, margin=dict(t=10, b=10))
    st.plotly_chart(fig2, use_container_width=True)

with c2:
    st.subheader("🚦 Status")
    status_counts = df["status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    fig3 = px.pie(status_counts, names="Status", values="Count",
                  color="Status",
                  color_discrete_map={"open": "#ff9800", "resolved": "#4caf50"},
                  hole=0.4)
    fig3.update_layout(height=350, margin=dict(t=10, b=10))
    st.plotly_chart(fig3, use_container_width=True)

st.subheader("🤖 Events per robot")
robot_counts = df["robot_id"].value_counts().reset_index()
robot_counts.columns = ["Robot", "Count"]
fig4 = px.bar(robot_counts, x="Robot", y="Count", color="Count",
              color_continuous_scale="Blues", text="Count")
fig4.update_layout(showlegend=False, height=350, margin=dict(t=20, b=20))
st.plotly_chart(fig4, use_container_width=True)

with st.expander("🔎 View raw data"):
    st.dataframe(df, use_container_width=True, hide_index=True)

st.download_button(
    "📥 Download CSV",
    df.to_csv(index=False),
    "drainbot_events.csv",
    "text/csv",
    use_container_width=True,
)