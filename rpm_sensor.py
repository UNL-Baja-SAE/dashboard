import time
from gpiozero import Button

# --- Configuration ---
HALL_PIN = 16
MAGNETS_PER_REV = 1

# --- State Variables ---
current_rpm = 0.0
last_pulse_time = time.time()

def pulse_callback():
    """Triggered automatically when the magnet passes (sensor goes LOW)."""
    global current_rpm, last_pulse_time
    
    current_time = time.time()
    time_diff = current_time - last_pulse_time
    
    # RPM = (60 seconds / time taken for 1 pulse) / number of magnets
    current_rpm = (60.0 / time_diff) / MAGNETS_PER_REV
    last_pulse_time = current_time

# Initialize the sensor
# pull_up=True ensures the internal pull-up resistor is active
# bounce_time=0.005 ignores duplicate erratic signals within 5 milliseconds
try:
    sensor = Button(HALL_PIN, pull_up=True, bounce_time=0.005)
    
    # 'when_pressed' triggers on a falling edge (3.3V dropping to 0V)
    sensor.when_pressed = pulse_callback
except Exception as e:
    print(f"Failed to initialize sensor on GPIO {HALL_PIN}: {e}")
    sensor = None

def get_rpm():
    """Returns the current RPM, resetting to 0 if rotation stops."""
    global current_rpm, last_pulse_time
    
    # Reset to 0 if no pulse is received for 1 second
    if time.time() - last_pulse_time > 1.0:
        current_rpm = 0.0
        
    return current_rpm