import serial
import time
import sys

# --- Configuration ---
PORT = 'COM7'
BAUDRATE = 115200

try:
    with serial.Serial(PORT, baudrate=BAUDRATE, timeout=1) as ser:
        print(f"Connected to Arduino on {PORT}. Waiting for RPM data...\n")
        ser.reset_input_buffer()
        
        # Track the last time we updated the screen
        last_display_time = time.time()
        
        while True:
            # 1. Read continuously to prevent the buffer from backing up
            raw_line = ser.readline()
            
            if raw_line:
                try:
                    text_data = raw_line.decode('utf-8').strip()
                    
                    if text_data == "Ready" or not text_data:
                        continue
                        
                    rpm_float = float(text_data)
                    rpm_int = int(rpm_float)
                    
                    # 2. Check if 0.1 seconds (10Hz) have passed since the last print
                    current_time = time.time()
                    if current_time - last_display_time >= 0.1:
                        sys.stdout.write(f"\rCurrent RPM: {rpm_int:<8}")
                        sys.stdout.flush()
                        
                        # Reset the timer for the next update
                        last_display_time = current_time
                        
                except ValueError:
                    pass

except serial.SerialException as e:
    print(f"\nError: Could not connect to {PORT}. Is the Arduino IDE Serial Monitor open?")
except KeyboardInterrupt:
    print("\n\nMonitoring stopped by user.")