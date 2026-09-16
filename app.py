"""DrainBot Streamlit — Main entry / Dashboard."""
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from utils import api, auth, helpers
from utils.config import REFRESH_SECONDS, COLORS

st.set_page_config(
    page_title="DrainBot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st_autorefresh(interval=REFRESH_SECONDS * 1000, key="drainbot_refresh")


# ============= SIDEBAR =============
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:12px 0 4px;">
            <div style="font-size:56px;">🤖</div>
            <div style="font-size:22px;font-weight:700;color:#00695c;">DrainBot</div>
            <div style="font-size:11px;color:#64748b;">Smart Drainage Monitoring</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    if auth.is_logged_in():
        user = auth.get_user()
        st.success(f"👤 **{user['username']}**  \n_{user['role']}_")
        if st.button("🚪 Logout", use_container_width=True):
            auth.logout()
            st.rerun()
    else:
        st.info("Login from the form on this page.")

    st.divider()
    st.caption("Backend status")
    if api.is_backend_up():
        st.success("🟢 Online")
    else:
        st.error("🔴 Offline — start `uvicorn`")


# ============= LOGIN GATE =============
if not auth.is_logged_in():
    st.markdown(
        """
        <h1 style="color:#00695c;">🤖 DrainBot</h1>
        <p style="color:#64748b;">Smart Drainage Monitoring & Robot Management</p>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("### 🔐 Sign In")
        with st.form("login_form"):
            username = st.text_input("Username", value="admin")
            password = st.text_input("Password", value="admin123", type="password")
            submit = st.form_submit_button("Sign In", use_container_width=True)

        if submit:
            if auth.login(username, password):
                st.success("✅ Logged in!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Try admin/admin123")

        st.caption(
            "**Demo accounts** — "
            "admin/admin123 · officer/officer123 · tech/tech123 · public/public"
        )
    st.stop()


# ============= DASHBOARD =============
helpers.page_header("Dashboard", "Live overview of the entire DrainBot fleet", "📊")

stats = api.get_dashboard()
if "error" in stats:
    st.error(f"Backend error: {stats['error']}")
    st.stop()

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    helpers.stat_card("Total Robots", stats.get("total_robots", 0), COLORS["info"], "🤖")
with c2:
    helpers.stat_card("Cleaning", stats.get("active_cleaning", 0), COLORS["success"], "🧹")
with c3:
    helpers.stat_card("Warnings", stats.get("warnings_open", 0), COLORS["warning"], "⚠️")
with c4:
    helpers.stat_card("Critical", stats.get("critical_open", 0), COLORS["danger"], "🚨")
with c5:
    helpers.stat_card("Full Bags", stats.get("full_bags", 0), "#9c27b0", "🗑️")

st.write("")

col_left, col_right = st.columns([1.4, 1])

with col_left:
    st.subheader("🤖 Robots")
    robots = api.get_robots()
    if isinstance(robots, list) and robots:
        for r in robots:
            helpers.robot_card(r)
    else:
        st.info("No robots online. Start the simulator.")

with col_right:
    st.subheader("🚨 Recent Alerts")
    events = api.get_events(limit=8)
    if isinstance(events, list) and events:
        for e in events:
            helpers.alert_card(e)
    else:
        st.info("No alerts yet.")

st.write("")
st.subheader("📋 Live Robot Metrics")

if isinstance(robots, list) and robots:
    import pandas as pd

    df = pd.DataFrame(robots)[
        ["robot_id", "battery", "solar", "water_level", "flow",
         "bag_level", "wing_pos", "motor_status", "task"]
    ]
    df.columns = ["Robot", "Battery %", "Solar W", "Water %",
                  "Flow L/min", "Bag %", "Wing", "Motor", "Task"]

    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No data to display.")

st.caption(
    f"🔄 Auto-refreshes every {REFRESH_SECONDS} seconds · "
    f"Backend: http://localhost:8000"
)