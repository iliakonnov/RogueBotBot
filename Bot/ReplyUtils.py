import logging
from time import sleep, time
from typing import Callable, Optional, Any

from Bot import telegrammer, ReplyFunc, ReplyResult, WeaponsPriority, BotState, Config, Message


def send_action(action: Optional[ReplyFunc], msg: Message.Message, state: BotState):
    if action:
        for i in action(msg, state):
            if i:
                logging.debug('Action: {}'.format(i))
                if isinstance(i, str):
                    telegrammer.send_msg(i)
                else:
                    for msg in i:
                        telegrammer.send_msg(msg)
    return time()


def get_info(func: Callable[..., Any]) -> Optional[str]:
    if not func:
        return '<![None]>'
    if func.__doc__:
        return func.__doc__
    # noinspection PyUnresolvedReferences
    closure = func.__closure__
    if closure is None:
        return '<*[{}]>'.format(func.__qualname__)
    args = []
    for i in closure:
        if isinstance(i, (str, int)):
            args.append(repr(i))
        elif callable(i):
            args.append(get_info(i))
        else:
            args.append('===')
    return '<*[{}]({})>'.format(func.__qualname__, ', '.join(args))


def get_reply(func: ReplyFunc, timeout=Config.retry_delay) -> ReplyFunc:
    """Возвращает резльтат func, но передает ей уже новое сообщение"""

    def f(_: Message.Message, state: BotState.BotState) -> ReplyResult:
        msg = telegrammer.get_message(timeout=timeout)
        if msg is not None:
            return func(msg, state)
        return []

    f.__doc__ = '<$[get_reply] {}...{}>'.format(timeout, get_info(func))

    return f


def repeat_message(msg: Message.Message, _: BotState.BotState) -> ReplyResult:
    """<$[repeat]>"""
    telegrammer.repeat_msg(msg)
    return []


def battle(msg: Message.Message, __: BotState.BotState) -> ReplyResult:
    """<#[battle]>"""
    """Битва с кем либо"""

    work = True
    while work:
        found = False
        for repl in msg.replies:
            for weap in WeaponsPriority.weapons:
                if repl.startswith('➰ Использовать: {}'.format(weap)):
                    found = True
                    yield repl
        if not found:
            if '👊 Ударить рукой' in msg.replies:
                yield '👊 Ударить рукой'
            else:
                work = False
                telegrammer.repeat_msg(msg)
        if work:
            msg = telegrammer.get_message()


def reply(out: ReplyResult, delay=0) -> ReplyFunc:
    """Просто отправляет сообщение"""

    def f(_: Message.Message, __: BotState.BotState) -> ReplyResult:
        sleep(delay)
        return out

    f.__doc__ = '<#[reply] {} "{}">'.format(delay, out)

    return f


go_away = reply("Уйти")
no_pet = reply('Нет')
nothing = reply([])
ignore = get_reply(nothing)


def set_item(name: str, cnt: int) -> ReplyFunc:
    """Устанавливает количество предмета name в инвентаре"""

    def f(_: Message.Message, state: BotState.BotState) -> ReplyResult:
        state.current_items[name] = cnt
        return []

    f.__doc__ = '<#[set_item] {} = {}>'.format(name, cnt)

    return f


def update_state(prop: str, new_val: Any, change: bool = False) -> ReplyFunc:
    """Обновляет свойство BotState. Если change == True, то прибавляет к текущему значению new_val"""

    def f(_: Message.Message, state: BotState.BotState) -> ReplyResult:
        if change:
            val = getattr(state, prop) + new_val
        else:
            val = new_val
        setattr(state, prop, val)
        return []

    f.__doc__ = "<#[update_state] {} {} {}>".format(prop, '+=' if change else '=', new_val)

    return f


def conditional(
        condition: Callable[[Message.Message, BotState.BotState], bool],
        func: ReplyFunc = None,
        else_func: ReplyFunc = None
) -> ReplyFunc:
    def f(msg: Message.Message, state: BotState.BotState) -> ReplyResult:
        if condition(msg, state):
            if func is not None:
                return func(msg, state)
        else:
            if else_func is not None:
                return else_func(msg, state)
        return []

    f.__doc__ = '<$[if] {} if {} else {}>'.format(
        get_info(func) if func is not None else None,
        get_info(condition),
        get_info(else_func) if else_func is not None else None
    )

    return f


def concat(*funcs: Optional[ReplyFunc], ignore_func: Optional[ReplyFunc] = ignore) -> ReplyFunc:
    """Объединяет несколько ответов в цепочку. Автоматически игнорирует промежуточные ответы от бота.
    Пропускает все None среди функций"""
    funcs = [i for i in funcs if i is not None]

    def f(msg: Message.Message, state: BotState.BotState) -> ReplyResult:
        l = len(funcs)
        n = 1
        for func in funcs:
            cur = func(msg, state)
            if cur:
                if isinstance(cur, str):
                    yield cur
                else:
                    yield from cur
                if n != l and ignore_func:
                    yield ignore_func(msg, state)
            n += 1

    def get_doc():
        l = len(funcs)
        n = 1
        for func in funcs:
            yield get_info(func)
            if n != l and ignore_func:
                yield get_info(ignore_func)
            n += 1

    f.__doc__ = '<$[concat] {}>'.format('; '.join(get_doc()))

    return f


dice = reply("🎲 Кинуть")
