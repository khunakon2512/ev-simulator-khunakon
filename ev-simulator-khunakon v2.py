import streamlit as st
import time
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="EV Interactive Simulator", page_icon="🚗", layout="wide")
st.title("🚗 Electric Vehicle Interactive Simulation")
st.write("จำลองการเคลื่อนที่และการใช้พลังงานของยานยนต์ไฟฟ้าแบบเรียลไทม์")

# -------------------------------
# Sidebar setup
# -------------------------------
st.sidebar.header("Vehicle Configuration")
battery_capacity = st.sidebar.slider("🔋 Battery Capacity (kWh)", 20, 120, 60, step=5)
motor_efficiency = st.sidebar.slider("⚙️ Motor Efficiency (%)", 60, 98, 90, step=1)
vehicle_weight = st.sidebar.slider("🚘 Vehicle Weight (kg)", 800, 2500, 1600, step=100)
aero_drag = st.sidebar.slider("💨 Aerodynamic Drag Coefficient (Cd)", 0.2, 0.5, 0.29)
rolling_resistance = st.sidebar.slider("🛞 Rolling Resistance (Cr)", 0.005, 0.015, 0.010)
speed = st.sidebar.slider("🏎️ Speed (km/h)", 0, 180, 80, step=5)

# -------------------------------
# Simulation base calculations
# -------------------------------
v = speed / 3.6  # m/s
air_density = 1.225  # kg/m³
frontal_area = 2.2  # m² (approx sedan)

drag_force = 0.5 * air_density * aero_drag * frontal_area * (v ** 2)
rolling_force = vehicle_weight * 9.81 * rolling_resistance
total_force = drag_force + rolling_force
power = total_force * v / (motor_efficiency / 100)
energy_per_km = power / (v * 1000)
range_km = battery_capacity / energy_per_km if energy_per_km > 0 else 0

# -------------------------------
# Interactive layout
# -------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("🛣️ Vehicle Movement")
    movement_placeholder = st.empty()

with col2:
    st.subheader("📊 Live Data")
    chart_placeholder = st.empty()
    metrics_placeholder = st.empty()

# -------------------------------
# Run Simulation
# -------------------------------
if st.button("▶️ Start Simulation"):
    st.toast("Starting EV simulation...", icon="🚗")
    total_time = 20  # seconds
    battery = battery_capacity
    distance = 0
    energy_used = 0
    time_series = []
    battery_series = []
    dist_series = []

    for t in range(total_time + 1):
        # --- Update values ---
        distance += (speed / 3600)  # km per second
        energy_used = distance * energy_per_km
        battery_remaining = battery_capacity - energy_used
        if battery_remaining <= 0:
            battery_remaining = 0

        # --- Append data ---
        time_series.append(t)
        battery_series.append(battery_remaining)
        dist_series.append(distance)

        # --- Vehicle movement (car icon animation) ---
        road = "—" * (t % 40)
        car_display = f"{road}🚗"
        movement_placeholder.markdown(f"<h3 style='text-align:center;'>{car_display}</h3>", unsafe_allow_html=True)

        # --- Plot live battery graph ---
        fig, ax = plt.subplots()
        ax.plot(time_series, battery_series, color="green", linewidth=2)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Battery (kWh)")
        ax.set_ylim(0, battery_capacity)
        ax.grid(True)
        chart_placeholder.pyplot(fig)

        # --- Live metrics ---
        metrics_placeholder.metric("Remaining Battery (kWh)", f"{battery_remaining:.2f}")
        time.sleep(0.3)

        if battery_remaining <= 0:
            st.error("🔋 Battery depleted!")
            break

    st.success("✅ Simulation Complete!")

st.caption("พัฒนาโดยใช้ Python + Streamlit • Interactive EV Simulator สำหรับการสอนระบบขับเคลื่อนไฟฟ้า")
