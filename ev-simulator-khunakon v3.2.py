import streamlit as st
import time
from PIL import Image, ImageDraw

st.set_page_config(page_title="EV Driving Game", page_icon="🚗", layout="wide")
st.title("🚗 EV Driving Simulator Game (Simple)")

# -------------------------------
# Sidebar: Vehicle settings
# -------------------------------
st.sidebar.header("Vehicle Configuration")
battery_capacity = st.sidebar.slider("🔋 Battery Capacity (kWh)", 20, 120, 60, step=5)
motor_efficiency = st.sidebar.slider("⚙️ Motor Efficiency (%)", 60, 98, 90, step=1)
vehicle_weight = st.sidebar.slider("🚘 Vehicle Weight (kg)", 800, 2500, 1600, step=100)
aero_drag = st.sidebar.slider("💨 Drag Coefficient (Cd)", 0.2, 0.5, 0.29)
rolling_resistance = st.sidebar.slider("🛞 Rolling Resistance (Cr)", 0.005, 0.015, 0.010)
max_speed = st.sidebar.slider("🏎️ Max Speed (km/h)", 50, 180, 120, step=5)

# -------------------------------
# Control sliders
# -------------------------------
st.sidebar.header("Controls")
throttle = st.sidebar.slider("Accelerator (%)", 0, 100, 0)
brake = st.sidebar.slider("Brake (%)", 0, 100, 0)

# -------------------------------
# Simulation variables
# -------------------------------
dt = 0.1  # time step in seconds
v = 0  # m/s
distance = 0  # km
battery = battery_capacity  # kWh
air_density = 1.225
frontal_area = 2.2  # m²
mass = vehicle_weight

# -------------------------------
# Placeholders
# -------------------------------
road_placeholder = st.empty()
metrics_placeholder = st.empty()
chart_placeholder = st.empty()

# -------------------------------
# Create a simple car image
# -------------------------------
def create_car_image(position, width=600, height=100):
    img = Image.new("RGB", (width, height), color=(200, 200, 200))
    draw = ImageDraw.Draw(img)
    # Draw road
    draw.rectangle([0, height//3, width, height*2//3], fill=(50, 50, 50))
    # Draw car
    car_width = 40
    car_height = 20
    x = int(position)
    y = height//2 - car_height//2
    draw.rectangle([x, y, x+car_width, y+car_height], fill=(255,0,0))
    return img

# -------------------------------
# Run simulation
# -------------------------------
run_sim = st.button("▶️ Start Driving")

if run_sim:
    st.toast("Simulation started!", icon="🚗")
    positions = []
    battery_series = []
    distance_series = []
    
    for step in range(300):  # simulate 30 seconds
        # --- Update speed ---
        acc = throttle/100*2 - brake/100*3  # simple acceleration model
        v += acc * dt
        v = max(0, min(v, max_speed/3.6))  # limit speed
        
        # --- Compute forces and energy ---
        drag = 0.5 * air_density * aero_drag * frontal_area * (v**2)
        rolling = mass * 9.81 * rolling_resistance
        power = (drag + rolling) * v / (motor_efficiency/100)  # W
        energy_used = power * dt / 3.6e6  # convert W*s to kWh
        battery -= energy_used
        if battery < 0:
            battery = 0
            v = 0  # stop car if battery dead
        
        # --- Update distance ---
        distance += v * dt / 1000  # km
        
        # --- Save series ---
        positions.append(min(560, step*2))  # for visualization
        battery_series.append(battery)
        distance_series.append(distance)
        
        # --- Update UI ---
        img = create_car_image(positions[-1])
        road_placeholder.image(img, use_container_width=True)
        
        metrics_placeholder.metric("Speed (km/h)", f"{v*3.6:.1f}")
        metrics_placeholder.metric("Battery (kWh)", f"{battery:.2f}")
        metrics_placeholder.metric("Distance (km)", f"{distance:.2f}")
        
        chart_placeholder.line_chart({"Battery": battery_series, "Distance": distance_series})
        
        time.sleep(dt)
        
        if battery <= 0:
            st.error("🔋 Battery depleted!")
            break
    
    st.success("✅ Simulation Ended!")
