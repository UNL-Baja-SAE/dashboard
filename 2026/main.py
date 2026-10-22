import pygame
import math
import threading
import time
import random
import queue

class GPS_data:
    def __init__(self,data_queue):
        self.queue = data_queue
        self.counter = 0
        self.alive = False
        self.thread = None

    def start(self):
        self.alive = True
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()

    def loop(self):
        # 1. Choose a center coordinate (e.g., Chicago, IL)
        center_lat = 41.8781
        center_lon = -87.6298
        
        # 2. Conversion scale: 1 degree approx. 69 miles. 
        # An amplitude of 0.0167 degrees creates a radius of ~1.15 miles, 
        # making the full diameter loop roughly 2.3 miles wide.
        scale = 0.0167 
        
        while self.alive:
            time.sleep(0.1) 
            
            # Base circular math (0.0 to 1.0) scaled into miles-to-degrees conversion
            base_x = math.cos(self.counter * 0.1) * scale
            base_y = math.sin(self.counter * 0.1) * scale
            
            # Simulated GPS jitter (scaled to represent roughly ~15-30 feet of random drift)
            jitter_x = (0.05 * random.random() - 0.025) * 0.01
            jitter_y = (0.05 * random.random() - 0.025) * 0.01
            
            # Combine center position, orbital motion, and noise
            generated_lat = center_lat + base_y + jitter_y
            generated_lon = center_lon + base_x + jitter_x
            
            self.counter += 1

            trunc_lat = round(generated_lat, 6)
            trunc_lon = round(generated_lon, 6)
            distance = self.haversine(trunc_lat,trunc_lon)
            # Push real geographical coordinates down the queue
            self.queue.put(trunc_lat,trunc_lon,distance)
    
    def haversine(coord1, coord2):
        """
        Calculate the great circle distance in kilometers between two points 
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(math.radians, [coord1[0], coord1[1], coord2[0], coord2[1]])

        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a)) 
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
        return c * r
    
    def path_sum(start, end, list):
        if start <= end:
            circular_sum = sum(list[start:end][2])

        else:
            circular_sum = sum(list[start:][2]) + sum(list[:end][2])
    
class Drawing:
    def __init__(self):
        # Store setup configurations here instead of initializing windows
        self.gps_queue = queue.Queue()
        self.active_list = []
        self.found_loop = []
        self.gpsData = GPS_data(self.gps_queue)
        self.running = False
        
        # Pygame instances will be bound at start
        self.screen = None
        self.clock = None

    def start(self):
        pygame.init()
        self.screen = pygame.display.set_mode((500, 500))
        pygame.display.set_caption("GPS Data Visualizer")
        self.clock = pygame.time.Clock()
        
        # Start data thread
        self.gpsData.start()
        self.running = True
        self.drawLoop()

    def drawLoop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

   
            while not self.gps_queue.empty():
                new_point = self.gps_queue.get()
                
                screen_x =  10000 * (new_point[0] - 41.8781) + 150
                screen_y =  10000 * (new_point[1] + 87.6298) + 150
                point = (screen_x, screen_y)
                print(point)

                if self.checkPoint(point):
                    
                    self.found_loop = self.active_list
                    self.active_list = []
                    self.active_list.append((point,True))
                else:
                    self.active_list.append((point,False))


            self.screen.fill("white")
            if self.found_loop:
                raw_points = [item[0] for item in self.found_loop]
            else:
                raw_points = [item[0] for item in self.active_list]
            
            
            
            if len(raw_points) >= 2:
                pygame.draw.lines(self.screen, color="blue", closed=self.found_loop, points=raw_points, width=3)
                
                pygame.draw.circle(self.screen, color="green", center=self.active_list[-1][0], radius=2)
            elif len(raw_points) == 1:
                pygame.draw.circle(self.screen, color="blue", center=raw_points[0], radius=2)

            pygame.display.flip()
            self.clock.tick(60) # Keep the drawing loop running smoothly at 60 FPS

        pygame.quit()  

    def checkPoint(self,point):
        if len(self.active_list) > 0:
            return math.dist(self.active_list[0][0], point) < 5
    
        return False

    def geographical_distance(coord1, coord2):
        """
        Calculates the great-circle distance between two points 
        on the Earth (specified in decimal degrees).
        Returns the distance in meters.
        """
        lat1, lon1 = coord1
        lat2, lon2 = coord2

        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
    
        # Radius of Earth in meters (use 3956 for miles)
        r = 6371000 
    
        return c * r



if __name__ == "__main__":
    drawing = Drawing()
    drawing.start()