from typing import Sequence

from Bot import ReplyFunc, ReplyUtils, telegrammer, notifier

'''
Эти действия выполняются после каждого действия.
'''
actions: Sequence[ReplyFunc] = [
    ReplyUtils.conditional(
        lambda _, __, state: (
                state.current_room == '__коридор' and
                all(state.current_items.get(i, 0) > 0 for i in ['Книга тайн №1', 'Книга тайн №2', 'Книга тайн №3'])
        ),
        ReplyUtils.concat(
            notifier.notify('Книги тайн собраны!'),
            ReplyUtils.reply('🎒 Посмотреть инвентарь'),
            ReplyUtils.ignore,
            ReplyUtils.reply('Книга тайн №1'),
            ReplyUtils.get_reply(
                ReplyUtils.conditional(
                    lambda _, replies, __: 'Забирай, они мне не нужны' in replies,
                    ReplyUtils.concat(
                        ReplyUtils.reply('Забирай, они мне не нужны'),
                        ReplyUtils.update_state("max_hp", 20, change=True),
                        ReplyUtils.set_item("Книга тайн №1", 0),
                        ReplyUtils.set_item("Книга тайн №2", 0),
                        ReplyUtils.set_item("Книга тайн №3", 0),
                        ignore_func=None
                    ),
                    ReplyUtils.reply('Ping')
                )
            ),
            ignore_func=None
        ),
    ),
    ReplyUtils.conditional(
        lambda _, __, state: state.gold % 1_000_000 == 0,
        notifier.notify('Очередной миллион золота!')
    )
]
