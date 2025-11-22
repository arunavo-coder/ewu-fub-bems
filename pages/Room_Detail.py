import streamlit as st
import plotly.express as px
from datetime import date, timedelta
from utils import *

st.set_page_config(layout="wide")

# THIS IS THE ONLY CORRECT WAY IN LATEST STREAMLIT
if "room" not in st.query_params:
    st.error("No room selected")
    st.stop()

room_id = st.query_params["room"]
room = get_rooms()[get_rooms().room_id == room_id].iloc[0]
device = get_devices()[get_devices().room_id == room_id].iloc[0]
live_power = get_live_power(device)

col1, col2 = st.columns([4,1])
with col1:
    st.title(f"{room.room_name}")
with col2:
    if st.button("← Dashboard"):
        st.switch_page("../Home.py")

start = st.date_input("From", date.today()-timedelta(days=7), key="rd1")
end = st.date_input("To", date.today(), key="rd2")

_, _, _, data = get_period_stats(start, end)
room_data = data[data.device_id == device.device_id].copy()
room_data['hour'] = room_data.timestamp.dt.strftime('%m/%d %H:%M')

kwh = room_data['power'].sum() *10/6000

c1,c2,c3 = st.columns(3)
c1.metric("Live Power", f"{live_power:.0f} W", delta="Realtime")
c2.metric("Period Energy", f"{kwh:.2f} kWh")
c3.metric("Status", "ON" if live_power>50 else "OFF")

if len(room_data)>0:
    fig = px.line(room_data, x='timestamp', y='power', title="Power Consumption Over Time")
    fig.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data in selected period")

st.subheader("Controls")
b1,b2,b3 = st.columns(3)
if b1.button("Turn ON", type="primary", use_container_width=True):
    get_devices().loc[get_devices().device_id == device.device_id, ['current_state','auto_schedule']] = ["on", False]
    save(get_devices(), "devices.csv")
    st.success("Turned ON"); st.rerun()
if b2.button("Turn OFF", type="primary", use_container_width=True):
    get_devices().loc[get_devices().device_id == device.device_id, ['current_state','auto_schedule']] = ["off", False]
    save(get_devices(), "devices.csv")
    st.success("Turned OFF"); st.rerun()
if b3.button("Enable Auto-Schedule", use_container_width=True):
    get_devices().loc[get_devices().device_id == device.device_id, 'auto_schedule'] = True
    save(get_devices(), "devices.csv")
    st.rerun()
