import serial

PORT = "/dev/serial0"
BAUD = 9600

print(f"Opening {PORT} at {BAUD} baud...")

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print("Port open! Listening for data. Press Ctrl+C to stop.")
    
    while True:
        # Read raw bytes directly from the port
        raw_data = ser.readline()
        
        if raw_data:
            # If we hear anything, print it immediately
            print(raw_data.decode('ascii', errors='replace').strip())
        else:
            # If the 1-second timeout hits with no data
            print("...silence...")

except Exception as e:
    print(f"Failed to open port: {e}")