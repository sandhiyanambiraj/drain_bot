"""Simple session-based auth for the Streamlit app."""
import streamlit as st


DEMO_USERS = {
    "admin":   {"password": "admin123",   "role": "Admin"},
    "officer": {"password": "officer123", "role": "Municipality Officer"},
    "tech":    {"password": "tech123",    "role": "Maintenance Team"},
    "public":  {"password": "public",     "role": "Public"},
}


def login(username: str, password: str) -> bool:
    user = DEMO_USERS.get(username.lower())
    if user and user["password"] == password:
        st.session_state["user"] = {
            "username": username,
            "role": user["role"],
        }
        return True
    return False


def logout():
    st.session_state.pop("user", None)


def get_user():
    return st.session_state.get("user")


def is_logged_in() -> bool:
    return "user" in st.session_state


def current_role() -> str:
    user = get_user()
    return user["role"] if user else "Guest"


def can_resolve() -> bool:
    return current_role() in ("Admin", "Municipality Officer")


def is_admin() -> bool:
    return current_role() == "Admin"


def require_login():
    if not is_logged_in():
        st.warning("🔒 Please login from the Home page first.")
        st.stop()