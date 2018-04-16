from time import time
import abc

from telethon.tl import types as tl_types

from Bot import Config


class BaseChannel(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def send_to_channel(self, message: tl_types.Message):
        raise NotImplementedError()


class DisabledChannel(BaseChannel):
    def send_to_channel(self, _):
        pass


class NormalChannel(BaseChannel):
    def __init__(self):
        import telepot
        self.channel_msg = ''
        self.channel_time = 0
        self.channel_bot = telepot.Bot(Config.bot_token)

    def send_to_channel(self, message: tl_types.Message):
        from_name = '`[{:%Y.%m.%d %H:%M:%S} UTC] {}:`\n'.format(
            message.date, 'Бот' if message.from_id == 253526115 else 'Я'
        )
        msg = '\n\n' + from_name + message.message

        t = time()
        if t - self.channel_time > Config.channel_delay:
            send_now = True
            self.channel_time = t
        else:
            new_len = len(self.channel_msg) + len(msg)
            send_now = new_len > 4096

        if send_now and self.channel_msg:
            self.channel_bot.sendMessage(Config.channel_id, self.channel_msg, parse_mode='Markdown', disable_notification=True)
            self.channel_msg = ''
        self.channel_msg += msg
        self.channel_msg.strip('\n')
