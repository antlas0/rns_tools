from typing import Optional
from dataclasses import dataclass


@dataclass
class LXMFMessageInfo:
    source_hash: str
    destination_hash: str
    source_instance: str
    destination_instance: str
    snr: Optional[float]=None
    q: Optional[float]=None
    rssi: Optional[float]=None
    packed_size: Optional[int]=None
    content: Optional[str]=None
