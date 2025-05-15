import argparse
import logging

from .manager import Manager

logging.basicConfig(format='[%(asctime)s][%(name)-35s][%(levelname)-7s] %(message)s',
                    datefmt='%y-%m-%d %H:%M:%S%z')
logging.getLogger().setLevel(logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reticulum vizualiser"
    )

    parser.add_argument("--rns-conf", action="store", default=None, help="Path to alternative Reticulum config directory.",type=str,)
    parser.add_argument("-a", "--announce", action="store_true", default=False, help="Announce at startup.",)
    parser.add_argument("-l", "--lxmf", action="store_true", default=False, help="Activate LXMF exchange.",)
    parser.add_argument("-s", "--file-sender", action="store", default=None, help="Send a file to a destination.",)
    parser.add_argument("-F", "--file-to-send", action="store", default=None, help="Choose the file to send.",)
    parser.add_argument("-r", "--file-receiver", action="store", default=None, help="Receive a file to directory",)

    args = parser.parse_args()
    m = Manager(args)
    m.setup()
    m.run()

