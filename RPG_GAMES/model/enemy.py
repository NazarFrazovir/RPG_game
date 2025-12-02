# model/enemy.py

class Enemy:
    def __init__(self, x: int, y: int, hp: int = 10, attack: int = 3):
        self.x = x
        self.y = y
        self.hp = hp
        self.attack = attack

        # для анімації
        self.direction = "down"     # up / down / left / right
        self.walk_timer = 0         # скільки кадрів ще "рухаються ноги"
        self.step_phase = 0         # 0 або 1 (чергування кроків)

        # для AI руху
        self.move_cooldown = 30     # кадрів між кроками (чим більше, тим повільніші)
        self.move_timer = 0         # скільки кадрів залишилось до наступного кроку

        # нове: чи вже “загротився” на гравця
        self.aggro = False

    def update(self):
        if self.walk_timer > 0:
            self.walk_timer -= 1
        if self.move_timer > 0:
            self.move_timer -= 1

    def start_walk(self):
        """Викликаємо, коли ворог зробив крок."""
        self.walk_timer = 10
        self.step_phase = (self.step_phase + 1) % 2

    def take_damage(self, amount: int):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def is_alive(self) -> bool:
        return self.hp > 0
