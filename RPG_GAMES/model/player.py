# model/player.py

from .dungeon import DungeonMap


class Player:
    def __init__(self, x: int, y: int):
        # координати в тайлах
        self.x = x
        self.y = y

        # стати
        self.max_hp = 20
        self.hp = 20
        self.attack = 5       # базовий attack (буде змінюватись зіллям, зброєю)
        self.defense = 0      # броня

        # інвентар
        self.inventory = []          # список Item
        self.inventory_capacity = 8  # ліміт слотів

        # екіп
        self.weapon = None  # Item або None
        self.armor = None   # Item або None

        # для анімації / напряму
        self.direction = "down"   # "up", "down", "left", "right"
        self.walk_timer = 0
        self.step_phase = 0

    def move(self, dx: int, dy: int, dungeon: DungeonMap):
        """Рух гравця з перевіркою стін + підготовка до анімації."""
        new_x = self.x + dx
        new_y = self.y + dy
        if not dungeon.is_walkable(new_x, new_y):
            return

        self.x = new_x
        self.y = new_y

        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        elif dy > 0:
            self.direction = "down"
        elif dy < 0:
            self.direction = "up"

        self.walk_timer = 10
        self.step_phase = (self.step_phase + 1) % 2

    def update(self):
        if self.walk_timer > 0:
            self.walk_timer -= 1

    def get_draw_offset(self):
        if self.walk_timer > 0 and self.step_phase == 0:
            return 0, -2
        return 0, 0

    # ----- ЕКІП -----
    def equip_weapon(self, item):
        """Екіпувати зброю: зняти стару, додати бонус нової."""
        # зняти старий бонус
        if self.weapon is not None:
            self.attack -= self.weapon.value
        self.weapon = item
        self.attack += item.value

    def equip_armor(self, item):
        """Екіпувати броню."""
        if self.armor is not None:
            self.defense -= self.armor.value
        self.armor = item
        self.defense += item.value

    # ----- Бій -----
    def take_damage(self, amount: int):
        # враховуємо defense
        effective = amount - self.defense
        if effective < 1:
            effective = 1
        self.hp -= effective
        if self.hp < 0:
            self.hp = 0

    def is_alive(self) -> bool:
        return self.hp > 0
