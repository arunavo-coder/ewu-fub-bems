# Home.py — FINAL PROFESSIONAL VERSION (Clean Floor Layout + Real Floor Numbers)
import streamlit as st
from datetime import date, timedelta
import plotly.express as px
from utils import *

st.set_page_config(page_title="EWU FUB BEMS", layout="wide")

# Beautiful Design
st.markdown("""
<style>
    .floor-header {font-size:1.8rem; color:#00d4aa; font-weight:bold; margin:20px 0 10px 0;}
    .room-tile {
        background:#1e293b; padding:22px; border-radius:16px; text-align:center;
        border:2px solid #334155; box-shadow:0 6px 20px rgba(0,212,170,0.2);
        transition:all 0.3s; margin:12px 0;
    }
    .room-tile:hover {border-color:#00d4aa; transform:translateY(-8px); box-shadow:0 12px 30px rgba(0,212,170,0.3);}
    .power-text {font-size:2.4rem; font-weight:bold; margin:12px 0;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;color:#00d4aa;'>EWU FUB Building Energy Management System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#888;'>Real-time Monitoring • Smart Scheduling • Floor-wise Dashboard</p>", unsafe_allow_html=True)

# Date Selector
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

# Load Data
devices = get_devices()

# ENSURE COLUMNS EXIST
if 'room_name' not in devices.columns:
    devices['room_name'] = devices['room_id'].str.replace('R', 'Room ')
if 'load_type' not in devices.columns:
    devices['load_type'] = ['IT' if 'Lab' in name else 'Non-IT' for name in devices['room_name']]
if 'floor' not in devices.columns:
    # REAL FLOOR ASSIGNMENT: Floor 1 to 7 (you can edit this list)
    floor_map = {
        'R001':1, 'R002':1, 'R003':1, 'R004':1,
        'R005':2, 'R006':2, 'R007':2, 'R008':2,
        'R009':3, 'R010':3, 'R011':3,
        'R012':4, 'R013':4, 'R014':4, 'R015':4,
        'R016':5, 'R017':5, 'R018':5,
        'R019':6, 'R020':6,
        'R021':7
    }
    devices['floor'] = devices['room_id'].map(floor_map).fillna(4)

# Create rooms list
rooms = devices[['room_id', 'room_name', 'floor']].drop_duplicates().sort_values(['floor', 'room_id'])

# Load period data
period_data = get_period_data(start_date, end_date)
if not period_data.empty and 'device_id' in period_data.columns:
    period_data = period_data.merge(devices[['device_id', 'load_type']], on='device_id', how='left')
    period_data['load_type'] = period_data['load_type'].fillna('Non-IT')

# Total Stats
total_kwh, total_taka, total_gco2 = calculate_stats(period_data)
savings = total_kwh * 0.20

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Energy", f"{total_kwh:.1f} kWh", f"{start_date} to {end_date}")
c2.metric("Estimated Cost", f"৳ {total_taka:.0f}")
c3.metric("Carbon Emission", f"{total_gco2:,} gCO₂")
c4.metric("Savings by Schedule", f"{savings:.1f} kWh", "+20%")

# IT vs Non-IT
it_kwh = period_data[period_data['load_type'] == 'IT']['power'].sum() / 12000 if not period_data.empty else 0
non_it_kwh = period_data[period_data['load_type'] != 'IT']['power'].sum() / 12000 if not period_data.empty else 0

fig = px.pie(values=[max(it_kwh,0.01), max(non_it_kwh,0.01)], names=['IT Loads','Non-IT Loads'],
             color_discrete_sequence=['#00d4aa','#ff4757'], hole=0.5)
fig.update_traces(textinfo='percent+label+value', textposition='inside')
fig.update_layout(title="IT vs Non-IT Energy Consumption", template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# FLOOR-WISE ROOMS — CLEAN & ORGANIZED
st.markdown("### Rooms by Floor")

for floor in sorted(rooms['floor'].unique()):
    st.markdown(f"<div class='floor-header'>Floor {int(floor)}</div>", unsafe_allow_html=True)
    floor_rooms = rooms[rooms['floor'] == floor]
    cols = st.columns(4)  # 4 rooms per row = clean grid
    
    for idx, room in enumerate(floor_rooms.itertuples()):
        with cols[idx % 4]:
            dev = devices[devices['room_id'] == room.room_id].iloc[0]
            live = get_current_readings(dev)
            live_power = live.get('power', 0)
            
            room_data = period_data[period_data['device_id'] == dev['device_id']]
            room_kwh = room_data['power'].sum() / 12000 if len(room_data) > 0 else 0.0
            
            st.markdown(f"""
            <div class="room-tile">
                <h3 style="color:#00d4aa;margin:8px 0;">{room.room_name}</h3>
                <div class="power-text" style="color:{'#ff4757' if live_power>1000 else '#2ed573'}">
                    {live_power:.0f} W
                </div>
                <p style="color:#889;color:#00bcd4;font-size:1rem;margin:8px 0;">
                    {room_kwh:.2f} kWh
                </p>
                <p style="color:#00d4aa;font-weight:bold;">
                    {dev.get('load_type','Non-IT')} Load
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("View Details", key=f"btn_{room.room_id}_floor{floor}", use_container_width=True):
                st.session_state.selected_room = room.room_id
                st.switch_page("pages/Room_Detail.py")
    
    st.markdown("<br>", unsafe_allow_html=True)  # spacing between floors

st.markdown("---")
st.caption("© 2025 EWU FUB Building Energy Management System • CSE407 Green Computing • Data: 01–15 Nov 2025")
