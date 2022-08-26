from http.client import HTTPException
from socket import timeout

import adbutils
import urllib3

from insomniac import __version__
from insomniac.device_facade import DeviceFacade
from insomniac.globals import is_insomniac
from insomniac.navigation import LanguageChangedException, close_instagram_and_system_dialogs, \
    InstagramOpener
from insomniac.sleeper import sleeper
from insomniac.utils import *


class RestartJobRequiredException(Exception):
    pass


def run_safely(device_wrapper):
    def actual_decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (IndexError, OSError, RuntimeError,
                    HTTPException, urllib3.exceptions.HTTPError,
                    DeviceFacade.JsonRpcError, adbutils.errors.AdbError) as ex:
                print(COLOR_FAIL + describe_exception(ex, with_stacktrace=__version__.__debug_mode__ or not is_insomniac()) + COLOR_ENDC)
                # Check that adb works fine
                check_adb_connection(device_wrapper.device_id, wait_for_device=True)
                # Try to save the crash
                save_crash(device_wrapper.get(), ex)
                print("No idea what it was. Let's try again.")
                # Hack for the case when IGTV was accidentally opened
                close_instagram_and_system_dialogs(device_wrapper.get())
                InstagramOpener.INSTANCE.open_instagram()
            except LanguageChangedException:
                print_timeless("")
                print("Language was changed. We'll have to start from the beginning.")
            except RestartJobRequiredException:
                print_timeless("")
                print("Restarting job...")
        return wrapper
    return actual_decorator


def run_registration_safely(device_wrapper):
    from insomniac.extra_features.actions_impl import airplane_mode_on_off
    from insomniac.extra_features.utils import new_identity

    def actual_decorator(func):
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except (DeviceFacade.JsonRpcError, IndexError, HTTPException, timeout) as ex:
                print(COLOR_FAIL + describe_exception(ex) + COLOR_ENDC)
                save_crash(device_wrapper.get(), ex)
                print("No idea what it was. Let's try again.")

                # For the registration flow we create new identity and turn airplane mode on-and-off before each
                # Instagram app restart
                new_identity(device_wrapper.device_id, device_wrapper.app_id)
                sleeper.random_sleep(multiplier=2.0)
                close_instagram_and_system_dialogs(device_wrapper.get())
                airplane_mode_on_off(device_wrapper)
                InstagramOpener.INSTANCE.open_instagram()
                sleeper.random_sleep()
        return wrapper
    return actual_decorator
