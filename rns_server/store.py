import RNS
from typing import Dict, List
from dataclasses import dataclass, field
from threading import Lock

from .announce_info import AnnounceInfo
from .lxmf_message_info import LXMFMessageInfo

@dataclass
class Store:
    _announces: Dict[str, AnnounceInfo]=field(default_factory=dict)
    _lxmf_messages: Dict[str, List[LXMFMessageInfo]]=field(default_factory=dict)

    def __post_init__(self) -> None:
        self._lock = Lock()

    @property
    def announces(self):
        return self._announces

    @property
    def messages(self):
        return self._lxmf_messages

    def store_announce(self, announce:AnnounceInfo) -> None:
        self._lock.acquire()
        if not announce.destination_hash in self._announces.keys():
            self._announces[announce.destination_hash] = announce
        else:
            self._announces[announce.destination_hash].date = announce.date
            self._announces[announce.destination_hash].destination_info = announce.destination_info
        self._lock.release()

    def store_message(self, message:LXMFMessageInfo) -> None:
        self._lock.acquire()
        if not message.source_hash in self._lxmf_messages.keys():
            self._lxmf_messages[message.source_hash] = []
        self._lxmf_messages[message.source_hash].append(message)
        self._lock.release()

        