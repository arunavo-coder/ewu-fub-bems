# pages/Room_Detail.py — FINAL SAFE VERSION
import streamlit as st
import plotly.express as px
from datetime import date, timedelta
from utils import *

st.set_page_config(page_title="Room Detail", layout="wide")

if st.button("Back to Dashboard"):
    if "selected_room" in st.session_state:
        del st.session_state.selected_room
    st.switch_page("Home.py")

if "selected_room" not in st.session_state:
    st.error("No room selected!")
    st.stop()

room_id = st.session_state.selected_room
devices = get_devices()
room_device = devices[devices['room_id'] == room_id]

if room_device.empty:
    st.error(f"Room {room_id} not found!")
    st.stop()

device = room_device.iloc[0]
room_name = device['room_name']

st.title(f"{room_name} • {room_id}")

# Date range
col1, col2 = st.columns(2)
with col1:
    start = st.date_input("From", date.today() - timedelta(days=7))
with col2:
    end = st.date_input("To", date.today())

data = get_period_data(start, end)
room_data = data[data['device_id'] == device['device_id']]

live = get_current_readings(device)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Live Power", f"{live['power']:.0f} W")
c2.metric("Voltage", f"{live['voltage']:.1f} V")
c3.metric("Current", f"{live['current']:.2f} A")
c4.metric("Status", "ON" if live['power'] > 50 else "OFF")

kwh, taka, gco2 = calculate_stats(room_data)
col1, col2, col3 = st.columns(3)
col1.metric("Energy", f"{kwh:.2f} kWh")
col2.metric("Cost", f"৳ {taka}")
col3.metric("Carbon", f"{gco2:,} gCO₂")

if not room_data.empty:
    col1, col2, col3 = st.columns(3)
    with col1:
        fig = px.line(room_data, x='timestamp', y='power', title="Power (W)", color_discrete_sequence=["#00d4aa"])
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.line(room_data, x='timestamp', y='voltage', title="Voltage (V)", color_discrete_sequence=["#ffa502"])
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    with col3:
        fig = px.line(room_data, x='timestamp', y='current', title="Current (A)", color_discrete_sequence=["#ff4757"])
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data in selected period")

# Control
st.markdown("### Control")
c1, c2 = st.columns(2)
if c1.button("Turn ON", type="primary", use_container_width=True):
    devices.loc[devices['device_id'] == device['device_id'], 'current_state'] = 'on'
    save(devices, "devices.csv")
    st.success("Turned ON"); st.rerun()
if c2.button("Turn OFF", use_container_width=True):
    devices.loc[devices['device_id'] == device['device_id'], 'current_state'] = 'off'
    save(devices, "devices.csv")
    st.success("Turned OFF"); st.rerun()
