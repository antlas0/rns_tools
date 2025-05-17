import RNS
import LXMF
import time
import threading
import logging
import tempfile
from typing import Any

from .resources import LXMF_REQUIRED_STAMP_COST, LXMF_ENFORCE_STAMPS, LXMF_DISPLAY_NAME
from .lxmf_delivery_handler import LXMFDeliveryHandler
from .store import Store

logger = logging.getLogger(__name__)


class LXMFServer(threading.Thread):
    def __init__(self, runtime_dir:str, store:Store):
        super().__init__()
        self._running:bool = True
        self._storage_path:str = runtime_dir if runtime_dir is not None else tempfile.mkdtemp() # currently won't be deteled when quitting
        logger.info(f"Using LXMF runtime dir {self._storage_path}")
        self._router = LXMF.LXMRouter(storagepath=self._storage_path, enforce_stamps=LXMF_ENFORCE_STAMPS)
        # hack to prevent signal to be overrided by LXMROUTER
        self._router.sigint_handler = lambda x:None
        self._destination = None
        self._delivery_handler = LXMFDeliveryHandler(store)
        self._recipient_hash = None
        self._peer = None
        self._message = None

    def setup(self, identity:RNS.Identity) -> bool:
        self._destination = self._router.register_delivery_identity(identity, display_name=LXMF_DISPLAY_NAME, stamp_cost=LXMF_REQUIRED_STAMP_COST)
        self._router.register_delivery_callback(self._delivery_handler.delivery_callback)
        logger.info(f"Ready to receive LXMF messages on {RNS.prettyhexrep(self._destination.hash)}")
        return True

    def set_message(self, message:str) -> None:
        self._message = message

    def set_peer(self, peer:str) -> None:
        self._recipient_hash = bytes.fromhex(peer)

    def send_message(self) -> bool:
        if self._recipient_hash and self._message:
            if not RNS.Transport.has_path(self._recipient_hash):
                logger.info("Destination is not yet known. Requesting path and waiting for announce to arrive...")
                RNS.Transport.request_path(self._recipient_hash)
                while not RNS.Transport.has_path(self._recipient_hash):
                    time.sleep(0.1)
                nh = RNS.Transport.next_hop(destination_hash=self._recipient_hash)
                if nh: nh = nh.hex()
                logger.info(f"Going through {nh} via {RNS.Transport.next_hop_interface(self._recipient_hash)}")

            recipient_identity = RNS.Identity.recall(self._recipient_hash)
            self._peer = RNS.Destination(recipient_identity, RNS.Destination.OUT, RNS.Destination.SINGLE, "lxmf", "delivery")

            lxm = LXMF.LXMessage(self._peer, self._destination, self._message, "New message", desired_method=LXMF.LXMessage.OPPORTUNISTIC, include_ticket=True)
            self._router.handle_outbound(lxm)
            logger.info(f"Sent message {self._message} to peer {self._peer.hash.hex()}")
            self.quit()

    def announce(self, interface:Any) -> None:
        self._router.announce(self._destination.hash, attached_interface=interface)
        logger.info(f"Announced LXMF server {self._destination.hash.hex()} through {interface}")

    def run(self) -> None:
        self.send_message()
        while self._running:
            time.sleep(0.1)

    def quit(self) -> None:
        logger.info(f"Quitting...")
        self._running = False