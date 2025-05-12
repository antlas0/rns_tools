import RNS
from typing import Dict
from dataclasses import dataclass, field
from threading import Lock

from .announce_info import AnnounceInfo

@dataclass
class Store:
    _announces: Dict[str, AnnounceInfo]=field(default_factory=dict)

    def __post_init__(self) -> None:
        self._lock = Lock()

    @property
    def announces(self):
        return self._announces
    
    def store_announce(self, announce:AnnounceInfo) -> bool:
        self._lock.acquire()
        if not announce.destination_hash in self._announces:
            self._announces[announce.destination_hash] = announce
        else:
            self._announces[announce.destination_hash].date = announce.date
            self._announces[announce.destination_hash].destination_info = announce.destination_info
        self._lock.release()

        