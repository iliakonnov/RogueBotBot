from typing import Dict

from Bot import BotState
from Bot.Constants import Num


def get_items(state: BotState) -> Dict[str, Num]:
    return {
        "Монетка": state.current_items['Монетка'],
        "Лазерный пистолет": state.current_items['Лазерный пистолет'],
        "Яблочко": state.current_items['Яблочко'],
        "Зубы": state.current_items['Зубы'],
        "Меч рыцаря": state.current_items['Меч рыцаря'] - 1,
        "Виски": state.current_items['Виски'],
        "Лазерная Пуля": state.current_items['Лазерная Пуля'],
        "Конфетка": state.current_items['Конфетка'],
        "Солнцезащитные очки": state.current_items['Солнцезащитные очки'],
        "Деревянная ложка": state.current_items['Деревянная ложка'],
        "Трезубец": state.current_items['Трезубец'],
        "Драконий убийца": state.current_items['Драконий убийца'],
    }
