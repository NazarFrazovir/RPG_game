# model/dungeon.py

class DungeonMap:
    def __init__(self, level_data):
        self.level_data = level_data
        self.width = len(level_data[0])
        self.height = len(level_data)

    def is_walkable(self, x: int, y: int) -> bool:
        """Перевіряємо, чи можна стати на клітинку (не вихід за межі і не стіна)."""
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return False
        tile = self.level_data[y][x]
        # усе, що не '#' — прохідне (включно з P, M, H, A)
        return tile != "#"

    def find_player_start(self):
        """Знаходимо позицію P у карті."""
        for y, row in enumerate(self.level_data):
            for x, ch in enumerate(row):
                if ch == "P":
                    return x, y
        return 1, 1

    def find_enemy_positions(self):
        """Повертаємо список координат усіх монстрів (M) на мапі."""
        positions = []
        for y, row in enumerate(self.level_data):
            for x, ch in enumerate(row):
                if ch == "M":
                    positions.append((x, y))
        return positions

    def find_item_positions(self):
        """Повертає список (x, y, ch) для предметів (H, A, W, R)."""
        positions = []
        for y, row in enumerate(self.level_data):
            for x, ch in enumerate(row):
                if ch in ("H", "A", "W", "R"):
                    positions.append((x, y, ch))
        return positions
