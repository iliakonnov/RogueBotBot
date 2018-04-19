import abc
import json
import logging
import socket
from datetime import datetime
from time import sleep, time
from typing import Sequence, Optional

from telethon import TelegramClient
from telethon.tl import types as tl_types

from Bot import channel, Config, Message, Constants


class BaseTelegrammer(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def send_to(self, entity: str, content: str):
        """Отправляет сообщение указанному entity (имя пользователя)"""
        raise NotImplementedError()

    @abc.abstractmethod
    def repeat_msg(self, message: Message.Message):
        """В следущем get_message бот вернет переданное сообщение"""
        raise NotImplementedError()

    @abc.abstractmethod
    def send_msg(self, content: str):
        """Отправляет сообщение боту"""
        raise NotImplementedError()

    @abc.abstractmethod
    def get_message(self, timeout: Constants.Num = None) -> Optional[Message.Message]:
        raise NotImplementedError()

    @abc.abstractmethod
    def disconnect(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def start(self):
        raise NotImplementedError()


class Telegrammer(BaseTelegrammer):
    def __init__(self):
        args = ['session', Config.api_id, Config.api_hash]
        kwargs = dict(update_workers=0)
        self.client: TelegramClient = TelegramClient(*args, **kwargs)
        self.last_time = 0
        self.message: Message.Message = None

    def send_to(self, entity: str, content: str) -> tl_types.Message:
        if content:
            logging.debug('Sending {}...'.format(content))
            delay = Config.message_delay - (time() - self.last_time)
            if delay > 0:
                sleep(delay)
            res = self.client.send_message(entity, content)
            self.last_time = time()
            return res

    def send_msg(self, content: str):
        msg = self.send_to(Config.bot_id, content)
        if msg:
            channel.send_to_channel(
                Message.Message(msg.message, [], msg.date, False)
            )

    def repeat_msg(self, message: Message.Message):
        self.message = message

    def get_message(self, timeout: Constants.Num = None) -> Optional[Message.Message]:
        if self.message:
            result = self.message
            self.message = None
            return result

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
                    msg = Message.Message(
                        message.message,
                        list(self._parse_replies(message.reply_markup)),
                        message.date,
                        True
                    )
                    channel.send_to_channel(msg)
                    return msg
        return None

    def _parse_replies(self, markup: tl_types.ReplyKeyboardMarkup) -> Sequence[str]:
        if not isinstance(markup, tl_types.ReplyKeyboardMarkup):
            return []
        for row in markup.rows:
            for btn in row.buttons:
                yield btn.text

    def disconnect(self):
        self.client.disconnect()

    def start(self):
        self.client.start()


class TestingTelegrammer(BaseTelegrammer):
    def __init__(self):
        """Несовместим с прокси!"""
        self.sock: socket.socket = socket.socket()
        self.conn: socket.socket = None
        self.message: Message.Message = None

    def _send(self, content: dict):
        command = json.dumps(content, ensure_ascii=False).encode('utf-8')
        self.conn.send(len(command).to_bytes(4, byteorder='little') + command)

    def send_to(self, entity: str, content: str):
        self._send({
            'action': 'send',
            'entity': entity,
            'content': content
        })
        sleep(Config.message_delay)

    def send_msg(self, content: str):
        self.send_to(Config.bot_id, content)

    def repeat_msg(self, message: Message.Message):
        self.message = message

    def get_message(self, timeout: Constants.Num = None) -> Optional[Message.Message]:
        if self.message:
            res = self.message
            self.message = None
            return res

        # self.conn.settimeout(timeout)
        try:
            size_data = self.conn.recv(4)
        except socket.timeout:
            command = {'action': 'timeout'}
        else:
            assert size_data
            size = int.from_bytes(size_data, byteorder='little')
            data: bytes = self.conn.recv(size)
            command = json.loads(data.decode('utf-8'))
        if command['action'] == 'message':
            result = Message.Message(command['text'], command['replies'], datetime.now(), True)
            self._send({
                'action': 'receive',
                'text': result.text,
                'replies': result.replies,
                'date': str(result.date),
                'from_bot': result.is_from_bot
            })
            return result
        elif command['action'] == 'timeout':
            self._send({
                'action': 'receive',
                'text': None,
                'replies': None,
                'date': None,
                'from_bot': None
            })
            return None
        raise Exception("Unknown action: {}".format(command['action']))

    def disconnect(self):
        self._send({'action': 'disconnect'})
        self.conn.close()
        self.sock.close()

    def start(self):
        self.sock.bind((Config.test_host, Config.test_port))
        self.sock.listen(1)
        self.conn, addr = self.sock.accept()
        self._send({'action': 'connect'})
