# Home.py
import streamlit as st
import numpy as np
from datetime import date, timedelta
import plotly.express as px
from utils import *

st.set_page_config(page_title="EWU FUB BEMS", layout="wide")

# Beautiful CSS
st.markdown("""
<style>
    .room-tile {
        background: #1e293b;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #334155;
        box-shadow: 0 4px 15px rgba(0,212,170,0.15);
        transition: all 0.3s;
    }
    .room-tile:hover {
        border-color: #00d4aa;
        transform: translateY(-5px);
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 style='text-align:center; color:#00d4aa;'>EWU FUB Building Energy Management System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#888;'>Real-time Monitoring • Smart Scheduling • Carbon Tracking • IT vs Non-IT Analytics</p>", unsafe_allow_html=True)

# Period selector
col1, col2, col3 = st.columns([1,1,1])
with col2:
    period = st.selectbox("Select Period", ["Today", "Last 7 Days", "Last 30 Days", "Custom Range"])

# Set dates correctly
if period == "Today":
    start_date = end_date = date.today()
elif period == "Last 7 Days":
    end_date = date.today()
    start_date = end_date - timedelta(days=6)
elif period == "Last 30 Days":
    end_date = date.today()
    start_date = end_date - timedelta(days=29)
else:  # Custom Range
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", date.today() - timedelta(days=7))
    with col2:
        end_date = st.date_input("To", date.today())

# Load data
rooms = get_rooms()
devices = get_devices()
period_data = get_period_data(start_date, end_date)

# Total stats
total_kwh, total_taka, total_gco2 = calculate_stats(period_data)
savings = total_kwh * 0.20

# Big metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Energy Used", f"{total_kwh:.1f} kWh", f"{start_date} to {end_date}")
c2.metric("Estimated Cost", f"৳ {total_taka:.0f}")
c3.metric("Carbon Emission", f"{total_gco2:,} gCO₂")
c4.metric("Savings by Schedule", f"{savings:.1f} kWh", "+20% reduction")

# IT vs Non-IT Pie Chart – FIXED KeyError
it_data = period_data[period_data['load_type'] == 'IT']
non_it_data = period_data[period_data['load_type'] == 'Non-IT']

it_kwh = calculate_stats(it_data)[0] if len(it_data) > 0 else 0
non_it_kwh = calculate_stats(non_it_data)[0] if len(non_it_data) > 0 else 0

fig = px.pie(
    values=[it_kwh, non_it_kwh],
    names=['IT Loads', 'Non-IT Loads'],
    color_discrete_sequence=['#00d4aa', '#ff4757'],
    hole=0.4
)
fig.update_layout(template="plotly_dark", title="Energy Consumption: IT vs Non-IT")
st.plotly_chart(fig, use_container_width=True)

# Room Tiles
st.markdown("### All Rooms – Click to View Details")
cols = st.columns(3)

for idx, room in rooms.iterrows():
    with cols[idx % 3]:
        dev = devices[devices['room_id'] == room.room_id].iloc[0]
        live = get_current_readings(dev)
        live_power = live['power']
        
        room_period = period_data[period_data['device_id'] == dev['device_id']]
        period_kwh = calculate_stats(room_period)[0] if len(room_period) > 0 else 0.0

        st.markdown(f"""
        <div class="room-tile">
            <h3 style="color:#00d4aa; margin:0;">{room.room_name}</h3>
            <p style="margin:8px 0; font-size:1.6rem; color:{'#ff4757' if live_power>50 else '#2ed573'}">
                {live_power:.0f} W
            </p>
            <p style="color:#888; margin:5px 0;">
                {period_kwh:.2f} kWh • {dev['load_type']} Load
            </p>
            <p style="color:#00d4aa;">
                Auto-schedule: {"ON" if dev['auto_schedule'] else "OFF"}
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("View Details", key=f"btn_{room.room_id}", use_container_width=True):
            st.session_state.selected_room = room.room_id
            st.switch_page("pages/Room_Detail.py")

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; color:#666;'>© 2025 EWU FUB BEMS • CSE407 Green Computing Project</p>", unsafe_allow_html=True)
