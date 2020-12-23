from http.client import HTTPException
from socket import timeout

from insomniac.device_facade import DeviceFacade
from insomniac.navigation import navigate, Tabs, LanguageChangedException
from insomniac.sleeper import sleeper
from insomniac.utils import *


def run_safely(device_wrapper):
    def actual_decorator(func):
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except (DeviceFacade.JsonRpcError, IndexError, HTTPException, timeout) as ex:
                print(COLOR_FAIL + traceback.format_exc() + COLOR_ENDC)
                save_crash(device_wrapper.get(), ex)
                print("No idea what it was. Let's try again.")
                # Hack for the case when IGTV was accidentally opened
                close_instagram(device_wrapper.device_id, device_wrapper.app_id)
                sleeper.random_sleep()
                open_instagram(device_wrapper.device_id, device_wrapper.app_id)
                sleeper.random_sleep()
                navigate(device_wrapper.get(), Tabs.PROFILE)
            except LanguageChangedException:
                print_timeless("")
                print("Language was changed. We'll have to start from the beginning.")
                navigate(device_wrapper.get(), Tabs.PROFILE)
        return wrapper
    return actual_decorator
