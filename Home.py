import streamlit as st
from datetime import date, timedelta
from utils import *

st.set_page_config(page_title="EWU FUB BEMS", layout="wide", page_icon="⚡")

st.markdown("""
<style>
    .big-title {font-size: 3.5rem !important; font-weight: 900; text-align: center;
                background: linear-gradient(90deg, #00d4aa, #0078d4);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .metric-card {background: linear-gradient(135deg, #1e293b, #111827); padding: 1.5rem; border-radius: 20px;
                  border: 1px solid #00d4aa44; box-shadow: 0 8px 32px rgba(0,212,170,0.2);}
    .room-tile {background: linear-gradient(135deg, #1e293b, #111827); padding: 1.5rem; border-radius: 20px;
                border: 2px solid transparent; transition: all 0.3s; text-align: center; height: 220px;}
    .room-tile:hover {border-color: #00d4aa; transform: translateY(-10px); box-shadow: 0 20px 40px rgba(0,212,170,0.3);}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='big-title'>EWU FUB • BEMS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#74b9ff; font-size:1.3rem;'>Real-time Monitoring • Smart Scheduling • Carbon Tracking • IT vs Non-IT Analytics</p>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
start_date = col1.date_input("From", date.today()-timedelta(days=7))
end_date = col2.date_input("To", date.today())

data = get_period_data(start_date, end_date)
devices = get_devices()
kwh, taka, co2 = calculate_stats(data)
total_power = sum(get_current_readings(d)["power"] for _, d in devices.iterrows())

c1, c2, c3, c4 = st.columns(4)
c1.markdown(f"<div class='metric-card'><h3>Live Power</h3><h1 style='color:#00d4aa'>{total_power:,.0f} W</h1></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='metric-card'><h3>Energy</h3><h1 style='color:#74b9ff'>{kwh} kWh</h1></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='metric-card'><h3>Cost</h3><h1 style='color:#fd79a8'>৳ {taka}</h1></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='metric-card'><h3>Carbon</h3><h1 style='color:#ff6b6b'>{co2:,} gCO₂</h1></div>", unsafe_allow_html=True)

st.markdown("## Floor-wise Room Monitoring")

for floor in sorted(get_rooms()['floor'].unique()):
    st.markdown(f"### Floor {floor}")
    rooms = get_rooms()[get_rooms()['floor'] == floor]
    cols = st.columns(4)
    for idx, room in enumerate(rooms.itertuples()):
        with cols[idx % 4]:
            dev = devices[devices['room_id'] == room.room_id].iloc[0]
            live = get_current_readings(dev)
            period_kwh = data[data['device_id'] == dev.device_id]['power'].sum() * (10/60) / 1000
            st.markdown(f"""
            <div class='room-tile'>
                <h3 style='color:#00d4aa; margin:0'>{room.room_name}</h3>
                <h2 style='color:{'#ff4757' if live['power']>50 else '#2ed573'}'>{live['power']:.0f} W</h2>
                <p style='margin:8px 0'>{period_kwh:.2f} kWh • {dev.load_type} Load</p>
                <p style='color:#00d4aa'>Auto: {'ON' if dev.auto_schedule else 'OFF'}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View Details", key=f"btn_{room.room_id}", use_container_width=True):
                st.query_params["room"] = room.room_id
                st.switch_page("pages/Room_Detail.py")
