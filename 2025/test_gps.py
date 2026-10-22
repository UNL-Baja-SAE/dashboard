import serial
import time
PORT = "/dev/serial0"
BAUD = 9600
ser = serial.Serial(PORT, BAUD, timeout=1)

print(f"Opening {PORT} at {BAUD} baud...")
try:
    # 2. If it's somehow open in this Python instance, close it
    if ser.is_open:
        ser.close()
        
    # 3. Open it fresh
    ser.open()
    
    # 4. Flush the pipes (THIS IS CRUCIAL FOR WEIRD BUGS)
    # This deletes any old, half-read messages sitting in the Pi's memory
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    
    print("Port securely opened and buffers flushed!")

except serial.SerialException as e:
    print(f"\n[ERROR] Port is locked by the OS. You need the Terminal fix. Details: {e}\n")
try:
    
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