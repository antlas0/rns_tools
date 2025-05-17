import logging

from .packet_info import PacketInfo
from .store import Store


logger = logging.getLogger(__name__)


class PacketHandler:
    def __init__(self, store:Store):
        self._store = store

    def handle_packet(self, data, packet) -> None:
        logger.info(str(packet))
        logger.info(data)
        p = PacketInfo(
            hash="",
            data=data.decode("utf-8")
        )