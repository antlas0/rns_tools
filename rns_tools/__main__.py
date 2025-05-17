import argparse
import logging

from .manager import Manager

logging.basicConfig(format='[%(asctime)s][%(name)-35s][%(levelname)-7s] %(message)s',
                    datefmt='%y-%m-%d %H:%M:%S%z')
logging.getLogger().setLevel(logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reticulum tools"
    )

    parser.add_argument("--rns-conf", action="store", default=None, help="Path to alternative Reticulum config directory.",type=str,)
    parser.add_argument("--rns-tools-conf", action="store", default=None, help="Path to alternative rns-server runtime directory.",type=str,)
    parser.add_argument("-a", "--announce", action="store_true", default=False, help="Announce at startup.",)
    parser.add_argument("-f", "--follow-announces", action="store_true", default=False, help="Show broadcasted announces.",)
    parser.add_argument("-l", "--lxmf", action="store_true", default=False, help="Activate LXMF exchange.",)
    parser.add_argument("-L", "--lxmf-display-name", action="store", default=None, type=str, help="LXMF node display name.",)
    parser.add_argument("-p", "--lxmf-peer", action="store", default=None, help="Specify a per to send a message to.",)
    parser.add_argument("-m", "--lxmf-message", action="store", default=None, help="Specify a message to be sent.",)
    parser.add_argument("-d", "--file-destination", action="store", default=None, help="Download a file from a RNS destination.",)
    parser.add_argument("-F", "--file-name", action="store", default=None, help="Specify the filename to download.",)
    parser.add_argument("-s", "--serve-directory", action="store", default=None, help="Specify which directory to server as a file server.",)

    args = parser.parse_args()
    m = Manager(args)
    if m.setup():
        m.run()

