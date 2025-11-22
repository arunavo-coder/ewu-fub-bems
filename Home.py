# Home.py
import streamlit as st
import plotly.express as px
from datetime import date, timedelta
from utils import *

# ========================================
# PAGE CONFIG & CUSTOM CSS (PROFESSIONAL LOOK)
# ========================================
st.set_page_config(
    page_title="EWU FUB • BEMS",
    page_icon="building",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional Dark + Green Theme
st.markdown("""
<style>
    .main {background-color: #0e1117; padding: 0;}
    .block-container {padding-top: 2rem;}
    h1 {font-family: 'Segoe UI; color: #00d4aa; text-align: center;}
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #111827 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #00d4aa33;
        box-shadow: 0 4px 15px rgba(0,212,170,0.15);
        text-align: center;
    }
    .room-tile {
        background: #1e293b;
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid #334155;
        transition: all 0.3s;
        height: 160px;
        text-align: center;
    }
    .room-tile:hover {
        transform: translateY(-8px);
        border-color: #00d4aa;
        box-shadow: 0 10px 25px rgba(0,212,170,0.3);
    }
    .status-on {color: #ff4757; font-weight: bold;}
    .status-off {color: #2ed573; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# ========================================
# HEADER
# ========================================
st.markdown("""
<div style="text-align:center; padding:1rem; background:linear-gradient(90deg,#00d4aa,#0078d4); border-radius:15px; margin-bottom:2rem;">
    <h1>East West University – FUB Building</h1>
    <h2 style="color:white; margin-top:-10px;">Building Energy Management System (BEMS)</h2>
    <p style="color:#e0e0e0; font-size:1.1rem;">Real-time Monitoring • Smart Scheduling • Carbon Tracking • IT vs Non-IT Analytics</p>
</div>
""", unsafe_allow_html=True)

# ========================================
# DATE RANGE
# ========================================
col1, col2, col3 = st.columns([2,2,4])
with col1:
    start_date = st.date_input("From", date.today() - timedelta(days=7))
with col2:
    end_date = st.date_input("To", date.today())

period_data = get_period_data(start_date, end_date)
devices = get_devices()
current_readings = {d['device_id']: get_current_readings(d) for _, d in devices.iterrows()}
total_power_now = sum(r['power'] for r in current_readings.values())
total_kwh, total_taka, total_gco2 = calculate_stats(period_data)

# IT vs Non-IT
merged = period_data.merge(devices[['device_id', 'load_type']], on='device_id', how='left')
it_kwh = merged[merged['load_type'] == "IT"]['power'].sum() * (10/60)/1000
non_it_kwh = total_kwh - it_kwh

# ========================================
# TOP METRICS (Beautiful Cards)
# ========================================
st.markdown("### Building Overview", unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color:#00d4aa; margin:0;">Live Power</h3>
        <h2 style="color:white; margin:5px 0;">{total_power_now:,.0f} <small>W</small></h2>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color:#74b9ff; margin:0;">Energy Used</h3>
        <h2 style="color:white; margin:5px 0;">{total_kwh} <small>kWh</small></h2>
        <p style="color:#aaa; margin:0;">{start_date} → {end_date}</p>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color:#fd79a8; margin:0;">Cost</h3>
        <h2 style="color:white; margin:5px 0;">৳ {total_taka}</h2>
    </div>
    """, unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color:#ff7675; margin:0;">Carbon</h3>
        <h2 style="color:white; margin:5px 0;">{total_gco2:,} <small>gCO₂</small></h2>
    </div>
    """, unsafe_allow_html=True)
with c5:
    savings = ((it_kwh + non_it_kwh) - total_kwh) / (it_kwh + non_it_kwh) * 100 if (it_kwh + non_it_kwh) > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color:#55efc4; margin:0;">Savings by Schedule</h3>
        <h2 style="color:white; margin:5px 0;">~{savings:.1f}%</h2>
        <p style="color:#aaa; margin:0;">vs always-on</p>
    </div>
    """, unsafe_allow_html=True)

# ========================================
# IT vs NON-IT PIE CHART
# ========================================
col1, col2 = st.columns([1,1])
with col1:
    fig_pie = px.pie(
        values=[it_kwh, non_it_kwh],
        names=['IT Load', 'Non-IT Load'],
        color_discrete_sequence=['#ff6b6b', '#1dd1a1'],
        hole=0.4
    )
    fig_pie.update_layout(title="Energy Split (kWh)", font=dict(color="white"), paper_bgcolor="#0e1117", title_x=0.5)
    st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

with col2:
    fig_bar = px.bar(
        x=['IT Load', 'Non-IT Load'],
        y=[it_kwh, non_it_kwh],
        text=[f"{it_kwh:.2f} kWh", f"{non_it_kwh:.2f} kWh"],
        color=['IT Load', 'Non-IT Load'],
        color_discrete_sequence=['#ff6b6b', '#1dd1a1']
    )
    fig_bar.update_layout(title="IT vs Non-IT Consumption", font=dict(color="white"), paper_bgcolor="#0e1117", showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

# ========================================
# ROOM TILES BY FLOOR
# ========================================
st.markdown("### Room Status Monitor", unsafe_allow_html=True)

floors = sorted(get_rooms()['floor'].unique())
tabs = st.tabs([f"Floor {f}" for f in floors])

for floor in floors:
    with tabs[floor-1]:
        floor_rooms = get_rooms()[get_rooms()['floor'] == floor]
        cols = st.columns(4)
        for idx, room in floor_rooms.iterrows():
            with cols[idx % 4]:
                dev = devices[devices['room_id'] == room['room_id']].iloc[0]
                live_power = current_readings[dev['device_id']]['power']
                period_kwh = period_data[period_data['device_id'] == dev['device_id']]['power'].sum() * (10/60)/1000
                status = "status-on" if live_power > 50 else "status-off"
                icon = "air conditioner" if live_power > 50 else "air conditioner off"

                st.markdown(f"""
              <div class="room-tile">
    <h3 style="color:#00d4aa; margin:0;">{room.room_name}</h3>
    <p style="margin:8px 0; font-size:1.4rem; color:{'#ff4757' if live_power>50 else '#2ed573'}">
        {live_power:.0f} W
    </p>
    <p style="color:#888; margin:5px 0; font-size:0.95rem;">
        {period_kwh:.2f} kWh • {dev['load_type']} Load
    </p>
    <p style="color:#00d4aa; font-size:0.9rem;">
        Auto-schedule: {"ON" if dev['auto_schedule'] else "OFF"}
    </p>
</div>
                """, unsafe_allow_html=True)

                if st.button("View Details", key=f"btn_{room.room_id}", use_container_width=True):
                    st.query_params["room"] = room.room_id
                    st.switch_page("pages/Room_Detail.py")

# Footer

st.markdown("<br><hr><p style='text-align:center; color:#666;'>CSE407 Green Computing • Midterm Project • EWU FUB BEMS Demo • 2025</p>", unsafe_allow_html=True)

