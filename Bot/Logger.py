import json
import sqlite3
from datetime import datetime

from Bot import BotState


class Logger(object):
    def __init__(self):
        self.conn = sqlite3.connect('RogBotBot.db')
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript('''
        CREATE TABLE IF NOT EXISTS `BotLog` (
          `id`  INTEGER PRIMARY KEY AUTOINCREMENT,
          `datetime` TEXT,
          `hp` INTEGER,
          `max_hp` INTEGER,
          `damage` INTEGER,
          `gold` INTEGER,
          `dice` integer,
          `old_room` TEXT,
          `current_room` TEXT,
          `crashes` INTEGER,
          `rooms_entered` INTEGER,
          `items`, TEXT
        );
        ''')
        self.last_row: int = None

    def close(self):
        self.conn.close()

    def log_state(self, state: BotState.BotState, old_room: str):
        new_items = {
            'datetime': datetime.now().isoformat(),
            'hp': state.health,
            'max_hp': state.max_hp,
            'damage': state.damage,
            'gold': state.gold,
            'dice': state.dice,
            'old_room': old_room,
            'current_room': state.current_room,
            'crashes': state.crashes,
            'rooms_entered': state.current_room_count,
            'items': json.dumps(state.current_items, ensure_ascii=False)
        }
        if self.last_row is not None:
            last = dict(self.conn.execute("""
                SELECT 
                    `datetime`,
                    `hp`,
                    `max_hp`,
                    `damage`,
                    `gold`,
                    `dice`,
                    `old_room`,
                    `current_room`,
                    `crashes`,
                    `rooms_entered`,
                    `items`
                FROM BotLog
                WHERE `id`=?;
            """, (self.last_row,)).fetchone())
            comapre_a = {key: value for key, value in new_items.items() if key != 'datetime'}
            comapre_b = {key: value for key, value in last.items() if key != 'datetime'}
            assert set(comapre_a.keys()) == set(comapre_b.keys())
            if comapre_a == comapre_b:
                return

        self.last_row = self.conn.execute(
            """
               INSERT INTO BotLog (
                  `datetime`,
                  `hp`,
                  `max_hp`,
                  `damage`,
                  `gold`,
                  `dice`,
                  `old_room`,
                  `current_room`,
                  `crashes`,
                  `rooms_entered`,
                  `items`
                ) VALUES (
                  :datetime,
                  :hp, :max_hp, :damage, :gold, :dice, 
                  :old_room, :current_room, :crashes, :rooms_entered,
                  :items
                )
            """,
            new_items
        ).lastrowid
        self.conn.commit()
