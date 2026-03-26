import pygame
import math

WIDTH, HEIGHT = 800, 480
CENTER_X, CENTER_Y = WIDTH // 4, HEIGHT // 2
RADIUS = 180
NEEDLE_LENGTH = 150
MAX_SPEED = 55

def draw_speedometer(screen, font, speed):
    start_angle = 135
    end_angle = 405

    speed = max(0, min(speed, MAX_SPEED))

    angle_deg = start_angle + (speed / MAX_SPEED) * (end_angle - start_angle)
    angle_rad = math.radians(angle_deg)

    needle_x = CENTER_X + NEEDLE_LENGTH * math.cos(angle_rad)
    needle_y = CENTER_Y + NEEDLE_LENGTH * math.sin(angle_rad)

    screen.fill((0, 0, 0))
    pygame.draw.circle(screen, (50, 100, 100), (CENTER_X, CENTER_Y), RADIUS, 4)

    for value in range(0, MAX_SPEED + 1, 5):
        tick_angle_deg = start_angle + (value / MAX_SPEED) * (end_angle - start_angle)
        tick_angle_rad = math.radians(tick_angle_deg)

        text_radius = RADIUS - 30
        text_x = CENTER_X + text_radius * math.cos(tick_angle_rad)
        text_y = CENTER_Y + text_radius * math.sin(tick_angle_rad)

        text_surface = font.render(str(value), True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(text_x, text_y))
        screen.blit(text_surface, text_rect)

    pygame.draw.line(screen, (255, 0, 0), (CENTER_X, CENTER_Y), (needle_x, needle_y), 4)
