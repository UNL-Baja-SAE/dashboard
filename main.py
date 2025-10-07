import pygame
import random

pygame.init()
pygame.font.init() # you have to call this at the start, 
                   # if you want to use this module.
my_font = pygame.font.SysFont('Comic Sans MS', 30)
# Screen setup
WIDTH, HEIGHT = 800, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Ball Example")
clock = pygame.time.Clock()

# Ball properties
ball_pos = pygame.Vector2(0, 0)  # starting position
ball_radius = 20
ball_velocity = pygame.Vector2(200, 150)  # pixels per second

running = True
while running:
    dt = clock.tick(60) / 1000  # delta time in seconds (frame-rate independent)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move the ball
    ball_pos += ball_velocity * dt

    # Bounce off walls
   

    # Draw everything
    screen.fill((0, 0, 0))  # black background
    pygame.draw.circle(screen, (255, 0, 0), ball_pos, ball_radius)  # red ball
    text_surface = my_font.render(f'{ random.randint(1,10) }', False, (255, 255, 255))
    screen.blit(text_surface, (0,0))
    pygame.display.flip()

pygame.quit()
