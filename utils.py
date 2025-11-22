# utils.py — 100% STANDALONE (NO CSV FILES NEEDED)
import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

# BUILT-IN DEVICES (NO devices.csv NEEDED)
@st.cache_data
def get_devices():
    data = {
        'device_id': [f"D{i:03d}" for i in range(1, 16)],
        'room_id': ['R101','R102','R103','R104','R201','R202','R203','R204','R301','R302','R401','R402','R403','R501','R502'],
        'room_name': ['Lab 101','Lab 102','Lab 103','Classroom 104','Lab 201','Lab 202','Lab 203','Classroom 204',
                      'Lab 301','Lab 302','Lab 401','Lab 402','Classroom 403','Faculty Room 501','Meeting Room 502'],
        'load_type': ['IT','IT','IT','Non-IT','IT','IT','IT','Non-IT','IT','IT','IT','IT','Non-IT','Non-IT','Non-IT'],
        'floor': [1,1,1,1,2,2,2,2,3,3,4,4,4,5,5],
        'current_state': ['on','on','off','on','on','on','off','on','on','on','on','on','off','on','off'],
        'auto_schedule': [True,True,False,True,True,True,False,True,True,True,True,True,True,True,False],
        'schedule_on': ['08:00']*15,
        'schedule_off': ['20:00','20:00','18:00','16:00','21:00','21:00','19:00','17:00','20:00','20:00','22:00','22:00','16:00','17:00','18:00']
    }
    return pd.DataFrame(data)

# BUILT-IN ROOMS
@st.cache_data
def get_rooms():
    devices = get_devices()
    return devices[['room_id', 'room_name', 'floor']].drop_duplicates().reset_index(drop=True)

# GENERATE FAKE READINGS (NO readings.csv NEEDED)
@st.cache_data(ttl=300)
def get_period_data(start_date, end_date):
    devices = get_devices()
    dates = pd.date_range(start=f"2025-11-01", end=f"2025-11-15", freq='5min')
    rows = []
    
    for _, dev in devices.iterrows():
        base_power = 1500 if dev['current_state'] == 'on' else 0
        for ts in dates:
            if start_date <= ts.date() <= end_date:
                power = max(0, base_power + random.randint(-300, 400))
                rows.append({
                    'timestamp': ts,
                    'device_id': dev['device_id'],
                    'power': power,
                    'voltage': 220 + random.randint(-15, 15),
                    'current': round(power / 220, 2) if power > 0 else 0
                })
    
    return pd.DataFrame(rows)

# LIVE READING SIMULATION
def get_current_readings(device):
    base = 1500 if device['current_state'] == 'on' else 0
    power = max(0, base + random.randint(-200, 300))
    return {
        'power': power,
        'voltage': 220 + random.randint(-10, 10),
        'current': round(power / 220, 2) if power > 0 else 0
    }

# STATS
def calculate_stats(data):
    if data.empty or 'power' not in data.columns:
        return 0, 0, 0
    kwh = data['power'].sum() / 12000
    taka = kwh * 8.5
    gco2 = kwh * 700
    return round(kwh, 2), round(taka), int(gco2)

# SAVE (FAKE — JUST FOR UI)
def save(df, filename):
    pass  # No file system, but buttons still work
