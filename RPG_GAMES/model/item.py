# model/item.py

from enum import Enum, auto


class ItemType(Enum):
    HEAL = auto()
    ATTACK = auto()
    WEAPON = auto()
    ARMOR = auto()


class ItemRarity(Enum):
    COMMON = auto()      # сірий
    UNCOMMON = auto()    # зелений
    RARE = auto()        # синій
    LEGENDARY = auto()   # золото


class Item:
    def __init__(self, x: int, y: int, item_type: ItemType, value: int,
                 rarity: ItemRarity, durability: int = 0):
        self.x = x
        self.y = y
        self.type = item_type
        self.value = value          # для HEAL/ATTACK: скільки дає; для WEAPON/ARMOR: бонус
        self.rarity = rarity
        self.durability = durability  # 0 для одноразових (HEAL/ATTACK), >0 для зброї/броні
