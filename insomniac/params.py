import argparse
import json

from insomniac.utils import *


def parse_arguments(all_args_dict, starter_conf_file_path):
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
    parser.add_argument('--activation-code',
                        help="provide an activation code via this argument. It will override the one passed via "
                             "start.py. You can get your activation code at https://insomniac-bot.com/activate/",
                        metavar="92002505-31c2-4551-a136-92799fc0800e",
                        default=None)

    if not len(sys.argv) > 1 and starter_conf_file_path is None:
        parser.print_help()
        return False, None

    args, unknown_args = parser.parse_known_args()

    if unknown_args:
        print(COLOR_FAIL + "Unknown arguments: " + ", ".join(str(arg) for arg in unknown_args) + COLOR_ENDC)
        parser.print_help()
        return False, None

    if starter_conf_file_path is not None:
        args.config_file = starter_conf_file_path

    if args.config_file is not None:
        if not os.path.exists(args.config_file):
            print(COLOR_FAIL + "Config file {0} could not be found".format(args.config_file) + COLOR_ENDC)
            parser.print_help()
            return False, None

        refresh_args_by_conf_file(args)

    return True, args


def refresh_args_by_conf_file(args, conf_file_name=None):
    config_file = conf_file_name
    if config_file is None:
        config_file = args.config_file

    if config_file is not None:
        if not os.path.exists(config_file):
            print(COLOR_FAIL + "Config file {0} could not be found - aborting. "
                               "Please check your file-path and try again.".format(config_file) + COLOR_ENDC)
            return False

        try:
            args_by_conf_file = args.__getattribute__('args_by_conf_file')
            for arg_name in args_by_conf_file:
                args.__setattr__(arg_name, None)
        except AttributeError:
            pass

        args_by_conf_file = []

        with open(config_file, encoding="utf-8") as json_file:
            params = json.load(json_file)

            for param in params:
                if param["enabled"]:
                    args.__setattr__(param["parameter-name"], param["value"])
                    args_by_conf_file.append(param["parameter-name"])

        args.__setattr__('args_by_conf_file', args_by_conf_file)

    return True
