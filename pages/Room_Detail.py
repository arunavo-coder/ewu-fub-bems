# pages/Room_Detail.py
import streamlit as st
import plotly.express as px
from datetime import date, timedelta, datetime
from utils import *

st.set_page_config(layout="wide")

# === 100% RELIABLE ROOM SELECTION WITH SESSION STATE ===
if "selected_room" not in st.session_state:
    st.error("No room selected")
    st.info("Please select a room from the main dashboard")
    if st.button("Go to Dashboard"):
        del st.session_state.selected_room  # Clear if exists
        st.switch_page("Home.py")
    st.stop()

room_id = st.session_state.selected_room

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title(f"Room {room_id} – Detailed Monitoring")
with col2:
    if st.button("← Back to Dashboard", use_container_width=True):
        del st.session_state.selected_room  # Clear for next time
        st.switch_page("Home.py")

# Date range
start_d = st.date_input("From", date.today() - timedelta(days=7), key="rs")
end_d = st.date_input("To", date.today(), key="re")

# Load data
try:
    room = get_rooms()[get_rooms()['room_id'] == room_id].iloc[0]
    device = get_devices()[get_devices()['room_id'] == room_id].iloc[0]
    live = get_current_readings(device)
except IndexError:
    st.error("Room not found")
    st.stop()

# Live metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Live Power", f"{live['power']:.1f} W", delta="Live")
c2.metric("Voltage", f"{live['voltage']:.1f} V")
c3.metric("Current", f"{live['current']:.2f} A")
c4.metric("Status", "ON" if live['power'] > 50 else "OFF")

# Period stats
room_data = get_period_data(start_d, end_d)
room_data = room_data[room_data['device_id'] == device['device_id']]
kwh, taka, gco2 = calculate_stats(room_data)

st.divider()
ca, cb, cc = st.columns(3)
ca.metric("Energy Used", f"{kwh:.3f} kWh", f"{start_d} → {end_d}")
cb.metric("Estimated Cost", f"৳ {taka:.1f}")
cc.metric("Carbon Emission", f"{gco2:,} gCO₂")

# Graph
if len(room_data) > 0:
    fig = px.line(room_data, x='timestamp', y='power', title="Power Trend", color_discrete_sequence=["#00d4aa"])
    fig.add_scatter(x=room_data['timestamp'], y=room_data['voltage'], name="Voltage", yaxis="y2")
    fig.update_layout(yaxis2=dict(overlaying="y", side="right"), template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data in selected date range")

# Control Panel
st.markdown("### Control Panel")
c1, c2, c3 = st.columns(3)
if c1.button("Turn ON", type="primary", use_container_width=True):
    df = get_devices()
    df.loc[df['device_id'] == device['device_id'], ['current_state','auto_schedule']] = ["on", False]
    save(df, "devices.csv")
    st.success("AC Turned ON")
    st.rerun()
if c2.button("Turn OFF", type="primary", use_container_width=True):
    df = get_devices()
    df.loc[df['device_id'] == device['device_id'], ['current_state','auto_schedule']] = ["off", False]
    save(df, "devices.csv")
    st.success("AC Turned OFF")
    st.rerun()
if c3.button("Enable Auto Schedule", use_container_width=True):
    df = get_devices()
    df.loc[df['device_id'] == device['device_id'], 'auto_schedule'] = True
    save(df, "devices.csv")
    st.success("Auto scheduling enabled")
    st.rerun()

# Schedule Editor
with st.expander("Edit Schedule"):
    current_on = datetime.strptime(device['schedule_on'], '%H:%M').time()
    current_off = datetime.strptime(device['schedule_off'], '%H:%M').time()
    on_time = st.time_input("Turn ON at", value=current_on)
    off_time = st.time_input("Turn OFF at", value=current_off)
    if st.button("Save Schedule", type="primary"):
        df = get_devices()
        df.loc[df['device_id'] == device['device_id'], ['schedule_on', 'schedule_off']] = [on_time.strftime('%H:%M'), off_time.strftime('%H:%M')]
        save(df, "devices.csv")
        st.success("Schedule updated!")
        st.rerun()
