import streamlit as st
import time
from PIL import Image, ImageDraw

st.set_page_config(page_title="EV Driving Game", page_icon="🚗", layout="wide")
st.title("🚗 EV Driving Simulator (Button Hold Control)")

# -------------------------------
# Vehicle settings
# -------------------------------
st.sidebar.header("Vehicle Configuration")
battery_capacity = st.sidebar.slider("🔋 Battery Capacity (kWh)", 20, 120, 60, step=5)
motor_efficiency = st.sidebar.slider("⚙️ Motor Efficiency (%)", 60, 98, 90, step=1)
vehicle_weight = st.sidebar.slider("🚘 Vehicle Weight (kg)", 800, 2500, 1600, step=100)
aero_drag = st.sidebar.slider("💨 Drag Coefficient (Cd)", 0.2, 0.5, 0.29)
rolling_resistance = st.sidebar.slider("🛞 Rolling Resistance (Cr)", 0.005, 0.015, 0.010)
max_speed = st.sidebar.slider("🏎️ Max Speed (km/h)", 50, 180, 120, step=5)

# -------------------------------
# Session state
# -------------------------------
if 'v' not in st.session_state:
    st.session_state.v = 0
if 'distance' not in st.session_state:
    st.session_state.distance = 0
if 'battery' not in st.session_state:
    st.session_state.battery = battery_capacity
if 'running' not in st.session_state:
    st.session_state.running = False

dt = 0.1  # timestep
air_density = 1.225
frontal_area = 2.2
mass = vehicle_weight

# -------------------------------
# Placeholders
# -------------------------------
road_placeholder = st.empty()
speed_placeholder = st.empty()
distance_placeholder = st.empty()
current_placeholder = st.empty()
chart_placeholder = st.empty()

# -------------------------------
# Car image function
# -------------------------------
def create_car_image(position, width=600, height=100):
    img = Image.new("RGB", (width, height), color=(200,200,200))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0,height//3,width,height*2//3], fill=(50,50,50))
    car_width = 40
    car_height = 20
    x = int(position)
    y = height//2 - car_height//2
    draw.rectangle([x,y,x+car_width,y+car_height], fill=(255,0,0))
    return img

# -------------------------------
# Control buttons
# -------------------------------
col1, col2 = st.columns(2)
with col1:
    accelerate = st.button("🚀 Accelerate")
    brake = st.button("🛑 Brake")
with col2:
    start = st.button("▶️ Start")
    stop = st.button("⏹️ Stop")

if start:
    st.session_state.running = True
if stop:
    st.session_state.running = False

positions = []
battery_series = []
distance_series = []
current_series = []

# -------------------------------
# Simulation loop
# -------------------------------
while st.session_state.running:
    # --- Check button hold ---
    acc_input = 2 if accelerate else 0
    brake_input = -3 if brake else 0
    net_acc = acc_input + brake_input

    # --- Update speed ---
    st.session_state.v += net_acc * dt
    st.session_state.v = max(0, min(st.session_state.v, max_speed/3.6))

    # --- Compute energy & current ---
    drag = 0.5 * air_density * aero_drag * frontal_area * (st.session_state.v**2)
    rolling = mass * 9.81 * rolling_resistance
    power = (drag + rolling) * st.session_state.v / (motor_efficiency/100)  # W
    current = power / 400 if st.session_state.v > 0 else 0  # assume 400V battery
    energy_used = power * dt / 3.6e6  # kWh
    st.session_state.battery -= energy_used
    if st.session_state.battery <= 0:
        st.session_state.battery = 0
        st.session_state.v = 0
        st.session_state.running = False
        st.error("🔋 Battery depleted!")

    # --- Update distance ---
    st.session_state.distance += st.session_state.v * dt / 1000

    # --- Save series ---
    positions.append(min(560, len(positions)*2))
    battery_series.append(st.session_state.battery)
    distance_series.append(st.session_state.distance)
    current_series.append(current)

    # --- Update UI ---
    img = create_car_image(positions[-1])
    road_placeholder.image(img, use_container_width=True)
    speed_placeholder.metric("Speed (km/h)", f"{st.session_state.v*3.6:.1f}")
    distance_placeholder.metric("Distance (km)", f"{st.session_state.distance:.2f}")
    current_placeholder.metric("Current (A)", f"{current:.1f}")

    chart_placeholder.line_chart({
        "Battery": battery_series,
        "Distance": distance_series,
        "Current": current_series
    })

    time.sleep(dt)

    if len(positions) >= 300:
        st.session_state.running = False
        st.success("✅ Simulation ended!")
        break
