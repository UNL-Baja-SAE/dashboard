import pygame
import math

pygame.init()
pygame.font.init()
my_font = pygame.font.SysFont(None, 30)
dail1 = "MPH"
dail2 = "RPM"
WIDTH, HEIGHT = 800, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))

MPH_dail_pos = 0

clock = pygame.time.Clock()
width, height = WIDTH // 4, HEIGHT // 2
radius = 180
needle_length = 150
speed = 0
max_speed = 55


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #speed = (speed + 0.3) % max_speed

    start_angle = 135
    end_angle = 405
    angle_deg = start_angle + (speed / max_speed) * (end_angle - start_angle)
    angle_rad = math.radians(angle_deg)

    x = width + needle_length * math.cos(angle_rad)
    y = height + needle_length * math.sin(angle_rad)
    screen.fill((0, 0, 0))

    pygame.draw.circle(screen, (50, 100, 100), (width, height), radius, 4)

    for value in range(0, max_speed + 1, 5):
        angle_deg = start_angle + (value / max_speed) * (end_angle - start_angle)
        angle_rad = math.radians(angle_deg)

        text_radius = radius - 30
        text_x = width + text_radius * math.cos(angle_rad)
        text_y = height + text_radius * math.sin(angle_rad)

        text_surface = my_font.render(str(value), True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(text_x, text_y))

        screen.blit(text_surface, text_rect)

    pygame.draw.line(screen, (255, 0, 0), (width, height), (x, y), 4)

    pygame.display.flip()

pygame.quit()
