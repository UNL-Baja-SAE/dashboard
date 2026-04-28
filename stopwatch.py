import time


class Stopwatch:
    def __init__(self):
        self.running = False
        self.start_time = 0.0
        self.laps = []
        self.pause_time = 0.0
        self.last_lap_end_time = 0.0

    def start(self):
        if not self.running:
            self.start_time = time.monotonic() - self.pause_time
            self.running = True


    def stop(self):
        if self.running:
            self.pause_time = time.monotonic() - self.start_time
            self.running = False

    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def new_lap(self):
        if self.running:
            # Addes the current time to the list
            lap_time = time.monotonic() - self.start_time
            self.last_lap_end_time = lap_time
            self.start_time = self.start_time + self.last_lap_end_time

            self.laps.append(lap_time)
            self.laps.sort()
            print(self.get_fastest_lap())

    def get_lap_time(self):
        current_elapsed = time.monotonic() - self.start_time
        return self.convert_time(current_elapsed)

    @staticmethod
    def convert_time(time):
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        milliseconds = int((seconds % 1) * 1000)

        time_string = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}.{milliseconds:03}"

        return time_string
    def get_fastest_lap(self):
        if len(self.laps) == 0:
            return "--:--:--.---"
        fastest_lap = self.laps[0]
        return self.convert_time(fastest_lap)
