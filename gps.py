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
        self.lock = threading.Lock()

    def update(self, speed, lat, lon):
        with self.lock:
            self.speed = speed
            self.lat = lat
            self.lon = lon

    def get_data(self):
        with self.lock:
            return {"speed": self.speed, "lat": self.lat, "lon": self.lon}
        
    def get_speed(self):
        with self.lock:
            return self.speed


# 2. Your GPS Logic, wrapped in a class to avoid globals
class GPSDevice:
    def __init__(self):
        self.PORT = "/dev/serial0"
        self.time_synced = False
        self.ser = None
        self.connect_and_configure()

    def connect_and_configure(self):
        """Moved your setup logic here so it only runs when we ask it to."""
        try:
            self.ser = serial.Serial(self.PORT, baudrate=9600, timeout=0.5)
            time.sleep(0.5)

            # Change to 38400
            self.ser.write(bytearray([0xB5,0x62,0x06,0x00,0x14,0x00,0x01,0x00,0x00,0x00,0xD0,0x08,0x00,0x00,0x00,0x96,0x00,0x00,0x07,0x00,0x03,0x00,0x00,0x00,0x00,0x00,0x93,0xC8]))
            self.ser.flush()
            time.sleep(0.1)
            
            self.ser.baudrate = 38400
            time.sleep(0.1)

            # 5Hz Update rate
            self.ser.write(bytearray([0xB5,0x62,0x06,0x08,0x06,0x00,0xC8,0x00,0x01,0x00,0x01,0x00,0xDE,0x6A]))
            
            # Disable extra sentences
            self.ser.write(b'$PUBX,40,GLL,0,0,0,0,0,0*5C\r\n')
            self.ser.write(b'$PUBX,40,GSV,0,0,0,0,0,0*59\r\n')
            self.ser.write(b'$PUBX,40,GSA,0,0,0,0,0,0*4E\r\n')
            
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
            return None

        try:
            read_line = self.ser.readline().decode('ascii', errors='replace').strip()
            if not read_line:
                return None
                
            if read_line.startswith('$GPRMC'):
                parsed_data = pynmea2.parse(read_line)
                
                if not self.time_synced:
                    self.sync_time(parsed_data)
                    
                if parsed_data.status == 'A':
                    speed_mph = (parsed_data.spd_over_grnd or 0) * 1.15078
                    return {
                        "speed": round(speed_mph, 1),
                        "lat": parsed_data.latitude,
                        "lon": parsed_data.longitude
                    }
                else:
                    return {"speed": 0.0, "lat": 0.0, "lon": 0.0}

        except Exception:
            pass # Ignore partial lines
            
        return None


# 3. The Thread Worker Function
def gps_worker(gps_data, stop_event):
    # Initialize the hardware INSIDE the thread. 
    # This prevents the UI from freezing while configuring the UBX chip!
    device = GPSDevice()

    while not stop_event.is_set():
        try:
            info = device.receive_data()
            if info is not None:
                # Safely pass the data back to the main UI thread
                gps_data.update(info["speed"], info["lat"], info["lon"])
            else:
                # If no data, tiny sleep to prevent pegging the CPU to 100%
                time.sleep(0.01) 
        except Exception as e:
            print(f"GPS Thread Error: {e}")
            time.sleep(1.0)