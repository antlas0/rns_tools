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
        self._rns_server_runtime_dir = os.path.join(os.path.expanduser('~'), f".{APP_NAME}")
        if args.rns_server_conf is not None:
            self._rns_server_runtime_dir = args.rns_server_conf
        self._rns_server_identity_file = os.path.join(self._rns_server_runtime_dir, "identity")
        if not os.path.isdir(self._rns_server_runtime_dir):
            os.mkdir(self._rns_server_runtime_dir)
        logger.info(f"Using rns_server runtime dir {self._rns_server_runtime_dir}")
        self._worker_runtime_dir = os.path.join(self._rns_server_runtime_dir, f".{APP_NAME}")
        self._reticulum = RNS.Reticulum(configdir=args.rns_conf) 
        self._store = Store()
        self._identity = None
        self._worker = None
        self._announce_handler = None

    def load_identity(self) -> Optional[RNS.Identity]:
        identity = None
        if os.path.isfile(self._rns_server_identity_file):
            try:
                identity = RNS.Identity.from_file(self._rns_server_identity_file)
                logger.info(f"Loaded identity from {self._rns_server_identity_file}")
            except Exception as e:
                logger.warning(f"Could not load local entity, generating new one")
        return identity

    def export_identity(self) -> bool:
        logger.info(f"Export identity to {self._rns_server_identity_file}")
        return RNS.Identity.to_file(self._identity, self._rns_server_identity_file)

    def setup(self) -> bool:
        self._identity = self.load_identity()

        if self._identity is None:
            self._identity = RNS.Identity()
            self.export_identity()

        self._destination = RNS.Destination(
                self._identity,
                RNS.Destination.IN,
                RNS.Destination.SINGLE,
                "rns_server",
            )
        self._destination.set_proof_strategy(RNS.Destination.PROVE_ALL)

        if self._config.lxmf:
            self._worker = LXMFServer(self._worker_runtime_dir, self._store)
            if self._config.lxmf_peer:
                self._worker.set_peer(self._config.lxmf_peer)
            if self._config.lxmf_message:
                self._worker.set_message(self._config.lxmf_message)
        if self._config.serve_directory:
            self._worker = FileServer(self._config.serve_directory)
        if self._config.file_destination:
            self._worker = FileClient(self._config.file_destination, self._config.file_name)
        if self._config.follow_announces:
            self._worker = AnnounceHandler(self._store)
            logger.info("Show received announces")
            RNS.Transport.register_announce_handler(self._worker)

        if self._worker:
            return self._worker.setup(self._identity)

        return True

    def announce(self, interface:Any) -> None:
        nickname = f"{self._destination.hash.hex()}"
        self._destination.announce(app_data=nickname.encode("utf-8"), attached_interface=interface)
        logger.info(f"Announced RNS identity {self._destination.hash.hex()} through {interface}")

    def run(self) -> None:
        if self._config.announce:
            for interface in RNS.Transport.interfaces:
                self.announce(interface)
                if self._worker:
                    self._worker.announce(interface)

        if self._worker:
            self._worker.run()
        self.quit()
    
    def quit(self) -> None:
        logger.info(f"Quitting...")
