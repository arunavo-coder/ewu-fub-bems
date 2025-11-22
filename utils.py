import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

RATE_TAKA_PER_KWH = 7.8
CO2_G_PER_KWH = 620

def load(filename, columns, defaults=None):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        df = pd.read_csv(path)
        for col in columns:
            if col not in df.columns:
                df[col] = np.nan
        return df[columns]
    else:
        df = pd.DataFrame(columns=columns)
        if defaults:
            df = pd.concat([df, pd.DataFrame(defaults)], ignore_index=True)
        df.to_csv(path, index=False)
        return df

def save(df, filename):
    df.to_csv(os.path.join(DATA_DIR, filename), index=False)

def get_rooms():
    return load("rooms.csv", ["room_id","floor","room_name","room_type"], defaults=[
        {"room_id":"101","floor":1,"room_name":"Classroom 101","room_type":"Classroom"},
        {"room_id":"102","floor":1,"room_name":"Classroom 102","room_type":"Classroom"},
        {"room_id":"103","floor":1,"room_name":"Computer Lab 103","room_type":"IT Lab"},
        {"room_id":"201","floor":2,"room_name":"Digital Lab 202","room_type":"IT Lab"},
        {"room_id":"305","floor":3,"room_name":"Classroom 305","room_type":"Classroom"},
        {"room_id":"501","floor":5,"room_name":"Server Room 501","room_type":"IT Lab"},
    ])

def get_devices():
    defaults = []
    for _, r in get_rooms().iterrows():
        defaults.append({
            "device_id": f"AC-{r['room_id']}",
            "room_id": r['room_id'],
            "name": "Air Conditioner",
            "load_type": "Non-IT" if "Classroom" in r['room_type'] else "IT",
            "current_state": "off",
            "auto_schedule": True,
            "schedule_on": "08:00",
            "schedule_off": "20:00",
            "mean_power": np.random.randint(1200, 1800)
        })
    return load("devices.csv", ["device_id","room_id","name","load_type","current_state","auto_schedule","schedule_on","schedule_off","mean_power"], defaults)

def generate_synthetic_data():
    devices = get_devices()
    all_data = []
    start = datetime.now() - timedelta(days=30)
    times = pd.date_range(start, datetime.now(), freq='10T')
    for _, dev in devices.iterrows():
        on_t = datetime.strptime(dev['schedule_on'], '%H:%M').time()
        off_t = datetime.strptime(dev['schedule_off'], '%H:%M').time()
        for ts in times:
            t = ts.time()
            scheduled = (on_t <= t < off_t) if on_t < off_t else (t >= on_t or t < off_t)
            state = "on" if (dev['auto_schedule'] and scheduled) or dev['current_state'] == "on" else "off"
            power = np.random.normal(dev['mean_power'], 200) if state == "on" else 0
            power = max(power, 0)
            all_data.append({"timestamp": ts, "device_id": dev['device_id'], "power": round(power, 2)})
    df = pd.DataFrame(all_data)
    save(df, "measurements.csv")
    return df

def get_measurements():
    path = os.path.join(DATA_DIR, "measurements.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    return generate_synthetic_data()

def get_current_readings(dev):
    now = datetime.now().time()
    on_t = datetime.strptime(dev['schedule_on'], '%H:%M').time()
    off_t = datetime.strptime(dev['schedule_off'], '%H:%M').time()
    scheduled = (on_t <= now < off_t) if on_t < off_t else (now >= on_t or now < off_t)
    state = "on" if (dev['auto_schedule'] and scheduled) or dev['current_state'] == "on" else "off"
    power = np.random.normal(dev['mean_power'], 200) if state == "on" else 0
    power = max(power, 0)
    return {"power": round(power, 2), "state": state}

def get_period_data(start, end):
    df = get_measurements()
    mask = (df['timestamp'].dt.date >= start) & (df['timestamp'].dt.date <= end)
    return df[mask]

def calculate_stats(df):
    kwh = df['power'].sum() * (10/60) / 1000
    return round(kwh, 3), round(kwh * RATE_TAKA_PER_KWH, 1), int(kwh * CO2_G_PER_KWH)
