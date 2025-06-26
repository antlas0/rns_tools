import RNS
import LXMF
import logging
import time

from .lxmf_message_info import LXMFMessageInfo
from .store import Store


logger = logging.getLogger(__name__)

class LXMFDeliveryHandler:
    def __init__(self, store:Store):
        self._store = store

    def delivery_callback(self, message) -> LXMFMessageInfo:
        stamp_string:str = ""
        time_string      = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(message.timestamp))
        signature_string = "Signature is invalid, reason undetermined"
        if message.signature_validated:
            signature_string = "Validated"
        else:
            if message.unverified_reason == LXMF.LXMessage.SIGNATURE_INVALID:
                signature_string = "Invalid signature"
            if message.unverified_reason == LXMF.LXMessage.SOURCE_UNKNOWN:
                signature_string = "Cannot verify, source is unknown"

            if message.stamp_valid:
                stamp_string = "Validated"
            else:
                stamp_string = "Invalid"

        logger.info("\t+--- LXMF Delivery ---------------------------------------------")
        logger.info("\t| Source hash            : "+RNS.prettyhexrep(message.source_hash))
        logger.info("\t| Source instance        : "+str(message.get_source()))
        logger.info("\t| Destination hash       : "+RNS.prettyhexrep(message.destination_hash))
        logger.info("\t| Destination instance   : "+str(message.get_destination()))
        logger.info("\t| Transport Encryption   : "+str(message.transport_encryption))
        logger.info("\t| Timestamp              : "+time_string)
        logger.info("\t| Title                  : "+str(message.title_as_string()))
        logger.info("\t| Content                : "+str(message.content_as_string()))
        logger.info("\t| Fields                 : "+str(message.fields))
        if message.ratchet_id:
            logger.info("\t| Ratchet                : "+str(RNS.Identity._get_ratchet_id(message.ratchet_id)))
            logger.info("\t| Message signature      : "+signature_string)
            logger.info("\t| Stamp                  : "+stamp_string)
            logger.info("\t+---------------------------------------------------------------")

        m = LXMFMessageInfo(
            source_hash=RNS.hexrep(message.source_hash, delimit=False),
            destination_hash=RNS.hexrep(message.destination_hash, delimit=False),
            source_instance=str(message.get_source()),
            destination_instance=str(message.get_destination()),
            rssi=message.rssi,
            q=message.q,
            snr=message.snr,
            packed_size=message.packed_size,
            content=message.content_as_string(),
        )
        self._store.store_message(m)
        return m

