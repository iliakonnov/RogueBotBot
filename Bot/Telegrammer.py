import logging
from time import sleep, time
from typing import Sequence, Optional

from telethon import TelegramClient
from telethon.tl import types as tl_types

from Bot import channel, ReplyFunc, BotState, Config


class Telegrammer(object):
    def __init__(self):
        args = ['session', Config.api_id, Config.api_hash]
        kwargs = dict(update_workers=0)
        self.client: TelegramClient = TelegramClient(*args, **kwargs)

    def send_to(self, entity: str, content: str):
        if content:
            logging.debug('Sending {}...'.format(content))
            sleep(Config.message_delay)
            return self.client.send_message(entity, content)

    def send_msg(self, content: str):
        msg = self.send_to(Config.bot_id, content)
        if msg:
            channel.send_to_channel(msg)

    def send_action(self, action: Optional[ReplyFunc], text: str, replies: Sequence[str], state: BotState):
        if action:
            for i in action(text, replies, state):
                if i:
                    logging.debug('Action: {}'.format(i))
                    if isinstance(i, str):
                        self.send_msg(i)
                    else:
                        for msg in i:
                            self.send_msg(msg)
        return time()

    def get_message(self, timeout=None) -> Optional[tl_types.Message]:
        new = None
        first = True
        while first or new is not None:
            first = False
            new = self.client.updates.poll(timeout=timeout)
            if new is None:
                return None
            if isinstance(new, tl_types.UpdateNewMessage):
                message = new.message
                if message.from_id == Config.bot_id and message.message:
                    channel.send_to_channel(message)
                    return message
        return None

    def disconnect(self):
        self.client.disconnect()

    def start(self):
        self.client.start()
