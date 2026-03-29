import pygame
import pygame.gfxdraw
import math

from pygame import Surface

WIDTH, HEIGHT = 800, 480
CENTER_X, CENTER_Y = WIDTH // 4, HEIGHT // 2

CENTER = (CENTER_X, CENTER_Y)
RADIUS = 180
NEEDLE_LENGTH = 135
NEEDLE_LENGTH_GAP = 100

MAX_SPEED = 55


def draw_rectangular_needle(screen, color, center_x, center_y, angle_rad, inner_radius, outer_radius, thickness):
    # 1. Find the center line points for the base and the tip
    base_mid_x = center_x + inner_radius * math.cos(angle_rad)
    base_mid_y = center_y + inner_radius * math.sin(angle_rad)

    tip_mid_x = center_x + outer_radius * math.cos(angle_rad)
    tip_mid_y = center_y + outer_radius * math.sin(angle_rad)

    # 2. Calculate the perpendicular angle to build the width
    perp_angle = angle_rad + (math.pi / 2)
    offset_x = (thickness / 2.0) * math.cos(perp_angle)
    offset_y = (thickness / 2.0) * math.sin(perp_angle)

    # 3. Calculate the 4 exact corners of the rectangular needle
    bottom_left = (base_mid_x + offset_x, base_mid_y + offset_y)
    bottom_right = (base_mid_x - offset_x, base_mid_y - offset_y)
    top_right = (tip_mid_x - offset_x, tip_mid_y - offset_y)
    top_left = (tip_mid_x + offset_x, tip_mid_y + offset_y)

    points = [bottom_left, bottom_right, top_right, top_left]

    # 4. Fill the solid rectangle and smooth the edges
    pygame.draw.polygon(screen, color, points)
    pygame.draw.aalines(screen, color, True, points)


class Gauge:
    def __init__(self, screen_w, screen_h, center_x, center_y, radius, max_value, font,scale=1):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.max_value = max_value
        self.scale = scale
        self.needle_len = int(radius * 0.75)  # Scale needle dynamically
        self.font = font

        # Each gauge generates its own transparent full-screen layer for its static parts
        self.static_bg = self._create_static_bg()

    def _create_static_bg(self):
        # Create a transparent surface for this specific gauge
        bg = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)

        # Draw the circles using this gauge's specific center
        start_angle = 135
        end_angle = 405
        self.draw_ticks(bg, end_angle, start_angle)

        pygame.draw.aacircle(bg, (50,100,100), (self.center_x,self.center_y), self.radius, 4)

        if hasattr(self, 'needle_gap'):
            pygame.draw.aacircle(bg, (50, 100, 100), (self.center_x, self.center_y), self.needle_gap, 4)
            text_surface = self.font.render("mph", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.center_x, self.center_y+50))
            bg.blit(text_surface, text_rect)


        return bg

    def draw_ticks(self, bg: Surface, end_angle: int, start_angle: int):
        tick_step = int(self.max_value / self.scale) // 11  # Adjust so we always have a clean number of ticks
        if tick_step == 0: tick_step = 1

        for value in range(0, int((self.max_value / self.scale) + 1), tick_step):
            tick_angle_deg = start_angle + (value / (self.max_value / self.scale)) * (end_angle - start_angle)
            tick_angle_rad = math.radians(tick_angle_deg)

            # --- Text Rendering ---
            text_radius = self.radius - 30
            text_x = self.center_x + text_radius * math.cos(tick_angle_rad)
            text_y = self.center_y + text_radius * math.sin(tick_angle_rad)

            text_surface = self.font.render(str(value), True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(int(text_x), int(text_y)))
            bg.blit(text_surface, text_rect)

            # --- Line Rendering (Directly to 1x background) ---
            tick_length = 12
            tick_start = self.radius - tick_length

            # Use the identical rectangular needle function to draw the tick marks!
            draw_rectangular_needle(
                bg,
                (255, 255, 255),
                self.center_x,
                self.center_y,
                tick_angle_rad,
                tick_start,
                self.radius - 2,
                3  # Thickness of the tick mark
            )

    def draw(self, screen, current_value):
        # 1. Stamp this gauge's static background

        # 2. Draw the text in the center
       # text_surface = self.custom_font.render(str(int(current_value)), True, (255, 255, 255))
       # text_rect = text_surface.get_rect(center=(self.center_x, self.center_y))
       # screen.blit(text_surface, text_rect)

        # 3. Calculate and draw the needle
        start_angle = 135
        end_angle = 405

        # Clamp the value so the needle doesn't spin backwards or past max
        clamped_value = max(0, min(current_value, self.max_value))

        angle_deg = start_angle + (clamped_value / self.max_value) * (end_angle - start_angle)
        angle_rad = math.radians(angle_deg)

        # (Assuming draw_supersampled_needle is available in this file)
        draw_rectangular_needle(
            screen, (255, 0, 0),
            self.center_x, self.center_y,
            angle_rad,
            getattr(self, 'needle_gap', 1)-1,  # Uses the gap if it exists, otherwise 0
            self.needle_len,
            3
        )
        screen.blit(self.static_bg, (0, 0))


class TextGauge(Gauge):
    def __init__(self, screen_w, screen_h, center_x, center_y, radius, max_value, font, custom_font,gap_width):
        self.custom_font = custom_font
        self.needle_len = int(radius * 0.75)
        self.needle_gap = self.needle_len - gap_width
        super().__init__(screen_w, screen_h, center_x, center_y, radius, max_value, font)




    def draw(self, screen, current_value):
        # 1. Stamp this gauge's static background
        super().draw(screen, current_value)

        # 2. Draw the text in the center
        text_surface = self.custom_font.render(str(int(current_value)), True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.center_x, self.center_y))
        screen.blit(text_surface, text_rect)


