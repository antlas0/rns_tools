import RNS
import datetime
from dataclasses import dataclass
from typing import Optional

from .destination_info import DestinationInfo

@dataclass
class AnnounceInfo:
    date: datetime.datetime
    destination_hash: str
    announced_identity: RNS.Identity
    app_data: Optional[str]
    destination_info: Optional[DestinationInfo]=None
