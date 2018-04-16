from typing import Dict

from Bot import BuyItems


class BotState(object):
    def __init__(self, state: Dict = None):
        if state is None:
            state = {}
        self.damage: int = state.get('damage', 0)
        self.gold: int = state.get('gold', 0)
        self.health: int = state.get('health', 0)
        self.current_items: Dict[str, int] = state.get('items', {key: 0 for key in BuyItems.items.keys()})
        self.current_room: str = state.get('room', '<none>')
        self.crashes: int = state.get('crashes', 0)
        self.rooms_entered: int = state.get('rooms', 0)
        self.max_hp: int = state.get('max_hp', 0)
        self.dice: int = state.get('dice', 0)

        self.current_room_count: int = 0
        self.current_retries_count: int = 0

    def to_dict(self):
        return {
            'items': self.current_items,
            'room': self.current_room,
            'damage': self.damage,
            'gold': self.gold,
            'health': self.health,
            'crashes': self.crashes,
            'rooms': self.rooms_entered,
            'max_hp': self.max_hp,
            'dice': self.dice
        }
