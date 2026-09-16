"""Alerts page."""
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from utils import api, auth, helpers
from utils.config import REFRESH_SECONDS

st.set_page_config(page_title="Alerts · DrainBot", page_icon="🚨", layout="wide")
st_autorefresh(interval=REFRESH_SECONDS * 1000, key="alerts_refresh")

auth.require_login()

helpers.page_header("Alerts & Events", "Real-time alerts from all robots", "🚨")

events = api.get_events(limit=300)

if not isinstance(events, list):
    st.error("Could not load events.")
    st.stop()

c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    severity_filter = st.multiselect(
        "Severity", ["critical", "warning", "info"],
        default=["critical", "warning", "info"],
    )
with c2:
    status_filter = st.selectbox("Status", ["All", "open", "resolved"], index=0)
with c3:
    robot_filter = st.text_input("Robot ID contains", "")

filtered = events
filtered = [e for e in filtered if e["severity"] in severity_filter]
if status_filter != "All":
    filtered = [e for e in filtered if e["status"] == status_filter]
if robot_filter:
    filtered = [e for e in filtered if robot_filter.lower() in e["robot_id"].lower()]

st.caption(f"Showing **{len(filtered)}** of **{len(events)}** events")

c1, c2, c3, c4 = st.columns(4)
c1.metric("🚨 Critical",
          len([e for e in events if e["severity"] == "critical" and e["status"] == "open"]))
c2.metric("⚠️ Warnings",
          len([e for e in events if e["severity"] == "warning" and e["status"] == "open"]))
c3.metric("ℹ️ Info",
          len([e for e in events if e["severity"] == "info" and e["status"] == "open"]))
c4.metric("✔️ Resolved",
          len([e for e in events if e["status"] == "resolved"]))

st.divider()

if not filtered:
    st.info("No alerts match the current filters.")
else:
    for e in filtered:
        col_left, col_right = st.columns([5, 1])
        with col_left:
            helpers.alert_card(e)
        with col_right:
            if e["status"] == "open" and auth.can_resolve():
                if st.button("✔ Resolve", key=f"resolve_{e['event_id']}",
                             use_container_width=True):
                    api.resolve_event(e["event_id"])
                    api.clear_cache()
                    st.rerun()
        st.write("")