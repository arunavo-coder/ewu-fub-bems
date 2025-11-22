# utils.py — FINAL 100% WORKING VERSION
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# CACHE EVERYTHING
@st.cache_data(ttl=60)
def load_csv(filename):
    try:
        return pd.read_csv(filename)
    except:
        st.error(f"Missing {filename} — upload it in Streamlit Cloud → Files")
        st.stop()

@st.cache_data(ttl=60)
def get_devices():
    df = load_csv("devices.csv")
    # FORCE REQUIRED COLUMNS
    if 'room_id' not in df.columns:
        st.error("devices.csv must have 'room_id' column")
        st.stop()
    if 'room_name' not in df.columns:
        df['room_name'] = "Room " + df['room_id'].astype(str)
    if 'load_type' not in df.columns:
        df['load_type'] = df['room_name'].apply(lambda x: 'IT' if 'Lab' in str(x) else 'Non-IT')
    if 'floor' not in df.columns:
        df['floor'] = ((df.index // 4) % 7) + 1
    if 'device_id' not in df.columns:
        df['device_id'] = "D" + df.index.astype(str).str.zfill(3)
    return df

@st.cache_data(ttl=60)
def get_readings():
    return load_csv("readings.csv")

# THIS IS THE KEY FIX — ROOMS COME FROM DEVICES, NOT A SEPARATE FILE
@st.cache_data(ttl=60)
def get_rooms():
    devices = get_devices()
    rooms = devices[['room_id', 'room_name', 'floor']].drop_duplicates().reset_index(drop=True)
    return rooms

@st.cache_data(ttl=300)
def get_period_data(start_date, end_date):
    df = get_readings()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    mask = (df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)
    return df.loc[mask]

def get_current_readings(device):
    # Simulate live reading (replace with real IoT later)
    import random
    base = 1200 if device.get('current_state', 'off') == 'on' else 0
    power = base + random.randint(-150, 200)
    return {
        'power': max(power, 0),
        'voltage': 220 + random.randint(-10, 10),
        'current': round(power / 220, 2) if power > 0 else 0
    }

def calculate_stats(data):
    if data.empty or 'power' not in data.columns:
        return 0, 0, 0
    kwh = data['power'].sum() / 12000
    taka = kwh * 8.5
    gco2 = kwh * 700
    return round(kwh, 2), round(taka), int(gco2)

def save(df, filename):
    df.to_csv(filename, index=False)
