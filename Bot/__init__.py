from typing import Union, Callable, Sequence

from . import utils  # None
from . import Constants  # None
from .Configurable import Config  # None
from .Configurable import RoomsPriority  # None
from .Configurable import WeaponsPriority  # None
from .Configurable import BuyItems  # Constants
from . import BotState  # BuyItems
from .Configurable import SellItems  # Constants, BotState
ReplyResult = Union[str, Sequence[str]]
ReplyFunc = Callable[[str, Sequence[str], BotState.BotState], ReplyResult]

if Config.proxy_enabled:
    from . import Proxy

from . import Channel  # Config
if Config.channel_enabled:
    channel: Channel.BaseChannel = Channel.NormalChannel()
else:
    channel: Channel.BaseChannel = Channel.DisabledChannel()

from . import Controller  # Config
if Config.controller_enabled:
    controller: Controller.BaseController = Controller.NormalController()
else:
    controller: Controller.BaseController = Controller.DisabledController()

from . import Telegrammer  # BotState, Constants, Channel, ReplyUtils
telegrammer: Telegrammer.Telegrammer = Telegrammer.Telegrammer()

from . import Notifier
if Config.notify_bot:
    notifier = Notifier.BotNotifier()
elif Config.echo_id:
    notifier = Notifier.EchoNotifier()
else:
    notifier = Notifier.DisabledNotifier()

from . import ReplyUtils  # telegrammer, utils, ReplyFunc, ReplyResult, WeaponsPriority, BotState, Config
from .Configurable import Actions  # ReplyFunc, ReplyUtils, telegrammer
from . import Room  # Constants, ReplyUtils
from .Configurable import Rooms  # BotState, ReplyResult, ReplyUtils, Room

from . import Bot  # Everything
