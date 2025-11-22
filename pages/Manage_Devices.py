# pages/2_Manage_Devices.py
import streamlit as st
from utils import *

st.title("Manage Rooms & Devices")

tab1, tab2 = st.tabs(["Rooms", "Devices"])

with tab1:
    rooms = get_rooms()
    edited = st.data_editor(rooms, num_rows="dynamic", use_container_width=True)
    if st.button("Save Changes to Rooms"):
        save(edited, "rooms.csv")
        st.success("Rooms updated!")

with tab2:
    devices = get_devices()
    edited = st.data_editor(devices, num_rows="dynamic", use_container_width=True)
    if st.button("Save Changes to Devices"):
        save(edited, "devices.csv")
        st.success("Devices updated!")
        st.rerun()