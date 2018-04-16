import abc
import enum
from typing import Sequence

from Bot import Config


class Command(enum.Enum):
    INVENTORY = 1
    PAUSE = 2
    UNPAUSE = 3


class BaseController(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_commands(self) -> Sequence[Command]:
        raise NotImplementedError()


class DisabledController(BaseController):
    def get_commands(self):
        return []


class NormalController(BaseController):
    def __init__(self):
        import telepot
        self.bot = telepot.Bot(Config.bot_token)
        self.offset = 0

    def get_commands(self):
        commands = {
            '/inventory': Command.INVENTORY,
            '/pause': Command.PAUSE,
            '/unpause': Command.UNPAUSE
        }
        updates = self.bot.getUpdates(self.offset)
        for upd in updates:
            self.offset = upd['update_id'] + 1
            if 'message' not in upd:
                continue
            msg = upd['message']
            if msg['from']['id'] != Config.admin_id:
                continue
            if msg['text'] in commands:
                self.bot.sendMessage(msg['from']['id'], 'Ok')
                yield commands[msg['text']]
            else:
                commands_help = []
                for cmd, info in commands.items():
                    commands_help.append('{}: `{}`'.format(cmd, info))
                self.bot.sendMessage(
                    msg['from']['id'],
                    'Unknown command. Available commands:\n{}'.format('\n'.join(commands_help)),
                    parse_mode='Markdown'
                )
