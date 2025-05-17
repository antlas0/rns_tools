from dataclasses import dataclass


@dataclass
class PacketInfo:
    hash: str
    data: str