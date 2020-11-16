import argparse
import sys

from insomniac.utils import *


def parse_arguments(all_args_dict):
    parser = argparse.ArgumentParser(
        description='Instagram bot for automated Instagram interaction using Android device via ADB',
        add_help=False
    )

    for name, val in all_args_dict.items():
        arg_name = "--{0}".format(name.replace('_', '-'))
        parser.add_argument(arg_name, **val)

    parser.add_argument('--config-file',
                        help='add this argument if you want to load your configuration from a config file. '
                             'Example can be found in config-examples folder')

    if not len(sys.argv) > 1:
        parser.print_help()
        return False, None

    args, unknown_args = parser.parse_known_args()

    if unknown_args:
        print(COLOR_FAIL + "Unknown arguments: " + ", ".join(str(arg) for arg in unknown_args) + COLOR_ENDC)
        parser.print_help()
        return False, None

    if args.config_file is not None:
        if not os.path.exists(args.config_file):
            print(COLOR_FAIL + "Config file {0} could not be found".format(args.config_file) + COLOR_ENDC)
            parser.print_help()
            return False, None

        refresh_args_by_conf_file(args)

    return True, args


def refresh_args_by_conf_file(args):
    if args.config_file is not None:
        if not os.path.exists(args.config_file):
            print(COLOR_FAIL + "Config file {0} could not be found. Continue with previous args".format(args.config_file) + COLOR_ENDC)
            return

        with open(args.config_file, encoding="utf-8") as json_file:
            params = json.load(json_file)

            for param in params:
                if param["enabled"]:
                    args.__setattr__(param["parameter-name"], param["value"])
