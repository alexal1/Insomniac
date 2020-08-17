from enum import Enum, unique

from src.utils import *


def navigate(device, tab):
    if not _do_navigate(device, tab):
        print("Trying to find profile button directly...")
        profile_button = device(resourceId='com.instagram.android:id/profile_tab',
                                className='android.widget.FrameLayout')
        if not profile_button.exists:
            print(COLOR_FAIL + "Cannot find profile button. No idea what to do, sorry..." + COLOR_ENDC)
            raise NavigationException()

        # Two clicks to reset tab content
        profile_button.click.wait()
        profile_button.click.wait()

        if not tab == Tabs.PROFILE:
            _do_navigate(device, tab)


def _do_navigate(device, tab):
    tab_name = tab.name.lower()
    tab_index = tab.value

    print("Press " + tab_name)
    tab_bar = device(resourceId='com.instagram.android:id/tab_bar', className='android.widget.LinearLayout')
    if not tab_bar.exists:
        print("Cannot find tab bar.")
        return False
    button = tab_bar.child(index=tab_index)

    # Two clicks to reset tab content
    button.click.wait()
    button.click.wait()
    return True


@unique
class Tabs(Enum):
    HOME = 0
    SEARCH = 1
    PLUS = 2
    LIKES = 3
    PROFILE = 4


class NavigationException(Exception):
    pass
