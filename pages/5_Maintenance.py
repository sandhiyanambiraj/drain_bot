"""Maintenance queue page."""
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from utils import api, auth, helpers
from utils.config import REFRESH_SECONDS

st.set_page_config(page_title="Maintenance · DrainBot", page_icon="🔧", layout="wide")
st_autorefresh(interval=REFRESH_SECONDS * 2 * 1000, key="maint_refresh")

auth.require_login()

helpers.page_header("Maintenance", "Fault queue and repair tracking", "🔧")

events = api.get_events(limit=500)

if not isinstance(events, list):
    st.error("Could not load events.")
    st.stop()

MAINT_TYPES = {"motor_fault", "bag_full", "low_battery", "comm_lost", "camera_offline"}
maint = [e for e in events if e["event_type"] in MAINT_TYPES]

open_items = [e for e in maint if e["status"] == "open"]
closed_items = [e for e in maint if e["status"] == "resolved"]

c1, c2, c3 = st.columns(3)
c1.metric("📋 Total", len(maint))
c2.metric("🔴 Open", len(open_items))
c3.metric("✅ Resolved", len(closed_items))

st.divider()

tab1, tab2 = st.tabs(["🔴 Open Items", "✅ Resolved"])

with tab1:
    if not open_items:
        st.success("🎉 No open maintenance items!")
    else:
        for e in open_items:
            c1, c2 = st.columns([5, 1])
            with c1:
                helpers.alert_card(e)
            with c2:
                if auth.can_resolve():
                    if st.button("✔ Done", key=f"done_{e['event_id']}",
                                 use_container_width=True):
                        api.resolve_event(e["event_id"], "Fixed by technician")
                        api.clear_cache()
                        st.rerun()
                else:
                    st.caption("View only")

with tab2:
    if not closed_items:
        st.info("No resolved items yet.")
    else:
        for e in closed_items:
            helpers.alert_card(e)