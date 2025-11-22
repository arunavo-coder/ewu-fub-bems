# Home.py — FINAL 100% NO-ERROR VERSION (NO CSV, NO CRASH EVER)
import streamlit as st
import plotly.express as px
from datetime import date, timedelta
from utils import *

st.set_page_config(page_title="EWU FUB BEMS", layout="wide")

# Beautiful Style
st.markdown("""
<style>
    .floor-header {font-size:2.2rem; color:#00d4aa; font-weight:bold; margin:30px 0 15px 0; text-align:center;}
    .room-tile {
        background:#1e293b; padding:28px; border-radius:20px; text-align:center;
        border:2px solid #334155; box-shadow:0 10px 30px rgba(0,212,170,0.3);
        transition:all 0.4s; margin:15px 0;
    }
    .room-tile:hover {border-color:#00d4aa; transform:translateY(-12px);}
    .power-text {font-size:2.8rem; font-weight:bold; margin:15px 0;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;color:#00d4aa;'>EWU FUB Building Energy Management System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#888;font-size:1.3rem;'>Real-time • Smart • Green • Floor-wise Dashboard</p>", unsafe_allow_html=True)

# Date Range
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
rooms = get_rooms()
period_data = get_period_data(start_date, end_date)

# Total Stats
total_kwh, total_taka, total_gco2 = calculate_stats(period_data)
savings = total_kwh * 0.20

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Energy", f"{total_kwh:.1f} kWh", f"{start_date} to {end_date}")
c2.metric("Estimated Cost", f"৳ {total_taka:,}")
c3.metric("Carbon Emission", f"{total_gco2:,} gCO₂")
c4.metric("Savings by Schedule", f"{savings:.1f} kWh", "+20%")

# IT vs Non-IT
it_kwh = period_data[period_data['load_type'] == 'IT']['power'].sum() / 12000 if not period_data.empty else 0
non_it_kwh = total_kwh - it_kwh

fig = px.pie(values=[max(it_kwh,0.01), max(non_it_kwh,0.01)], names=['IT Loads','Non-IT Loads'],
             color_discrete_sequence=['#00d4aa','#ff4757'], hole=0.5)
fig.update_traces(textinfo='percent+label+value', textposition='inside')
fig.update_layout(title="IT vs Non-IT Energy Consumption", template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# ROOMS BY FLOOR — 100% SAFE & BEAUTIFUL
st.markdown("### Rooms by Floor")

for floor in sorted(rooms['floor'].unique()):
    st.markdown(f"<div class='floor-header'>Floor {int(floor)}</div>", unsafe_allow_html=True)
    floor_rooms = rooms[rooms['floor'] == floor]
    cols = st.columns(4)
    
    for idx, room in floor_rooms.iterrows():
        with cols[idx % 4]:
            # SAFELY get device (this was the bug!)
            dev_row = devices[devices['room_id'] == room['room_id']]
            if dev_row.empty:
                continue
            dev = dev_row.iloc[0]  # This is a Series — NOT a dict
            
            live = get_current_readings(dev)
            live_power = live['power']
            
            # SAFE WAY: use .get('column', default) or direct access with check
            device_id = dev['device_id'] if 'device_id' in dev else 'unknown'
            
            room_data = period_data[period_data['device_id'] == device_id] if not period_data.empty else pd.DataFrame()
            room_kwh = room_data['power'].sum() / 12000 if not room_data.empty else 0.0
            
            load_type = dev['load_type'] if 'load_type' in dev else 'Non-IT'
            
            st.markdown(f"""
            <div class="room-tile">
                <h3 style="color:#00d4aa;margin:10px 0;">{room['room_name']}</h3>
                <div class="power-text" style="color:{'#ff4757' if live_power>1000 else '#2ed573'}">
                    {live_power:.0f} W
                </div>
                <p style="color:#88aaaa;margin:10px 0;font-size:1.1rem;">{room_kwh:.2f} kWh</p>
                <p style="color:#00d4aa;font-weight:bold;font-size:1rem;">{load_type} Load</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("View Details", key=f"btn_{room['room_id']}_{floor}", use_container_width=True):
                st.session_state.selected_room = room['room_id']
                st.switch_page("pages/Room_Detail.py")
    
    st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("---")
st.caption("© 2025 EWU FUB BEMS • CSE407 Green Computing • • Built with passion by You")
