from telethon.tl import types as tl_types


def parse_replies(markup: tl_types.ReplyKeyboardMarkup):
    if not isinstance(markup, tl_types.ReplyKeyboardMarkup):
        return []
    for row in markup.rows:
        for btn in row.buttons:
            yield btn.text


def try_find(regexp, text, group=1, post=lambda x: x, default=None):
    match = regexp.search(text)
    if match:
        return post(match.group(group))
    return default
