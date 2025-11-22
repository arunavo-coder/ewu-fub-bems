# pages/3_About.py
import streamlit as st

st.set_page_config(layout="wide")

# Custom CSS for a stunning About page
st.markdown("""
<style>
    .big-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00d4aa, #0078d4);
        -webkit-background-clip-text: url(#gradient);
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0;
    }
    .subtitle {
        font-size: 1.6rem;
        color: #74b9ff;
        text-align: center;
        margin-top: 10px;
    }
    .card {
        background: linear-gradient(135deg, #1e293b 0%, #111827 100%);
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid #00d4aa44;
        box-shadow: 0 8px 30px rgba(0, 212, 170, 0.2);
        margin: 1rem 0;
    }
    .highlight {
        color: #00d4aa;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='big-title'>EWU FUB BEMS</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Building Energy Management System • CSE407 Green Computing</p>", unsafe_allow_html=True)
st.divider()

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("https://www.ewubd.edu/themes/custom/ewu/logo.png", width=200)
st.markdown("<br>", unsafe_allow_html=True)

# Project Overview
st.markdown("""
<div class="card">
    <h2 style="color:#00d4aa; text-align:center;">Project Overview</h2>
    <p style="font-size:1.2rem; text-align:center;">
        A full-featured <span class="highlight">IoT-based Building Energy Management System (BEMS)</span> designed for 
        <strong>East West University – FUB Building</strong> to monitor, control, and optimize energy consumption using 
        smart scheduling and real-time analytics.
    </p>
</div>
""", unsafe_allow_html=True)

# Features
st.markdown("""
<div class="card">
    <h2 style="color:#74b9ff;">Key Features Implemented</h2>
    <ul style="font-size:1.2rem; line-height:2rem;">
        <li>Real-time monitoring of Voltage, Current, Power (W), Energy (kWh), Cost (৳), Carbon (gCO₂)</li>
        <li>Central dashboard with clickable room tiles across all floors</li>
        <li>Custom date range analytics (daily, weekly, monthly)</li>
        <li>Manual + Scheduled On/Off control with <strong>~20% estimated savings</strong></li>
        <li>IT Load vs Non-IT Load visualization (Bonus Feature)</li>
        <li>Admin panel to add/delete/update rooms and devices (future-proof)</li>
        <li>Synthetic data generated from real AC measurements</li>
        <li>100% Python + Streamlit • Hosted free forever for free</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Team & Course
st.markdown("""
<div class="card">
    <h2 style="color:#fd79a8;">Course Information</h2>
    <p style="font-size:1.2rem;">
        <strong>Course:</strong> CSE407 – Green Computing<br>
        <strong>Assessment:</strong> Midterm Scaling-up Project<br>
        <strong>University:</strong> East West University (EWU), Dhaka<br>
        <strong>Session:</strong> Fall 2025<br>
        <strong>Customer:</strong> EWU Facility Management (FUB Building)
    </p>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; padding:2rem; background:#1e293b; border-radius:15px;">
    <h3 style="color:#00d4aa;">Made with ❤️ using Python & Streamlit</h3>
    <p>Designed & Developed for Sustainable Campus Initiative • EWU 2025</p>
    <p style="color:#888; margin-top:20px;">
        This is a demonstration project • All data is synthetically generated • 
        Ready for real IoT integration with ESP32/Sonoff/Tuya smart plugs
    </p>
</div>
""", unsafe_allow_html=True)

# Back button
if st.button("← Back to Dashboard", use_container_width=True):
    st.switch_page("../Home.py")