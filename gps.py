import serial
import pynmea2

PORT = "/dev/serial0" 
BAUD = 9600

# Initialize globally, but set to None if it fails
try:
    ser = serial.Serial(PORT, baudrate=BAUD, timeout=0.5)
except Exception as e:
    print(f"Failed to connect to GPS on {PORT}: {e}")
    ser = None

def receive_data():
    if not is_connected():
        return None

    try:
        # Optional: If you notice lag, uncomment the line below to clear old data.
        # ser.reset_input_buffer() 
        
        # Loop until we specifically find the GPRMC sentence or hit a timeout
        while True:
            read_line = ser.readline().decode('ascii', errors='replace').strip()
            
            # If the line is empty, the 0.5s timeout was reached without data
            if not read_line:
                return None
                
            if read_line.startswith('$GPRMC'):
                parsed_data = pynmea2.parse(read_line)
                
                # 'A' means Active/Valid fix. 'V' means Void/Invalid.
                if parsed_data.status == 'A':
                    init_speed = parsed_data.spd_over_grnd
                    speed_mph = init_speed * 1.15078
                    return round(speed_mph, 1) # Rounding is usually best for displays
                else:
                    # GPS is connected but doesn't have a satellite fix yet
                    return 0.0 

    except pynmea2.ParseError as e:
        print(f"Parse Error: {e}")
    except Exception as e:
        print(f"Serial Error: {e}")
        
    return None

def is_connected():
    return ser is not None and ser.is_open