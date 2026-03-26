import pygame
from gps import receive_data
from dash import draw_speedometer, WIDTH, HEIGHT

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.SysFont(None, 30)
clock = pygame.time.Clock()

def main():
    running = True
    current_speed = 0.0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        gps_speed = receive_data()
        if gps_speed is not None:
            current_speed = gps_speed

        draw_speedometer(screen, font, current_speed)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()