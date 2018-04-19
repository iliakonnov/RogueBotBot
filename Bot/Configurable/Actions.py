from typing import Sequence

from Bot import ReplyFunc, ReplyUtils, notifier
from Bot.Configurable import Config

'''
Эти действия выполняются после каждого действия.
'''
actions: Sequence[ReplyFunc] = [
    ReplyUtils.conditional(
        lambda _, state: (
                state.current_room == '__коридор' and
                all(state.current_items.get(i, 0) > 0 for i in ['Книга тайн №1', 'Книга тайн №2', 'Книга тайн №3'])
        ),
        ReplyUtils.concat(
            ReplyUtils.concat(
                ReplyUtils.reply('🎒 Посмотреть инвентарь'),
                ReplyUtils.reply('Книга тайн №1'),
                ReplyUtils.reply('Забирай, они мне не нужны'),
                notifier.notify('Книги тайн собраны!'),
            ),
            ReplyUtils.set_item("Книга тайн №1", 0),
            ReplyUtils.set_item("Книга тайн №2", 0),
            ReplyUtils.set_item("Книга тайн №3", 0),
            # ReplyUtils.update_state("max_hp", 20, change=True),
            ignore_func=None
        ),
    ),
    ReplyUtils.conditional(
        lambda _, state: state.current_retries_count >= Config.battle_count,
        ReplyUtils.battle
    ),
    ReplyUtils.conditional(
        lambda _, state: state.gold % 1_000_000 == 0,
        notifier.notify('Очередной миллион золота!')
    )
]
