from enum import Enum, unique

from insomniac.utils import *
from insomniac.views import TabBarView, ProfileView

SEARCH_CONTENT_DESC_REGEX = '[Ss]earch and [Ee]xplore'
SETTINGS_LIST_ID_REGEX = 'android:id/list|{0}:id/recycler_view'
SETTINGS_LIST_CLASS_NAME_REGEX = 'android.widget.ListView|androidx.recyclerview.widget.RecyclerView'


def navigate(device, tab):
    tab_name = tab.name.lower()
    tab_index = tab.value

    print("Press " + tab_name)
    if tab == Tabs.SEARCH:
        _navigate_to_search(device)
        return

    device.close_keyboard()
    tab_bar = device.find(resourceId=f'{device.app_id}:id/tab_bar', className='android.widget.LinearLayout')
    button = tab_bar.child(index=tab_index)

    # Two clicks to reset tab content
    button.click()
    button.click()


def search_for(device, username=None, hashtag=None, place=None, on_action=None):
    search_view = TabBarView(device).navigate_to_search()
    target_view = None

    if username is not None:
        target_view = search_view.navigate_to_username(username, on_action)

    if hashtag is not None:
        target_view = search_view.navigate_to_hashtag(hashtag)

    if place is not None:
        target_view = search_view.navigate_to_place(place)

    return target_view is not None


def switch_to_english(device):
    print(COLOR_OKGREEN + "Switching to English locale" + COLOR_ENDC)
    navigate(device, Tabs.PROFILE)
    ProfileView(device) \
        .navigate_to_options() \
        .navigate_to_settings() \
        .switch_to_english()


def _navigate_to_search(device):
    # Search tab is a special case, because on some accounts there is "Reels" tab instead. If so, we have to go to the
    # "Home" tab and press search in the action bar.

    device.close_keyboard()

    tab_bar = device.find(resourceId=f'{device.app_id}:id/tab_bar', className='android.widget.LinearLayout')
    search_in_tab_bar = tab_bar.child(descriptionMatches=SEARCH_CONTENT_DESC_REGEX)
    if search_in_tab_bar.exists():
        # Two clicks to reset tab content
        search_in_tab_bar.click()
        search_in_tab_bar.click()
        return

    print("Didn't find search in the tab bar...")
    navigate(device, Tabs.HOME)
    print("Press search in the action bar")
    action_bar = device.find(resourceId=f'{device.app_id}:id/action_bar', className='android.widget.LinearLayout')
    search_in_action_bar = action_bar.child(descriptionMatches=SEARCH_CONTENT_DESC_REGEX)
    if search_in_action_bar.exists():
        search_in_action_bar.click()
        return

    print(COLOR_FAIL + "Cannot find search tab neither in the tab bar, nor in the action bar. Maybe not English "
                       "language is set?" + COLOR_ENDC)
    save_crash(device)
    switch_to_english(device)
    raise LanguageChangedException()


class LanguageChangedException(Exception):
    pass


@unique
class Tabs(Enum):
    HOME = 0
    SEARCH = 1
    PLUS = 2
    LIKES = 3
    PROFILE = 4
