import os
from hashlib import blake2b
from typing import Sequence, Union, Dict, Optional

from Bot import ReplyFunc


class Room(object):
    DEFAULT_SEP = '/'

    def __init__(self, name: Union[str, Sequence[str]], hashes: Optional[Dict[str, Optional[str]]], action: ReplyFunc):
        if isinstance(name, str):
            self._name: Union[str, Sequence[str]] = name
        else:
            self._name: Union[str, Sequence[str]] = set(name)
        self._action = action
        if hashes:
            if os.path.sep != self.DEFAULT_SEP:
                self._hashes = {}
                for k, v in hashes.items():
                    self._hashes[k.replace(self.DEFAULT_SEP, os.path.sep)] = v
            else:
                self._hashes = hashes
        else:
            self._hashes = {}
        self._frozen = frozenset(self._hashes)

    def check_changed(self, repo_path) -> bool:
        for path, hex_hash in self._hashes.items():
            if hex_hash is None:
                continue
            p = os.path.join(repo_path, path)
            if not os.path.isfile(p):
                return False
            h = blake2b(digest_size=20)
            with open(p, 'rb') as f:
                h.update(f.read())
            if h.hexdigest() != hex_hash:
                return False
        return True

    def check_name(self, names: Union[str, Sequence[str]]) -> Optional[str]:
        if isinstance(names, str):
            names = [names]
        for n in names:
            if isinstance(self._name, str):
                if n == self._name:
                    return n
            elif n in self._name:
                return n
        return None

    @property
    def name(self) -> Union[str, Sequence[str]]:
        return self._name

    @property
    def hashes(self) -> Dict[str, Optional[str]]:
        return self._hashes

    @property
    def action(self) -> ReplyFunc:
        return self._action

    def __eq__(self, other):
        if isinstance(other, Room):
            return other.name == self.name and other.hashes == self.hashes
        else:
            return False

    def __ne__(self, other):
        return self != other

    def __hash__(self):
        h = 17
        h = h * 23 + hash(self.name)
        h = h * 23 + hash(self._frozen)
        return h


def check_rooms(path_to_repo: str, rooms: Sequence[Room]):
    path_to_rooms = os.path.join(path_to_repo, 'rooms')
    rooms_files = set()
    for group in os.listdir(path_to_rooms):
        path_to_group = os.path.join(path_to_rooms, group)
        if not os.path.isdir(path_to_group):
            continue
        for dirpath, dirnames, filenames in os.walk(path_to_group):
            for fname in filenames:
                if not fname.endswith('.py'):
                    continue
                rooms_files.add(os.path.join(path_to_group, dirpath, fname))

    changed = set()
    removed = set()
    found = set()
    for r in rooms:
        is_removed = False
        for p in r.hashes.keys():
            real_path = os.path.join(path_to_repo, p)
            if real_path not in rooms_files:
                removed.add(real_path)
                is_removed = True
            else:
                found.add(real_path)
        if not is_removed and not r.check_changed(path_to_repo):
            changed.add(r)
    added = rooms_files.difference(found)

    return changed, removed, added
