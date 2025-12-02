# view/intro_screen.py

import pygame
import settings


class IntroScreen:
    """Екран вступу з історією гри."""

    def __init__(self, screen_w: int, screen_h: int):
        self.screen_w = screen_w
        self.screen_h = screen_h

        self.bg_color = (5, 5, 15)
        self.text_color = (230, 230, 230)
        self.box_color = (20, 20, 40)
        self.border_color = (120, 120, 180)

        self.font = pygame.font.SysFont(None, 32)
        self.lines = settings.INTRO_LINES

    def draw(self, surface: pygame.Surface):
        surface.fill(self.bg_color)

        # заголовок
        title_font = pygame.font.SysFont(None, 56)
        title_surf = title_font.render("Вступ", True, (240, 240, 255))
        title_rect = title_surf.get_rect(center=(self.screen_w // 2, self.screen_h // 5))
        surface.blit(title_surf, title_rect)

        # прямокутник з текстом
        box_width = self.screen_w * 0.8
        box_height = self.screen_h * 0.5
        box_x = (self.screen_w - box_width) // 2
        box_y = (self.screen_h - box_height) // 2

        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(surface, self.box_color, box_rect)
        pygame.draw.rect(surface, self.border_color, box_rect, 2)

        # текст лініями
        line_height = self.font.get_height() + 6
        cur_y = box_y + 20

        for line in self.lines:
            surf = self.font.render(line, True, self.text_color)
            rect = surf.get_rect(center=(self.screen_w // 2, cur_y))
            surface.blit(surf, rect)
            cur_y += line_height

        # хінт унизу
        hint_font = pygame.font.SysFont(None, 24)
        hint_surf = hint_font.render("Натисни будь-яку клавішу, щоб продовжити...", True, (200, 200, 220))
        hint_rect = hint_surf.get_rect(center=(self.screen_w // 2, self.screen_h - 40))
        surface.blit(hint_surf, hint_rect)
