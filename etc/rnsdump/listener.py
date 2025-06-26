import os
import RNS
import LXMF
import logging
from typing import Optional
import time

from .announce_handler import AnnounceHandler
from .resources import APP_NAME, LXMF_ENFORCE_STAMPS
from .packets_viewer import packet_viewer, proof_viewer, link_viewer

logger = logging.getLogger(__name__)


class Listener:
    def __init__(self, args:dict):
        logger.info(f"Using RNS configdir {args.rns_conf}")
        self._runtime_dir = os.path.join(os.path.expanduser('~'), f".{APP_NAME}")
        if args.app_conf is not None:
            self._runtime_dir = args.app_conf
        self._app_identity_file = os.path.join(self._runtime_dir, "identity")
        if not os.path.isdir(self._runtime_dir):
            os.mkdir(self._runtime_dir)
        logger.info(f"Using rnsdump runtime dir {self._runtime_dir}")
        self._reticulum = RNS.Reticulum(configdir=args.rns_conf) 
        self._in, self._out, self._router = None, None, None
        self._lxmf_display_name = args.lxmf_display_name
        self._reannounce = args.reannounce
        self._lxmf_reply = args.lxmf_reply

    def load_identity(self) -> Optional[RNS.Identity]:
        identity = None
        if os.path.isfile(self._app_identity_file):
            try:
                identity = RNS.Identity.from_file(self._app_identity_file)
                logger.info(f"Loaded identity from {self._app_identity_file}")
            except Exception as e:
                logger.warning(f"Could not load local entity, generating new one")
        return identity

    def export_identity(self) -> bool:
        logger.info(f"Export identity to {self._app_identity_file}")
        return RNS.Identity.to_file(self._identity, self._app_identity_file)

    def setup(self) -> bool:
        self._identity = self.load_identity()

        if self._identity is None:
            self._identity = RNS.Identity()
            self.export_identity()
        
        self._in = RNS.Destination(
                self._identity,
                RNS.Destination.IN,
                RNS.Destination.SINGLE,
                APP_NAME,
                "lxmf",
                "delivery"
            )
        self._in.set_proof_strategy(RNS.Destination.PROVE_ALL)
        self._in.set_packet_callback(packet_viewer)
        self._in.set_proof_requested_callback(proof_viewer)
        self._in.set_link_established_callback(link_viewer)

        self._router = LXMF.LXMRouter(self._identity, storagepath=self._runtime_dir, enforce_stamps=LXMF_ENFORCE_STAMPS)
        self._router.register_delivery_callback(self.lxmf_delivery_callback)
        self._local_source = self._router.register_delivery_identity(self._identity, display_name=self._lxmf_display_name, stamp_cost=None)

        self.lxmf_announce()

        announce_handler = AnnounceHandler(reannounce=self._reannounce, callback_reannounce=self.lxmf_announce)
        RNS.Transport.register_announce_handler(announce_handler)

        def __f(data, packet):
            res = packet_viewer(data, packet)
            RNS.Transport.path_request_handler(
                res[0],
                res[1]
                )
        RNS.Transport.path_request_destination.set_packet_callback(__f)

        def __g(data, packet):
            res = packet_viewer(data, packet)
            RNS.Transport.tunnel_synthesize_handler(
                res[0],
                res[1]
                )
        RNS.Transport.tunnel_synthesize_destination.set_packet_callback(__g)
        return True

    def lxmf_delivery_callback(self, message) -> None:
        # time_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(message.timestamp))
        signature_string = "Signature is invalid, reason undetermined"
        if message.signature_validated:
            signature_string = "Validated"
        else:
            if message.unverified_reason == LXMF.LXMessage.SIGNATURE_INVALID:
                signature_string = "Invalid signature"
            if message.unverified_reason == LXMF.LXMessage.SOURCE_UNKNOWN:
                signature_string = "Cannot verify, source is unknown"

        trace = []

        trace.append("src: " + str(message.source_hash.hex()))
        trace.append("dst: " + str(message.destination_hash.hex()))
        trace.append("title: " + str(message.title_as_string() if message.title_as_string() else None))
        trace.append("message: " + str(message.content_as_string() if message.content_as_string() else None))
        trace.append("encrypted:" + str(message.transport_encryption))
        trace.append("sign: "+ signature_string)
        trace.append("snr: " + str(message.snr))
        trace.append("rssi: " + str(message.rssi))
        trace.append("q: " + str(message.q))
        logger.info(" | ".join(trace))

        if self._lxmf_reply:
            reply = "73's from F4LFN. Details: " + " | ".join(trace)
            self.lxmf_reply(message.source, reply)

    def lxmf_announce(self) -> None:
        self._local_source.announce()
        logger.info(f"Announced LXMF server {self._local_source.hash.hex()} with display name {self._lxmf_display_name}")

    def lxmf_reply(self, destination, message) -> None:
        lxm = LXMF.LXMessage(destination, self._local_source, content=message, title=None, desired_method=LXMF.LXMessage.DIRECT, include_ticket=True)
        self._router.handle_outbound(lxm)
        logger.info(f"Sent message {message} to peer {destination}")

    def run(self) -> None:
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
