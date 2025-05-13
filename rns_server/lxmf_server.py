import RNS
import LXMF
import time
import threading
import logging
import tempfile

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
        self._destination = None
        self._delivery_handler = LXMFDeliveryHandler(store)

    def setup(self, identity:RNS.Identity) -> bool:
        self._destination = self._router.register_delivery_identity(identity, display_name=LXMF_DISPLAY_NAME, stamp_cost=LXMF_REQUIRED_STAMP_COST)
        self._router.register_delivery_callback(self._delivery_handler.delivery_callback)
        logger.info(f"Ready to receive LXMF messages on {RNS.prettyhexrep(self._destination.hash)}")
        return True

    def announce(self) -> None:
        logger.info(f"Announced LXMF server {self._destination.hash.hex()}")
        self._router.announce(self._destination.hash)

    def run(self) -> None:
        while self._running:
            time.sleep(1)

    def quit(self) -> None:
        logger.info(f"Quitting...")
        self._running = False