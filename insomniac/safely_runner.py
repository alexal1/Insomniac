from http.client import HTTPException
from socket import timeout

from insomniac.device_facade import DeviceFacade
from insomniac.navigation import navigate, LanguageChangedException
from insomniac.sleeper import sleeper
from insomniac.utils import *
from insomniac.views import TabBarTabs


class RestartJobRequiredException(Exception):
    pass


def run_safely(device_wrapper):
    def actual_decorator(func):
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except (DeviceFacade.JsonRpcError, IndexError, HTTPException, timeout) as ex:
                print(COLOR_FAIL + describe_exception(ex) + COLOR_ENDC)
                save_crash(device_wrapper.get(), ex)
                print("No idea what it was. Let's try again.")
                # Hack for the case when IGTV was accidentally opened
                close_instagram(device_wrapper.device_id, device_wrapper.app_id)
                sleeper.random_sleep()
                open_instagram(device_wrapper.device_id, device_wrapper.app_id)
                navigate(device_wrapper.get(), TabBarTabs.PROFILE)
            except LanguageChangedException:
                print_timeless("")
                print("Language was changed. We'll have to start from the beginning.")
                navigate(device_wrapper.get(), TabBarTabs.PROFILE)
            except RestartJobRequiredException:
                print_timeless("")
                print("Restarting job...")
                navigate(device_wrapper.get(), TabBarTabs.PROFILE)
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
                close_instagram(device_wrapper.device_id, device_wrapper.app_id)
                airplane_mode_on_off(device_wrapper.get())
                open_instagram(device_wrapper.device_id, device_wrapper.app_id)
                sleeper.random_sleep()
        return wrapper
    return actual_decorator
