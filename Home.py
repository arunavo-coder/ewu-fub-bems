# Home.py — FINAL PERFECT VERSION WITH FLOORS
import streamlit as st
from datetime import date, timedelta
import plotly.express as px
from utils import *

st.set_page_config(page_title="EWU FUB BEMS", layout="wide")

st.markdown("""
<style>
    .room-tile {background:#1e293b;padding:20px;border-radius:15px;border:2px solid #334155;
                box-shadow:0 4px 15px rgba(0,212,170,0.15);transition:all 0.3s;}
    .room-tile:hover {border-color:#00d4aa;transform:translateY(-5px);}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;color:#00d4aa;'>EWU FUB Building Energy Management System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#888;'>Real-time Monitoring • Smart Scheduling • Carbon Tracking • Floor-wise View</p>", unsafe_allow_html=True)

# Period selector
col1, col2, col3 = st.columns([1,1,1])
with col2:
    period = st.selectbox("Select Period", ["Today", "Last 7 Days", "Last 30 Days", "Custom Range"])

if period == "Today":
    start_date = end_date = date.today()
elif period == "Last 7 Days":
    end_date = date.today(); start_date = end_date - timedelta(days=6)
elif period == "Last 30 Days":
    end_date = date.today(); start_date = end_date - timedelta(days=29)
else:
    col1, col2 = st.columns(2)
    with col1: start_date = st.date_input("From", date.today()-timedelta(days=14))
    with col2: end_date = st.date_input("To", date.today())

# Load data
rooms = get_rooms()
devices = get_devices()
period_data = get_period_data(start_date, end_date)

# Merge load_type
if not period_data.empty:
    period_data = period_data.merge(devices[['device_id', 'load_type', 'room_id']], on='device_id', how='left')

# FLOOR SELECTOR
st.markdown("### Select Floor")
floor_options = ["All Floors"] + sorted(rooms['floor'].astype(str).unique().tolist())
selected_floor = st.selectbox("Floor", floor_options, key="floor_select")

if selected_floor != "All Floors":
    rooms = rooms[rooms['floor'].astype(str) == selected_floor]

# Total stats
total_kwh, total_taka, total_gco2 = calculate_stats(period_data)
savings = total_kwh * 0.20

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Energy", f"{total_kwh:.1f} kWh", f"{start_date} to {end_date}")
c2.metric("Estimated Cost", f"৳ {total_taka:.0f}")
c3.metric("Carbon Emission", f"{total_gco2:,} gCO₂")
c4.metric("Savings by Schedule", f"{savings:.1f} kWh", "+20%")

# IT vs Non-IT Chart
it_kwh = non_it_kwh = 0
if not period_data.empty and 'load_type' in period_data.columns:
    it_kwh = calculate_stats(period_data[period_data['load_type'] == 'IT'])[0]
    non_it_kwh = calculate_stats(period_data[period_data['load_type'] == 'Non-IT'])[0]

fig = px.pie(values=[it_kwh+0.01, non_it_kwh+0.01], names=['IT Loads', 'Non-IT Loads'],
             color_discrete_sequence=['#00d4aa', '#ff4757'], hole=0.5)
fig.update_traces(textinfo='percent+label')
fig.update_layout(title="IT vs Non-IT Energy Consumption", template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# Room Tiles
st.markdown(f"### Floor {selected_floor} – All Rooms")
cols = st.columns(3)
for idx, room in rooms.iterrows():
    with cols[idx % 3]:
        dev = devices[devices['room_id'] == room.room_id].iloc[0]
        live = get_current_readings(dev)
        live_power = live['power']
        room_period = period_data[period_data['device_id'] == dev['device_id']]
        period_kwh = calculate_stats(room_period)[0] if len(room_period)>0 else 0.0

        st.markdown(f"""
        <div class="room-tile">
            <h3 style="color:#00d4aa;margin:0;">{room.room_name}</h3>
            <p style="margin:8px 0;font-size:1.8rem;color:{'#ff4757' if live_power>50 else '#2ed573'}">
                {live_power:.0f} W
            </p>
            <p style="color:#888;">{period_kwh:.2f} kWh • {dev['load_type']} • Floor {room['floor']}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("View Details", key=f"btn_{room.room_id}", use_container_width=True):
            st.session_state.selected_room = room.room_id
            st.switch_page("pages/Room_Detail.py")

st.markdown("---")
st.caption("© 2025 EWU FUB BEMS • CSE407 Green Computing • Data: 01–15 Nov 2025")
