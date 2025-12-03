import pygame
import settings
import os
from model.item import ItemType, ItemRarity


class Renderer:
    """Малювання карти, гравця (зі спрайт-листом), ворогів, предметів і HUD."""

    def __init__(self, screen, dungeon, player, enemies, items, hud, offset_x=0, offset_y=0):
        self.screen = screen
        self.dungeon = dungeon
        self.player = player
        self.enemies = enemies   # список Enemy
        self.items = items       # список Item
        self.hud = hud

        self.offset_x = offset_x
        self.offset_y = offset_y

        # Кольори (RGB)
        self.COLOR_FLOOR = (30, 30, 30)
        self.COLOR_WALL = (100, 100, 100)
        self.COLOR_BG = (0, 0, 0)

        # ---- СПРАЙТИ ----
        # запасний одиночний спрайт героя (якщо sheet не знайдеться)
        self.hero_image = self.load_sprite("assets/hero.png")
        self.enemy_image = self.load_sprite("assets/enemy.png")
        self.heal_image = self.load_sprite("assets/heal_potion.png")
        self.attack_image = self.load_sprite("assets/damage_potion.png")

        # sprite sheet героя
        self.hero_frames = self.load_hero_sheet(
            "assets/hero_sheet.png",
            cols=3,  # кадри: idle, walk1, walk2
            rows=4   # напрями: down, left, right, up
        )

        # sprite sheet ворога (1 рядок, 3 кадри)
        self.enemy_frames = self.load_enemy_sheet(
            "assets/enemy_sheet.png",
            cols=3,
            rows=4
        )
        self.enemy_anim_timer = 0
        self.enemy_anim_index = 0
        self.enemy_anim_speed = 10  # чим менше, тим швидше анімація

        # окремі спрайти для зброї по рідкості
        self.weapon_images = {
            ItemRarity.COMMON: self.load_sprite("assets/sword_common_32x32.png"),
            ItemRarity.UNCOMMON: self.load_sprite("assets/sword_uncommon_32x32.png"),
            ItemRarity.RARE: self.load_sprite("assets/sword_rare_32x32.png"),
            ItemRarity.LEGENDARY: self.load_sprite("assets/sword_legendary_32x32.png"),
        }

        # окремі спрайти для броні по рідкості
        self.armor_images = {
            ItemRarity.COMMON: self.load_sprite("assets/armor_common_32x32.png"),
            ItemRarity.UNCOMMON: self.load_sprite("assets/armor_uncommon_32x32.png"),
            ItemRarity.RARE: self.load_sprite("assets/armor_rare_32x32.png"),
            ItemRarity.LEGENDARY: self.load_sprite("assets/armor_legendary_32x32.png"),
        }

        # тайлові спрайти
        self.floor_image = self.load_sprite("assets/floor.png")
        self.wall_image = self.load_sprite("assets/wall.png")
        self.door_closed_image = self.load_sprite("assets/door_closed.png")
        self.door_open_image = self.load_sprite("assets/door_open.png")

        # стан дверей (оновлюється з Game)
        self.doors_open = False



    # ---------- завантаження спрайтів ----------

    def load_sprite(self, path: str):
        """Завантажує картинку і масштабує під TILE_SIZE. Якщо не вийшло — повертає None."""
        if not os.path.exists(path):
            print(f"[WARN] Sprite not found: {path}")
            return None

        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(
                img,
                (settings.TILE_SIZE, settings.TILE_SIZE)
            )
            return img
        except Exception as e:
            print(f"[ERROR] Failed to load sprite {path}: {e}")
            return None

    def load_hero_sheet(self, path: str, cols: int, rows: int):
        """Ріже sprite sheet героя на кадри: dict[(direction, frame)] = Surface."""
        if not os.path.exists(path):
            print(f"[WARN] Hero sheet not found: {path}")
            return None

        try:
            sheet = pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"[ERROR] Failed to load hero sheet {path}: {e}")
            return None

        sheet_w, sheet_h = sheet.get_width(), sheet.get_height()
        frame_w = sheet_w // cols
        frame_h = sheet_h // rows

        frames = {}

        # порядок рядків: 0-down, 1-left, 2-right, 3-up
        row_dir = {
            0: "down",
            1: "left",
            2: "right",
            3: "up",
        }

        for row in range(rows):
            direction = row_dir.get(row, "down")
            for col in range(cols):
                rect = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
                frame_surf = sheet.subsurface(rect).copy()
                # масштабуємо до TILE_SIZE
                frame_surf = pygame.transform.smoothscale(
                    frame_surf,
                    (settings.TILE_SIZE, settings.TILE_SIZE)
                )
                frames[(direction, col)] = frame_surf

        print(f"[INFO] Loaded hero sheet with {len(frames)} frames")
        return frames


    def load_enemy_sheet(self, path: str, cols: int, rows: int):
        """Ріже sprite sheet ворогів: dict[(direction, frame)] = Surface."""
        if not os.path.exists(path):
            print(f"[WARN] Enemy sheet not found: {path}")
            return None

        try:
            sheet = pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"[ERROR] Failed to load enemy sheet {path}: {e}")
            return None

        sheet_w, sheet_h = sheet.get_width(), sheet.get_height()
        frame_w = sheet_w // cols
        frame_h = sheet_h // rows

        frames = {}

        # 0-down, 1-left, 2-right, 3-up
        row_dir = {
            0: "down",
            1: "left",
            2: "right",
            3: "up",
        }

        for row in range(rows):
            direction = row_dir.get(row, "down")
            for col in range(cols):
                rect = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
                frame_surf = sheet.subsurface(rect).copy()
                frame_surf = pygame.transform.smoothscale(
                    frame_surf,
                    (settings.TILE_SIZE, settings.TILE_SIZE)
                )
                frames[(direction, col)] = frame_surf

        print(f"[INFO] Loaded enemy sheet with {len(frames)} frames")
        return frames


    # ---------- малювання ----------

    def draw(self):
        self.screen.fill(self.COLOR_BG)
        tile = settings.TILE_SIZE

        # ---- Малюємо карту тайлами ----
        for y, row in enumerate(self.dungeon.level_data):
            for x, ch in enumerate(row):
                draw_x = self.offset_x + x * tile
                draw_y = self.offset_y + y * tile

                # 1) Спочатку — ПІДЛОГА майже всюди
                if self.floor_image:
                    self.screen.blit(self.floor_image, (draw_x, draw_y))
                else:
                    floor_rect = pygame.Rect(draw_x, draw_y, tile, tile)
                    pygame.draw.rect(self.screen, self.COLOR_FLOOR, floor_rect)

                # 2) Поверх — стіни / двері / інші особливі тайли
                if ch == "#":
                    # стіна
                    if self.wall_image:
                        self.screen.blit(self.wall_image, (draw_x, draw_y))
                    else:
                        wall_rect = pygame.Rect(draw_x, draw_y, tile, tile)
                        pygame.draw.rect(self.screen, self.COLOR_WALL, wall_rect)

                elif ch == "E":
                    # двері (вихід)
                    img = self.door_open_image if self.doors_open else self.door_closed_image
                    if img:
                        self.screen.blit(img, (draw_x, draw_y))
                    else:
                        door_rect = pygame.Rect(draw_x, draw_y, tile, tile)
                        color = (200, 150, 40) if self.doors_open else (100, 80, 30)
                        pygame.draw.rect(self.screen, color, door_rect)

                # інші символи (., P, M, H, A, W, R...) — підлога вже намальована, нічого не робимо



        # ---- Малюємо предмети ----
        for item in self.items:
            draw_x = self.offset_x + item.x * tile
            draw_y = self.offset_y + item.y * tile

            # рамка по рідкості
            border_color = self._get_item_rarity_color(item)
            border_rect = pygame.Rect(draw_x + 2, draw_y + 2, tile - 4, tile - 4)
            pygame.draw.rect(self.screen, border_color, border_rect, 2)

            # сам спрайт
            if item.type == ItemType.HEAL and self.heal_image:
                self.screen.blit(self.heal_image, (draw_x, draw_y))

            elif item.type == ItemType.ATTACK and self.attack_image:
                self.screen.blit(self.attack_image, (draw_x, draw_y))

            elif item.type == ItemType.WEAPON:
                img = self.weapon_images.get(item.rarity)
                if img is not None:
                    self.screen.blit(img, (draw_x, draw_y))
                else:
                    size = int(tile * 0.5)
                    item_rect = pygame.Rect(
                        draw_x + (tile - size) // 2,
                        draw_y + (tile - size) // 2,
                        size,
                        size
                    )
                    pygame.draw.rect(self.screen, (200, 200, 200), item_rect)

            elif item.type == ItemType.ARMOR:
                img = self.armor_images.get(item.rarity)
                if img is not None:
                    self.screen.blit(img, (draw_x, draw_y))
                else:
                    size = int(tile * 0.5)
                    item_rect = pygame.Rect(
                        draw_x + (tile - size) // 2,
                        draw_y + (tile - size) // 2,
                        size,
                        size
                    )
                    pygame.draw.rect(self.screen, (180, 180, 200), item_rect)

            else:
                # на всякий випадок — невідомий тип
                size = int(tile * 0.5)
                item_rect = pygame.Rect(
                    draw_x + (tile - size) // 2,
                    draw_y + (tile - size) // 2,
                    size,
                    size
                )
                pygame.draw.rect(self.screen, (220, 200, 80), item_rect)

        # ---- Анімація ворогів (оновлюємо кадр) ----
        if self.enemy_frames:
            self.enemy_anim_timer += 1
            if self.enemy_anim_timer >= self.enemy_anim_speed:
                self.enemy_anim_timer = 0
                self.enemy_anim_index = (self.enemy_anim_index + 1) % len(self.enemy_frames)

        # ---- Малюємо ворогів ----
        for enemy in self.enemies:
            if not enemy.is_alive():
                continue

            draw_x = self.offset_x + enemy.x * tile
            draw_y = self.offset_y + enemy.y * tile

            frame = None
            if self.enemy_frames:
                # 0 = idle, 1/2 = кроки
                if enemy.walk_timer == 0:
                    frame_idx = 0
                else:
                    frame_idx = 1 if enemy.step_phase == 0 else 2

                frame = self.enemy_frames.get((enemy.direction, frame_idx))

            if frame is not None:
                self.screen.blit(frame, (draw_x, draw_y))
            elif self.enemy_image:
                self.screen.blit(self.enemy_image, (draw_x, draw_y))
            else:
                rect = pygame.Rect(draw_x, draw_y, tile, tile)
                pygame.draw.rect(self.screen, (200, 60, 60), rect)

        # ---- Малюємо гравця зі спрайт-листа ----
        player_x = self.offset_x + self.player.x * tile
        player_y = self.offset_y + self.player.y * tile

        # невеликий зсув для "підстрибування"
        off_x, off_y = self.player.get_draw_offset()
        player_x += off_x
        player_y += off_y

        hero_img = self.get_hero_frame()

        if hero_img:
            self.screen.blit(hero_img, (player_x, player_y))
        elif self.hero_image:
            # fallback, якщо нема sheet'а
            self.screen.blit(self.hero_image, (player_x, player_y))
        else:
            rect = pygame.Rect(player_x, player_y, tile, tile)
            pygame.draw.rect(self.screen, (200, 200, 50), rect)

        # ---- HUD поверх ----
        self.hud.draw(self.screen)
        # flip робиться в Game.draw()

    def get_hero_frame(self):
        """Обирає кадр героя залежно від напрямку і walk_timer."""
        if not self.hero_frames:
            return None

        direction = self.player.direction

        # 0 = idle, 1 і 2 = кроки
        if self.player.walk_timer == 0:
            frame_idx = 0
        else:
            # проста логіка: поки таймер великий -> кадр 1, потім кадр 2
            # можна погратися з порогом для іншого ефекту
            if self.player.walk_timer > 5:
                frame_idx = 1
            else:
                frame_idx = 2

        return self.hero_frames.get((direction, frame_idx))

    def _get_item_rarity_color(self, item):
        if item.rarity == ItemRarity.COMMON:
            return (120, 120, 120)
        elif item.rarity == ItemRarity.UNCOMMON:
            return (60, 180, 100)
        elif item.rarity == ItemRarity.RARE:
            return (70, 120, 220)
        elif item.rarity == ItemRarity.LEGENDARY:
            return (230, 180, 40)
        return (200, 200, 200)

