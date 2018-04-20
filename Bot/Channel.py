import abc
from time import time
from typing import List

from Bot import Config, Message


class BaseChannel(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def send_to_channel(self, message: Message.Message):
        raise NotImplementedError()


class DisabledChannel(BaseChannel):
    def send_to_channel(self, _):
        pass


class NormalChannel(BaseChannel):
    def __init__(self):
        import telepot
        self.messages: List[Message.Message] = []
        self.channel_msg = ''
        self.channel_time = 0
        self.channel_bot = telepot.Bot(Config.bot_token)

    def send_to_channel(self, message: Message.Message = None):
        if message is not None:
            self.messages.append(message)
            self.messages.sort(key=lambda x: x.date)

        msg = self._prepare_msg()

        send_now = (
                (time() - self.channel_time > Config.channel_delay)
                or msg[2]  # length limited
        )

        if send_now and msg[0]:
            self.channel_bot.sendMessage(
                Config.channel_id,
                msg[0],
                parse_mode='Markdown',
                disable_notification=True
            )
            self.messages = self.messages[msg[1]:]  # offset
            self.channel_time = time()

    def _prepare_msg(self):
        if not self.messages:
            return '', 0, False

        msg = ''
        length_limited = False
        offset = 0
        m = self.messages[offset]
        while True:
            from_name = '`[{:%Y.%m.%d %H:%M:%S} UTC] {}:`\n'.format(
                m.date, 'Бот' if m.is_from_bot else 'Я'
            )
            new_msg = msg + '\n\n' + from_name + m.text
            new_msg.strip('\n')
            if len(new_msg) > 4096:
                length_limited = True
                break
            elif offset + 1 < len(self.messages):
                msg = new_msg
                offset += 1
                m = self.messages[offset]
            else:
                break
        return msg, offset, length_limited
