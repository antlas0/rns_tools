import os
import RNS
import time
import logging
from typing import Optional, Any

from .announce_handler import AnnounceHandler
from .lxmf_server import LXMFServer
from .file_server import FileServer
from .file_client import FileClient
from .store import Store
from .resources import APP_NAME

logger = logging.getLogger(__name__)


class Manager:
    def __init__(self, args:dict):
        self._running:bool = True
        self._config = args
        logger.info(f"Using RNS configdir {args.rns_conf}")
        self._rns_tools_runtime_dir = os.path.join(os.path.expanduser('~'), f".{APP_NAME}")
        if args.rns_tools_conf is not None:
            self._rns_tools_runtime_dir = args.rns_tools_conf
        self._rns_tools_identity_file = os.path.join(self._rns_tools_runtime_dir, "identity")
        if not os.path.isdir(self._rns_tools_runtime_dir):
            os.mkdir(self._rns_tools_runtime_dir)
        logger.info(f"Using rns_tools runtime dir {self._rns_tools_runtime_dir}")
        self._worker_runtime_dir = os.path.join(self._rns_tools_runtime_dir)
        self._reticulum = RNS.Reticulum(configdir=args.rns_conf) 
        self._store = Store()
        self._identity = None
        self._worker = None
        self._announce_handler = None
        self._announce_follower = None

    def load_identity(self) -> Optional[RNS.Identity]:
        identity = None
        if os.path.isfile(self._rns_tools_identity_file):
            try:
                identity = RNS.Identity.from_file(self._rns_tools_identity_file)
                logger.info(f"Loaded identity from {self._rns_tools_identity_file}")
            except Exception as e:
                logger.warning(f"Could not load local entity, generating new one")
        return identity

    def export_identity(self) -> bool:
        logger.info(f"Export identity to {self._rns_tools_identity_file}")
        return RNS.Identity.to_file(self._identity, self._rns_tools_identity_file)

    def setup(self) -> bool:
        self._identity = self.load_identity()

        if self._identity is None:
            self._identity = RNS.Identity()
            self.export_identity()

        if self._config.lxmf:
            self._worker = LXMFServer(self._worker_runtime_dir, self._store, display_name=self._config.lxmf_display_name)
        if self._config.serve_directory:
            self._worker = FileServer(self._config.serve_directory)
        if self._config.file_destination:
            self._worker = FileClient(self._config.file_destination, self._config.file_name)
        self._announce_follower = AnnounceHandler(self._store)

        self._announce_follower.setup(self._identity)
        self._worker.setup(self._identity)

        return True

    def run(self) -> None:
        if self._config.announce:
            for interface in RNS.Transport.interfaces:
                self._worker.announce(interface)

        self._announce_follower.start()
        self._worker.start()

        self._announce_follower.join()
        self._worker.join()

    def quit(self) -> None:
        logger.info(f"Quitting...")
        self._worker.quit()
