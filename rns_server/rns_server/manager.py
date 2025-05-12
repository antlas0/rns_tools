import os
import RNS
import logging
from typing import Optional

from .announce_handler import AnnounceHandler
from .lxmf_server import LXMFServer
from .store import Store
from .resources import APP_NAME

logger = logging.getLogger(__name__)


class Manager:
    def __init__(self, args:dict):
        self._running:bool = True
        self._config = args
        logger.info(f"Using RNS configdir {args.rns}")
        self._rns_server_runtime_dir = os.path.join(os.path.expanduser('~'), f".{APP_NAME}")
        self._rns_server_identity_file = os.path.join(self._rns_server_runtime_dir, "identity")
        if not os.path.isdir(self._rns_server_runtime_dir):
            os.mkdir(self._rns_server_runtime_dir)
        logger.info(f"Using rns_server runtime dir {self._rns_server_runtime_dir}")
        self._lxmf_server_runtime_dir = os.path.join(os.path.expanduser('~'), f".{APP_NAME}")
        self._reticulum = RNS.Reticulum(configdir=args.rns)        
        self._announce_handler = None
        self._store = Store()
        self._lxmf_server = LXMFServer(self._lxmf_server_runtime_dir)
        self._identity = None

    def load_identity(self) -> Optional[RNS.Identity]:
        identity = None
        try:
            identity = RNS.Identity.from_file(self._rns_server_identity_file)
            logger.info(f"Loaded identity from {self._rns_server_identity_file}")
        except Exception as e:
            logger.warning(f"Could not load local entity, generating new one")
        return identity

    def export_identity(self) -> bool:
        return RNS.Identity.to_file(self._identity, self._rns_server_identity_file)

    def setup(self) -> bool:
        self._identity = self.load_identity()

        if self._identity is None:
            self._identity = RNS.Identity()

        self._destination = RNS.Destination(
                self._identity,
                RNS.Destination.IN,
                RNS.Destination.SINGLE,
                "rns_server",
                "lxmf",
            )
        self._destination.set_proof_strategy(RNS.Destination.PROVE_ALL)

        self._announce_handler = AnnounceHandler(self._store)
        RNS.Transport.register_announce_handler(self._announce_handler)
        self._lxmf_server.setup(self._identity)
        return True

    def announce(self) -> None:
        nickname = f"{self._destination.hash.hex()}"
        for interface in RNS.Transport.interfaces:
            logger.info(f"{interface}")
            self._destination.announce(app_data=nickname.encode("utf-8"), attached_interface=interface)
            logger.info(f"Announced RNS identity {self._destination.hash.hex()} through {interface}")

    def run(self) -> None:
        self._lxmf_server.start()
        if self._config.announce:
            self.announce()
            self._lxmf_server.announce()

        self._lxmf_server.join()
    
    def quit(self, sig, frame) -> None:
        logger.info(f"Quitting...")
        self._running = False
        self.export_identity()
        self._lxmf_server.quit()
