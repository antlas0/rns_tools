import RNS
import logging

logger = logging.getLogger(__name__)


def packet_viewer(data, packet):
    reticulum = RNS.Reticulum.get_instance()

    reception_snr, reception_rssi = None, None
    if reticulum.is_connected_to_shared_instance:
        reception_rssi = reticulum.get_packet_rssi(packet.packet_hash)
        reception_snr  = reticulum.get_packet_snr(packet.packet_hash)
    else:
        if packet.rssi != None:
            reception_rssi = str(packet.rssi)
        if packet.snr != None:
            reception_snr = str(packet.snr)

    info = [
        "header_type", 
        "packet_type", 
        "transport_type", 
        "context", 
        "context_flag", 
        "destination", 
        "transport_id", 
        "data",
        ]
    trace = []
    for key in info:
        trace.append(f"{key[0]}:{getattr(packet, key)}")

    trace.append(f"f: {packet.get_packed_flags()}")
    trace.append(f"snr: {reception_snr}")
    trace.append(f"rssi: {reception_rssi}")
    logger.info(" | ".join(trace))

    return [data, packet]


def proof_viewer(packet) -> None:
    logger.info(packet)

def link_viewer(link) -> None:
    logger.info(link)

