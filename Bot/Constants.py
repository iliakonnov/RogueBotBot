import re
from typing import Union

damage_re = re.compile(r'урон. равный (\d+)')
hp_gold_re = re.compile(r'🔴HP: (\d+) 🔵MP: \d+ 💰Gold: (\d+)')
room_re = re.compile(r'Вы открываете дверь, а за ней\.\.\.\n\n(.+)!\n')
item_re = re.compile(r'Также в комнате ты нашел\.\.\n\n(.+)')
dice_re = re.compile(r'🎲 Твой результат (\d+)')
inventory_re = re.compile(r'(.+) \((\d+) шт\. .+\) :')

Num = Union[int, float]
inf = float('+inf')
