from enum import Enum, unique

from src.utils import *


def navigate(device, tab):
    tab_name = tab.name.lower()
    tab_index = tab.value

    print("Press " + tab_name)
    tab_bar = device(resourceId='com.instagram.android:id/tab_bar', className='android.widget.LinearLayout')
    if not tab_bar.exists:
        _navigate_alternative(device, tab)
        return
    button = tab_bar.child(index=tab_index)

    # Two clicks to reset tab content
    button.click.wait()
    button.click.wait()


def _navigate_alternative(device, tab):
    print("Standard way of navigation failed, trying another one...")
    if tab == Tabs.HOME:
        button = device(description='Home', className='android.widget.FrameLayout')
    elif tab == Tabs.SEARCH:
        button = device(description='Search and Explore', className='android.widget.FrameLayout')
    elif tab == Tabs.PLUS:
        button = device(description='Camera', className='android.widget.FrameLayout')
    elif tab == Tabs.LIKES:
        button = device(description='Activity', className='android.widget.FrameLayout')
    else:
        button = device(description='Profile', className='android.widget.FrameLayout')

    if not button.exists:
        tab_name = tab.name.lower()
        print(COLOR_FAIL + "Cannot find " + tab_name + " button. Switch to English please." + COLOR_ENDC)
        raise NavigationException("Cannot find " + tab_name + " button.")

    # Two clicks to reset tab content
    button.click.wait()
    button.click.wait()


@unique
class Tabs(Enum):
    HOME = 0
    SEARCH = 1
    PLUS = 2
    LIKES = 3
    PROFILE = 4


class NavigationException(Exception):
    pass
