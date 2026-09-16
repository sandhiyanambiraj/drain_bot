"""Public report page."""
import streamlit as st
from datetime import datetime

from utils import api, helpers
from utils.config import DEFAULT_LAT, DEFAULT_LON

st.set_page_config(page_title="Public Report · DrainBot", page_icon="📝", layout="wide")

helpers.page_header(
    "Public Report",
    "Submit a drainage issue — visible to municipality officers",
    "📝",
)

st.info(
    "🌍 This page is designed to be opened by the public. "
    "Anyone can report an issue — no login required."
)

with st.form("public_report", clear_on_submit=True):
    c1, c2 = st.columns(2)

    with c1:
        problem_type = st.selectbox(
            "Problem Type",
            ["blockage", "overflow", "waste", "damage", "other"],
        )
        reporter_name = st.text_input("Your Name (optional)", "")

    with c2:
        lat = st.number_input("Latitude", value=DEFAULT_LAT, format="%.4f")
        lon = st.number_input("Longitude", value=DEFAULT_LON, format="%.4f")

    description = st.text_area(
        "Description *",
        placeholder="Describe the issue in detail...",
        height=120,
    )

    submitted = st.form_submit_button("🚀 Submit Report", use_container_width=True)

    if submitted:
        if not description.strip():
            st.error("Please enter a description.")
        else:
            payload = {
                "robot_id": f"PUBLIC-{(reporter_name or 'ANON')[:8].upper()}",
                "lat": lat,
                "lon": lon,
                "event_type": problem_type,
                "severity": "info",
                "notes": description,
                "sensor_snapshot": {
                    "source": "public_report",
                    "reporter": reporter_name or "Anonymous",
                    "submitted_at": datetime.utcnow().isoformat(),
                },
            }
            result = api.create_event(payload)

            if "error" in result:
                st.error(f"Failed to submit: {result['error']}")
            else:
                st.success(
                    f"✅ Report submitted! Event ID: **#{result.get('event_id')}**  \n"
                    "Municipality officers can see this in their Alerts page."
                )
                api.clear_cache()

st.divider()
st.subheader("📬 Recent public reports")

events = api.get_events(limit=200)
if isinstance(events, list):
    public_reports = [e for e in events if e["robot_id"].startswith("PUBLIC-")]

    if not public_reports:
        st.info("No public reports yet.")
    else:
        for e in public_reports[:20]:
            helpers.alert_card(e)