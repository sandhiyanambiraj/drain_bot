"""Thin wrapper around the DrainBot FastAPI backend."""
import requests
import streamlit as st
from .config import API_BASE, API_TIMEOUT


@st.cache_data(ttl=2)
def _get(path: str):
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=API_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def _post(path: str, data=None):
    try:
        r = requests.post(f"{API_BASE}{path}", json=data, timeout=API_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def is_backend_up() -> bool:
    try:
        r = requests.get(f"{API_BASE}/health", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def get_dashboard():
    return _get("/dashboard")


def get_robots():
    return _get("/robots")


def get_robot(robot_id: str):
    return _get(f"/robots/{robot_id}")


def get_events(limit: int = 200):
    return _get(f"/events?limit={limit}")


def get_robot_events(robot_id: str):
    return _get(f"/events/robot/{robot_id}")


def get_analytics():
    return _get("/dashboard/waste_analytics")


def resolve_event(event_id: int, notes: str = "Resolved from Streamlit"):
    return _post(f"/events/{event_id}/resolve?notes={notes}")


def create_event(payload: dict):
    return _post("/events", payload)


def clear_cache():
    _get.clear()