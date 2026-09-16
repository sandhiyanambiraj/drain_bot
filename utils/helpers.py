"""UI helpers and formatters."""
import streamlit as st
from .config import COLORS, SEVERITY_COLORS


def status_color(robot: dict) -> str:
    if robot.get("motor_status") != "ok" or robot.get("comm_status") != "online":
        return COLORS["danger"]
    if robot.get("battery", 100) < 20 or robot.get("bag_level", 0) > 90:
        return COLORS["warning"]
    return COLORS["success"]


def robot_status_label(robot: dict) -> str:
    if robot.get("motor_status") != "ok":
        return "🔴 Fault"
    if robot.get("comm_status") != "online":
        return "🔴 Offline"
    if robot.get("battery", 100) < 20:
        return "🟠 Low Battery"
    if robot.get("bag_level", 0) > 90:
        return "🟠 Bag Full"
    if robot.get("task") == "cleaning":
        return "🟢 Cleaning"
    return "🟢 Idle"


def severity_color(sev: str) -> str:
    return SEVERITY_COLORS.get(sev, COLORS["info"])


def stat_card(label: str, value, color: str, icon: str = ""):
    st.markdown(
        f"""
        <div style="
            background:white;
            border-left:5px solid {color};
            border-radius:12px;
            padding:16px 18px;
            box-shadow:0 2px 8px rgba(0,0,0,0.06);
        ">
            <div style="font-size:22px;">{icon}</div>
            <div style="font-size:30px;font-weight:700;color:{color};line-height:1.1;">
                {value}
            </div>
            <div style="font-size:12px;color:#64748b;text-transform:uppercase;
                        letter-spacing:0.5px;margin-top:4px;">
                {label}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def robot_card(robot: dict):
    color = status_color(robot)
    label = robot_status_label(robot)
    st.markdown(
        f"""
        <div style="
            background:white;
            border-left:5px solid {color};
            border-radius:10px;
            padding:14px 16px;
            margin-bottom:10px;
            box-shadow:0 1px 4px rgba(0,0,0,0.06);
        ">
            <div style="display:flex;justify-content:space-between;
                        align-items:center;margin-bottom:6px;">
                <span style="font-size:17px;font-weight:700;">
                    🤖 {robot['robot_id']}
                </span>
                <span style="font-size:12px;font-weight:600;">{label}</span>
            </div>
            <div style="font-size:13px;color:#475569;">
                🔋 {robot.get('battery',0):.0f}% &nbsp;·&nbsp;
                💧 {robot.get('water_level',0):.0f}% &nbsp;·&nbsp;
                🗑️ {robot.get('bag_level',0):.0f}% &nbsp;·&nbsp;
                ⚡ {robot.get('solar',0):.1f} W
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def alert_card(event: dict, show_resolve: bool = True):
    sev = event.get("severity", "info")
    color = severity_color(sev)
    resolved = event.get("status") == "resolved"
    opacity = "0.55" if resolved else "1"

    st.markdown(
        f"""
        <div style="
            background:white;
            border-left:5px solid {color};
            border-radius:10px;
            padding:12px 16px;
            margin-bottom:10px;
            opacity:{opacity};
            box-shadow:0 1px 4px rgba(0,0,0,0.06);
        ">
            <div style="display:flex;justify-content:space-between;
                        align-items:center;">
                <b style="font-size:13px;text-transform:uppercase;">
                    {event.get('event_type','').replace('_',' ')}
                </b>
                <span style="font-size:10px;font-weight:700;padding:2px 8px;
                             background:{color};color:white;border-radius:6px;">
                    {sev.upper()}
                </span>
            </div>
            <div style="font-size:13px;color:#334155;margin:6px 0;">
                {event.get('notes','')}
            </div>
            <div style="font-size:11px;color:#64748b;display:flex;
                        justify-content:space-between;">
                <span>🤖 {event.get('robot_id','')}</span>
                <span>{event.get('timestamp','')[:19].replace('T',' ')}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = "", icon: str = ""):
    st.markdown(
        f"""
        <div style="margin-bottom:20px;">
            <h1 style="margin:0;color:#00695c;">
                {icon} {title}
            </h1>
            {f'<p style="color:#64748b;margin-top:4px;">{subtitle}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )