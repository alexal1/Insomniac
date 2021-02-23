import argparse
import json

import insomniac.__version__ as __version__
from insomniac import network
from insomniac.activation import activation_controller
from insomniac.network import HTTP_OK
from insomniac.params import parse_arguments
from insomniac.utils import *


def run(activation_code="", starter_conf_file_path=None):
    if not __version__.__debug_mode__:
        print_timeless(COLOR_OKGREEN + __version__.__logo__ + COLOR_ENDC)
        print_version()

    activation_code_from_args = _get_activation_code_from_args()
    if activation_code_from_args is not None:
        activation_code = activation_code_from_args

    activation_controller.validate(activation_code)
    if not activation_controller.is_activated:
        from insomniac.session import InsomniacSession
        print_timeless("Using insomniac session-manager without extra-features")
        insomniac_session = InsomniacSession(starter_conf_file_path)
    else:
        from insomniac.extra_features.session import ExtendedInsomniacSession
        insomniac_session = ExtendedInsomniacSession(starter_conf_file_path)

    insomniac_session.run()


def is_newer_version_available():
    def versiontuple(v):
        return tuple(map(int, (v.split("."))))

    current_version = __version__.__version__
    latest_version = _get_latest_version('insomniac')
    if latest_version is not None and versiontuple(latest_version) > versiontuple(current_version):
        return True, latest_version

    return False, None


def print_version():
    print_timeless_ui(COLOR_HEADER + f"Insomniac v{__version__.__version__}" + COLOR_ENDC)
    is_new_version_available, latest_version = is_newer_version_available()
    if is_new_version_available:
        print_timeless(COLOR_HEADER + f"Newer version is available (v{latest_version}). Please run" + COLOR_ENDC)
        print_timeless(COLOR_HEADER + COLOR_BOLD + "python3 -m pip install insomniac --upgrade" + COLOR_ENDC)
    print_timeless("")


def _get_latest_version(package):
    latest_version = None
    code, body, _ = network.get(f"https://pypi.python.org/pypi/{package}/json")
    if code == HTTP_OK and body is not None:
        json_package = json.loads(body)
        latest_version = json_package['info']['version']
    return latest_version


def _get_activation_code_from_args():
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--activation-code')
    try:
        args, _ = parser.parse_known_args()
    except (argparse.ArgumentError, TypeError):
        return None
    return args.activation_code


class ArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        pass
