import streamlit as st
import plotly.express as px
from datetime import date, timedelta
from utils import *

st.set_page_config(page_title="EWU FUB BEMS", layout="wide", page_icon="🏢")

st.markdown("""
<style>
    .main {background-color: #0e1117;}
    .metric-card {background: #1e293b; padding: 1.5rem; border-radius: 15px; text-align: center; border: 1px solid #00d4aa44;}
    .room-tile {background: #1e293b; padding: 1.2rem; border-radius: 12px; height: 170px; text-align: center;}
    .room-tile:hover {border-color: #00d4aa; transform: translateY(-5px);}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#00d4aa;'>EWU FUB • Building Energy Management System</h1>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
start_date = col1.date_input("From", date.today() - timedelta(days=7))
end_date = col2.date_input("To", date.today())

period_data = get_period_data(start_date, end_date)
devices = get_devices()
current_readings = {d: get_current_readings(dev) for d, dev in devices.set_index("device_id").iterrows()}
total_power = sum(r["power"] for r in current_readings.values())
total_kwh, total_taka, total_co2 = calculate_stats(period_data)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Live Power", f"{total_power:,.0f} W")
c2.metric("Energy Used", f"{total_kwh} kWh")
c3.metric("Cost", f"৳ {total_taka}")
c4.metric("Carbon", f"{total_co2:,} gCO₂")

st.markdown("### Room Status Monitor")
floors = sorted(get_rooms()['floor'].unique())
tabs = st.tabs([f"Floor {f}" for f in floors])

for floor in floors:
    with tabs[floor-1]:
        rooms = get_rooms()[get_rooms()['floor'] == floor]
        cols = st.columns(4)
        for idx, room in rooms.iterrows():
            with cols[idx % 4]:
                dev = devices[devices['room_id'] == room['room_id']].iloc[0]
                live = current_readings[dev['device_id']]
                period_kwh = period_data[period_data['device_id'] == dev['device_id']]['power'].sum() * (10/60)/1000
                st.markdown(f"""
                <div class="room-tile">
                    <h3 style="color:#00d4aa;">{room.room_name}</h3>
                    <h2 style="color:{'#ff4757' if live['power']>50 else '#2ed573'}">{live['power']:.0f} W</h2>
                    <p>{period_kwh:.2f} kWh • {dev['load_type']} • Auto: {'ON' if dev['auto_schedule'] else 'OFF'}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("View Details", key=f"btn_{room.room_id}", use_container_width=True):
                    st.query_params["room"] = room.room_id
                    st.switch_page("pages/Room_Detail.py")
