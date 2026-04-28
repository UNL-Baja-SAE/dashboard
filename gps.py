import serial
import pynmea2
import time
import datetime
import os


time_synced = False 
PORT = "/dev/serial0" 
# We start at 9600 to talk to the GPS, then we will switch to 38400
BAUD = 9600

try:
    # 1. Open at default speed
    ser = serial.Serial(PORT, baudrate=BAUD, timeout=0.5)
    time.sleep(0.5)

    # 2. SEND UBX COMMANDS (Turbo Mode)
    # Change GPS internal baud rate to 38400 (Required for 5Hz bandwidth)
    ser.write(bytearray([0xB5,0x62,0x06,0x00,0x14,0x00,0x01,0x00,0x00,0x00,0xD0,0x08,0x00,0x00,0x00,0x96,0x00,0x00,0x07,0x00,0x03,0x00,0x00,0x00,0x00,0x00,0x93,0xC8]))
    ser.flush()
    time.sleep(0.1)
    
    # 3. Switch Raspberry Pi Serial Port to match
    ser.baudrate = 38400
    time.sleep(0.1)

    # 4. Set GPS update rate to 5Hz (200ms interval)
    ser.write(bytearray([0xB5,0x62,0x06,0x08,0x06,0x00,0xC8,0x00,0x01,0x00,0x01,0x00,0xDE,0x6A]))
    
    # 5. Disable extra sentences to save CPU and bandwidth
    ser.write(b'$PUBX,40,GLL,0,0,0,0,0,0*5C\r\n')
    ser.write(b'$PUBX,40,GSV,0,0,0,0,0,0*59\r\n')
    ser.write(b'$PUBX,40,GSA,0,0,0,0,0,0*4E\r\n')
    
    print("GPS Configured: 5Hz @ 38400 Baud")

except Exception as e:
    print(f"Failed to connect to GPS: {e}")
    ser = None

def receive_data():
    if not is_connected():
        return None

    try:
        # Optimization: We read the latest line available. 
        # We REMOVED the while loop and buffer reset to ensure no lag at 5Hz.
        read_line = ser.readline().decode('ascii', errors='replace').strip()
        
        if not read_line:
            return None
            
        if read_line.startswith('$GPRMC'):
            parsed_data = pynmea2.parse(read_line)
            if not time_synced:
                sync_time(parsed_data)
            if parsed_data.status == 'A':
                # Calculation: Knots to MPH
                speed_mph = (parsed_data.spd_over_grnd or 0) * 1.15078
                return {
                    "speed": round(speed_mph, 1),
                    "lat": parsed_data.latitude,
                    "lon": parsed_data.longitude
                }
            else:
                # No fix (Searching for satellites)
                return {"speed": 0.0, "lat": 0.0, "lon": 0.0}

    except Exception:
        pass # Ignore partial lines to keep the dashboard smooth
        
    return None
def sync_time(msg):
    global time_synced
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
    time_synced = True
def is_connected():
    return ser is not None and ser.is_open
