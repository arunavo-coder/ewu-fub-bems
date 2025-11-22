# pages/Room_Detail.py — FINAL BULLETPROOF VERSION
import streamlit as st
import plotly.express as px
from datetime import date, timedelta
from utils import *

st.set_page_config(page_title="Room Detail", layout="wide")

# BACK BUTTON
if st.button("Back to Dashboard"):
    if "selected_room" in st.session_state:
        del st.session_state.selected_room
    st.switch_page("Home.py")

# SAFELY GET SELECTED ROOM
if "selected_room" not in st.session_state or not st.session_state.selected_room:
    st.error("No room selected. Please go back to dashboard and click 'View Details' on a room.")
    st.stop()

room_id = st.session_state.selected_room

# LOAD DATA SAFELY
try:
    rooms_df = get_rooms()
    devices_df = get_devices()
except:
    st.error("Cannot load data. Check your CSV files.")
    st.stop()

# FIND THE ROOM SAFELY
room_row = rooms_df[rooms_df['room_id'] == room_id]
if room_row.empty:
    st.error(f"Room {room_id} not found in rooms list.")
    st.stop()
room = room_row.iloc[0]

# FIND THE DEVICE FOR THIS ROOM
device_row = devices_df[devices_df['room_id'] == room_id]
if device_row.empty:
    st.error(f"No device found for room {room_id}")
    st.stop()
device = device_row.iloc[0]

# PAGE TITLE
st.title(f"{room['room_name']} • Room {room_id}")

# DATE RANGE
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("From", date.today() - timedelta(days=7), key="rd_start")
with col2:
    end_date = st.date_input("To", date.today(), key="rd_end")

# LOAD READINGS FOR THIS PERIOD
period_data = get_period_data(start_date, end_date)
room_data = period_data[period_data['device_id'] == device['device_id']] if not period_data.empty else pd.DataFrame()

# LIVE READING
live = get_current_readings(device)
live_power = live.get('power', 0) if isinstance(live, dict) else 0
live_voltage = live.get('voltage', 0)
live_current = live.get('current', 0)

# LIVE METRICS
c1, c2, c3, c4 = st.columns(4)
c1.metric("Live Power", f"{live_power:.1f} W", "Real-time")
c2.metric("Voltage", f"{live_voltage:.1f} V")
c3.metric("Current", f"{live_current:.2f} A")
c4.metric("Status", "ON" if live_power > 50 else "OFF", 
          "High" if live_power > 1000 else "Normal")

# TOTAL FOR PERIOD
kwh = room_data['power'].sum() / 12000 if not room_data.empty and 'power' in room_data.columns else 0
taka = kwh * 8.5  # approx rate
gco2 = kwh * 700   # gCO2 per kWh

col1, col2, col3 = st.columns(3)
col1.metric("Energy Used", f"{kwh:.2f} kWh")
col2.metric("Estimated Cost", f"৳ {taka:.0f}")
col3.metric("Carbon Emission", f"{gco2:,.0f} gCO₂")

# GRAPHS — THREE SEPARATE
if not room_data.empty:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig_p = px.line(room_data, x='timestamp', y='power', title="Power (W)", color_discrete_sequence=["#00d4aa"])
        fig_p.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_p, use_container_width=True)
    
    with col2:
        fig_v = px.line(room_data, x='timestamp', y='voltage', title="Voltage (V)", color_discrete_sequence=["#ffa502"])
        fig_v.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_v, use_container_width=True)
    
    with col3:
        fig_i = px.line(room_data, x='timestamp', y='current', title="Current (A)", color_discrete_sequence=["#ff4757"])
        fig_i.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_i, use_container_width=True)
else:
    st.info("No data available for the selected period.")

# CONTROL PANEL
st.markdown("### Control Panel")
c1, c2, c3 = st.columns(3)

if c1.button("Turn ON", type="primary", use_container_width=True):
    devices_df.loc[devices_df['device_id'] == device['device_id'], 'current_state'] = 'on'
    save(devices_df, "devices.csv")
    st.success("AC Turned ON")
    st.rerun()

if c2.button("Turn OFF", type="primary", use_container_width=True):
    devices_df.loc[devices_df['device_id'] == device['device_id'], 'current_state'] = 'off'
    save(devices_df, "devices.csv")
    st.success("AC Turned OFF")
    st.rerun()

if c3.button("Enable Auto Schedule", use_container_width=True):
    devices_df.loc[devices_df['device_id'] == device['device_id'], 'auto_schedule'] = True
    save(devices_df, "devices.csv")
    st.success("Auto Schedule Enabled")
    st.rerun()

# SCHEDULE EDITOR
with st.expander("Edit Schedule"):
    current_on = device.get('schedule_on', '08:00')
    current_off = device.get('schedule_off', '18:00')
    
    new_on = st.time_input("Turn ON at", value=pd.to_datetime(current_on, format='%H:%M').time())
    new_off = st.time_input("Turn OFF at", value=pd.to_datetime(current_off, format='%H:%M').time())
    
    if st.button("Save Schedule"):
        devices_df.loc[devices_df['device_id'] == device['device_id'], 'schedule_on'] = str(new_on)[:5]
        devices_df.loc[devices_df['device_id'] == device['device_id'], 'schedule_off'] = str(new_off)[:5]
        save(devices_df, "devices.csv")
        st.success("Schedule saved!")
        st.rerun()

st.markdown("---")
st.caption(f"EWU FUB BEMS • Room {room_id} • Data: 01–15 Nov 2025")
