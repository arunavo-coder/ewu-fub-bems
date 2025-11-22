import streamlit as st
from datetime import date, timedelta
from utils import *

st.set_page_config(page_title="EWU FUB BEMS", layout="wide", page_icon="⚡")

st.markdown("""
<style>
    .big{font-size:3.5rem !important; font-weight:900; text-align:center;
          background:-webkit-linear-gradient(#00d4aa, #0078d4);
          -webkit-background-clip:text; -webkit-text-fill-color:transparent;}
    .card{background:linear-gradient(135deg,#1e293b,#111827);padding:1.5rem;border-radius:15px;
          border:1px solid #00d4aa33; text-align:center;}
    .tile{background:linear-gradient(135deg,#1e293b,#111827);padding:1.8rem;border-radius:18px;
          border:2px solid transparent; transition:0.3s; text-align:center;}
    .tile:hover{border-color:#00d4aa; transform:translateY(-8px);}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='big'>EWU FUB • BEMS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#74b9ff;font-size:1.3rem;'>Real-time • Scheduling • Carbon • IT vs Non-IT</p>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
start = col1.date_input("From", date.today()-timedelta(days=7))
end = col2.date_input("To", date.today())

kwh, cost, co2, period_data = get_period_stats(start, end)
total_live = sum(get_live_power(d) for _, d in get_devices().iterrows())

c1,c2,c3,c4 = st.columns(4)
c1.markdown(f"<div class='card'><h4>Live Power</h4><h1 style='color:#00d4aa'>{total_live:,.0f} W</h1></div>",True)
c2.markdown(f"<div class='card'><h4>Energy</h4><h1 style='color:#74b9ff'>{kwh:.2f} kWh</h1></div>",True)
c3.markdown(f"<div class='card'><h4>Cost</h4><h1 style='color:#fd79a8'>৳ {cost}</h1></div>",True)
c4.markdown(f"<div class='card'><h4>Carbon</h4><h1 style='color:#ff6b6b'>{co2:,} gCO₂</h1></div>",True)

st.markdown("## Floor-wise Monitoring")
for floor in sorted(get_rooms().floor.unique()):
    st.subheader(f"Floor {floor}")
    rooms = get_rooms()[get_rooms().floor == floor]
    cols = st.columns(4)
    for i, r in enumerate(rooms.itertuples()):
        with cols[i%4]:
            dev = get_devices()[get_devices().room_id == r.room_id].iloc[0]
            power = get_live_power(dev)
            kwh_room = period_data[period_data.device_id == dev.device_id]['power'].sum() *10/6000
            st.markdown(f"""
            <div class='tile'>
                <h4 style='color:#00d4aa'>{r.room_name}</h4>
                <h2 style='color:{'#ff4757' if power>50 else '#2ed573'}'>{power:.0f} W</h2>
                <p>{kwh_room:.2f} kWh • {dev.load_type}</p>
                <p style='color:#00d4aa'><b>Auto: {'ON' if dev.auto_schedule else 'OFF'}</b></p>
            </div>
            """, True)
            if st.button("View Details", key=r.room_id, use_container_width=True):
                st.query_params["room"] = r.room_id
                st.switch_page("pages/room_detail.py")

