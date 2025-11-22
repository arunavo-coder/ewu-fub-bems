# Home.py — FINAL FLOOR TABS + IT vs Non-IT 100% FIXED
import streamlit as st
from datetime import date, timedelta
import plotly.express as px
from utils import *

st.set_page_config(page_title="EWU FUB BEMS", layout="wide")

st.markdown("<h1 style='text-align:center;color:#00d4aa;'>EWU FUB Building Energy Management System</h1>", unsafe_allow_html=True)

# Load data
devices = get_devices()
rooms = devices[['room_id', 'room_name', 'floor']].drop_duplicates().sort_values('floor')
period_data = get_period_data(date(2025,11,1), date(2025,11,15))  # full 2 weeks

# Merge load_type
if not period_data.empty:
    period_data = period_data.merge(devices[['device_id', 'load_type']], on='device_id', how='left')

# TOTAL STATS (whole building)
total_kwh, total_taka, total_gco2 = calculate_stats(period_data)
savings = total_kwh * 0.20

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Energy (2 weeks)", f"{total_kwh:.1f} kWh")
c2.metric("Estimated Cost", f"৳ {total_taka:.0f}")
c3.metric("Carbon Emission", f"{total_gco2:,} gCO₂")
c4.metric("Savings by Schedule", f"{savings:.1f} kWh", "+20%")

# IT vs Non-IT — NOW 100% CORRECT
it_kwh = period_data[period_data['load_type'] == 'IT']['power'].sum() / 12000   # W → kWh
non_it_kwh = period_data[period_data['load_type'] == 'Non-IT']['power'].sum() / 12000

fig = px.pie(
    values=[it_kwh, non_it_kwh],
    names=['IT Loads', 'Non-IT Loads'],
    color_discrete_sequence=['#00d4aa', '#ff4757'],
    hole=0.5
)
fig.update_traces(textinfo='percent+label+value', textposition='inside')
fig.update_layout(title="IT vs Non-IT Energy Consumption (01–15 Nov 2025)", template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# FLOOR TABS — BEAUTIFUL & CLICKABLE
st.markdown("### Select Floor to View Rooms")
floors = sorted(rooms['floor'].unique())
tabs = st.tabs([f"Floor {f}" for f in floors])

for tab, floor in zip(tabs, floors):
    with tab:
        floor_rooms = rooms[rooms['floor'] == floor]
        cols = st.columns(3)
        
        for idx, room in floor_rooms.iterrows():
            with cols[idx % 3]:
                dev = devices[devices['room_id'] == room.room_id].iloc[0]
                live = get_current_readings(dev)
                live_power = live['power']
                
                # 2-week kWh for this room
                room_data = period_data[period_data['device_id'] == dev['device_id']]
                room_kwh = room_data['power'].sum() / 12000 if len(room_data)>0 else 0
                
                st.markdown(f"""
                <div style="background:#1e293b;padding:20px;border-radius:15px;border:2px solid #334155;
                            box-shadow:0 4px 15px rgba(0,212,170,0.2);text-align:center;">
                    <h3 style="color:#00d4aa;margin:8px 0;">{room.room_name}</h3>
                    <p style="font-size:2rem;margin:10px 0;color:{'#ff4757' if live_power>50 else '#2ed573'}">
                        {live_power:.0f} <small>W</small>
                    </p>
                    <p style="color:#888;margin:5px 0;">{room_kwh:.2f} kWh (2 weeks)</p>
                    <p style="color:#00bcd4;font-weight:bold;">{dev['load_type']} Load</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("View Details", key=f"room_{room.room_id}_floor{floor}", use_container_width=True):
                    st.session_state.selected_room = room.room_id
                    st.switch_page("pages/Room_Detail.py")
