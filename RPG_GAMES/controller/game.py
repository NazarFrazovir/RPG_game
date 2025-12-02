import sys
import pygame
from enum import Enum, auto
import random


import settings
from model.dungeon import DungeonMap
from model.player import Player
from model.enemy import Enemy
from model.item import Item, ItemType, ItemRarity
from view.renderer import Renderer
from view.hud import HUD
from view.menu import MainMenu
from view.intro_screen import IntroScreen
from .input import InputHandler
from pygame import mixer, mixer_music


class GameState(Enum):
    MENU = auto()
    INTRO = auto()
    PLAYING = auto()


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        # --- Інформація про екран ---
        info = pygame.display.Info()
        screen_w, screen_h = info.current_w, info.current_h

        self.screen = pygame.display.set_mode(
            (screen_w, screen_h), pygame.FULLSCREEN
        )
        pygame.display.set_caption(settings.GAME_TITLE)

        # --- Стан гри ---
        self.state = GameState.MENU

        # одразу включаємо музику меню
        self.play_menu_music()

        # --- Меню та вступ ---
        self.menu = MainMenu(screen_w, screen_h)
        self.intro_screen = IntroScreen(screen_w, screen_h)

        # --- Модель: карта, гравець, вороги, предмети ---
        self.dungeon = DungeonMap(settings.LEVEL_MAP)
        start_x, start_y = self.dungeon.find_player_start()
        self.player = Player(start_x, start_y)

        # Вороги
        enemy_positions = self.dungeon.find_enemy_positions()
        self.enemies = [Enemy(x, y) for x, y in enemy_positions]

        # Предмети
        self.items = []
        for x, y, ch in self.dungeon.find_item_positions():
            rarity = self.get_random_rarity()

            if ch == "H":
                heal_value = self.get_heal_value_by_rarity(rarity)
                self.items.append(
                    Item(x, y, ItemType.HEAL, value=heal_value, rarity=rarity)
                )

            elif ch == "A":
                atk_value = self.get_attack_value_by_rarity(rarity)
                self.items.append(
                    Item(x, y, ItemType.ATTACK, value=atk_value, rarity=rarity)
                )

            elif ch == "W":
                value, dur = self.get_weapon_stats_by_rarity(rarity)
                self.items.append(
                    Item(x, y, ItemType.WEAPON, value=value,
                         rarity=rarity, durability=dur)
                )

            elif ch == "R":
                value, dur = self.get_armor_stats_by_rarity(rarity)
                self.items.append(
                    Item(x, y, ItemType.ARMOR, value=value,
                         rarity=rarity, durability=dur)
                )

        # --- Розрахунок TILE_SIZE під карту ---
        tile_size = min(
            screen_w // self.dungeon.width,
            screen_h // self.dungeon.height
        )
        if tile_size <= 0:
            tile_size = 32

        settings.TILE_SIZE = tile_size

        map_w = self.dungeon.width * tile_size
        map_h = self.dungeon.height * tile_size

        offset_x = (screen_w - map_w) // 2
        offset_y = (screen_h - map_h) // 2

        # HUD та Renderer (для PLAYING)
        self.hud = HUD(self.player)
        self.hud.add_message("Ласкаво просимо до підземелля!")

        self.renderer = Renderer(
            self.screen, self.dungeon, self.player,
            self.enemies, self.items,
            self.hud, offset_x=offset_x, offset_y=offset_y
        )

        # Controller
        self.input_handler = InputHandler()

        self.clock = pygame.time.Clock()
        self.running = True

    # ---------- Головний цикл ----------
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()  # <- малюємо через Game.draw, а не напряму Renderer.draw
            self.clock.tick(settings.FPS)

        # ---------- МУЗИКА ----------
    def play_menu_music(self):
        """Включити музику головного меню (по колу)."""
        try:
            pygame.mixer.music.load("sound/main_menu.mp3")
            pygame.mixer.music.set_volume(0.5)  #
            pygame.mixer.music.play(-1)  # -1 = лупити безкінечно
        except Exception as e:
            print(f"[WARN] Не вдалося завантажити музику меню: {e}")

    def stop_music(self):
        """Плавно зупинити будь-яку поточну музику."""
        pygame.mixer.music.fadeout(800)  # мілісекунд

    def go_to_menu(self):
        """Перехід у головне меню + включення музики."""
        self.state = GameState.MENU
        self.play_menu_music()
    # ---------- Обробка подій ----------
    def handle_events(self):
        for event in pygame.event.get():
            # спільне: вихід через хрестик
            if event.type == pygame.QUIT:
                self.running = False
                return

            # ESC
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.state == GameState.PLAYING:
                    # з гри → в меню
                    self.go_to_menu()
                else:
                    # з меню / інтро → вихід з гри
                    self.running = False
                return

            # обробка по станах
            if self.state == GameState.MENU:
                self.handle_menu_event(event)
            elif self.state == GameState.INTRO:
                self.handle_intro_event(event)
            elif self.state == GameState.PLAYING:
                self.input_handler.handle_event(event, self)

    def handle_menu_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_UP, pygame.K_w):
            self.menu.move_selection(-1)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.menu.move_selection(1)
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            option = self.menu.get_selected_option()
            if option == "Нова гра":
                self.start_new_game()
                self.state = GameState.INTRO
            elif option == "Вихід":
                self.running = False

    def handle_intro_event(self, event):
        # будь-яка клавіша → у гру
        if event.type == pygame.KEYDOWN:
            self.state = GameState.PLAYING

    # ---------- Ігрова логіка ----------
    def start_new_game(self):
        """Скидаємо стати, відновлюємо монстрів і предмети."""
        self.stop_music()
        start_x, start_y = self.dungeon.find_player_start()
        self.player.x = start_x
        self.player.y = start_y
        self.player.hp = self.player.max_hp
        self.hud.messages.clear()
        self.hud.add_message("Ти прокинувся в підземеллі...")

        # відновимо монстрів
        self.enemies = [Enemy(x, y) for x, y in self.dungeon.find_enemy_positions()]
        self.renderer.enemies = self.enemies

        # відновимо предмети
        self.items = []
        for x, y, ch in self.dungeon.find_item_positions():
            rarity = self.get_random_rarity()

            if ch == "H":
                heal_value = self.get_heal_value_by_rarity(rarity)
                self.items.append(
                    Item(x, y, ItemType.HEAL, value=heal_value, rarity=rarity)
                )

            elif ch == "A":
                atk_value = self.get_attack_value_by_rarity(rarity)
                self.items.append(
                    Item(x, y, ItemType.ATTACK, value=atk_value, rarity=rarity)
                )

            elif ch == "W":
                value, dur = self.get_weapon_stats_by_rarity(rarity)
                self.items.append(
                    Item(x, y, ItemType.WEAPON, value=value,
                         rarity=rarity, durability=dur)
                )

            elif ch == "R":
                value, dur = self.get_armor_stats_by_rarity(rarity)
                self.items.append(
                    Item(x, y, ItemType.ARMOR, value=value,
                         rarity=rarity, durability=dur)
                )

        self.renderer.items = self.items

    def get_random_rarity(self) -> ItemRarity:
        """Випадкова рідкість з вагами."""
        r = random.random()
        if r < 0.6:
            return ItemRarity.COMMON
        elif r < 0.85:
            return ItemRarity.UNCOMMON
        elif r < 0.95:
            return ItemRarity.RARE
        else:
            return ItemRarity.LEGENDARY

    def get_weapon_stats_by_rarity(self, rarity: ItemRarity):
        """Повертає (attack_bonus, durability) для зброї."""
        if rarity == ItemRarity.COMMON:
            return 1, 10
        elif rarity == ItemRarity.UNCOMMON:
            return 2, 15
        elif rarity == ItemRarity.RARE:
            return 3, 20
        elif rarity == ItemRarity.LEGENDARY:
            return 5, 30
        return 1, 8

    def get_armor_stats_by_rarity(self, rarity: ItemRarity):
        """Повертає (defense_bonus, durability) для броні."""
        if rarity == ItemRarity.COMMON:
            return 1, 12
        elif rarity == ItemRarity.UNCOMMON:
            return 2, 18
        elif rarity == ItemRarity.RARE:
            return 3, 24
        elif rarity == ItemRarity.LEGENDARY:
            return 5, 35
        return 1, 10

    def get_heal_value_by_rarity(self, rarity: ItemRarity) -> int:
        """Скільки HP відновлює зілля залежно від рідкості."""
        if rarity == ItemRarity.COMMON:
            return 5
        elif rarity == ItemRarity.UNCOMMON:
            return 10
        elif rarity == ItemRarity.RARE:
            return 15
        elif rarity == ItemRarity.LEGENDARY:
            return 20
        return 5

    def get_attack_value_by_rarity(self, rarity: ItemRarity) -> int:
        """Скільки ATK дає зілля сили залежно від рідкості."""
        if rarity == ItemRarity.COMMON:
            return 1
        elif rarity == ItemRarity.UNCOMMON:
            return 2
        elif rarity == ItemRarity.RARE:
            return 3
        elif rarity == ItemRarity.LEGENDARY:
            return 5
        return 1


    def try_move_or_attack(self, dx: int, dy: int):
        """Рух або атака по ворогу в напрямку."""
        if self.state != GameState.PLAYING:
            return

        new_x = self.player.x + dx
        new_y = self.player.y + dy

        if not self.dungeon.is_walkable(new_x, new_y):
            return

        target_enemy = None
        for enemy in self.enemies:
            if enemy.is_alive() and enemy.x == new_x and enemy.y == new_y:
                target_enemy = enemy
                break

        if target_enemy:
            self.handle_combat(target_enemy)
        else:
            # рух
            self.player.move(dx, dy, self.dungeon)
            # перевірка, чи наступив на предмет
            self.check_item_pickup()

    def handle_combat(self, enemy: Enemy):
        """Гравець атакує ворога, ворог (якщо живий) б'є у відповідь."""
        enemy.take_damage(self.player.attack)
        self.hud.add_message("Ти вдарив монстра!")

        # 🔹 знос зброї
        if self.player.weapon is not None:
            self.player.weapon.durability -= 1
            if self.player.weapon.durability <= 0:
                broken = self.player.weapon
                self.player.attack -= broken.value
                self.player.weapon = None
                self.hud.add_message("Твоя зброя зламалася!")

        if not enemy.is_alive():
            self.hud.add_message("Монстр переможений!")
            return

        self.player.take_damage(enemy.attack)
        self.hud.add_message("Монстр вдарив у відповідь!")

        # 🔹 знос броні
        if self.player.armor is not None:
            self.player.armor.durability -= 1
            if self.player.armor.durability <= 0:
                broken = self.player.armor
                self.player.defense -= broken.value
                self.player.armor = None
                self.hud.add_message("Твоя броня зламалася!")

        if not self.player.is_alive():
            self.hud.add_message("Ви загинули...")
            self.go_to_menu()

    def check_item_pickup(self):
        """Перевіряє, чи на клітинці гравця є предмет, і кладе його в інвентар."""
        inventory = self.player.inventory

        for item in list(self.items):
            if item.x == self.player.x and item.y == self.player.y:
                if len(inventory) >= self.player.inventory_capacity:
                    self.hud.add_message("Інвентар повний! Не можу підняти предмет.")
                    continue

                inventory.append(item)
                self.items.remove(item)

                from model.item import ItemType
                if item.type == ItemType.HEAL:
                    self.hud.add_message("Підібрано зілля лікування.")
                elif item.type == ItemType.ATTACK:
                    self.hud.add_message("Підібрано зілля сили.")
                elif item.type == ItemType.WEAPON:
                    self.hud.add_message("Підібрано зброю.")
                elif item.type == ItemType.ARMOR:
                    self.hud.add_message("Підібрано броню.")
                else:
                    self.hud.add_message("Підібрано предмет.")

    # ---------- ІНВЕНТАР ----------
    def toggle_inventory(self):
        """Відкрити/закрити інвентар."""
        if not self.hud.show_inventory:
            self.hud.show_inventory = True
            # підганяємо вибраний індекс
            if self.player.inventory:
                if self.hud.inventory_selected_index >= len(self.player.inventory):
                    self.hud.inventory_selected_index = len(self.player.inventory) - 1
            else:
                self.hud.inventory_selected_index = 0
        else:
            self.hud.show_inventory = False

    def move_inventory_selection(self, delta: int):
        """Змінюємо виділений слот у інвентарі."""
        inv = self.player.inventory
        if not inv:
            self.hud.inventory_selected_index = 0
            return

        n = len(inv)
        idx = (self.hud.inventory_selected_index + delta) % n
        self.hud.inventory_selected_index = idx

    def use_selected_item(self):
        """Використати виділений у інвентарі предмет."""
        inv = self.player.inventory
        if not inv:
            self.hud.add_message("Інвентар порожній.")
            return

        idx = self.hud.inventory_selected_index
        if idx < 0 or idx >= len(inv):
            return

        item = inv[idx]
        from model.item import ItemType

        if item.type == ItemType.HEAL:
            old_hp = self.player.hp
            self.player.hp = min(self.player.max_hp, self.player.hp + item.value)
            gained = self.player.hp - old_hp
            if gained > 0:
                self.hud.add_message(f"Використано зілля: +{gained} HP")
            else:
                self.hud.add_message("HP вже повне.")
            del inv[idx]

        elif item.type == ItemType.ATTACK:
            self.player.attack += item.value
            self.hud.add_message(f"Використано зілля сили: +{item.value} ATK")
            del inv[idx]

        elif item.type == ItemType.WEAPON:
            self.player.equip_weapon(item)
            self.hud.add_message(
                f"Екіповано зброю (+{item.value} ATK, durability {item.durability})."
            )
            # зброю прибираємо з інвентарю, тепер вона в слоті weapon
            del inv[idx]

        elif item.type == ItemType.ARMOR:
            self.player.equip_armor(item)
            self.hud.add_message(
                f"Екіповано броню (+{item.value} DEF, durability {item.durability})."
            )
            del inv[idx]

        else:
            self.hud.add_message("Нічого не сталося...")

        if self.hud.inventory_selected_index >= len(inv):
            self.hud.inventory_selected_index = max(0, len(inv) - 1)

    def update_enemies_ai(self):
        """Простий AI: скелети крокують до гравця.
        Якщо хоч раз тебе побачили в радіусі — переслідують завжди.
        """
        for enemy in self.enemies:
            if not enemy.is_alive():
                continue

            # чекаємо кулдаун руху
            if enemy.move_timer > 0:
                continue

            enemy.move_timer = enemy.move_cooldown

            dx = self.player.x - enemy.x
            dy = self.player.y - enemy.y
            dist = abs(dx) + abs(dy)

            # радіус, з якого ВПЕРШЕ помічають гравця
            chase_radius = 4  # твоє число тут

            # 🔹 якщо ще не агро і гравець далеко — ігноримо
            if not enemy.aggro and dist > chase_radius:
                continue

            # 🔹 якщо гравця хоч раз побачили в радіусі — запам’ятали
            if dist <= chase_radius:
                enemy.aggro = True

            # якщо раптом опинились на тій самій клітинці
            if dist == 0:
                self.enemy_attack(enemy)
                continue

            # вибираємо напрямок кроку (до гравця)
            step_x, step_y = 0, 0
            if abs(dx) >= abs(dy) and dx != 0:
                step_x = 1 if dx > 0 else -1
            elif dy != 0:
                step_y = 1 if dy > 0 else -1

            target_x = enemy.x + step_x
            target_y = enemy.y + step_y

            # атака, якщо впритул заходить на клітинку гравця
            if target_x == self.player.x and target_y == self.player.y:
                self.enemy_attack(enemy)
                continue

            # не проходимо крізь стіни
            if not self.dungeon.is_walkable(target_x, target_y):
                continue

            # не ліземо в іншого ворога
            blocked = False
            for other in self.enemies:
                if other is enemy or not other.is_alive():
                    continue
                if other.x == target_x and other.y == target_y:
                    blocked = True
                    break
            if blocked:
                continue

            # рухаємо ворога
            enemy.x = target_x
            enemy.y = target_y

            # напрямок для анімації
            if step_x > 0:
                enemy.direction = "right"
            elif step_x < 0:
                enemy.direction = "left"
            elif step_y > 0:
                enemy.direction = "down"
            elif step_y < 0:
                enemy.direction = "up"

            enemy.start_walk()

    def update(self):
        if self.state != GameState.PLAYING:
            return

        # 🔹 Якщо відкритий інвентар — гра "на паузі"
        if self.hud.show_inventory:
            return

        # Звичайний апдейт, коли інвентар закритий
        self.player.update()

        for enemy in self.enemies:
            enemy.update()

        self.update_enemies_ai()

    def enemy_attack(self, enemy: Enemy):
        """Скелет б'є гравця, без зустрічного удару."""
        self.player.take_damage(enemy.attack)
        self.hud.add_message("Скелет вдарив тебе!")

        if not self.player.is_alive():
            self.hud.add_message("Ти загинув...")
            self.go_to_menu()

    # ---------- Малювання ----------
    def draw(self):
        if self.state == GameState.MENU:
            self.menu.draw(self.screen)
        elif self.state == GameState.INTRO:
            self.intro_screen.draw(self.screen)
        elif self.state == GameState.PLAYING:
            self.renderer.draw()

        pygame.display.flip()








