import os
import RNS
import threading
import logging
from typing import Any
import time
import datetime

from .store import Store

logger = logging.getLogger(__name__)


class FileClient(threading.Thread):
    def __init__(self, destination:str, filepath:str):
        super().__init__()
        self._running:bool = True
        self._destination:str = destination
        self._filepath:str = filepath
        logger.info(f"Will download {self._filepath} from {self._destination}")

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
        return True

    def announce(self, interface:Any) -> None:
        pass

    def run(self) -> None:
        # Recall the server identity
        if not RNS.Transport.has_path(self._destination_hash):
            logger.info("Destination is not yet known. Requesting path and waiting for announce to arrive...")
            RNS.Transport.request_path(self._destination_hash)
            while not RNS.Transport.has_path(self._destination_hash):
                time.sleep(0.1)

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
        self._link = RNS.Link(server_destination)
        self._link.set_resource_strategy(RNS.Link.ACCEPT_ALL)
        self._link.set_link_established_callback(self._link_established)
        self._link.set_resource_started_callback(self._receive_began)
        self._link.set_resource_concluded_callback(self._receive_concluded)

        while self._running:
            time.sleep(0.1)

    def _link_established(self, link) -> None:
        logger.info(f"Link {link} established")
        logger.info(f"Requesting file {self._filepath}")
        p = RNS.Packet(link, self._filepath.encode("utf-8"), create_receipt=False)
        p.send()

    def _receive_began(self, resource:RNS.Resource) -> None:
        logger.info("Began to receive")

    def _receive_concluded(self, resource:RNS.Resource) -> None:
        logger.info("Finished to receive")
        if resource.status == RNS.Resource.COMPLETE:
            datum = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S%z")
            filename = os.path.join("./", f"resource_{datum}")
            logger.info(f"Resource {resource} received")
            with open(filename, "wb") as f:
                f.write(resource.data.read())
        else:
            logger.info(f"Receiving resource {resource} failed")
        self.quit()

    def quit(self) -> None:
        logger.info(f"Quitting...")
        self._running = False
        if self._link:
            self._link.teardown()