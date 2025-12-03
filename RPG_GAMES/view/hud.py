# view/hud.py

import pygame
from model.item import ItemType, ItemRarity


class HUD:
    """HUD з полоскою HP, логом повідомлень і вікном інвентарю."""

    def __init__(self, player):
        self.player = player

        # розміри та позиція полоски HP
        self.bar_width = 200
        self.bar_height = 20
        self.margin = 20  # відступ від краю екрану

        # кольори
        self.color_bg = (50, 50, 50)
        self.color_hp = (200, 50, 50)
        self.color_border = (255, 255, 255)
        self.color_text = (255, 255, 255)
        self.color_log_bg = (20, 20, 20)

        # шрифт
        self.font = pygame.font.SysFont(None, 24)

        # лог повідомлень
        self.messages = []
        self.max_messages = 3

        # інвентар
        self.show_inventory = False
        self.inventory_selected_index = 0

    # ---- ЛОГ ПОВІДОМЛЕНЬ ----
    def add_message(self, text: str):
        """Додає нове повідомлення в лог (зберігаємо тільки останні N)."""
        self.messages.append(text)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    # ---- МАЛЮВАННЯ ----
    def draw(self, surface: pygame.Surface):
        """Малює HUD: HP, лог, інвентар (якщо відкритий)."""
        self._draw_hp_bar(surface)
        self._draw_messages(surface)
        if self.show_inventory:
            self._draw_inventory(surface)

    def _draw_hp_bar(self, surface: pygame.Surface):
        if self.player.max_hp <= 0:
            hp_ratio = 0
        else:
            hp_ratio = max(0, self.player.hp / self.player.max_hp)

        x = self.margin
        y = self.margin

        # фон полоски
        bg_rect = pygame.Rect(x, y, self.bar_width, self.bar_height)
        pygame.draw.rect(surface, self.color_bg, bg_rect)

        # заливка HP
        fill_width = int(self.bar_width * hp_ratio)
        fill_rect = pygame.Rect(x, y, fill_width, self.bar_height)
        pygame.draw.rect(surface, self.color_hp, fill_rect)

        # рамка
        pygame.draw.rect(surface, self.color_border, bg_rect, 2)

        # текст HP + ATK
        text = f"HP: {self.player.hp}/{self.player.max_hp}  |  ATK: {self.player.attack}  |  DEF: {self.player.defense}"
        text_surf = self.font.render(text, True, self.color_text)
        surface.blit(text_surf, (x, y + self.bar_height + 5))

    def _draw_messages(self, surface: pygame.Surface):
        """Малює останні повідомлення внизу екрана."""
        if not self.messages:
            return

        screen_w = surface.get_width()
        screen_h = surface.get_height()

        line_height = self.font.get_height() + 4
        total_height = line_height * len(self.messages) + 10

        # прямокутник фону для лога
        x = 20
        y = screen_h - total_height - 20
        bg_rect = pygame.Rect(x, y, screen_w - 40, total_height)
        pygame.draw.rect(surface, self.color_log_bg, bg_rect)
        pygame.draw.rect(surface, self.color_border, bg_rect, 1)

        # малюємо рядки зверху вниз
        cur_y = y + 5
        for msg in self.messages:
            text_surf = self.font.render(msg, True, self.color_text)
            surface.blit(text_surf, (x + 8, cur_y))
            cur_y += line_height

    def _draw_inventory(self, surface: pygame.Surface):
        """Малює вікно інвентарю по центру екрана."""
        screen_w = surface.get_width()
        screen_h = surface.get_height()

        panel_width = min(420, screen_w - 40)
        panel_height = min(320, screen_h - 40)
        x = (screen_w - panel_width) // 2
        y = (screen_h - panel_height) // 2

        panel_rect = pygame.Rect(x, y, panel_width, panel_height)
        pygame.draw.rect(surface, (15, 15, 25), panel_rect)
        pygame.draw.rect(surface, self.color_border, panel_rect, 2)

        # заголовок
        title_surf = self.font.render("Інвентар", True, self.color_text)
        surface.blit(title_surf, (x + 10, y + 10))

        # інформація про стати
        stats_text = f"HP: {self.player.hp}/{self.player.max_hp}  |  ATK: {self.player.attack}"
        stats_surf = self.font.render(stats_text, True, self.color_text)
        surface.blit(stats_surf, (x + 10, y + 35))

        equip_text = "Зброя: "
        if self.player.weapon is not None:
            equip_text += f"+{self.player.weapon.value} ATK (dur {self.player.weapon.durability})"
        else:
            equip_text += "немає"

        armor_text = "Броня: "
        if self.player.armor is not None:
            armor_text += f"+{self.player.armor.value} DEF (dur {self.player.armor.durability})"
        else:
            armor_text += "немає"

        equip_surf = self.font.render(equip_text, True, self.color_text)
        armor_surf = self.font.render(armor_text, True, self.color_text)
        surface.blit(equip_surf, (x + 10, y + 55))
        surface.blit(armor_surf, (x + 10, y + 75))


        # список предметів
        start_y = y + 100
        line_height = self.font.get_height() + 6

        inventory = self.player.inventory
        capacity = self.player.inventory_capacity

        for i in range(capacity):
            slot_y = start_y + i * line_height
            if slot_y + line_height > y + panel_height - 50:
                break  # не влазить більше рядків

            # фон для виділеного
            if i == self.inventory_selected_index:
                slot_rect = pygame.Rect(x + 8, slot_y - 2, panel_width - 16, line_height)
                pygame.draw.rect(surface, (50, 70, 110), slot_rect)

            if i < len(inventory):
                item = inventory[i]
                name = self._get_item_name(item)
                color = self._get_rarity_color(item)
            else:
                name = "(порожньо)"
                color = self.color_text

            text_surf = self.font.render(f"{i + 1}. {name}", True, color)
            surface.blit(text_surf, (x + 14, slot_y))

        # підказки
        hint_text1 = "↑/↓ — вибір, Enter — використати"
        hint_text2 = "I або Esc — закрити інвентар"
        hint1_surf = self.font.render(hint_text1, True, self.color_text)
        hint2_surf = self.font.render(hint_text2, True, self.color_text)

        surface.blit(hint1_surf, (x + 10, y + panel_height - 45))
        surface.blit(hint2_surf, (x + 10, y + panel_height - 25))


    def _get_item_name(self, item):
        """Текст назви з урахуванням типу і рідкості."""
        rarity_prefix = {
            ItemRarity.COMMON: "Звичайний",
            ItemRarity.UNCOMMON: "Хороший",
            ItemRarity.RARE: "Епічний",
            ItemRarity.LEGENDARY: "Легендарний",
        }.get(item.rarity, "Невідомий")

        if item.type == ItemType.HEAL:
            base = f"зілля лікування (+{item.value} HP)"
        elif item.type == ItemType.ATTACK:
            base = f"зілля сили (+{item.value} ATK)"
        elif item.type == ItemType.WEAPON:
            base = f"Меч"
        elif item.type == ItemType.ARMOR:
            base = f"Броня"
        else:
            base = f"<Предмет>"

        return f"[{rarity_prefix}] {base}"

    def _get_rarity_color(self, item):
        """Колір тексту для різних рідкостей."""
        if item.rarity == ItemRarity.COMMON:
            return (180, 180, 180)      # сірий
        elif item.rarity == ItemRarity.UNCOMMON:
            return (80, 200, 120)      # зелений
        elif item.rarity == ItemRarity.RARE:
            return (90, 140, 230)      # синій
        elif item.rarity == ItemRarity.LEGENDARY:
            return (240, 200, 80)      # золотий
        return self.color_text
