import pygame
import pygame_gui
import datetime
import time
import os
from stopwatch import Stopwatch
# Assuming dash.py is in the same folder on your laptop
from dash import TextGauge, Gauge, WIDTH, HEIGHT

# --- 1. MOCK HARDWARE CLASSES ---
# These replace gpiozero and hardware inputs for testing on a PC.

class MockServo:
    def __init__(self):
        self.value = -0.25

class MockCPUTemperature:
    @property
    def temperature(self):
        return 45.0  # Static dummy temperature

class MockButton:
    def __init__(self):
        self.is_pressed = False
        self.held_time = None
        self._press_start_time = None

    def update(self, is_pressed_now):
        if is_pressed_now and not self.is_pressed:
            self.is_pressed = True
            self._press_start_time = time.time()
            self.held_time = 0.0
        elif is_pressed_now and self.is_pressed:
            self.held_time = time.time() - self._press_start_time
        else:
            self.is_pressed = False
            self.held_time = None
            self._press_start_time = None

# --- 2. HARDWARE FUNCTIONS ---

def activate_four_wheel(four_engaged, motor):
    if not four_engaged:
        print("Engaged 4WD")
        motor.value = 0.25
        four_engaged = True
    return four_engaged

def deactive_four_wheel(four_engaged, motor):
    if four_engaged:
        print("Disengaged 4WD")
        motor.value = -0.25
        four_engaged = False
    return four_engaged

# --- 3. MAIN APPLICATION ---

def main():
    # Initialize Mock Hardware
    motor = MockServo()
    r_button = MockButton()
    toggle_switch = MockButton()
    cpu = MockCPUTemperature()

    pygame.init()
    pygame.font.init()

    # Using a standard window instead of FULLSCREEN so you don't get trapped on your laptop
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Laptop GUI Test Mode")
    
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
    temp_rect = pygame.Rect((WIDTH // 2 - 275, 10), (150, 40))
    temp_label = pygame_gui.elements.UILabel(
        relative_rect=temp_rect,
        text=f"CPU Temp: {cpu.temperature} °C",
        manager=manager,
        object_id="#clock_box"
    )

    fwd_rect = pygame.Rect((WIDTH // 2 + 125, 10), (150, 40))
    shutdown_rect = pygame.Rect((WIDTH // 2 - 75, HEIGHT // 2 - 20), (150, 40))

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
    deactive_four_wheel(True, motor)

    shutting_down = False
    app_is_running = True
    
    # Mock data targets instead of threaded sensor data
    mock_gps_speed = 0.0
    mock_rpm = 0.0
    
    current_speed = 0.0
    current_rpm = 0.0

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
                    app_is_running = False

            manager.process_events(event)
            
        # --- LAPTOP KEYBOARD CONTROLS ---
        keys = pygame.key.get_pressed()
        keys2 = pygame.key.get_just_released()

        
        # Update mock hardware states based on keys
        r_button.update(keys[pygame.K_r])
        toggle_switch.update(keys[pygame.K_t])
        
        # Simulate gauges with arrow keys and W/S
        if keys[pygame.K_UP]: mock_gps_speed = min(55.0, mock_gps_speed + 0.5)
        if keys[pygame.K_DOWN]: mock_gps_speed = max(0.0, mock_gps_speed - 0.5)
        if keys[pygame.K_w]: mock_rpm = min(7000.0, mock_rpm + 150)
        if keys[pygame.K_s]: mock_rpm = max(0.0, mock_rpm - 150)
        if keys2[pygame.K_a]: timer.toggle()
        if keys2[pygame.K_d]: timer.new_lap()
        if keys2[pygame.K_r]: timer.reset()
        # --------------------------------

        current_time_string = datetime.datetime.now().strftime("%I:%M:%S %p")
        clock_label.set_text(current_time_string)
        temp_label.set_text(f"CPU Temp: {cpu.temperature:.0f} °C")
        lap_label.set_text(timer.get_lap_time())
        best_lap_label.set_text(timer.get_fastest_lap())
        speed_smoothing = 5.0  
        rpm_smoothing = 15.0   
        
        # Pull from our mock variables instead of the threads
        latest_gps_speed = mock_gps_speed
        latest_rpm = mock_rpm
        
        current_speed += (latest_gps_speed - current_speed) * (speed_smoothing * time_delta)
        current_rpm += (latest_rpm - current_rpm) * (rpm_smoothing * time_delta)
        
        if latest_gps_speed == 0.0 and current_speed < 0.5:
            current_speed = 0.0       
        if latest_rpm == 0.0 and current_rpm < 50.0:
            current_rpm = 0.0
             
        # 4WD Logic
        if not keys[pygame.K_t]: # Reset clean_start when key is released
            clean_start = True

        if clean_start:
            if toggle_switch.is_pressed and not four_wheel_drive:
                if four_wheel_drive != activate_four_wheel(four_wheel_drive, motor):
                    four_wheel_drive = True
                clean_start = False # Prevent rapid toggling on a single press
                
            elif toggle_switch.is_pressed and four_wheel_drive:
                if four_wheel_drive != deactive_four_wheel(four_wheel_drive, motor):
                    four_wheel_drive = False
                clean_start = False

        # Update 4WD UI
        if four_wheel_drive != last_fwd_state:
            if fwd_label:
                fwd_label.kill()
            if four_wheel_drive:
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
            
        # Shutdown Logic Check
        if r_button.is_pressed and r_button.held_time is not None:
            if r_button.held_time > 1.0:
                if not shutting_down:
                    shutting_down = True
                    shutdown_label = pygame_gui.elements.UILabel(
                        relative_rect=shutdown_rect,
                        text="Shutting Down in 3",
                        manager=manager,
                        object_id="#shutdown_label"
                    )
                else:
                    if r_button.held_time > 4.0:
                        app_is_running = False
                        print("TEST MODE: PC Shutdown triggered.")
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
        x_surface = font.render("GPS", True, (255, 0, 0))
            
            # Position it. Adjust the coordinates (200, 320) to put it exactly 
            # where you want it on the speedometer face.
        x_pos = 200 - (x_surface.get_width() // 2)
        y_pos = 350 
        screen.blit(x_surface, (x_pos, y_pos))
        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()