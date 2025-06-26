import RNS
from dataclasses import dataclass


@dataclass
class DestinationInfo:
    destination_hash:str
    hops_to:int
    next_hop:str
    has_path:bool
    next_hop_interface:str


class DestinationInfoQuerier:
    def __init__(self, destination_hash:str) -> None:
        self._destination_hash = destination_hash

    def fill(self) -> DestinationInfo:
        return DestinationInfo(
                destination_hash=self._destination_hash,
                hops_to=RNS.Transport.hops_to(destination_hash=bytes.fromhex(self._destination_hash)),
                next_hop=RNS.Transport.next_hop(destination_hash=bytes.fromhex(self._destination_hash).hex()),
                next_hop_interface=RNS.Transport.next_hop_interface(destination_hash=bytes.fromhex(self._destination_hash)),
                has_path=RNS.Transport.has_path(destination_hash=bytes.fromhex(self._destination_hash)),
            )
