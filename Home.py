# Home.py — FINAL, ABSOLUTELY PERFECT VERSION (2025-11-22)
import streamlit as st
from datetime import date, timedelta
import plotly.express as px
from utils import *

st.set_page_config(page_title="EWU FUB BEMS", layout="wide")

# Beautiful Design
st.markdown("""
<style>
    .room-tile {
        background:#1e293b; padding:20px; border-radius:15px; text-align:center;
        border:2px solid #334155; box-shadow:0 4px 15px rgba(0,212,170,0.15);
        transition:all 0.3s;
    }
    .room-tile:hover {border-color:#00d4aa; transform:translateY(-5px);}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;color:#00d4aa;'>EWU FUB Building Energy Management System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#888;font-size:1.1rem;'>Real-time Monitoring • Smart Scheduling • Carbon Tracking • Floor-wise View</p>", unsafe_allow_html=True)

# === DATE RANGE SELECTOR ===
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
    with col1: start_date = st.date_input("From", date.today() - timedelta(days=14))
    with col2: end_date = st.date_input("To", date.today())

# === LOAD DATA ===
devices = get_devices()
# Extract rooms from devices (no separate rooms.csv needed!)
rooms = devices[['room_id', 'room_name', 'floor']].drop_duplicates().sort_values('floor')
period_data = get_period_data(start_date, end_date)

# Merge load_type safely
if not period_data.empty and 'device_id' in period_data.columns:
    period_data = period_data.merge(devices[['device_id', 'load_type']], on='device_id', how='left')

# === TOTAL BUILDING STATS ===
total_kwh, total_taka, total_gco2 = calculate_stats(period_data)
savings = total_kwh * 0.20

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Energy", f"{total_kwh:.1f} kWh", f"{start_date} to {end_date}")
c2.metric("Estimated Cost", f"৳ {total_taka:.0f}")
c3.metric("Carbon Emission", f"{total_gco2:,} gCO₂")
c4.metric("Savings by Schedule", f"{savings:.1f} kWh", "+20%")

# === IT vs NON-IT PIE CHART — 100% FIXED ===
it_kwh = non_it_kwh = 0
if not period_data.empty and 'load_type' in period_data.columns:
    it_data = period_data[period_data['load_type'] == 'IT']
    non_it_data = period_data[period_data['load_type'] == 'Non-IT']
    it_kwh = calculate_stats(it_data)[0] if len(it_data) > 0 else 0
    non_it_kwh = calculate_stats(non_it_data)[0] if len(non_it_data) > 0 else 0

# Force display even if one is zero
fig = px.pie(
    values=[max(it_kwh, 0.01), max(non_it_kwh, 0.01)],
    names=['IT Loads', 'Non-IT Loads'],
    color_discrete_sequence=['#00d4aa', '#ff4757'],
    hole=0.5
)
fig.update_traces(textinfo='percent+label+value', textposition='inside')
fig.update_layout(title="IT vs Non-IT Energy Consumption", template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# === FLOOR TABS — BEAUTIFUL & CLICKABLE ===
st.markdown("### Rooms by Floor")
floors = sorted(rooms['floor'].unique())
tabs = st.tabs([f"Floor {int(f)}" for f in floors])

for tab, floor in zip(tabs, floors):
    with tab:
        floor_rooms = rooms[rooms['floor'] == floor]
        cols = st.columns(3)
        
        for idx, room in floor_rooms.iterrows():
            with cols[idx % 3]:
                dev = devices[devices['room_id'] == room.room_id].iloc[0]
                live = get_current_readings(dev)
                live_power = live['power']
                
                # kWh for this room in selected period
                room_period = period_data[period_data['device_id'] == dev['device_id']]
                room_kwh = calculate_stats(room_period)[0] if len(room_period) > 0 else 0.0
                
                st.markdown(f"""
                <div class="room-tile">
                    <h3 style="color:#00d4aa;margin:5px 0;">{room.room_name}</h3>
                    <p style="font-size:2rem;margin:10px 0;color:{'#ff4757' if live_power>50 else '#2ed573'}">
                        {live_power:.0f} W
                    </p>
                    <p style="color:#888;margin:5px 0;">{room_kwh:.2f} kWh this period</p>
                    <p style="color:#00bcd4;font-weight:bold;margin:5px 0;">
                        {dev['load_type']} • Floor {int(floor)}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("View Details →", key=f"btn_{room.room_id}_floor{floor}", use_container_width=True):
                    st.session_state.selected_room = room.room_id
                    st.switch_page("pages/Room_Detail.py")

# Footer
st.markdown("---")
st.caption("© 2025 EWU FUB BEMS • CSE407 Green Computing • Synthetic Data: 01–15 November 2025")
