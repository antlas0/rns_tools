import datetime
import logging

from .announce_info import AnnounceInfo
from .destination_info import DestinationInfoQuerier
from .store import Store

logger = logging.getLogger(__name__)

class AnnounceHandler:
    # The initialisation method takes the optional
    # aspect_filter argument. If aspect_filter is set to
    # None, all announces will be passed to the instance.
    # If only some announces are wanted, it can be set to
    # an aspect string.
    def __init__(self, store:Store, aspect_filter=None):
        self.aspect_filter = aspect_filter
        self._store = store

    def received_announce(self, destination_hash, announced_identity, app_data):
        data = None
        if app_data is not None:
            try:
                data = app_data.decode("utf-8")
            except Exception:
                pass

        announce = AnnounceInfo(
            destination_hash=destination_hash.hex(),
            announced_identity=announced_identity,
            app_data=data,
            date=datetime.datetime.now(),
            destination_info=DestinationInfoQuerier(destination_hash.hex()).fill(),
        )
        self._store.store_announce(announce)
        
        trace = []
        trace.append(announce.date.strftime("%Y-%m-%d %H:%M:%S%z"))
        trace.append(announce.destination_hash)
        trace.append(str(announce.app_data))
        trace.append(str(announce.destination_info.hops_to))
        trace.append(str(announce.destination_info.next_hop))
        trace.append(str(announce.destination_info.next_hop_interface.name))
        logger.info(" | ".join(trace))
        
