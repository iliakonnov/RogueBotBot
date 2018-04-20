"""
Based on https://github.com/LonamiWebs/Telethon/blob/master/telethon/extensions/html.py
Simple HTML <- Telegram entity parser.
"""
import struct
from collections import deque
from html import escape, unescape
from html.parser import HTMLParser

from telethon.tl.types import (
    MessageEntityBold, MessageEntityItalic, MessageEntityCode,
    MessageEntityPre, MessageEntityEmail, MessageEntityUrl,
    MessageEntityTextUrl
)


# Helpers from [markdown.py](https://github.com/LonamiWebs/Telethon/blob/master/telethon/extensions/markdown.py)
def _add_surrogate(text):
    return ''.join(
        ''.join(chr(y) for y in struct.unpack('<HH', x.encode('utf-16le')))
        if (0x10000 <= ord(x) <= 0x10FFFF) else x for x in text
    )


def _del_surrogate(text):
    return text.encode('utf-16', 'surrogatepass').decode('utf-16')


def unparse(text, entities):
    """
    Performs the reverse operation to .parse(), effectively returning HTML
    given a normal text and its MessageEntity's.
    :param text: the text to be reconverted into HTML.
    :param entities: the MessageEntity's applied to the text.
    :return: a HTML representation of the combination of both inputs.
    """
    if not entities:
        return text

    text = _add_surrogate(text)
    html = []
    last_offset = 0
    for entity in entities:
        if entity.offset > last_offset:
            html.append(escape(text[last_offset:entity.offset]))
        elif entity.offset < last_offset:
            continue

        skip_entity = False
        entity_text = escape(text[entity.offset:entity.offset + entity.length])
        entity_type = type(entity)

        if entity_type == MessageEntityBold:
            html.append('<strong>{}</strong>'.format(entity_text))
        elif entity_type == MessageEntityItalic:
            html.append('<em>{}</em>'.format(entity_text))
        elif entity_type == MessageEntityCode:
            html.append('<code>{}</code>'.format(entity_text))
        elif entity_type == MessageEntityPre:
            # Without <code> inside <pre> and indentation inside pre
            html.append('<pre>{}</pre>'.format(entity_text))
        elif entity_type == MessageEntityEmail:
            html.append('<a href="mailto:{0}">{0}</a>'.format(entity_text))
        elif entity_type == MessageEntityUrl:
            html.append('<a href="{0}">{0}</a>'.format(entity_text))
        elif entity_type == MessageEntityTextUrl:
            html.append('<a href="{}">{}</a>'
                        .format(escape(entity.url), entity_text))
        else:
            skip_entity = True
        last_offset = entity.offset + (0 if skip_entity else entity.length)
    html.append(text[last_offset:])
    return _del_surrogate(''.join(html))