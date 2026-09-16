"""Live Map page."""
import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

from utils import api, auth, helpers
from utils.config import REFRESH_SECONDS

st.set_page_config(page_title="Live Map · DrainBot", page_icon="🗺️", layout="wide")
st_autorefresh(interval=REFRESH_SECONDS * 1000, key="map_refresh")

auth.require_login()

helpers.page_header("Live Map", "GPS locations of all DrainBots", "🗺️")

robots = api.get_robots()

if not isinstance(robots, list) or not robots:
    st.warning("No robots online.")
    st.stop()

df = pd.DataFrame(robots)
map_df = df[["lat", "lon"]].copy()

st.map(map_df, zoom=13, use_container_width=True)

st.subheader(f"📍 {len(robots)} robots on map")
for r in robots:
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    with c1:
        st.markdown(f"**🤖 {r['robot_id']}**")
    with c2:
        st.write(f"🔋 {r['battery']:.0f}%")
    with c3:
        st.write(f"💧 {r['water_level']:.0f}%")
    with c4:
        st.write(f"_{r['task']}_")