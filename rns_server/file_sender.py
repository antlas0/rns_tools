import os
import RNS
import threading
import logging
from typing import Any
import time

from .store import Store

logger = logging.getLogger(__name__)


class FileSender(threading.Thread):
    def __init__(self, destination:str, filepath:str):
        super().__init__()
        self._running:bool = True
        self._destination:str = destination
        self._filepath:str = filepath
        logger.info(f"Will upload {self._filepath} to {self._destination}")

    def setup(self, identity:RNS.Identity) -> bool:
        try:
            dest_len = (RNS.Reticulum.TRUNCATED_HASHLENGTH//8)*2
            if len(self._destination) != dest_len:
                raise ValueError(
                    "Destination length is invalid, must be {hex} hexadecimal characters ({byte} bytes).".format(hex=dest_len, byte=dest_len//2)
                )
            self._destination_hash = bytes.fromhex(self._destination)
        except:
            logger.info("Invalid destination entered. Check your input!\n")
            return False

        if not RNS.Transport.has_path(self._destination_hash):
            logger.info("Destination is not yet known. Requesting path and waiting for announce to arrive...")
            RNS.Transport.request_path(self._destination_hash)
            while not RNS.Transport.has_path(self._destination_hash):
                time.sleep(0.1)
        return True

    def announce(self, interface:Any) -> None:
        pass

    def run(self) -> None:
        # Recall the server identity
        server_identity = RNS.Identity.recall(self._destination_hash)
        logger.info(f"Establishing link with {self._destination}...")
        server_destination = RNS.Destination(
            server_identity,
            RNS.Destination.OUT,
            RNS.Destination.SINGLE,
            "FileSender",
            "filetransfer",
            "server"
        )
        server_destination.set_proof_strategy(RNS.Destination.PROVE_ALL)
        link = RNS.Link(server_destination)
        link.set_link_established_callback(self._link_established)
        link.set_link_closed_callback(self._link_closed)

        while self._running:
            time.sleep(0.1)

    def _link_established(self, link) -> None:
        try:
            file = open(os.path.join(self._filepath), "rb")
        except Exception as e:
            logger.warning(f"Could not open file {self._filepath}: {e}")
        else:
            RNS.Resource(
                file.read(),
                link,
                callback=self._resource_sending_concluded
            )

    def _link_closed(self, link):
        if link.teardown_reason == RNS.Link.TIMEOUT:
            logger.info("The link timed out, exiting now")
        elif link.teardown_reason == RNS.Link.DESTINATION_CLOSED:
            logger.info("The link was closed by the server, exiting now")
        else:
            logger.info("Link closed, exiting now")
        
        time.sleep(1.5)

    def _resource_sending_concluded(self, resource:RNS.Resource) -> None:
        logger.info(f"Sending finished")
        if resource.status == RNS.Resource.COMPLETE:
            logger.info(f"The resource {resource} was sent successfully")
        else:
            logger.info(f"Sending the resource {resource} failed")

    def quit(self) -> None:
        logger.info(f"Quitting...")
        self._running = False