import streamlit as st
from utils import *

st.set_page_config(layout="wide")

if "room" not in st.query_params:
    st.error("No room selected")
    st.stop()

room_id = st.query_params["room"]
room = get_rooms()[get_rooms()['room_id'] == room_id].iloc[0]
device = get_devices()[get_devices()['room_id'] == room_id].iloc[0]
live = get_current_readings(device)

st.title(f"Room {room_id} • {room.room_name}")
col1, col2, col3 = st.columns(3)
col1.metric("Live Power", f"{live['power']:.0f} W")
col2.metric("Status", "ON" if live['power'] > 50 else "OFF")
col3.metric("Auto Schedule", "ON" if device['auto_schedule'] else "OFF")

if st.button("← Back to Dashboard"):
    st.switch_page("../Home.py")
