# controller/input.py

import pygame


class InputHandler:
    """Обробляє події введення (клавіатура, закриття вікна) під час гри."""

    def handle_event(self, event, game):
        # Закриття вікна
        if event.type == pygame.QUIT:
            game.running = False
            return

        if event.type != pygame.KEYDOWN:
            return

        key = event.key

        # Клавіша I — відкрити/закрити інвентар
        if key == pygame.K_i:
            game.toggle_inventory()
            return

        if key == pygame.K_TAB:
            game.toggle_inventory()
            return

        # Якщо інвентар відкритий — працюємо тільки з ним
        if game.hud.show_inventory:
            if key in (pygame.K_UP, pygame.K_w):
                game.move_inventory_selection(-1)
            elif key in (pygame.K_DOWN, pygame.K_s):
                game.move_inventory_selection(1)
            elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                game.use_selected_item()
            elif key in (pygame.K_ESCAPE, pygame.K_i):
                game.toggle_inventory()
            # не рухаємо гравця, поки інвентар відкритий
            return

        # Якщо інвентар закритий — звичайний рух / ESC
        if key == pygame.K_ESCAPE:
            # можна буде зробити паузу, поки просто вихід з гри
            game.running = False
            return

        dx, dy = 0, 0
        if key in (pygame.K_UP, pygame.K_w):
            dy = -1
        elif key in (pygame.K_DOWN, pygame.K_s):
            dy = 1
        elif key in (pygame.K_LEFT, pygame.K_a):
            dx = -1
        elif key in (pygame.K_RIGHT, pygame.K_d):
            dx = 1

        if dx != 0 or dy != 0:
            game.try_move_or_attack(dx, dy)
