import argparse
import logging

from .listener import Listener

logging.basicConfig(format='[%(asctime)s][%(name)-20s][%(levelname)-7s] %(message)s',
                    datefmt='%y-%m-%d %H:%M:%S%z')
logging.getLogger().setLevel(logging.INFO)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reticulum packet dumper"
    )

    parser.add_argument("--rns-conf", action="store", default=None, help="Path to alternative Reticulum config directory.",type=str,)
    parser.add_argument("--app-conf", action="store", default=None, help="Path to alternative rnsdump runtime directory.",type=str,)
    parser.add_argument("-L", "--lxmf-display-name", action="store", default="LXMF_SERVER", help="Display name for LXMF server, default LXMF_SERVER.",type=str,)
    parser.add_argument("-A", "--reannounce", action="store_true", default=False, help="If True, it will announce when it gets an announce.")
    parser.add_argument("-R", "--lxmf-reply", action="store_true", default=False, help="If True, it will reply a tempalte message to LXMF messages.")

    args = parser.parse_args()
    l = Listener(args)
    if l.setup():
        l.run()


if __name__ == "__main__":
    main()
