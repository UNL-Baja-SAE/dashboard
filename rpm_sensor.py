import time
import threading
from gpiozero import Button




# Initialize the sensor
# pull_up=True ensures the internal pull-up resistor is active
# bounce_time=0.005 ignores duplicate erratic signals within 5 milliseconds




class SharedRPMData:
    def __init__(self):
        self.rpm = 0.0
        self.lock = threading.Lock()

    def update(self, rpm):
        with self.lock:
            self.rpm = rpm

    def get_rpm(self):
        with self.lock:
            return self.rpm
        
class RPMDevice:
    HALL_PIN = 16
    MAGNETS_PER_REV = 1
    def __init__(self):
        # --- Configuration --- 
        self.current_rpm = 0.0
        self.last_pulse_time = time.time()
    def setup_sensor(self):
        try:
            sensor = Button(self.HALL_PIN, pull_up=True, bounce_time=0.005)
    
            # 'when_pressed' triggers on a falling edge (3.3V dropping to 0V)
            sensor.when_pressed = self.pulse_callback
        except Exception as e:
            print(f"Failed to initialize sensor on GPIO {self.HALL_PIN}: {e}")
            sensor = None
    def pulse_callback(self):
        """Triggered automatically when the magnet passes (sensor goes LOW)."""
        global current_rpm, last_pulse_time
    
        current_time = time.time()
        time_diff = current_time - self.last_pulse_time
    
        # RPM = (60 seconds / time taken for 1 pulse) / number of magnets
        self.current_rpm = (60.0 / time_diff) / self.MAGNETS_PER_REV
        self.last_pulse_time = current_time
    def get_rpm(self):
        """Returns the current RPM, resetting to 0 if rotation stops."""
    
        # Reset to 0 if no pulse is received for 1 second
        if time.time() - self.last_pulse_time > 1.0:
            self.current_rpm = 0.0
        
        return current_rpm

def rpm_worker(rpm_data, stop_event):
    device = RPMDevice()

    while not stop_event.is_set():
        try:
            new_rpm = device.get_rpm()
            if new_rpm is not None:
                rpm_data.update(new_rpm)
                
        except Exception as e:
            print(f"RPM Worker Error: {e}")
            time.sleep(1.0) 
            
        time.sleep(0.01)