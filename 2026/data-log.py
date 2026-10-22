import csv
import queue
import threading
import time
import serial

class SerialCSVLogger:
    def __init__(self, filename, baudrate, port):

        self.port = port
        self.baudrate = baudrate
        self.filename = filename

        self.queue = queue.Queue()
        self.running = False

        self.writer_thread = None
        self.reader_thread = None
    
    def start(self):
        self.running = True
        self.writer_thread = threading.Thread(target=self.run_writer, daemon=True)
        self.reader_thread = threading.Thread(target=self.run_reader, daemon=True)
        self.writer_thread.start()
        self.reader_thread.start()

    def run_reader(self):
        try:
            with serial.Serial(self.port, baudrate=self.baudrate, timeout=1) as ser:
                ser.reset_input_buffer()

                while self.running:
                    raw_line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if raw_line:
                        parts = raw_line.split()
                        if len(parts) >= 5:
                            raw_time = parts[1]
                            raw_dist = parts[5]
                            if raw_time.isdigit() and raw_dist.replace('.','',1).isdigit():
                                time_us = int(raw_time)
                                dist_in = float(raw_dist)
                                self.queue.put([time_us] + [dist_in])
                        #timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                        #[timestamp] +
                        

        except Exception as e:
            print(f"\nSerial Error: {e}")
            self.running = False

    
    def run_writer(self):
        with open(self.filename, 'a', newline='', encoding='utf-8', buffering=1) as csvfile:
            writer = csv.writer(csvfile);

            if csvfile.tell() == 0:
                writer.writerow(["Time","Dist"]);

            while self.running or not self.queue.empty():
                try:
                    row = self.queue.get(timeout=0.5)
                    writer.writerow(row)
                    self.queue.task_done()
                except queue.Empty:
                    continue
            
    def stop(self):
        self.running = False
        if self.reader_thread:
            self.reader_thread.join()
        if self.writer_thread:
            self.writer_thread.join()

if __name__ == "__main__":
    # Replace with your actual COM port / dev path and baudrate
    LOGGER = SerialCSVLogger(port='COM8', baudrate=9600, filename='serial_data2.csv')
    LOGGER.start()
    print("Logging started. Press Ctrl+C to stop.")
    
    try:
        while LOGGER.running:
            time.sleep(1)  # Keep main thread alive
    except KeyboardInterrupt:
        LOGGER.stop()