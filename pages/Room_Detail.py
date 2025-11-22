# pages/1_Room_Detail.py
import streamlit as st
import plotly.express as px
from datetime import date, timedelta
from utils import *

st.set_page_config(layout="wide")
room_id = st.query_params.get("room")
if not room_id:
    st.error("No room selected")
    st.stop()

col1, col2 = st.columns([3,1])
with col1:
    st.title(f"Room {room_id} – Detailed Monitoring")
with col2:
    if st.button("Back to Dashboard"):
        st.switch_page("../Home.py")

start_d = st.date_input("From", date.today()-timedelta(days=7), key="rs")
end_d = st.date_input("To", date.today(), key="re")

room = get_rooms()[get_rooms()['room_id'] == room_id].iloc[0]
device = get_devices()[get_devices()['room_id'] == room_id].iloc[0]
live = get_current_readings(device)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Live Power", f"{live['power']:.1f} W", delta="Live")
c2.metric("Voltage", f"{live['voltage']:.1f} V")
c3.metric("Current", f"{live['current']:.2f} A")
c4.metric("Status", "ON" if live['power']>50 else "OFF")

room_data = get_period_data(start_d, end_d)
room_data = room_data[room_data['device_id'] == device['device_id']]
kwh, taka, gco2 = calculate_stats(room_data)

st.divider()
ca, cb, cc = st.columns(3)
ca.metric("Energy Used", f"{kwh} kWh", f"{start_d} → {end_d}")
cb.metric("Estimated Cost", f"৳ {taka}")
cc.metric("Carbon Emission", f"{gco2:,} gCO₂")

if len(room_data) > 0:
    fig = px.line(room_data, x='timestamp', y='power', title="Power Trend")
    fig.add_scatter(x=room_data['timestamp'], y=room_data['voltage'], name="Voltage", yaxis="y2")
    fig.update_layout(yaxis2=dict(overlaying="y", side="right"))
    st.plotly_chart(fig, use_container_width=True)

# Controls
st.subheader("Control Panel")
col1, col2, col3 = st.columns(3)
if col1.button("Turn ON", type="primary", use_container_width=True):
    get_devices().loc[get_devices()['device_id'] == device['device_id'], ['current_state','auto_schedule']] = ["on", False]
    save(get_devices(), "devices.csv")
    st.success("AC Turned ON"); st.rerun()
if col2.button("Turn OFF", type="primary", use_container_width=True):
    get_devices().loc[get_devices()['device_id'] == device['device_id'], ['current_state','auto_schedule']] = ["off", False]
    save(get_devices(), "devices.csv")
    st.success("AC Turned OFF"); st.rerun()
if col3.button("Enable Auto Schedule", use_container_width=True):
    get_devices().loc[get_devices()['device_id'] == device['device_id'], 'auto_schedule'] = True
    save(get_devices(), "devices.csv")
    st.success("Auto scheduling enabled"); st.rerun()

with st.expander("Edit Schedule"):
    on = st.time_input("ON", value=datetime.strptime(device['schedule_on'], '%H:%M'))
    off = st.time_input("OFF", value=datetime.strptime(device['schedule_off'], '%H:%M'))
    if st.button("Save Schedule"):
        get_devices().loc[get_devices()['device_id'] == device['device_id'], ['schedule_on','schedule_off']] = [on.strftime('%H:%M'), off.strftime('%H:%M')]
        save(get_devices(), "devices.csv")
        st.success("Updated!"); st.rerun()