def try_find(regexp, text, group=1, post=lambda x: x, default=None):
    match = regexp.search(text)
    if match:
        return post(match.group(group))
    return default
