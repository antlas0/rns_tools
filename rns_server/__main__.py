import argparse
import logging
import signal

from .manager import Manager

logging.basicConfig(format='[%(asctime)s][%(name)-35s][%(levelname)-7s] %(message)s',
                    datefmt='%y-%m-%d %H:%M:%S%z')
logging.getLogger().setLevel(logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reticulum vizualiser"
    )

    parser.add_argument(
        "--rns",
        action="store",
        default=None,
        help="path to alternative Reticulum config directory",
        type=str,
    )

    parser.add_argument(
        "--announce",
        action="store_true",
        default=False,
        help="Announce at startup",
    )

    args = parser.parse_args()
    m = Manager(args)
    signal.signal(signal.SIGINT, m.quit)
    m.setup()
    m.run()

