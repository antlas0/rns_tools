import RNS
import LXMF
import time
import threading
import logging
import tempfile
from typing import Any, Optional

from .resources import LXMF_REQUIRED_STAMP_COST, LXMF_ENFORCE_STAMPS, LXMF_DISPLAY_NAME
from .lxmf_delivery_handler import LXMFDeliveryHandler
from .store import Store

logger = logging.getLogger(__name__)


class LXMFServer(threading.Thread):
    def __init__(self, runtime_dir:str, store:Store, display_name:Optional[str]=None):
        super().__init__()
        self._running:bool = True
        self._storage_path:str = runtime_dir if runtime_dir is not None else tempfile.mkdtemp() # currently won't be deteled when quitting
        logger.info(f"Using LXMF runtime dir {self._storage_path}")
        self._router = None
        self._local_source = None
        self._delivery_handler = LXMFDeliveryHandler(store)
        self._display_name = display_name

    def setup(self, identity:RNS.Identity) -> bool:
        self._router = LXMF.LXMRouter(identity, storagepath=self._storage_path, enforce_stamps=LXMF_ENFORCE_STAMPS)
        # hack to prevent signal to be overrided by LXMROUTER
        self._router.sigint_handler = lambda x:None
        display_name = LXMF_DISPLAY_NAME
        if self._display_name is not None:
            display_name = self._display_name
        self._local_source = self._router.register_delivery_identity(identity, display_name=display_name, stamp_cost=LXMF_REQUIRED_STAMP_COST)
        self._router.register_delivery_callback(self.delivery_callback)
        logger.info(f"Ready to receive LXMF messages on {RNS.prettyhexrep(self._local_source.hash)}")
        return True

    def delivery_callback(self, message) -> None:
        m = self._delivery_handler.delivery_callback(message)
        self.send_message(m.source_hash, m.content)

    def send_message(self, recipient:str, message:str) -> bool:
        recipient_hash = bytes.fromhex(recipient)
    
        if not len(recipient_hash) == RNS.Reticulum.TRUNCATED_HASHLENGTH//8:
            RNS.log("Invalid destination hash length", RNS.LOG_ERROR)
            return False

        if not RNS.Transport.has_path(recipient_hash):
            logger.info("Destination is not yet known. Requesting path...")
            RNS.Transport.request_path(recipient_hash)
            if not RNS.Transport.has_path(recipient_hash):
                logger.info("No path detected, waiting for announce to arrive...")
                return False

        nh = RNS.Transport.next_hop(destination_hash=recipient_hash)
        if nh: nh = nh.hex()
        logger.info(f"Going through {nh} via {RNS.Transport.next_hop_interface(recipient_hash)}")

        recipient_identity = RNS.Identity.recall(recipient_hash)
        dest = RNS.Destination(recipient_identity, RNS.Destination.OUT, RNS.Destination.SINGLE, "lxmf", "delivery")

        lxm = LXMF.LXMessage(dest, self._local_source, content=message, desired_method=LXMF.LXMessage.DIRECT)
        self._router.handle_outbound(lxm)
        logger.info(f"Sent message {message} to peer {dest.hash.hex()}")

    def announce(self, interface:Any) -> None:
        self._local_source.announce(attached_interface=interface)
        try:
            display_name = self._router.delivery_destinations[self._local_source.hash].display_name
        except UnicodeDecodeError:
            display_name = None
        logger.info(f"Announced LXMF server {self._local_source.hash.hex()} with display name {display_name} through {interface}")

    def run(self) -> None:
        while self._running:
            time.sleep(1)

    def quit(self) -> None:
        logger.info(f"Quitting...")
        self._running = False
