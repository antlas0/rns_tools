import os
import RNS
import threading
import logging
import datetime
from typing import Any
import time

from .store import Store

logger = logging.getLogger(__name__)


class FileReceiver(threading.Thread):
    def __init__(self, directory:str):
        super().__init__()
        self._running:bool = True
        self._destination:str = None
        self._directory:str = directory

    def setup(self, identity:RNS.Identity) -> bool:
        try:
            os.makedirs(self._directory, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not create directoy {self._directory}: {e}")
            return False

        self._destination = RNS.Destination(
                identity,
                RNS.Destination.IN,
                RNS.Destination.SINGLE,
                "FileSender",
                "filetransfer",
                "server"
            )
        self._destination.set_proof_strategy(RNS.Destination.PROVE_ALL)
        self._destination.set_link_established_callback(self._client_connected)
        logger.info(f"Ready to get files on {self._destination}")
        return True

    def announce(self, interface:Any) -> None:
        self._destination.announce(attached_interface=interface)
        logger.info(f"Announced file server {self._destination.hash.hex()} through {interface}")

    def _client_disconnected(self) -> None:
        logger.info(f"Client disconnected")

    def _client_connected(self, link) -> None:
        link.set_link_closed_callback(self._client_disconnected)
        link.set_resource_strategy(RNS.Link.ACCEPT_ALL)
        link.set_resource_started_callback(self._receive_began)
        link.set_resource_concluded_callback(self._receive_concluded)

    def _receive_began(self, resource:RNS.Resource) -> None:
        logger.info("Began to receive")

    def _receive_concluded(self, resource:RNS.Resource) -> None:
        logger.info("Finished to receive")
        if resource.status == RNS.Resource.COMPLETE:
            datum = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S%z")
            filename = os.path.join(self._directory, f"resource_{datum}")
            logger.info(f"Resource {resource} received")
            with open(filename, "wb") as f:
                f.write(resource.data.read())
        else:
            logger.info(f"Receiving resource {resource} failed")

    def _link_established(self) -> None:
        logger.info("Link established")

    def _link_closed(self) -> None:
        logger.info("Link closed")


    def run(self) -> None:
        while self._running:
            time.sleep(0.1)

    def quit(self) -> None:
        logger.info(f"Quitting...")
        self._running = False