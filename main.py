import pygame
import pygame_gui
import datetime
import time
import threading
from gps import receive_data, is_connected
from dash import TextGauge,Gauge, WIDTH, HEIGHT

pygame.init()
pygame.font.init()

monitor_info = pygame.display.Info()
screen_width = monitor_info.current_w
screen_height = monitor_info.current_h

is_pi = screen_height == HEIGHT and screen_width == WIDTH

if is_pi:
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    screen = pygame.display.set_mode((WIDTH, HEIGHT),pygame.FULLSCREEN)
    manager = pygame_gui.UIManager((WIDTH, HEIGHT),theme_path="theme.json")

else:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    manager = pygame_gui.UIManager((WIDTH, HEIGHT),theme_path="theme.json")


screen = pygame.display.set_mode((WIDTH, HEIGHT))
manager = pygame_gui.UIManager((WIDTH, HEIGHT),theme_path="theme.json")

time_rect = pygame.Rect((WIDTH // 2 - 75, 10), (150, 40))
clock_label = pygame_gui.elements.UILabel(
    relative_rect=time_rect,
    text="--:--",
    manager=manager,
    object_id="#clock_box"
)

try:
    custom_font = pygame.font.Font('fonts/Russo_One/RussoOne-Regular.ttf', 90)
    font = pygame.font.Font('fonts/Russo_One/RussoOne-Regular.ttf', 18)


except FileNotFoundError:
    print("CustomFont.ttf not found. Using default font.")
    custom_font = pygame.font.Font(None, 90)
    font = pygame.font.SysFont(None, 30)

clock = pygame.time.Clock()

app_is_running = False
latest_gps_speed = 0
def gps_worker():
    global latest_gps_speed

    with open("gps_log.csv", "a") as log_file:
        
        # Optional: Write a header column when the script starts
        log_file.write("Timestamp,Speed_MPH,Latitude,Longitude\n")
        log_file.flush()


        while app_is_running:
            if is_connected():
                gps_info = receive_data()
                if gps_info is not None:
                    latest_gps_speed = gps_info["speed"]

                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # 3. Write the time and speed separated by a comma
                    log_file.write(f"{timestamp},{gps_info['speed']},{gps_info['lat']},{gps_info['lon']}\n")
                    log_file.flush()

            else:
                time.sleep(0.5)


def main():
    global app_is_running
    app_is_running = True
    current_speed = 0.0
    current_rpm = 0.0
    
    gps_thread = threading.Thread(target=gps_worker, daemon=True)
    gps_thread.start()
    
    speedo = TextGauge(WIDTH, HEIGHT, center_x=200, center_y=240, radius=160, max_value=55, font=font,
                   custom_font=custom_font,gap_width=35)
    tacho = Gauge(WIDTH,HEIGHT,center_x=600, center_y=240, radius=160, max_value=7000, font=font,scale=1000)
    while app_is_running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app_is_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.display.set_mode((800, 600))

            manager.process_events(event)
        current_time_string = datetime.datetime.now().strftime("%I:%M %p")

        # Update the label
        clock_label.set_text(current_time_string)

        current_speed = latest_gps_speed
        
        pressed_keys = pygame.key.get_pressed()  #


        if pressed_keys[pygame.K_UP]:
            current_speed += 1
            current_rpm += 100


        #if gps_speed is not None:
         #   current_speed = gps_speed
        screen.fill((0, 0, 0))
        speedo.draw(screen, current_speed)
        tacho.draw(screen, current_rpm)
        
        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.update()
        clock.tick(30)

    pygame.quit()



if __name__ == "__main__":
    main()