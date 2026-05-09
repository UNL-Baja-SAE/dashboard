import serial
import pynmea2
import time
import datetime
import os
import threading

# 1. The Thread-Safe Data Container (From earlier)
class SharedGPSData:
    def __init__(self):
        self.speed = 0.0
        self.lat = 0.0
        self.lon = 0.0
        self.is_silent = True  # Assume silent until we hear the first byte
        self.lock = threading.Lock()

    def update(self, speed, lat, lon, is_silent):
        with self.lock:
            self.speed = speed
            self.lat = lat
            self.lon = lon
            self.is_silent = is_silent
    def get_data(self):
        with self.lock:
            return {"speed": self.speed, "lat": self.lat, "lon": self.lon}
        
    def get_speed(self):
        with self.lock:
            return self.speed

    def get_is_silent(self): # <-- NEW: Check if the wiring is dead
        with self.lock:
            return self.is_silent
# 2. Your GPS Logic, wrapped in a class to avoid globals
class GPSDevice:
    def __init__(self):
        self.PORT = "/dev/serial0"
        self.time_synced = False
        self.ser = None
        self.last_heard_from = time.time()
        self.connect_and_configure()

    def connect_and_configure(self):
        """Moved your setup logic here so it only runs when we ask it to."""
        try:
            self.ser = serial.Serial(self.PORT, baudrate=9600, timeout=0.5)
            time.sleep(0.5)

            # Change to 38400
            #self.ser.write(bytearray([0xB5,0x62,0x06,0x00,0x14,0x00,0x01,0x00,0x00,0x00,0xD0,0x08,0x00,0x00,0x00,0x96,0x00,0x00,0x07,0x00,0x03,0x00,0x00,0x00,0x00,0x00,0x93,0xC8]))
            #self.ser.flush()
            #time.sleep(0.1)
            
            #self.ser.baudrate = 38400
            #time.sleep(0.1)

            # 5Hz Update rate
            #self.ser.write(bytearray([0xB5,0x62,0x06,0x08,0x06,0x00,0xC8,0x00,0x01,0x00,0x01,0x00,0xDE,0x6A]))
            
    
            
            print("GPS Configured: 5Hz @ 38400 Baud")
        except Exception as e:
            print(f"Failed to connect to GPS: {e}")
            self.ser = None

    def is_connected(self):
        return self.ser is not None and self.ser.is_open

    def sync_time(self, msg):
        gps_dt = datetime.datetime.combine(msg.datestamp, msg.timestamp)
        sys_dt = datetime.datetime.utcnow()
        time_diff = abs((gps_dt - sys_dt).total_seconds())
            
        if time_diff > 60:
            print(f"Clock error ({int(time_diff)}s). Syncing to GPS...")
            gps_iso_str = gps_dt.strftime("%Y-%m-%d %H:%M:%S")
            os.system(f"sudo date -u -s '{gps_iso_str}'")
            os.system("sudo fake-hwclock save")
            print("Time synced successfully.")
        else:
            print("System clock is already accurate.")
        self.time_synced = True

def receive_data(self):
        if not self.is_connected():
            return {"error": True} # Indicate connection/wiring error

        try:
            # Read raw bytes FIRST to check for physical electrical activity
            raw_data = self.ser.readline()
            
            if len(raw_data) > 0:
                # We received actual voltage changes/bytes! Reset the watchdog.
                self.last_heard_from = time.time()
            elif time.time() - self.last_heard_from > 2.0:
                # It's been over 2 seconds since we heard ANY bytes over the wire
                return {"error": True}

            # Now try to decode it normally
            read_line = raw_data.decode('ascii', errors='replace').strip()
            
            if read_line.startswith('$GPRMC'):
                parsed_data = pynmea2.parse(read_line)
                
                if parsed_data.status == 'A':
                    speed_mph = (parsed_data.spd_over_grnd or 0) * 1.15078
                    return {
                        "speed": round(speed_mph, 1),
                        "lat": parsed_data.latitude,
                        "lon": parsed_data.longitude,
                        "error": False # Wiring is good, signal is good
                    }
                else:
                    # Wiring is good, but no satellite fix yet. 
                    return {"speed": 0.0, "lat": 0.0, "lon": 0.0, "error": False}

        except Exception:
            pass # Ignore bad characters from partial lines
            
        # Catch-all watchdog check in case we get stuck in exceptions
        if time.time() - self.last_heard_from > 2.0:
            return {"error": True}
            
        return None


# 3. Update the Worker Function
def gps_worker(gps_data, stop_event):
    device = GPSDevice()

    while not stop_event.is_set():
        try:
            info = device.receive_data()
            if info is not None:
                if info.get("error", False):
                    # Silence detected (bad wiring / disconnected)
                    gps_data.update(0.0, 0.0, 0.0, is_silent=True)
                else:
                    # We have physical data
                    gps_data.update(info["speed"], info["lat"], info["lon"], is_silent=False)
            else:
                time.sleep(0.01) 
        except Exception as e:
            print(f"GPS Thread Error: {e}")
            time.sleep(1.0)