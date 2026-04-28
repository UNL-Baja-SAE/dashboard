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
from gps import gps_worker, SharedGPSData
from rpm_sensor import rpm_worker, SharedRPMData
from gpiozero import Button, CPUTemperature
from dash import TextGauge, Gauge, WIDTH, HEIGHT
from gpiozero import Servo
from time import sleep
from stopwatch import Stopwatch


# MS24 Pulse Widths: 0.5ms to 2.5ms
# On Pi 4, GPIO 18 is Physical Pin 12

print("Pi 4B + MS24 Test Starting...")

def activate_four_wheel(four_engaged,motor):
    if not four_engaged:
        print("eaaengaged")
        motor.value = 0.25
        four_engaged = True
    return four_engaged

def deactive_four_wheel(four_engaged,motor):
    if four_engaged:
        print("disaaengaged")
        motor.value = -0.25
        four_engaged = False
    return four_engaged



def main():

    motor = Servo(18, min_pulse_width=0.0005, max_pulse_width=0.0025,initial_value=-0.25)

    r_button = Button(3, pull_up=True,)

    #Power off button
    l_button = Button(19, pull_up=True,bounce_time=0.1)
    toggle_switch = Button(21, pull_up=True)
    print(r_button.is_pressed,l_button.is_pressed, toggle_switch.is_pressed)
    pygame.init()
    pygame.font.init()
    pygame.mouse.set_visible(False)


    monitor_info = pygame.display.Info()
    screen_width = monitor_info.current_w
    screen_height = monitor_info.current_h
    cpu = CPUTemperature()

    screen = pygame.display.set_mode((WIDTH, HEIGHT),pygame.FULLSCREEN)
    base_path = os.path.dirname(os.path.abspath(__file__))
    theme_path = os.path.join(base_path, 'theme.json')
    
    # 1. Point directly to the BOLD file
    bold_font_path = os.path.join(base_path, 'fonts','NotoSansDisplay', 'NotoSansDisplay_Condensed-Bold.ttf')
    
    # 2. Create the manager WITHOUT the theme path yet
    manager = pygame_gui.UIManager((WIDTH, HEIGHT))
    
    # 3. Add the font. Notice we assign the BOLD file to the 'regular_path'
    manager.add_font_paths(font_name="dash_bold", 
                           regular_path=bold_font_path)

    # 4. Preload it as 'regular'
    manager.preload_fonts([
        {'name': 'dash_bold', 'point_size': 24, 'style': 'regular'},
        {'name': 'dash_bold', 'point_size': 16, 'style': 'regular'}
    ])

    # 5. NOW load the theme
    if os.path.exists(theme_path):
        manager.get_theme().load_theme(theme_path)




    time_rect = pygame.Rect((WIDTH // 2 - 75, 10), (150, 40))
    clock_label = pygame_gui.elements.UILabel(
        relative_rect=time_rect,
        text="--:--",
        manager=manager,
        object_id="#clock_box"
    )
    lap_rect = pygame.Rect((WIDTH // 2 - 75, HEIGHT-100), (150, 40))
    lap_label = pygame_gui.elements.UILabel(
        relative_rect=lap_rect,
        text="--:--",
        manager=manager,
        object_id="#lap_label"
    )

    best_lap_rect = pygame.Rect((WIDTH // 2 - 75, HEIGHT-60), (150, 40))
    best_lap_label = pygame_gui.elements.UILabel(
        relative_rect=best_lap_rect,
        text="--:--",
        manager=manager,
        object_id="#best_lap_label"
    )
    timer = Stopwatch()
    l_button.when_pressed = timer.toggle
    r_button.when_pressed = timer.new_lap
    temp_rect = pygame.Rect((WIDTH // 2 - 275, 10), (150, 40))
    temp_label = pygame_gui.elements.UILabel(
        relative_rect=temp_rect,
        text=f"CPU Temp: {cpu.temperature} °C",
        manager=manager,
        object_id="#clock_box"
    )

    fwd_rect = pygame.Rect((WIDTH // 2 + 125, 10), (150, 40))
    shutdown_rect = pygame.Rect((WIDTH // 2, HEIGHT // 2), (150, 40))

    try:
        custom_font = pygame.font.Font('fonts/Russo_One/RussoOne-Regular.ttf', 90)
        font = pygame.font.Font('fonts/Russo_One/RussoOne-Regular.ttf', 18)

    except FileNotFoundError:
        print("CustomFont.ttf not found. Using default font.")
        custom_font = pygame.font.Font(None, 90)
        font = pygame.font.SysFont(None, 30)

    clock = pygame.time.Clock()


    four_wheel_drive = False
    clean_start = False
    deactive_four_wheel(True,motor)

    if not toggle_switch.is_pressed:
        clean_start = True
    shutting_down = False
    app_is_running = True
    current_speed = 0.0
    current_rpm = 0.0
    latest_gps_speed = 0.0
    latest_rpm = 0.0
    gps_data = SharedGPSData()
    stop_event = threading.Event()
    gps_thread = threading.Thread(
        target=gps_worker, 
        args=(gps_data, stop_event),
        daemon=True)  
    gps_thread.start()

    rpm_data = SharedRPMData()
    rpm_thread = threading.Thread(
        target=rpm_worker, 
        args=(rpm_data, stop_event),
        daemon=True) 
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
        if l_button.held_time is not None and l_button.held_time > 3:
            timer.reset()
        current_time_string = datetime.datetime.now().strftime("%I:%M:%S %p")
        clock_label.set_text(current_time_string)
        temp_label.set_text(f"CPU Temp: {cpu.temperature:.0f} °C")
        lap_label.set_text(timer.get_lap_time())
        best_lap_label.set_text(timer.get_fastest_lap())
        # Independent smoothing factors for different gauge responsiveness
        speed_smoothing = 5.0  # Slower, smoother needle for GPS speed
        rpm_smoothing = 15.0   # Faster, snappier needle for Hall effect RPM
        latest_gps_speed = gps_data.get_speed()
        latest_rpm = rpm_data.get_rpm()
        current_speed += (latest_gps_speed - current_speed) * (speed_smoothing * time_delta)
        current_rpm += (latest_rpm - current_rpm) * (rpm_smoothing * time_delta)
        
        if latest_gps_speed == 0.0 and current_speed < 0.5:
            current_speed = 0.0       
        if latest_rpm == 0.0 and current_rpm < 50.0:
            current_rpm = 0.0
             

        if clean_start:
            if toggle_switch.is_pressed and not four_wheel_drive:
                print("Pressed" + current_time_string)
                if four_wheel_drive != activate_four_wheel(four_wheel_drive,motor):
                    four_wheel_drive = True
                
            elif not toggle_switch.is_pressed and four_wheel_drive:
                print("Pressed2")

                if four_wheel_drive != deactive_four_wheel(four_wheel_drive,motor):
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
        if r_button.is_pressed:
            if r_button.held_time is not None and r_button.held_time > 1:
                if not shutting_down:
                    shutting_down = True
                
                    shutdown_label = pygame_gui.elements.UILabel(
                    relative_rect=shutdown_rect,
                    text="Shutting Down in 3",
                    manager=manager,
                    object_id="#shutdown_label"
                    )
                else:
                    if r_button.held_time > 4:
                        app_is_running = False
                    else:
                        countdown = 4.0 - r_button.held_time
                        shutdown_label.set_text(f'Shutting Down in {countdown:.0f}')
            else:
                if shutting_down:
                    shutting_down = False
                    shutdown_label.kill()

        screen.fill((0, 0, 0))
        speedo.draw(screen, current_speed)
        tacho.draw(screen, current_rpm)
        
        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.update()
    stop_event.set()
    pygame.quit()
    if shutting_down:
        subprocess.run(['sudo', 'shutdown', '-h', 'now'])

if __name__ == "__main__":
    main()