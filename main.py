import os
import subprocess

# 1. Force the pin factory
os.environ['GPIOZERO_PIN_FACTORY'] = 'pigpio'

# 2. Restart pigpiod to clear any zombie hardware states
try:
    subprocess.run(['sudo', 'killall', 'pigpiod'], capture_output=True)
    subprocess.run(['sudo', 'pigpiod'], check=True)
    print("pigpiod daemon restarted successfully.")
except Exception as e:
    print(f"Warning: Could not restart pigpiod: {e}")
import pygame
import pygame_gui
import datetime
import time
import threading

from rpm_sensor import get_rpm
from gpiozero import Button, CPUTemperature
from gps import receive_data, is_connected
from dash import TextGauge, Gauge, WIDTH, HEIGHT
from gpiozero import Servo
from time import sleep

# MS24 Pulse Widths: 0.5ms to 2.5ms
# On Pi 4, GPIO 18 is Physical Pin 12
motor = Servo(18, min_pulse_width=0.0005, max_pulse_width=0.0025,initial_value=-0.25)

print("Pi 4B + MS24 Test Starting...")

def activate_four_wheel(four_engaged):
    if not four_engaged:
        print("eaaengaged")
        motor.value = 0.25
        four_engaged = True
    return four_engaged

def deactive_four_wheel(four_engaged):
    if four_engaged:
        print("disaaengaged")
        motor.value = -0.25
        four_engaged = False
    return four_engaged

pygame.init()
pygame.font.init()

monitor_info = pygame.display.Info()
screen_width = monitor_info.current_w
screen_height = monitor_info.current_h
cpu = CPUTemperature()

screen = pygame.display.set_mode((WIDTH, HEIGHT),pygame.FULLSCREEN)
base_path = os.path.dirname(os.path.abspath(__file__))
theme_path = os.path.join(base_path, 'theme.json')
manager = pygame_gui.UIManager((WIDTH, HEIGHT), theme_path=theme_path)

four_wheel_drive = False

clean_start = False

r_button = Button(26, pull_up=True)
l_button = Button(19, pull_up=True)
toggle_switch = Button(21, pull_up=True)
print(r_button.is_pressed,l_button.is_pressed, toggle_switch.is_pressed)
time_rect = pygame.Rect((WIDTH // 2 - 75, 10), (150, 40))
clock_label = pygame_gui.elements.UILabel(
    relative_rect=time_rect,
    text="--:--",
    manager=manager,
    object_id="#clock_box"
)

temp_rect = pygame.Rect((WIDTH // 2 - 300, 10), (150, 40))
temp_label = pygame_gui.elements.UILabel(
    relative_rect=temp_rect,
    text=f"CPU Temp: {cpu.temperature} °C",
    manager=manager,
    object_id="#clock_box"
)

fwd_rect = pygame.Rect((WIDTH // 2 +100, 10), (150, 40))


try:
    custom_font = pygame.font.Font('fonts/Russo_One/RussoOne-Regular.ttf', 90)
    font = pygame.font.Font('fonts/Russo_One/RussoOne-Regular.ttf', 18)

except FileNotFoundError:
    print("CustomFont.ttf not found. Using default font.")
    custom_font = pygame.font.Font(None, 90)
    font = pygame.font.SysFont(None, 30)

clock = pygame.time.Clock()

app_is_running = False
latest_gps_speed = 0.0
latest_rpm = 0.0

def gps_worker():
    global latest_gps_speed
    
    while app_is_running:
        try:
            if is_connected():
                gps_info = receive_data() 
                
                if gps_info is not None:
                    latest_gps_speed = gps_info["speed"]
            else:
                time.sleep(1.0)
                
        except Exception as e:
            print(f"GPS Worker Error: {e}")
            time.sleep(1.0) 
        
        # GPS is slow, check at 20Hz
        time.sleep(0.05)

def rpm_worker():
    global latest_rpm
    
    while app_is_running:
        try:
            new_rpm = get_rpm()
            if new_rpm is not None:
                latest_rpm = new_rpm
                
        except Exception as e:
            print(f"RPM Worker Error: {e}")
            time.sleep(1.0) 
            
        # Hall sensor is fast, poll at 100Hz
        time.sleep(0.01)

def main():
    global toggle_switch
    global r_button
    global l_button
    global app_is_running
    global four_wheel_drive
    global clean_start

    deactive_four_wheel(True)

    if not toggle_switch.is_pressed:
        clean_start = True

    app_is_running = True
    current_speed = 0.0
    current_rpm = 0.0
    
    gps_thread = threading.Thread(target=gps_worker, daemon=True)
    gps_thread.start()
    
    rpm_thread = threading.Thread(target=rpm_worker, daemon=True)
    rpm_thread.start()
    
    speedo = TextGauge(WIDTH, HEIGHT, center_x=200, center_y=240, radius=160, max_value=55, font=font,
                       custom_font=custom_font, gap_width=35)
    tacho = Gauge(WIDTH, HEIGHT, center_x=600, center_y=240, radius=160, max_value=7000, font=font, scale=1000)
    last_fwd_state = None
    fwd_label = pygame_gui.elements.UILabel(
        relative_rect=fwd_rect,
        text="Disengaged",
        manager=manager,
        object_id="#fwd_box"
    )
    
    while app_is_running:
        time_delta = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app_is_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.display.set_mode((800, 600))

            manager.process_events(event)
            
        current_time_string = datetime.datetime.now().strftime("%I:%M:%S %p")
        clock_label.set_text(current_time_string)
        temp_label.set_text(f"CPU Temp: {cpu.temperature:.0f} °C")
        # Independent smoothing factors for different gauge responsiveness
        speed_smoothing = 5.0  # Slower, smoother needle for GPS speed
        rpm_smoothing = 15.0   # Faster, snappier needle for Hall effect RPM
        
        current_speed += (latest_gps_speed - current_speed) * (speed_smoothing * time_delta)
        current_rpm += (latest_rpm - current_rpm) * (rpm_smoothing * time_delta)
        
        if latest_gps_speed == 0.0 and current_speed < 0.5:
            current_speed = 0.0       
        if latest_rpm == 0.0 and current_rpm < 50.0:
            current_rpm = 0.0
             
        pressed_keys = pygame.key.get_pressed()  

        if pressed_keys[pygame.K_UP]:
            current_speed += 1
            current_rpm += 10            
        if clean_start:
            if toggle_switch.is_pressed and not four_wheel_drive:
                print("Pressed" + current_time_string)
                if four_wheel_drive != activate_four_wheel(four_wheel_drive):
                    four_wheel_drive = True
                
            elif not toggle_switch.is_pressed and four_wheel_drive:
                print("Pressed2")

                if four_wheel_drive != deactive_four_wheel(four_wheel_drive):
                    four_wheel_drive = False
        else:
            if not toggle_switch.is_pressed:
                clean_start = True
                last_fwd_state = None
                four_wheel_drive= False

        
        if four_wheel_drive != last_fwd_state:
            
            if fwd_label:
                fwd_label.kill()
            if not clean_start:
                new_text = "FLIP TO DISENAGE"
                new_id = "#fwd_box_disengaged" 
            elif four_wheel_drive:
                new_text = "Engaged"
                new_id = "#fwd_box_engaged"  
            else:
                new_text = "Disengaged"
                new_id = "#fwd_box_disengaged" 

            fwd_label = pygame_gui.elements.UILabel(
                relative_rect=fwd_rect,
                text=new_text,
                manager=manager,
                object_id=new_id
            )
            
            last_fwd_state = four_wheel_drive
        screen.fill((0, 0, 0))
        speedo.draw(screen, current_speed)
        tacho.draw(screen, current_rpm)
        
        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()