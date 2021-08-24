import argparse
import json

from insomniac.utils import *

DEFAULT_APP_ID = "com.instagram.android"

CONFIG_PARAMETER_ENABLED = "enabled"
CONFIG_PARAMETER_NAME = "parameter-name"
CONFIG_PARAMETER_VALUE = "value"

PARAMETER_APP_ID = "app_id"
PARAMETER_DEVICE_ID = "device"
PARAMETER_APP_NAME = "app_name"


def parse_arguments(all_args_dict, starter_conf_file_path):
    parser = argparse.ArgumentParser(
        description='Instagram bot for automated Instagram interaction using Android device via ADB',
        add_help=False
    )

    for name, val in all_args_dict.items():
        arg_name = "--{0}".format(name.replace('_', '-'))
        if "help" not in val:
            parser.add_argument(arg_name, **val, help=argparse.SUPPRESS)
        else:
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

    params = _load_params(config_file)
    if params is None:
        return False

    try:
        args_by_conf_file = args.__getattribute__('args_by_conf_file')
        for arg_name in args_by_conf_file:
            args.__setattr__(arg_name, None)
    except AttributeError:
        pass

    args_by_conf_file = []
    for param in params:
        if param[CONFIG_PARAMETER_ENABLED]:
            args.__setattr__(param[CONFIG_PARAMETER_NAME], param[CONFIG_PARAMETER_VALUE])
            args_by_conf_file.append(param[CONFIG_PARAMETER_NAME])

    args.__setattr__('args_by_conf_file', args_by_conf_file)

    return True


def load_app_id(config_file):
    params = _load_params(config_file)
    if params is None:
        return DEFAULT_APP_ID

    app_id = None
    device_id = None
    app_name = None

    for param in params:
        if param.get(CONFIG_PARAMETER_NAME) == PARAMETER_APP_ID and param.get(CONFIG_PARAMETER_ENABLED):
            app_id = param.get(CONFIG_PARAMETER_VALUE)
        elif param.get(CONFIG_PARAMETER_NAME) == PARAMETER_DEVICE_ID and param.get(CONFIG_PARAMETER_ENABLED):
            device_id = param.get(CONFIG_PARAMETER_VALUE)
        elif param.get(CONFIG_PARAMETER_NAME) == PARAMETER_APP_NAME and param.get(CONFIG_PARAMETER_ENABLED):
            app_name = param.get(CONFIG_PARAMETER_VALUE)

    return resolve_app_id(app_id, device_id, app_name)


def resolve_app_id(app_id, device_id, app_name):
    if app_name is not None:
        from insomniac.extra_features.utils import get_package_by_name
        app_id_by_name = get_package_by_name(device_id, app_name)
        if app_id_by_name is not None:
            print(f"Found app id by app name: {app_id_by_name}")
            return app_id_by_name
        else:
            print(COLOR_FAIL + f"You provided app name \"{app_name}\" but there's no app with such name" + COLOR_ENDC)

    return app_id or DEFAULT_APP_ID


def _load_params(config_file):
    if config_file is None:
        return None

    if not os.path.exists(config_file):
        print(COLOR_FAIL + "Config file {0} could not be found".format(config_file) + COLOR_ENDC)
        return None

    with open(config_file, encoding="utf-8") as json_file:
        return json.load(json_file)
