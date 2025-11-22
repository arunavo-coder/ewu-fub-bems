# pages/Room_Detail.py — FINAL WITH 3 GRAPHS
import streamlit as st
import plotly.express as px
from datetime import date, timedelta, datetime
from utils import *

st.set_page_config(layout="wide")

# Reliable room selection
if "selected_room" not in st.session_state:
    st.error("No room selected"); st.stop()
room_id = st.session_state.selected_room

room = get_rooms()[get_rooms()['room_id'] == room_id].iloc[0]
device = get_devices()[get_devices()['room_id'] == room_id].iloc[0]
live = get_current_readings(device)

col1, col2 = st.columns([3,1])
with col1:
    st.title(f"{room.room_name} – Room {room_id}")
with col2:
    if st.button("Back to Dashboard"):
        if "selected_room" in st.session_state:
            del st.session_state.selected_room
        st.switch_page("Home.py")

start_d = st.date_input("From", date.today()-timedelta(days=7), key="rs")
end_d = st.date_input("To", date.today(), key="re")
room_data = get_period_data(start_d, end_d)
room_data = room_data[room_data['device_id'] == device['device_id']]

# Live metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Live Power", f"{live['power']:.1f} W", "Live")
c2.metric("Voltage", f"{live['voltage']:.1f} V")
c3.metric("Current", f"{live['current']:.2f} A")
c4.metric("Status", "ON" if live['power']>50 else "OFF")

kwh, taka, gco2 = calculate_stats(room_data)
st.divider()
ca, cb, cc = st.columns(3)
ca.metric("Energy Used", f"{kwh:.2f} kWh")
cb.metric("Estimated Cost", f"৳ {taka:.1f}")
cc.metric("Carbon Emission", f"{gco2:,} gCO₂")

# THREE SEPARATE GRAPHS — LOOKS PROFESSIONAL
if len(room_data) > 0:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig_p = px.line(room_data, x='timestamp', y='power', title="Power Trend (W)",
                        color_discrete_sequence=["#00d4aa"])
        fig_p.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_p, use_container_width=True)
    
    with col2:
        fig_v = px.line(room_data, x='timestamp', y='voltage', title="Voltage Trend (V)",
                        color_discrete_sequence=["#ffa502"])
        fig_v.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_v, use_container_width=True)
    
    with col3:
        fig_i = px.line(room_data, x='timestamp', y='current', title="Current Trend (A)",
                        color_discrete_sequence=["#ff4757"])
        fig_i.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_i, use_container_width=True)
else:
    st.info("No data in selected period")

# Control Panel (same as before — already perfect)
st.markdown("### Control Panel")
c1, c2, c3 = st.columns(3)
if c1.button("Turn ON", type="primary", use_container_width=True):
    df = get_devices()
    df.loc[df['device_id'] == device['device_id'], ['current_state','auto_schedule']] = ["on", False]
    save(df, "devices.csv")
    st.success("AC Turned ON"); st.rerun()
if c2.button("Turn OFF", type="primary", use_container_width=True):
    df = get_devices()
    df.loc[df['device_id'] == device['device_id'], ['current_state','auto_schedule']] = ["off", False]
    save(df, "devices.csv")
    st.success("AC Turned OFF"); st.rerun()
if c3.button("Enable Auto Schedule", use_container_width=True):
    df = get_devices()
    df.loc[df['device_id'] == device['device_id'], 'auto_schedule'] = True
    save(df, "devices.csv")
    st.success("Auto Schedule ON"); st.rerun()

with st.expander("Edit Schedule"):
    on = st.time_input("ON Time", value=datetime.strptime(device['schedule_on'], '%H:%M').time())
    off = st.time_input("OFF Time", value=datetime.strptime(device['schedule_off'], '%H:%M').time())
    if st.button("Save Schedule"):
        df = get_devices()
        df.loc[df['device_id'] == device['device_id'], ['schedule_on','schedule_off']] = [str(on)[:5], str(off)[:5]]
        save(df, "devices.csv")
        st.success("Schedule saved!"); st.rerun()
