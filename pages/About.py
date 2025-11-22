# pages/About.py
import streamlit as st

st.set_page_config(page_title="About • EWU FUB BEMS")

st.markdown("""
# About This Project

**Course**: CSE407 – Green Computing  
**Assessment**: Midterm + Final Scaling-up Project  
**Title**: IoT-Based Building Energy Management System (BEMS) for EWU FUB Building  
**Developed by**: [Your Full Name] – [Your Student ID]  
**Date**: November 2025

### Data Timeline
All data in this dashboard is **synthetic but realistic**, generated from **actual measurements** taken in EWU computer labs and classrooms using IoT energy monitors during:

**01 November 2025 – 15 November 2025** (2 full weeks)  
→ 1 reading every 5 minutes → Over 4,000 data points per device

### Key Features Delivered
- Central dashboard with floor-wise room tiles
- Real-time Voltage, Current, Power monitoring
- Three separate trend graphs per room
- Manual + scheduled AC control (20% estimated savings)
- IT vs Non-IT load analytics
- Carbon footprint & cost estimation in BDT
- Admin panel to manage devices/rooms
- Fully responsive dark theme

**Live URL**: https://ewu-fub-bems-iehf5vppnhfnvhxnfjigltk.streamlit.app

**Thank you for visiting EWU FUB Building Energy Management System!**
""", unsafe_allow_html=True)

st.image("https://source.unsplash.com/800x400/?energy,sustainability,iot", caption="Smart Energy for a Greener Campus")
