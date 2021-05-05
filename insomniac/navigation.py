from insomniac.sleeper import sleeper
from insomniac.utils import *
from insomniac.views import TabBarView, ProfileView, TabBarTabs, LanguageNotEnglishException

SEARCH_CONTENT_DESC_REGEX = '[Ss]earch and [Ee]xplore'


def navigate(device, tab, switch_to_english_on_exception=True):
    try:
        TabBarView(device).navigate_to(tab)
    except LanguageNotEnglishException as e:
        if not switch_to_english_on_exception:
            raise e
        save_crash(device)
        switch_to_english(device)
        raise LanguageChangedException()


def search_for(device, username=None, hashtag=None, place=None, on_action=None):
    tab_bar_view = TabBarView(device)

    # There may be no TabBarView if Instagram was opened via a deeplink. Then we have to clear the backstack.
    is_message_printed = False
    while not tab_bar_view.is_visible():
        if not is_message_printed:
            print(COLOR_OKGREEN + "Clearing the back stack..." + COLOR_ENDC)
            is_message_printed = True
        tab_bar_view.press_back_arrow()
        sleeper.random_sleep()

    search_view = tab_bar_view.navigate_to_search()
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
    navigate(device, TabBarTabs.PROFILE, switch_to_english_on_exception=False)
    ProfileView(device) \
        .navigate_to_options() \
        .navigate_to_settings() \
        .switch_to_english()


class LanguageChangedException(Exception):
    pass
