import abc

from Bot import ReplyFunc, BotState, ReplyResult, Config, Message


class BaseNotifier(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def notify(self, content: str) -> ReplyFunc:
        raise NotImplementedError()


class DisabledNotifier(BaseNotifier):
    def notify(self, content: str) -> ReplyFunc:
        def f(_: Message.Message, __: BotState) -> ReplyResult:
            return []

        f.__doc__ = '<#[notify] {}>'.format(content)
        return f


class EchoNotifier(BaseNotifier):
    def __init__(self):
        from Bot import telegrammer
        self.telegrammer = telegrammer

    def notify(self, content: str) -> ReplyFunc:
        def f(_: Message.Message, __: BotState) -> ReplyResult:
            self.telegrammer.send_to(Config.echo_id, content)
            return []

        f.__doc__ = '<#[notify] {}>'.format(content)
        return f


class BotNotifier(BaseNotifier):
    def __init__(self):
        import telepot
        self.bot = telepot.Bot(Config.bot_token)

    def notify(self, content: str) -> ReplyFunc:
        def f(_: Message.Message, __: BotState) -> ReplyResult:
            self.bot.sendMessage(Config.admin_id, content)
            return []

        f.__doc__ = '<#[notify] {}>'.format(content)
        return f
