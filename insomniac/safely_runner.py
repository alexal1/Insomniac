import sys
import traceback
from http.client import HTTPException
from socket import timeout

from insomniac.device_facade import DeviceFacade
from insomniac.navigation import navigate, Tabs, LanguageChangedException
from insomniac.report import print_full_report
from insomniac.utils import *


def run_safely(device_wrapper):
    def actual_decorator(func):
        def wrapper(*args, **kwargs):
            from insomniac.session import sessions
            session_state = sessions[-1]
            try:
                func(*args, **kwargs)
            except KeyboardInterrupt:
                close_instagram(device_wrapper.device_id)
                print_copyright()
                print_timeless(COLOR_REPORT + "-------- FINISH: " + str(datetime.now().time()) + " --------" +
                               COLOR_ENDC)
                print_full_report(sessions)
                sessions.persist(directory=session_state.my_username)
                sys.exit(0)
            except (DeviceFacade.JsonRpcError, IndexError, HTTPException, timeout):
                print(COLOR_FAIL + traceback.format_exc() + COLOR_ENDC)
                save_crash(device_wrapper.get())
                print("No idea what it was. Let's try again.")
                # Hack for the case when IGTV was accidentally opened
                close_instagram(device_wrapper.device_id)
                random_sleep()
                open_instagram(device_wrapper.device_id)
                navigate(device_wrapper.get(), Tabs.PROFILE)
            except LanguageChangedException:
                print_timeless("")
                print("Language was changed. We'll have to start from the beginning.")
                navigate(device_wrapper.get(), Tabs.PROFILE)
            except Exception as e:
                save_crash(device_wrapper.get())
                close_instagram(device_wrapper.device_id)
                print_full_report(sessions)
                sessions.persist(directory=session_state.my_username)
                raise e
        return wrapper
    return actual_decorator
