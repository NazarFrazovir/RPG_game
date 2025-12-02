import pygame
import settings


class MainMenu:
    """Головне меню з вибором пунктів."""

    def __init__(self, screen_w: int, screen_h: int):
        self.screen_w = screen_w
        self.screen_h = screen_h

        self.options = ["Нова гра", "Вихід"]
        self.selected_index = 0

        self.bg_color = (10, 10, 20)
        self.title_color = (230, 230, 255)
        self.option_color = (200, 200, 200)
        self.option_selected_color = (255, 220, 120)

        self.title_font = pygame.font.SysFont(None, 80)
        self.option_font = pygame.font.SysFont(None, 40)

    def move_selection(self, direction: int):
        """direction = -1 (вгору) або +1 (вниз)."""
        self.selected_index = (self.selected_index + direction) % len(self.options)

    def get_selected_option(self) -> str:
        return self.options[self.selected_index]

    def draw(self, surface: pygame.Surface):
        surface.fill(self.bg_color)

        # назва гри
        title_surf = self.title_font.render(settings.GAME_TITLE, True, self.title_color)
        title_rect = title_surf.get_rect(center=(self.screen_w // 2, self.screen_h // 3))
        surface.blit(title_surf, title_rect)

        # опції меню
        start_y = self.screen_h // 2
        spacing = 50

        for i, text in enumerate(self.options):
            is_selected = (i == self.selected_index)
            color = self.option_selected_color if is_selected else self.option_color

            surf = self.option_font.render(text, True, color)
            rect = surf.get_rect(center=(self.screen_w // 2, start_y + i * spacing))
            surface.blit(surf, rect)

        # невеликий хінт унизу
        hint_font = pygame.font.SysFont(None, 24)
        hint_surf = hint_font.render("Стрілки ↑↓ / W,S — вибір, Enter — підтвердити", True, (180, 180, 200))
        hint_rect = hint_surf.get_rect(center=(self.screen_w // 2, self.screen_h - 40))
        surface.blit(hint_surf, hint_rect)
