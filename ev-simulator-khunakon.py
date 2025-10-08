import streamlit as st
import time
import math

st.set_page_config(page_title="EV Simulator", page_icon="🚗", layout="wide")

st.title("🚗 Electric Vehicle Simulation Dashboard")
st.write("จำลองการทำงานของระบบขับเคลื่อนและการใช้พลังงานของรถยนต์ไฟฟ้า")

# -------------------------------
# Sidebar setup
# -------------------------------
st.sidebar.header("Vehicle Configuration")
battery_capacity = st.sidebar.slider("🔋 Battery Capacity (kWh)", 20, 120, 60, step=5)
motor_efficiency = st.sidebar.slider("⚙️ Motor Efficiency (%)", 60, 98, 90, step=1)
vehicle_weight = st.sidebar.slider("🚘 Vehicle Weight (kg)", 800, 2500, 1600, step=100)
aero_drag = st.sidebar.slider("💨 Aerodynamic Drag Coefficient (Cd)", 0.2, 0.5, 0.29)
rolling_resistance = st.sidebar.slider("🛞 Rolling Resistance Coefficient (Cr)", 0.005, 0.015, 0.010)
speed = st.sidebar.slider("🏎️ Average Speed (km/h)", 0, 180, 60, step=5)

# -------------------------------
# Simulation calculation
# -------------------------------
st.subheader("🔧 Simulation Parameters")

# Convert units
v = speed / 3.6  # m/s
air_density = 1.225  # kg/m³
frontal_area = 2.2  # m² (approx for sedan)

# Forces
drag_force = 0.5 * air_density * aero_drag * frontal_area * (v ** 2)
rolling_force = vehicle_weight * 9.81 * rolling_resistance
total_force = drag_force + rolling_force

# Power and consumption
power = total_force * v / (motor_efficiency / 100)
energy_per_km = power / (v * 1000)  # kWh/km
range_km = battery_capacity / energy_per_km if energy_per_km > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Power Consumption", f"{power/1000:.2f} kW")
col2.metric("Energy Efficiency", f"{1/energy_per_km:.2f} km/kWh")
col3.metric("Estimated Range", f"{range_km:.0f} km")

# -------------------------------
# Battery drain simulation
# -------------------------------
if st.button("▶️ Start Simulation"):
    st.write("Simulating battery usage...")
    progress = st.progress(0)
    text = st.empty()
    for i in range(101):
        remaining_range = range_km * (1 - i / 100)
        progress.progress(i)
        text.text(f"Battery remaining: {100 - i:.0f}% | Range left: {remaining_range:.0f} km")
        time.sleep(0.05)
    st.success("Simulation complete ✅")

# -------------------------------
# Display chart
# -------------------------------
import numpy as np
import pandas as pd

speeds = np.linspace(0, 180, 50)
energies = []
for s in speeds:
    v = s / 3.6
    drag = 0.5 * air_density * aero_drag * frontal_area * (v ** 2)
    roll = vehicle_weight * 9.81 * rolling_resistance
    total = drag + roll
    power = total * v / (motor_efficiency / 100)
    e_per_km = power / (v * 1000)
    energies.append(e_per_km)

data = pd.DataFrame({"Speed (km/h)": speeds, "Energy (kWh/km)": energies})
st.line_chart(data.set_index("Speed (km/h)"))

st.caption("พัฒนาโดยใช้ Python + Streamlit • เหมาะสำหรับสาธิตหลักการทำงานของยานยนต์ไฟฟ้าในห้องเรียน")
