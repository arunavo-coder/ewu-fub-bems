import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True, exist_ok=True)

RATE = 7.8
CO2_PER_KWH = 620

def save(df, name):
    df.to_csv(f"{DATA_DIR}/{name}", index=False)

def load(name, cols, defaults=None):
    path = f"{DATA_DIR}/{name}"
    if os.path.exists(path):
        df = pd.read_csv(path)
        for c = set(cols)
        for col in c - set(df.columns):
            df[col] = None
        return df[list(c)]
    else:
        df = pd.DataFrame(columns=cols)
        if defaults:
            df = pd.concat([df, pd.DataFrame(defaults)], ignore_index=True)
        save(df, name)
        return df

# ROOMS
def get_rooms():
    return load("rooms.csv", ["room_id","floor","room_name","room_type"], [
        {"room_id":"101","floor":1,"room_name":"Classroom 101","room_type":"Classroom"},
        {"room_id":"102","floor":1,"room_name":"Classroom 102","room_type":"Classroom"},
        {"room_id":"103","floor":1,"room_name":"Computer Lab 103","room_type":"IT Lab"},
        {"room_id":"201","floor":2,"room_name":"Digital Lab 202","room_type":"IT Lab"},
        {"room_id":"305","floor":3,"room_name":"Classroom 305","room_type":"Classroom"},
        {"room_id":"501","floor":5,"room_name":"Server Room 501","room_type":"IT Lab"},
    ])

# DEVICES
def get_devices():
    defaults = []
    for _, r in get_rooms().iterrows():
        defaults.append({
            "device_id": f"AC-{r.room_id}",
            "room_id": r.room_id,
            "name": "Air Conditioner",
            "load_type": "IT" if "IT" in r.room_type else "Non-IT",
            "current_state": "off",
            "auto_schedule": True,
            "schedule_on": "08:00",
            "schedule_off": "18:00",
            "mean_power": np.random.randint(1300, 1700)
        })
    return load("devices.csv", ["device_id","room_id","name","load_type","current_state","auto_schedule","schedule_on","schedule_off","mean_power"], defaults)

# MEASUREMENTS + SYNTHETIC DATA
def generate_data():
    devices = get_devices()
    data = []
    start = datetime.now() - timedelta(days=15)
    for ts in pd.date_range(start, datetime.now(), freq="10min"):
        for _, dev in devices.iterrows():
            on = datetime.strptime(dev.schedule_on, "%H:%M").time()
            off = datetime.strptime(dev.schedule_off, "%H:%M").time()
            t = ts.time()
            scheduled = (on <= t < off) if on < off else (t >= on or t < off)
            state = "on" if (dev.auto_schedule and scheduled) or dev.current_state=="on" else "off"
            power = np.random.normal(dev.mean_power, 180) if state=="on" else 0
            power = max(0, power)
            data.append({"timestamp": ts, "device_id": dev.device_id, "power": round(power,1)})
    df = pd.DataFrame(data)
    save(df, "measurements.csv")
    return df

def get_measurements():
    if not os.path.exists(f"{DATA_DIR}/measurements.csv"):
        return generate_data()
    df = pd.read_csv(f"{DATA_DIR}/measurements.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

# CURRENT READING
def get_live_power(dev):
    now = datetime.now().time()
    on = datetime.strptime(dev.schedule_on, "%H:%M").time()
    off = datetime.strptime(dev.schedule_off, "%H:%M").time()
    scheduled = (on <= now < off) if on < off else (now >= on or now < off)
    state = "on" if (dev.auto_schedule and scheduled) or dev.current_state=="on" else "off"
    power = np.random.normal(dev.mean_power, 180) if state=="on" else 0
    return round(max(0, power), 1)

def get_period_stats(start_date, end_date):
    df = get_measurements()
    mask = (df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)
    period = df[mask]
    kwh = period['power'].sum() * 10 / 6000
    cost = round(kwh * RATE, 1)
    co2 = int(kwh * CO2_PER_KWH)
    return kwh, cost, co2, period
