import pygame
import pygame_gui
import datetime
from gps import receive_data, is_connected
from dash import TextGauge,Gauge, WIDTH, HEIGHT

pygame.init()
pygame.font.init()

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



def main():
    running = True
    current_speed = 0.0
    current_rpm = 0.0
    speedo = TextGauge(WIDTH, HEIGHT, center_x=200, center_y=240, radius=160, max_value=55, font=font,
                   custom_font=custom_font,gap_width=35)
    tacho = Gauge(WIDTH,HEIGHT,center_x=600, center_y=240, radius=160, max_value=7000, font=font,scale=1000)
    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


            manager.process_events(event)
        current_time_string = datetime.datetime.now().strftime("%I:%M %p")

        # Update the label
        clock_label.set_text(current_time_string)

        if is_connected():
            gps_speed = receive_data()
        else:
            gps_speed = 0.0
        pressed_keys = pygame.key.get_pressed()  #


        if pressed_keys[pygame.K_UP]:
            current_speed += .5
            current_rpm += 100


        #if gps_speed is not None:
         #   current_speed = gps_speed
        screen.fill((0, 0, 0))
        speedo.draw(screen, current_speed)
        tacho.draw(screen, current_rpm)
        current_speed = current_speed - 0.25 if current_speed > 0.25 else 0
        current_rpm = current_rpm - 50 if current_rpm > 50 else 0
        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.update()
        #clock.tick(30)

    pygame.quit()



if __name__ == "__main__":
    main()