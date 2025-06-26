from typing import Any, Optional
import logging
from .destination_info import DestinationInfoQuerier

logger = logging.getLogger(__name__)


class AnnounceHandler:
    # The initialisation method takes the optional
    # aspect_filter argument. If aspect_filter is set to
    # None, all announces will be passed to the instance.
    # If only some announces are wanted, it can be set to
    # an aspect string.
    def __init__(self, aspect_filter=None, reannounce:bool=False, callback_reannounce:Optional[Any]=None):
        self.aspect_filter = aspect_filter
        self.reannounce = reannounce
        self.cbr = callback_reannounce

    def received_announce(self, destination_hash, announced_identity, app_data):
        data = None
        if app_data is not None:
            try:
                data = app_data.decode("UTF-8", errors="ignore")
            except Exception as e:
                logger.warning(f"Error when decoding announce: {e}")


        destination_info=DestinationInfoQuerier(destination_hash.hex()).fill()

        trace = []
        trace.append(f"dst: {destination_hash.hex()}")
        trace.append(f"id: {announced_identity}")
        trace.append(f"dt: {data}")
        trace.append(f"nh: {destination_info.next_hop_interface}")
        logger.info(" | ".join(trace))

        if self.reannounce:
            self.cbr()