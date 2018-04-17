from typing import Sequence
from datetime import datetime


class Message(object):
    def __init__(self, text: str, replies: Sequence[str], date: datetime, is_from_bot: bool):
        self._replies = replies
        self._text = text
        self._date = date
        self._is_from_bot = is_from_bot

    @property
    def text(self) -> str:
        return self._text

    @property
    def date(self) -> datetime:
        return self._date

    @property
    def replies(self) -> Sequence[str]:
        return self._replies

    @property
    def is_from_bot(self) -> bool:
        return self._is_from_bot
