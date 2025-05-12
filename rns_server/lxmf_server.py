import RNS
import LXMF
import time
import threading
import logging
import tempfile

from .resources import LXMF_REQUIRED_STAMP_COST, LXMF_ENFORCE_STAMPS, LXMF_DISPLAY_NAME


logger = logging.getLogger(__name__)


class LXMFServer(threading.Thread):
    def __init__(self, runtime_dir:str):
        super().__init__()
        self._running:bool = True
        self._storage_path:str = runtime_dir if runtime_dir is not None else tempfile.mkdtemp() # currently won't be deteled when quitting
        logger.info(f"Using LXMF runtime dir {self._storage_path}")
        self._router = LXMF.LXMRouter(storagepath=self._storage_path, enforce_stamps=LXMF_ENFORCE_STAMPS)
        self._destination = None

    def delivery_callback(self, message):
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

        dest = message.source
        lxm = LXMF.LXMessage(dest, self._destination, message.content_as_string(), None, desired_method=LXMF.LXMessage.DIRECT, include_ticket=True)
        self._router.handle_outbound(lxm)

    def setup(self, identity:RNS.Identity) -> bool:
        self._destination = self._router.register_delivery_identity(identity, display_name=LXMF_DISPLAY_NAME, stamp_cost=LXMF_REQUIRED_STAMP_COST)
        self._router.register_delivery_callback(self.delivery_callback)
        logger.info(f"Ready to receive LXMF messages on {RNS.prettyhexrep(self._destination.hash)}")
        return True

    def announce(self) -> None:
        logger.info(f"Announced LXMF server {self._destination.hash.hex()}")
        self._router.announce(self._destination.hash)

    def run(self) -> None:
        while self._running:
            time.sleep(1)

    def quit(self) -> None:
        logger.info(f"Quitting...")
        self._running = False