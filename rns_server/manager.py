import os
import RNS
import logging
import time
import signal
from typing import Optional, Any

from .announce_handler import AnnounceHandler
from .lxmf_server import LXMFServer
from .file_receiver import FileReceiver
from .file_sender import FileSender
from .store import Store
from .resources import APP_NAME

logger = logging.getLogger(__name__)


class Manager:
    def __init__(self, args:dict):
        self._running:bool = True
        self._config = args
        logger.info(f"Using RNS configdir {args.rns_conf}")
        self._rns_server_runtime_dir = os.path.join(os.path.expanduser('~'), f".{APP_NAME}")
        self._rns_server_identity_file = os.path.join(self._rns_server_runtime_dir, "identity")
        if not os.path.isdir(self._rns_server_runtime_dir):
            os.mkdir(self._rns_server_runtime_dir)
        logger.info(f"Using rns_server runtime dir {self._rns_server_runtime_dir}")
        self._lxmf_server_runtime_dir = os.path.join(os.path.expanduser('~'), f".{APP_NAME}")
        self._reticulum = RNS.Reticulum(configdir=args.rns_conf) 
        self._store = Store()
        self._lxmf_server = None
        self._identity = None
        self._announce_handler = AnnounceHandler(self._store)
        self._file_manager = None

    def load_identity(self) -> Optional[RNS.Identity]:
        identity = None
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

        if self._config.lxmf:
            self._lxmf_server = LXMFServer(self._lxmf_server_runtime_dir, self._store)
        if self._config.file_receiver:
            self._file_manager = FileReceiver(self._config.file_receiver)
        if self._config.file_sender:
            self._file_manager = FileSender(self._config.file_sender, self._config.file_to_send)

        if self._lxmf_server:
            self._lxmf_server.setup(self._identity)
        if self._file_manager:
            self._file_manager.setup(self._identity)

        self._destination.set_proof_strategy(RNS.Destination.PROVE_ALL)

        self._announce_handler = AnnounceHandler(self._store)
        RNS.Transport.register_announce_handler(self._announce_handler)
        signal.signal(signal.SIGINT, self.quit)
        return True

    def announce(self, interface:Any) -> None:
        nickname = f"{self._destination.hash.hex()}"
        self._destination.announce(app_data=nickname.encode("utf-8"), attached_interface=interface)
        logger.info(f"Announced RNS identity {self._destination.hash.hex()} through {interface}")

    def run(self) -> None:
        if self._config.announce:
            for interface in RNS.Transport.interfaces:
                self.announce(interface)
                if self._lxmf_server:
                    self._lxmf_server.announce(interface)
                if self._file_manager:
                    self._file_manager.announce(interface)
        if self._lxmf_server:
            self._lxmf_server.start()
        if self._file_manager:
            self._file_manager.start()
        if self._lxmf_server:
            self._lxmf_server.join()
        if self._file_manager:
            self._file_manager.join()

        while self._running:
            time.sleep(0.1)
    
    def quit(self, sig, frame) -> None:
        logger.info(f"Quitting...")
        self._running = False
        if self._lxmf_server:
            self._lxmf_server.quit()
        if self._file_manager:
            self._file_manager.quit()
