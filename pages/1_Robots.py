"""Robots list page."""
import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

from utils import api, auth, helpers
from utils.config import REFRESH_SECONDS

st.set_page_config(page_title="Robots · DrainBot", page_icon="🤖", layout="wide")
st_autorefresh(interval=REFRESH_SECONDS * 1000, key="robots_refresh")

auth.require_login()

helpers.page_header("Robots", "All registered robots and their status", "🤖")

robots = api.get_robots()

if not isinstance(robots, list) or not robots:
    st.warning("No robots available. Start the simulator: `python fake_robot.py`")
    st.stop()

col1, col2 = st.columns([2, 1])
with col1:
    search = st.text_input("🔍 Search robot ID", "")
with col2:
    status_filter = st.selectbox(
        "Filter", ["All", "Cleaning", "Idle", "Charging", "Fault"], index=0
    )

filtered = robots
if search:
    filtered = [r for r in filtered if search.lower() in r["robot_id"].lower()]
if status_filter != "All":
    filtered = [r for r in filtered if r.get("task", "").lower() == status_filter.lower()]

st.caption(f"Showing {len(filtered)} of {len(robots)} robots")

cols = st.columns(3)
for i, robot in enumerate(filtered):
    with cols[i % 3]:
        helpers.robot_card(robot)

st.divider()
st.subheader("📋 Detailed table")
df = pd.DataFrame(robots)
st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()
st.subheader("🔍 Inspect a specific robot")

selected = st.selectbox("Choose robot", [r["robot_id"] for r in robots])

if selected:
    robot = api.get_robot(selected)

    if "error" in robot:
        st.error(f"Error: {robot['error']}")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🔋 Battery", f"{robot['battery']:.0f}%")
        c2.metric("💧 Water", f"{robot['water_level']:.0f}%")
        c3.metric("🗑️ Bag", f"{robot['bag_level']:.0f}%")
        c4.metric("⚡ Solar", f"{robot['solar']:.1f} W")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🌊 Flow", f"{robot['flow']:.2f} L/min")
        c2.metric("🪶 Wing", robot.get("wing_pos", "-"))
        c3.metric("⚙️ Motor", robot.get("motor_status", "-"))
        c4.metric("📡 Comm", robot.get("comm_status", "-"))

        st.subheader("📜 Event history")
        events = api.get_robot_events(selected)
        if isinstance(events, list) and events:
            for e in events:
                helpers.alert_card(e)
        else:
            st.info("No events for this robot.")