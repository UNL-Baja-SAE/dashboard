import serial
import time

SERIAL_PORT = '/dev/serial0' 
BAUD_RATE = 9600

current_rpm = 0.0
last_data_time = time.time()
ser = None

def init_serial():
    global ser
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    except (serial.SerialException, OSError) as e:
        # Fails silently or with a simple print, but doesn't crash main
        print(f"Hall effect sensor not found on {SERIAL_PORT}. RPM will stay at 0.")
        ser = None

# Run once on import
init_serial()

def get_rpm():
    global current_rpm, last_data_time, ser
    
    # If serial failed to open, just return 0.0 safely
    if ser is None:
        return 0.0

    try:
        if ser.is_open:
            while ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if line:
                    try:
                        current_rpm = float(line)
                        last_data_time = time.time()
                    except ValueError:
                        pass # Ignore malformed strings
            
            # Reset to 0 if no data received for 1 second
            if time.time() - last_data_time > 1.0:
                current_rpm = 0.0
                
    except (serial.SerialException, OSError):
        # If the sensor is unplugged while running
        ser = None 
        current_rpm = 0.0
            
    return current_rpm
