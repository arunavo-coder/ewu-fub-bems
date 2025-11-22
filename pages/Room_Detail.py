# pages/Room_Detail.py
import streamlit as st
import plotly.express as px
from datetime import date, timedelta, datetime
from utils import *

st.set_page_config(layout="wide")

# === CORRECT WAY TO READ QUERY PARAMS (2025 Streamlit) ===
if "room" not in st.query_params:
    st.error("No room selected")
    st.stop()

room_id = st.query_params["room"]   # This is the correct way now

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title(f"Room {room_id} – Detailed Monitoring")
with col2:
    if st.button("← Back to Dashboard", use_container_width=True):
        st.switch_page("Home.py")

# Date range
start_d = st.date_input("From", date.today() - timedelta(days=7), key="rs")
end_d = st.date_input("To", date.today(), key="re")

# Load data
room = get_rooms()[get_rooms()['room_id'] == room_id].iloc[0]
device = get_devices()[get_devices()['room_id'] == room_id].iloc[0]
live = get_current_readings(device)

# Live metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Live Power", f"{live['power']:.1f} W", delta="Live")
c2.metric("Voltage", f"{live['voltage']:.1f} V")
c3.metric("Current", f"{live['current']:.2f} A")
c4.metric("Status", "ON" if live['power'] > 50 else "OFF", 
          delta="ON" if live['power'] > 50 else "OFF")

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
    fig = px.line(room_data, x='timestamp', y='power', title="Power Consumption Over Time")
    fig.add_scatter(x=room_data['timestamp'], y=room_data['voltage']*5, name="Voltage ×5", yaxis="y2")
    fig.update_layout(
        yaxis2=dict(title="Voltage ×5", overlaying="y", side="right"),
        legend=dict(x=0, y=1.1),
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data in selected date range")

# Control Panel
st.markdown("### Control Panel")
col1, col2, col3 = st.columns(3)

if col1.button("Turn ON", type="primary", use_container_width=True):
    devices = get_devices()
    devices.loc[devices['device_id'] == device['device_id'], ['current_state', 'auto_schedule']] = ["on", False]
    save(devices, "devices.csv")
    st.success("AC Turned ON")
    st.rerun()

if col2.button("Turn OFF", type="primary", use_container_width=True):
    devices = get_devices()
    devices.loc[devices['device_id'] == device['device_id'], ['current_state', 'auto_schedule']] = ["off", False]
    save(devices, "devices.csv")
    st.success("AC Turned OFF")
    st.rerun()

if col3.button("Enable Auto Schedule", use_container_width=True):
    devices = get_devices()
    devices.loc[devices['device_id'] == device['device_id'], 'auto_schedule'] = True
    save(devices, "devices.csv")
    st.success("Auto Schedule Enabled")
    st.rerun()

# Schedule Editor
with st.expander("Edit Auto Schedule"):
    current_on = datetime.strptime(device['schedule_on'], "%H:%M").time()
    current_off = datetime.strptime(device['schedule_off'], "%H:%M").time()
    
    on_time = st.time_input("Turn ON at", value=current_on)
    off_time = st.time_input("Turn OFF at", value=current_off)
    
    if st.button("Save Schedule", type="primary"):
        devices = get_devices()
        devices.loc[devices['device_id'] == device['device_id'], 
                   ['schedule_on', 'schedule_off']] = [on_time.strftime("%H:%M"), off_time.strftime("%H:%M")]
        save(devices, "devices.csv")
        st.success("Schedule updated successfully!")
        st.rerun()
