import os
import RNS
import threading
import logging
import datetime
from typing import Any
import time

from .store import Store

logger = logging.getLogger(__name__)


class FileServer(threading.Thread):
    def __init__(self, directory:str):
        super().__init__()
        self._running:bool = True
        self._destination:str = None
        self._directory:str = directory

    def setup(self, identity:RNS.Identity) -> bool:
        if not os.path.isdir(self._directory):
            logger.warning(f"Directory {os.path.abspath(self._directory)} not a directory")
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
        logger.info(f"Ready to serve files on {self._destination.hash.hex()} of directory {self._directory}")
        return True

    def announce(self, interface:Any) -> None:
        self._destination.announce(attached_interface=interface)
        logger.info(f"Announced file server {self._destination.hash.hex()} through {interface}")

    def _client_connected(self, link) -> None:
        logger.info(f"Link {link} established")
        link.set_packet_callback(self._transfer_file)
        link.set_link_closed_callback(self._link_closed)

    def _transfer_file(self, message, packet) -> None:
        try:
            filename = message.decode("utf-8")
        except Exception as e:
            filename = None

        filepath = os.path.join(self._directory, filename)
        if os.path.isfile(filepath):
            try:
                logger.info(f"Client requested {filepath}")
                file = open(filepath, "rb")
                
                file_resource = RNS.Resource(
                    file.read(),
                    packet.link,
                    callback=self._resource_sending_concluded
                )

                file_resource.filepath = filepath
            except Exception as e:
                logger.warning(f"Error while reading file {filepath}")
                packet.link.teardown()
                raise e
        else:
            logger.info(f"Client requested unknown file {filepath}")
            packet.link.teardown()        

    def _resource_sending_concluded(self, resource:RNS.Resource) -> None:
        logger.info(f"Sending finished")
        if resource.status == RNS.Resource.COMPLETE:
            logger.info(f"The resource {resource} was sent successfully")
        else:
            logger.info(f"Sending the resource {resource} failed")

    def _link_closed(self, link):
        if link.teardown_reason == RNS.Link.TIMEOUT:
            logger.info("The link timed out")
        elif link.teardown_reason == RNS.Link.DESTINATION_CLOSED:
            logger.info("The link was closed")
        else:
            logger.info("Link closed")        
        time.sleep(1.5)

    def _link_established(self) -> None:
        logger.info("Link established")

    def run(self) -> None:
        while self._running:
            time.sleep(0.1)

    def quit(self) -> None:
        logger.info(f"Quitting...")
        self._running = False