import serial
import pynmea2

port = "/dev/serial0" 
baud = 9600
try:
    ser = serial.Serial(port, baudrate=baud, timeout=0.5)
except Exception as e:
    print(f"Error: {e}")

def receive_data():
    try:
        read_line = ser.readline().decode('ascii', errors= 'replace')
        if read_line.startswith('$GPRMC'):
            parsed_data = pynmea2.parse(read_line)
            if parsed_data.status == 'A':
                init_speed = parsed_data.spd_over_grnd
                speed_mph = init_speed * 1.15078
                return speed_mph
    except Exception as e:
        print(f"Error: {e}")
    return None
    
def is_connected():
    # Check if 'ser' exists and is open
    if 'ser' in globals() and ser.is_open:
        return True
    return False
