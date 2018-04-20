from typing import Union, Callable, Sequence

from . import utils  # None
from . import Constants  # None

try:
    from .Configurable import Config  # None
except ImportError:
    raise Exception("Не удалось найти Configurable/Config.py")

from .Configurable import RoomsPriority  # None
from .Configurable import WeaponsPriority  # None
from .Configurable import BuyItems  # Constants
from . import BotState  # BuyItems
from .Configurable import SellItems  # Constants, BotState
from . import Message  # None
ReplyResult = Union[str, Sequence[str]]
ReplyFunc = Callable[[Message.Message, BotState.BotState], ReplyResult]

if Config.proxy_enabled:
    from . import Proxy


from . import Logger  # BotState
logger = Logger.Logger()

from . import Channel  # Config, Message
if Config.channel_enabled:
    channel: Channel.BaseChannel = Channel.NormalChannel()
else:
    channel: Channel.BaseChannel = Channel.DisabledChannel()

from . import Controller  # Config
if Config.controller_enabled:
    controller: Controller.BaseController = Controller.NormalController()
else:
    controller: Controller.BaseController = Controller.DisabledController()

from . import Telegrammer  # BotState, Constants, Channel, ReplyUtils, Message

if Config.test:
    telegrammer: Telegrammer.BaseTelegrammer = Telegrammer.TestingTelegrammer()
else:
    telegrammer: Telegrammer.BaseTelegrammer = Telegrammer.Telegrammer()

from . import Notifier  # ReplyFunc, BotState, ReplyResult, Config, Message
if Config.notify_bot:
    notifier = Notifier.BotNotifier()
elif Config.echo_id:
    notifier = Notifier.EchoNotifier()
else:
    notifier = Notifier.DisabledNotifier()

from . import ReplyUtils  # telegrammer, utils, ReplyFunc, ReplyResult, WeaponsPriority, BotState, Config
from .Configurable import Actions  # ReplyFunc, ReplyUtils, telegrammer
from . import Room  # Constants, ReplyUtils, telegrammer
from .Configurable import Rooms  # BotState, ReplyResult, ReplyUtils, Room, Message

from . import Bot  # Everything
