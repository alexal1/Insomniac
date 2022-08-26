import datetime
from enum import Enum, unique

from PIL.Image import Image

from insomniac.actions_types import GetProfileAction
from insomniac.counters_parser import parse
from insomniac.device_facade import DeviceFacade
from insomniac.globals import do_location_permission_dialog_checks
from insomniac.hardban_indicator import hardban_indicator
from insomniac.scroll_end_detector import ScrollEndDetector
from insomniac.sleeper import sleeper
from insomniac.utils import *

TEXTVIEW_OR_BUTTON_REGEX = 'android.widget.TextView|android.widget.Button'
VIEW_OR_VIEWGROUP_REGEX = 'android.view.View|android.view.ViewGroup'
RECYCLERVIEW_OR_LISTVIEW_REGEX = 'androidx.recyclerview.widget.RecyclerView|android.widget.ListView'


def case_insensitive_re(str_list):
    if isinstance(str_list, str):
        strings = str_list
    else:
        strings = "|".join(str_list)
    re_str = f"(?i)({strings})"
    return re_str


class TabBarTabs(Enum):
    HOME = 0
    SEARCH = 1
    REELS = 2
    ORDERS = 3
    ACTIVITY = 4
    PROFILE = 5


class SearchTabs(Enum):
    TOP = 0
    ACCOUNTS = 1
    TAGS = 2
    PLACES = 3


class ProfileTabs(Enum):
    POSTS = 0
    IGTV = 1
    REELS = 2
    EFFECTS = 3
    PHOTOS_OF_YOU = 4


class InstagramView:
    ACTION_BAR_TITLE_ID = "{0}:id/action_bar_title"
    USERNAME_ALLOWED_SYMBOLS_REGEX = re.compile(r'[a-z0-9._-]+')

    def __init__(self, device: DeviceFacade):
        self.device = device

    def is_visible(self) -> bool:
        raise NotImplemented(f"is_visible() is not implemented for {self.__class__.__name__}")

    def wait_until_visible(self, max_wait_seconds=5) -> bool:
        start_time = datetime.now()
        current_time = start_time
        while current_time - start_time < timedelta(seconds=max_wait_seconds):
            if self.is_visible():
                return True
            current_time = datetime.now()
        return False

    def get_title(self) -> Optional[str]:
        action_bar_title = self.device.find(resourceId=f'{self.device.app_id}:id/action_bar_title',
                                            className='android.widget.TextView')
        if action_bar_title.exists():
            return action_bar_title.get_text()
        else:
            return None

    def press_back_arrow(self) -> 'InstagramView':
        button_back = self.device.find(resourceId=f'{self.device.app_id}:id/action_bar_button_back',
                                       className='android.widget.ImageView')
        if button_back.exists():
            button_back.click()
        else:
            print(COLOR_FAIL + f"Cannot find back arrow in {self.__class__.__name__}, press hardware back" + COLOR_ENDC)
            if not self.device.back():
                raise RuntimeError("Unexpected app state: want to go back but can't")
        return self.on_back_pressed()

    def on_back_pressed(self) -> 'InstagramView':
        # Override this method to return a view after press_back_arrow()
        return self

    def format_username(self, raw_text):
        return ''.join(re.findall(self.USERNAME_ALLOWED_SYMBOLS_REGEX, raw_text))


class TabBarView(InstagramView):
    HOME_CONTENT_DESC = "Home"
    SEARCH_CONTENT_DESC = "[Ss]earch and [Ee]xplore"
    REELS_CONTENT_DESC = "Reels"
    ORDERS_CONTENT_DESC = "Orders"
    ACTIVITY_CONTENT_DESC = "Activity"
    PROFILE_CONTENT_DESC = "Profile"

    top = None

    def __init__(self, device: DeviceFacade):
        super().__init__(device)
        self.top = None

    def is_visible(self) -> bool:
        if self._get_tab_bar().exists(quick=True):
            return True
        self.device.close_keyboard()
        return self._get_tab_bar().exists()

    def _get_tab_bar(self):
        tab_bar = self.device.find(
            resourceIdMatches=case_insensitive_re(f"{self.device.app_id}:id/tab_bar"),
            className="android.widget.LinearLayout",
        )
        return tab_bar

    def get_top(self):
        top = self._get_top()
        if top is not None:
            return top
        self.device.close_keyboard()
        return self._get_top()

    def navigate_to_home(self):
        self.navigate_to(TabBarTabs.HOME)
        return HomeView(self.device)

    def navigate_to_search(self):
        self.navigate_to(TabBarTabs.SEARCH)
        return SearchView(self.device)

    def navigate_to_reels(self):
        self.navigate_to(TabBarTabs.REELS)

    def navigate_to_orders(self):
        self.navigate_to(TabBarTabs.ORDERS)

    def navigate_to_activity(self):
        self.navigate_to(TabBarTabs.ACTIVITY)

    def navigate_to_profile(self):
        self.navigate_to(TabBarTabs.PROFILE)
        return ProfileView(self.device, is_own_profile=True)

    def navigate_to(self, tab: TabBarTabs):
        tab_name = tab.name
        print_debug(f"Navigate to {tab_name}")
        button = None
        tab_bar_view = self._get_tab_bar()

        if not self.is_visible():
            # There may be no TabBarView if Instagram was opened via a deeplink. Then we have to clear the backstack.
            is_backstack_cleared = self._clear_backstack()
            if not is_backstack_cleared:
                raise RuntimeError("Unexpected app state: cannot clear back stack")

        if tab == TabBarTabs.HOME:
            button = tab_bar_view.child(
                descriptionMatches=case_insensitive_re(TabBarView.HOME_CONTENT_DESC)
            )
        elif tab == TabBarTabs.SEARCH:
            button = tab_bar_view.child(
                descriptionMatches=case_insensitive_re(TabBarView.SEARCH_CONTENT_DESC)
            )
            if not button.exists():
                # Some accounts display the search btn only in Home -> action bar
                print_debug("Didn't find search in the tab bar...")
                home_view = self.navigate_to_home()
                home_view.navigate_to_search()
                return
        elif tab == TabBarTabs.REELS:
            button = tab_bar_view.child(
                descriptionMatches=case_insensitive_re(TabBarView.REELS_CONTENT_DESC)
            )
        elif tab == TabBarTabs.ORDERS:
            button = tab_bar_view.child(
                descriptionMatches=case_insensitive_re(TabBarView.ORDERS_CONTENT_DESC)
            )
        elif tab == TabBarTabs.ACTIVITY:
            button = tab_bar_view.child(
                descriptionMatches=case_insensitive_re(TabBarView.ACTIVITY_CONTENT_DESC)
            )
        elif tab == TabBarTabs.PROFILE:
            button = tab_bar_view.child(
                descriptionMatches=case_insensitive_re(TabBarView.PROFILE_CONTENT_DESC)
            )

        timer = Timer(seconds=20)
        while not timer.is_expired():
            if button.exists():
                # Two clicks to reset tab content
                button.click()
                button.click()
                if self._is_correct_tab_opened(tab):
                    return
                else:
                    print(COLOR_OKGREEN + f"{tab_name} tab is not opened, will try again." + COLOR_ENDC)
                    sleeper.random_sleep()
            else:
                seconds_left = timer.get_seconds_left()
                if seconds_left > 0:
                    print(COLOR_OKGREEN + f"Opening {tab_name}, {seconds_left} seconds left..." + COLOR_ENDC)
                    # Maybe we are banned?
                    hardban_indicator.detect_webview(self.device)

        print(COLOR_FAIL + f"Didn't find tab {tab_name} in the tab bar... "
                           f"Maybe English language is not set!?" + COLOR_ENDC)

        raise LanguageNotEnglishException()

    def _clear_backstack(self):
        attempt = 0
        max_attempts = 10
        is_message_printed = False
        while not self.is_visible():
            if not is_message_printed:
                print(COLOR_OKGREEN + "Clearing the back stack..." + COLOR_ENDC)
                is_message_printed = True
            if attempt > 0 and attempt % 2 == 0:
                hardban_indicator.detect_webview(self.device)
            if attempt >= max_attempts:
                return False
            self.press_back_arrow()
            # On fresh apps there may be a location request window after a backpress
            DialogView(self.device).close_location_access_dialog_if_visible()
            attempt += 1
        return True

    def _is_correct_tab_opened(self, tab: TabBarTabs) -> bool:
        if tab == TabBarTabs.HOME:
            return HomeView(self.device).is_visible()
        elif tab == TabBarTabs.SEARCH:
            return SearchView(self.device).is_visible()
        elif tab == TabBarTabs.PROFILE:
            return ProfileView(self.device, is_own_profile=True).is_visible()
        else:
            # We can support more tabs' checks here
            return True

    def _get_top(self):
        if self.top is None:
            try:
                self.top = self._get_tab_bar().get_bounds()["top"]
            except DeviceFacade.JsonRpcError:
                return None
        return self.top


class ActionBarView(InstagramView):
    INSTANCE = None

    action_bar = None
    top = None
    bottom = None
    tab_bar_top = None

    # DON'T USE INIT IN THIS CLASS!
    # ActionBarView is instantiated once and saved to the INSTANCE variable.
    # Use just ActionBarView.INSTANCE for better performance.
    def __init__(self, device: DeviceFacade):
        super().__init__(device)
        self.action_bar = self._get_action_bar()
        self.get_top()
        self.get_bottom()
        self.get_tab_bar_top()

    def get_top(self):
        if self.top is None:
            try:
                self.top = self._get_action_bar().get_bounds()["top"]
            except DeviceFacade.JsonRpcError:
                return None
        return self.top

    def get_bottom(self):
        if self.bottom is None:
            try:
                self.bottom = self._get_action_bar().get_bounds()["bottom"]
            except DeviceFacade.JsonRpcError:
                return None
        return self.bottom

    def get_height(self):
        if self.get_top() is not None and self.get_bottom() is not None:
            return self.get_bottom() - self.get_top()
        else:
            return None

    def get_tab_bar_top(self):
        if self.tab_bar_top is None:
            self.tab_bar_top = TabBarView(self.device).get_top()
        return self.tab_bar_top

    def get_child(self, *args, **kwargs):
        return self.action_bar.child(*args, **kwargs)

    def _get_action_bar(self):
        tab_bar = self.device.find(
            resourceIdMatches=case_insensitive_re(f"{self.device.app_id}:id/action_bar_container"),
            className="android.widget.FrameLayout")
        return tab_bar

    @staticmethod
    def is_in_interaction_rect(view):
        if ActionBarView.INSTANCE.get_bottom() is None or ActionBarView.INSTANCE.get_tab_bar_top() is None:
            print(COLOR_FAIL + "Interaction rect is not specified." + COLOR_ENDC)
            return True

        view_top = view.get_bounds()['top']
        view_bottom = view.get_bounds()['bottom']
        return ActionBarView.INSTANCE.get_bottom() <= view_top and view_bottom <= ActionBarView.INSTANCE.get_tab_bar_top()

    @staticmethod
    def create_instance(device):
        ActionBarView.INSTANCE = ActionBarView(device)
        return ActionBarView.INSTANCE


class HomeView(InstagramView):
    LOGO_ID_REGEX = '{0}:id/(action_bar_textview_custom_title_container|action_bar_textview_title_container)'
    LOGO_CLASS_NAME = 'android.widget.FrameLayout'

    def is_visible(self) -> bool:
        return self.device.find(resourceIdMatches=self.LOGO_ID_REGEX.format(self.device.app_id),
                                className=self.LOGO_CLASS_NAME).exists()

    def navigate_to_search(self):
        print_debug("Navigate to Search")
        search_btn = ActionBarView.INSTANCE.get_child(
            descriptionMatches=case_insensitive_re(TabBarView.SEARCH_CONTENT_DESC)
        )
        search_btn.click()

        return SearchView(self.device)


class HashTagView(InstagramView):
    def _get_recycler_view(self):
        CLASSNAME = "(androidx.recyclerview.widget.RecyclerView|android.view.View)"

        return self.device.find(classNameMatches=CLASSNAME)

    def _get_first_image_view(self, recycler):
        return recycler.child(
            className="android.widget.ImageView",
            resourceIdMatches=f"{self.device.app_id}:id/image_button",
        )

    def _get_recent_tab(self):
        return self.device.find(
            className="android.widget.TextView",
            text="Recent",
        )


class PlacesView(InstagramView):
    def _get_recycler_view(self):
        CLASSNAME = "(androidx.recyclerview.widget.RecyclerView|android.view.View)"

        return self.device.find(classNameMatches=CLASSNAME)

    def _get_first_image_view(self, recycler):
        return recycler.child(
            className="android.widget.ImageView",
            resourceIdMatches=f"{self.device.app_id}:id/image_button",
        )

    def _get_recent_tab(self):
        return self.device.find(
            className="android.widget.TextView",
            text="Recent",
        )


class SearchView(InstagramView):
    SEARCH_TEXT_ID = '{0}:id/echo_text'
    SEARCH_TEXT_CLASSNAME = 'android.widget.TextView'

    def is_visible(self) -> bool:
        return self._get_search_edit_text().exists()

    def refresh(self):
        posts_grid = self.device.find(resourceId=PostsGridView.POSTS_GRID_RESOURCE_ID.format(self.device.app_id),
                                      classNameMatches=PostsGridView.POSTS_GRID_CLASS_NAME)
        if posts_grid.exists():
            posts_grid.scroll(DeviceFacade.Direction.TOP)

    def _get_search_edit_text(self):
        search_edit_text = self.device.find(resourceId=f"{self.device.app_id}:id/action_bar_search_edit_text",
                                            className="android.widget.EditText")
        if not search_edit_text.exists(quick=True):
            print(COLOR_OKGREEN + "Cannot find search bar. Will try to refresh the page." + COLOR_ENDC)
            self.refresh()
        return search_edit_text

    def _get_username_row(self, username):
        return self.device.find(
            resourceIdMatches=case_insensitive_re(
                f"{self.device.app_id}:id/row_search_user_username"
            ),
            className="android.widget.TextView",
            text=username,
        )

    def _get_hashtag_row(self, hashtag):
        return self.device.find(
            resourceIdMatches=case_insensitive_re(
                f"{self.device.app_id}:id/row_hashtag_textview_tag_name"
            ),
            className="android.widget.TextView",
            text=f"#{hashtag}",
        )

    def _get_place_row(self, place):
        if place is None:
            return self.device.find(
                resourceIdMatches=case_insensitive_re(
                    f"{self.device.app_id}:id/row_place_title"
                ),
                className="android.widget.TextView"
            )
        else:
            return self.device.find(
                resourceIdMatches=case_insensitive_re(
                    f"{self.device.app_id}:id/row_place_title"
                ),
                className="android.widget.TextView",
                textMatches = case_insensitive_re(place)
            )

    def _open_tab(self, tab: SearchTabs) -> bool:
        tab_layout = self.device.find(resourceId=f"{self.device.app_id}:id/fixed_tabbar_tabs_container",
                                      className="android.widget.LinearLayout")
        tab_text_view = tab_layout.child(resourceId=f"{self.device.app_id}:id/tab_button_name_text",
                                         className="android.widget.TextView",
                                         textMatches=case_insensitive_re(tab.name))
        if tab_text_view.exists(quick=True):
            tab_text_view.click()
            return True

        print_debug(f"Cannot find tab with text {tab.name}. Fallback to opening by swiping.")

        def check_hint_contains_tab_name() -> bool:
            return self.device\
                .find(resourceId=f"{self.device.app_id}:id/action_bar_search_hints_text_layout",
                      className="android.widget.FrameLayout") \
                .child(className="android.widget.TextView",
                       textMatches=case_insensitive_re(f".*?{tab.name}.*?")) \
                .exists(quick=True)

        max_attempts = 10
        attempt = 0
        while not check_hint_contains_tab_name():
            self.device.swipe(DeviceFacade.Direction.LEFT, scale=0.9)
            attempt += 1
            if attempt >= max_attempts:
                print(COLOR_FAIL + f"Cannot find tab: {tab.name}." + COLOR_ENDC)
                save_crash(self.device)
                return False

        return True

    def find_username(self, username) -> bool:
        search_edit_text = self._get_search_edit_text()
        search_edit_text.click()
        self._handle_permission_request()

        username_view_recent = self._get_username_row(username)
        if username_view_recent.exists(quick=True):
            return True
        print(f"@{username} is not in recent searching history...")

        if not self._open_tab(SearchTabs.ACCOUNTS):
            return False

        search_edit_text.set_text(username)
        search_text = self.device.find(resourceId=self.SEARCH_TEXT_ID.format(self.device.app_id),
                                       className=self.SEARCH_TEXT_CLASSNAME)
        search_text.click(ignore_if_missing=True)

        username_view = self._get_username_row(username)
        return username_view.exists()

    def navigate_to_username(self, username, on_action):
        print_debug(f"Navigate to profile @{username}")

        search_edit_text = self._get_search_edit_text()
        search_edit_text.click()
        self._handle_permission_request()

        # Check if username already exists in the recent search list -> act as human
        username_view_recent = self._get_username_row(username)
        if username_view_recent.exists(quick=True):
            username_view_recent.click()
            on_action(GetProfileAction(user=username))
            return ProfileView(self.device, is_own_profile=False)
        print(f"@{username} is not in recent searching history...")

        if not self._open_tab(SearchTabs.ACCOUNTS):
            return None

        search_edit_text.set_text(username)
        search_text = self.device.find(resourceId=self.SEARCH_TEXT_ID.format(self.device.app_id),
                                       className=self.SEARCH_TEXT_CLASSNAME)
        search_text.click(ignore_if_missing=True)

        username_view = self._get_username_row(username)
        if not username_view.exists():
            print(COLOR_FAIL + f"Cannot find profile @{username}, abort." + COLOR_ENDC)
            save_crash(self.device)
            return None

        username_view.click()
        on_action(GetProfileAction(user=username))

        return ProfileView(self.device, is_own_profile=False)

    def navigate_to_hashtag(self, hashtag):
        print_debug(f"Navigate to hashtag #{hashtag}")

        search_edit_text = self._get_search_edit_text()
        search_edit_text.click()
        self._handle_permission_request()

        # Check if hashtag already exists in the recent search list -> act as human
        hashtag_view_recent = self._get_hashtag_row(hashtag)
        if hashtag_view_recent.exists(quick=True):
            hashtag_view_recent.click()
            sleeper.random_sleep()
            return HashTagView(self.device)
        print(f"#{hashtag} is not in recent searching history...")

        if not self._open_tab(SearchTabs.TAGS):
            return None

        search_edit_text.set_text(hashtag)
        search_text = self.device.find(resourceId=self.SEARCH_TEXT_ID.format(self.device.app_id),
                                       className=self.SEARCH_TEXT_CLASSNAME)
        search_text.click(ignore_if_missing=True)

        hashtag_view = self._get_hashtag_row(hashtag)
        if not hashtag_view.exists():
            print(COLOR_FAIL + f"Cannot find hashtag #{hashtag}, abort." + COLOR_ENDC)
            save_crash(self.device)
            return None

        hashtag_view.click()
        return HashTagView(self.device)

    def navigate_to_place(self, place):
        print_debug(f"Navigate to place {place}")

        search_edit_text = self._get_search_edit_text()
        search_edit_text.click()
        self._handle_permission_request()

        # Check if place already exists in the recent search list -> act as human
        place_view_recent = self._get_place_row(place)
        if place_view_recent.exists(quick=True):
            place_view_recent.click()
            sleeper.random_sleep()
            return PlacesView(self.device)
        print(f"{place} is not in recent searching history...")

        if not self._open_tab(SearchTabs.PLACES):
            return None

        search_edit_text.set_text(place)
        search_text = self.device.find(resourceId=self.SEARCH_TEXT_ID.format(self.device.app_id),
                                       className=self.SEARCH_TEXT_CLASSNAME)
        search_text.click(ignore_if_missing=True)

        place_view = self._get_place_row(None)  # just open first place we see
        if not place_view.exists():
            print(COLOR_FAIL + f"Cannot find place {place}, abort." + COLOR_ENDC)
            save_crash(self.device)
            return None

        place_view.click()
        return PlacesView(self.device)

    def _handle_permission_request(self):
        DialogView(self.device).close_location_access_dialog_if_visible()


class PostsViewList(InstagramView):
    LOAD_MORE_ROW_ID_REGEX = '{0}:id/row_load_more_button'
    RETRY_BUTTON_CLASS_NAME = 'android.widget.ImageView'

    def is_visible(self):
        # We suppose that at least one post must be visible
        return OpenedPostView(self.device).is_visible()

    def open_likers(self):
        likes_view = self.device.find(resourceId=f'{self.device.app_id}:id/row_feed_textview_likes',
                                      className='android.widget.TextView')
        if likes_view.exists(quick=True) and ActionBarView.is_in_interaction_rect(likes_view):
            print("Opening post likers")
            likes_view.click()
            return True
        else:
            return False

    def scroll_down(self):
        # Check if retry button is shown
        load_more_row = self.device.find(resourceId=self.LOAD_MORE_ROW_ID_REGEX.format(self.device.app_id))
        if load_more_row.exists(quick=True):
            print("Press \"Load\" button")
            retry_button = load_more_row.child(className=self.RETRY_BUTTON_CLASS_NAME)
            retry_button.click()
            sleeper.random_sleep()

        recycler_view = self.device.find(resourceId='android:id/list',
                                         className='androidx.recyclerview.widget.RecyclerView')
        recycler_view.scroll(DeviceFacade.Direction.BOTTOM)

    def get_current_post(self) -> 'OpenedPostView':
        display_width = self.device.get_info()["displayWidth"] / 2
        display_height = self.device.get_info()["displayHeight"] / 2
        action_bar_bottom = ActionBarView.INSTANCE.get_bottom()
        accuracy = ActionBarView.INSTANCE.get_height() / 2
        diff = display_height
        max_swipes = 10
        swipes = 0
        while abs(diff) > accuracy:
            if swipes >= max_swipes:
                break
            post_view_top = OpenedPostView(self.device).get_top()
            diff = action_bar_bottom - post_view_top
            self.device.swipe_points(
                display_width / 2,
                display_height / 2,
                display_width / 2,
                min(max(display_height / 2 + diff, 0), display_height),
            )
            swipes += 1
        return OpenedPostView(self.device)


class LikersListView(InstagramView):

    def is_visible(self):
        return self.get_title() == 'Likes'

    def on_back_pressed(self) -> 'InstagramView':
        return PostsViewList(self.device)


class LanguageView(InstagramView):
    def setLanguage(self, language: str):
        print_debug(f"Set language to {language}")
        search_edit_text = self.device.find(
            resourceId=f"{self.device.app_id}:id/search",
            className="android.widget.EditText",
        )
        search_edit_text.set_text(language)

        list_view = self.device.find(
            resourceId=f"{self.device.app_id}:id/language_locale_list",
            className="android.widget.ListView",
        )
        first_item = list_view.child(index=0)
        first_item.click()


class AccountView(InstagramView):
    LIST_ID_REGEX = '{0}:id/recycler_view|android:id/list'
    LIST_CLASSNAME_REGEX = RECYCLERVIEW_OR_LISTVIEW_REGEX

    def navigate_to_language(self):
        print_debug("Navigate to Language")
        button = self.device.find(
            textMatches=case_insensitive_re("Language"),
            resourceId=f"{self.device.app_id}:id/row_simple_text_textview",
            className="android.widget.TextView",
        )
        button.click()

        return LanguageView(self.device)

    def switch_to_business_account(self):
        recycler_view = self.device.find(resourceIdMatches=self.LIST_ID_REGEX.format(self.device.app_id),
                                         classNameMatches=self.LIST_CLASSNAME_REGEX)
        recycler_view.scroll(DeviceFacade.Direction.BOTTOM)

        switch_button = self.device.find(textMatches=case_insensitive_re("Switch to Professional Account"))
        switch_button.click()
        radio_button = self.device.find(className="android.widget.RadioButton")
        while not radio_button.exists(quick=True):
            continue_button = self.device.find(textMatches=case_insensitive_re("Continue"))
            continue_button.click()
        radio_button.click()
        sleeper.random_sleep(multiplier=2.0)
        done_button = self.device.find(textMatches=case_insensitive_re("Done"))
        done_button.click()
        sleeper.random_sleep(multiplier=2.0)

        DialogView(self.device).click_ok()

        business_account_item = self.device.find(textMatches=case_insensitive_re("Business"))
        business_account_item.click()

        next_or_skip_button = self.device.find(textMatches=case_insensitive_re("Next|Skip"))
        close_button = self.device.find(resourceId=f"{self.device.app_id}:id/action_bar_button_action",
                                        descriptionMatches=case_insensitive_re("Close"))
        while not close_button.exists(quick=True):
            next_or_skip_button.click()
        close_button.click()


class SettingsView(InstagramView):
    SETTINGS_LIST_ID_REGEX = 'android:id/list|{0}:id/recycler_view'
    SETTINGS_LIST_CLASS_NAME_REGEX = 'android.widget.ListView|androidx.recyclerview.widget.RecyclerView'
    LOG_OUT_TEXT = "Log Out"

    def switch_to_english(self):
        """
        We want to keep this method free of language-specific strings because it's used in language switching.
        """
        for account_item_index in range(6, 9):
            list_view = self.device.find(resourceIdMatches=self.SETTINGS_LIST_ID_REGEX.format(self.device.app_id),
                                         classNameMatches=self.SETTINGS_LIST_CLASS_NAME_REGEX)
            account_item = list_view.child(index=account_item_index, clickable=True)
            account_item.click()

            list_view = self.device.find(resourceIdMatches=self.SETTINGS_LIST_ID_REGEX.format(self.device.app_id),
                                         classNameMatches=self.SETTINGS_LIST_CLASS_NAME_REGEX)
            if not list_view.exists(quick=True):
                print("Opened a wrong tab, going back")
                self.device.back()
                continue
            language_item = list_view.child(index=4, clickable=True)
            if not language_item.exists(quick=True):
                print("Opened a wrong tab, going back")
                self.device.back()
                continue
            language_item.click()

            search_edit_text = self.device.find(resourceId=f'{self.device.app_id}:id/search',
                                                className='android.widget.EditText')
            if not search_edit_text.exists(quick=True):
                print("Opened a wrong tab, going back")
                self.device.back()
                self.device.back()
                continue
            search_edit_text.set_text("english")

            list_view = self.device.find(resourceId=f'{self.device.app_id}:id/language_locale_list',
                                         className='android.widget.ListView')
            english_item = list_view.child(index=0)
            if english_item.child(resourceId=f'{self.device.app_id}:id/language_checkmark',
                                  className='android.widget.ImageView').exists():
                # Raising exception to not get into a loop
                raise Exception("Tried to switch language to English, but English is already set!")
            english_item.click()

            break

    def log_out(self):
        settings_list = self.device.find(scrollable=True)
        settings_list.scroll(DeviceFacade.Direction.BOTTOM)

        # Click the last button (it's usually log out)
        log_out_button = None
        for log_out_button in settings_list.child(clickable=True):
            pass
        if log_out_button is not None:
            log_out_button.click(ignore_if_missing=True)

        # Confirm Log Out
        log_out_button = self.device.find(textMatches=case_insensitive_re(self.LOG_OUT_TEXT))
        negative_button = self.device.find(resourceId=f"{self.device.app_id}:id/negative_button",
                                           className="android.widget.Button")
        first_button = self.device.find(resourceId=f"{self.device.app_id}:id/first_button",
                                        className="android.widget.TextView")
        switched_language = False
        while not log_out_button.exists(quick=True):
            if negative_button.exists(quick=True):
                negative_button.click()
                continue
            if first_button.exists(quick=True):
                first_button.click()
                continue
            if not switched_language:
                self.device.back()
                print(COLOR_FAIL + "Cannot find Log Out button. Maybe not English language is set?" + COLOR_ENDC)
                print(COLOR_OKGREEN + "Switching to English locale" + COLOR_ENDC)
                TabBarView(self.device) \
                    .navigate_to_profile() \
                    .navigate_to_options() \
                    .navigate_to_settings() \
                    .switch_to_english()
                switched_language = True
                continue
            break
        log_out_button.click(ignore_if_missing=True)

    def navigate_to_account(self):
        print_debug("Navigate to Account")
        button = self.device.find(
            textMatches=case_insensitive_re("Account"),
            resourceId=f"{self.device.app_id}:id/row_simple_text_textview",
            className="android.widget.TextView",
        )
        button.click()
        return AccountView(self.device)


class OptionsView(InstagramView):

    def navigate_to_settings(self):
        """
        We want to keep this method free of language-specific strings because it's used in language switching.

        :return: SettingsView instance
        """
        print_debug("Navigate to Settings")
        settings_button = self.device.find(resourceId=f'{self.device.app_id}:id/menu_settings_row',
                                           classNameMatches=TEXTVIEW_OR_BUTTON_REGEX)
        if not settings_button.exists():
            # Just take the first item
            settings_button = self.device.find(resourceIdMatches=f'{self.device.app_id}:id/menu_option_text',
                                               classNameMatches=TEXTVIEW_OR_BUTTON_REGEX)
        settings_button.click()
        return SettingsView(self.device)


class OpenedPostView(InstagramView):
    POSTS_HEADER_HEIGHT = None

    POST_VIEW_ID_REGEX = '{0}:id/zoomable_view_container|{1}:id/carousel_image|{2}:id/layout_container_main'
    POST_VIEW_CLASSNAME = 'android.widget.FrameLayout'
    POST_HEADER_ID = '{0}:id/row_feed_profile_header'
    POST_HEADER_CLASSNAME = 'android.view.ViewGroup'
    BUTTON_LIKE_ID = '{0}:id/row_feed_button_like'
    BUTTON_LIKE_CLASSNAME = 'android.widget.ImageView'
    TEXT_AUTHOR_NAME_ID = '{0}:id/row_feed_photo_profile_name'
    TEXT_AUTHOR_NAME_CLASSNAME = 'android.widget.TextView'

    def __init__(self, device: DeviceFacade):
        super().__init__(device)
        if OpenedPostView.POSTS_HEADER_HEIGHT is None:
            post_header = self.device.find(
                resourceIdMatches=self.POST_HEADER_ID.format(self.device.app_id),
                className=self.POST_HEADER_CLASSNAME
            )
            if post_header.exists():
                bounds = post_header.get_bounds()
                OpenedPostView.POSTS_HEADER_HEIGHT = bounds["bottom"] - bounds["top"]

    def is_visible(self) -> bool:
        return self.device.find(
            resourceIdMatches=self.POST_VIEW_ID_REGEX.format(self.device.app_id,
                                                             self.device.app_id,
                                                             self.device.app_id),
            className=self.POST_VIEW_CLASSNAME
        ).exists(quick=True)

    def get_top(self):
        try:
            return self.device.find(
                resourceIdMatches=self.POST_HEADER_ID.format(self.device.app_id),
                className=self.POST_HEADER_CLASSNAME
            ).get_bounds()["top"]
        except DeviceFacade.JsonRpcError:
            # Sometimes we don't see any post header on the screen, so will take a post
            post_top = self.device.find(
                resourceIdMatches=self.POST_VIEW_ID_REGEX.format(self.device.app_id,
                                                                 self.device.app_id,
                                                                 self.device.app_id),
                className=self.POST_VIEW_CLASSNAME
            ).get_bounds()["top"]
            if OpenedPostView.POSTS_HEADER_HEIGHT is not None:
                post_top -= OpenedPostView.POSTS_HEADER_HEIGHT
            return post_top

    def get_author_name(self) -> Optional[str]:
        text_author_name = self.device.find(
            resourceId=self.TEXT_AUTHOR_NAME_ID.format(self.device.app_id),
            className=self.TEXT_AUTHOR_NAME_CLASSNAME
        )
        try:
            return self.format_username(text_author_name.get_text())
        except DeviceFacade.JsonRpcError:
            print(COLOR_FAIL + "Cannot read post author's name" + COLOR_ENDC)
            return None

    def like(self):
        print("Double click!")
        post_view = self.device.find(
            resourceIdMatches=OpenedPostView.POST_VIEW_ID_REGEX.format(self.device.app_id,
                                                                       self.device.app_id,
                                                                       self.device.app_id),
            className=OpenedPostView.POST_VIEW_CLASSNAME
        )
        post_view.double_click()
        if not self.is_visible():
            print(COLOR_OKGREEN + "Accidentally went out of the post page, going back..." + COLOR_ENDC)
            self.device.back()

        # If like button is not visible, scroll down
        like_button = self.device.find(resourceId=self.BUTTON_LIKE_ID.format(self.device.app_id),
                                       className=self.BUTTON_LIKE_CLASSNAME)
        if not like_button.exists(quick=True) or not ActionBarView.is_in_interaction_rect(like_button):
            print("Swiping down a bit to see if is liked")
            self.device.swipe(DeviceFacade.Direction.TOP)

        # If double click didn't work, set like by icon click
        try:
            # Click only button which is under the action bar and above the tab bar.
            # It fixes bugs with accidental back / home clicks.
            for like_button in self.device.find(resourceId=self.BUTTON_LIKE_ID.format(self.device.app_id),
                                                className=self.BUTTON_LIKE_CLASSNAME,
                                                selected=False):
                if ActionBarView.is_in_interaction_rect(like_button):
                    print("Double click didn't work, click on icon.")
                    like_button.click()
                    sleeper.random_sleep()
                    break
        except DeviceFacade.JsonRpcError:
            print("Double click worked successfully.")


class PostsGridView(InstagramView):

    POSTS_GRID_RESOURCE_ID = '{0}:id/recycler_view'
    POSTS_GRID_CLASS_NAME = 'androidx.recyclerview.widget.RecyclerView|android.view.View'
    POST_CLASS_NAME_REGEX = 'android.widget.ImageView|android.widget.Button'

    def open_random_post(self) -> Optional['PostsViewList']:
        # Scroll down several times to pick random post
        scroll_times = randint(0, 5)
        posts_grid = self.device.find(resourceId=self.POSTS_GRID_RESOURCE_ID.format(self.device.app_id),
                                      classNameMatches=self.POSTS_GRID_CLASS_NAME)
        print(f"Scroll down {scroll_times} times.")
        for _ in range(0, scroll_times):
            posts_grid.scroll(DeviceFacade.Direction.BOTTOM)
            sleeper.random_sleep()

        # Scan for available posts' coordinates
        available_posts_coords = []
        print("Choosing a random post from those on the screen")
        for post_view in posts_grid.child(resourceId=f'{self.device.app_id}:id/image_button',
                                          classNameMatches=self.POST_CLASS_NAME_REGEX):
            if not ActionBarView.is_in_interaction_rect(post_view):
                continue
            bounds = post_view.get_bounds()
            left = bounds["left"]
            top = bounds["top"]
            right = bounds["right"]
            bottom = bounds["bottom"]
            coords = (left + (right - left) / 2, top + (bottom - top) / 2)
            available_posts_coords.append(coords)
        if len(available_posts_coords) == 0:
            print(COLOR_FAIL + f"No posts here. Abort." + COLOR_ENDC)
            return None

        # Pick random post from available ones
        coords = random.choice(available_posts_coords)
        print(f"Open the post at {coords}")
        self.device.screen_click_by_coordinates(coords[0], coords[1])
        sleeper.random_sleep()
        posts_view_list = PostsViewList(self.device)

        if posts_view_list.is_visible():
            return posts_view_list
        else:
            print("Couldn't open a post, will try again.")
            self.device.screen_click_by_coordinates(coords[0], coords[1])
            sleeper.random_sleep()

        if posts_view_list.is_visible():
            return posts_view_list
        else:
            print(COLOR_FAIL + "Couldn' open a post twice. Abort." + COLOR_ENDC)
            return None


class ProfileView(InstagramView):

    FOLLOWERS_BUTTON_ID_REGEX = '{0}:id/row_profile_header_followers_container|{1}:id/row_profile_header_container_followers'
    FOLLOWING_BUTTON_ID_REGEX = '{0}:id/row_profile_header_following_container|{1}:id/row_profile_header_container_following'
    PROFILE_IMAGE_ID_REGEX = '{0}:id/row_profile_header_imageview'
    PROFILE_IMAGE_CLASS_NAME = 'android.widget.ImageView'
    MESSAGE_BUTTON_CLASS_NAME_REGEX = TEXTVIEW_OR_BUTTON_REGEX

    def __init__(self, device: DeviceFacade, is_own_profile=False):
        super().__init__(device)
        self.is_own_profile = is_own_profile

    def is_visible(self):
        return self.device.find(resourceId=self.PROFILE_IMAGE_ID_REGEX.format(self.device.app_id),
                                className=self.PROFILE_IMAGE_CLASS_NAME).exists(quick=True)

    def refresh(self):
        re_case_insensitive = case_insensitive_re(
            [
                f"{self.device.app_id}:id/coordinator_root_layout",
            ]
        )
        coordinator_layout = self.device.find(resourceIdMatches=re_case_insensitive)
        if coordinator_layout.exists():
            coordinator_layout.scroll(DeviceFacade.Direction.TOP)

    def navigate_to_options(self):
        """
        We want to keep this method free of language-specific strings because it's used in language switching.

        :return: OptionsView instance
        """
        print_debug("Navigate to Options")
        # We wanna pick last view in the action bar
        options_view = None
        for options_view in ActionBarView.INSTANCE.get_child(clickable=True):
            pass
        if options_view is None or not options_view.exists():
            print(COLOR_FAIL + "No idea how to open menu..." + COLOR_ENDC)
            return None
        options_view.click()
        return OptionsView(self.device)

    def navigate_to_actions(self) -> 'ProfileActionsView':
        """
        Only for other users' profiles!

        :return: ProfileActionsView instance
        """
        action_bar_icon = self.device.find(resourceId=f'{self.device.app_id}:id/action_bar_overflow_icon',
                                           className='android.widget.ImageView')
        action_bar_icon.click()
        return ProfileActionsView(self.device)

    def change_to_username(self, username):
        action_bar = self._get_action_bar_title_btn()

        def is_username_profile_opened():
            return action_bar.get_text().strip().upper() == username.upper()

        if is_username_profile_opened():
            print(COLOR_OKBLUE + f"You are already logged as {username}!" + COLOR_ENDC)
            return True

        action_bar.click()
        sleeper.random_sleep()
        found_obj = self.device.find(
            resourceId=f"{self.device.app_id}:id/row_user_textview",
            textMatches=case_insensitive_re(username),
        )
        if found_obj.exists():
            print(f"Switching to {username}...")
            found_obj.click()
            sleeper.random_sleep()
            if is_username_profile_opened():
                return True
        return False

    def _get_action_bar_title_btn(self):
        re_case_insensitive = case_insensitive_re(
            [
                f"{self.device.app_id}:id/title_view",
                f"{self.device.app_id}:id/action_bar_title",
                f"{self.device.app_id}:id/action_bar_large_title",
                f"{self.device.app_id}:id/action_bar_textview_title",
                f"{self.device.app_id}:id/action_bar_large_title_auto_size"
            ]
        )
        return ActionBarView.INSTANCE.get_child(
            resourceIdMatches=re_case_insensitive, className="android.widget.TextView"
        )

    def get_username(self):
        title_view = self._get_action_bar_title_btn()
        if title_view.exists():
            username = self.format_username(title_view.get_text())
            if len(username) > 0:
                return username
            else:
                print(COLOR_FAIL + f"Cannot parse username" + COLOR_ENDC)
                return None

        print(COLOR_FAIL + "Cannot get username" + COLOR_ENDC)
        return None

    def get_followers_count(self, swipe_up_if_needed=False) -> Optional[int]:
        followers_text_view = self.device.find(
            resourceId=f'{self.device.app_id}:id/row_profile_header_textview_followers_count',
            className='android.widget.TextView'
        )

        def get_count():
            followers_text = followers_text_view.get_text()
            if followers_text:
                try:
                    return parse(followers_text)
                except ValueError:
                    print(COLOR_FAIL + f"Cannot parse \"{followers_text}\". "
                                       f"Maybe not English language is set?" + COLOR_ENDC)
                    raise LanguageNotEnglishException()
            else:
                print_timeless(COLOR_FAIL + "Cannot get followers count text" + COLOR_ENDC)
                return None

        if followers_text_view.exists():
            return get_count()
        else:
            if swipe_up_if_needed:
                print("Cannot find followers count text, maybe its a little bit upper.")
                print("Swiping up a bit.")
                self.device.swipe(DeviceFacade.Direction.BOTTOM)

                if followers_text_view.exists():
                    return get_count()
            print_timeless(COLOR_FAIL + "Cannot find followers count view" + COLOR_ENDC)
        return None

    def get_following_count(self, swipe_up_if_needed=False) -> Optional[int]:
        followings_text_view = self.device.find(
            resourceId=f'{self.device.app_id}:id/row_profile_header_textview_following_count',
            className='android.widget.TextView'
        )

        def get_count():
            followings_text = followings_text_view.get_text()
            if followings_text:
                try:
                    return parse(followings_text)
                except ValueError:
                    print(COLOR_FAIL + f"Cannot parse \"{followings_text}\". "
                                       f"Maybe not English language is set?" + COLOR_ENDC)
                    raise LanguageNotEnglishException()
            else:
                print_timeless(COLOR_FAIL + "Cannot get followings count text" + COLOR_ENDC)
                return None

        if followings_text_view.exists():
            return get_count()
        else:
            if swipe_up_if_needed:
                print("Cannot find following count text, maybe its a little bit upper.")
                print("Swiping up a bit.")
                self.device.swipe(DeviceFacade.Direction.BOTTOM)

                if followings_text_view.exists():
                    return get_count()
            print_timeless(COLOR_FAIL + "Cannot find followings count view" + COLOR_ENDC)
        return None

    def get_posts_count(self) -> Optional[int]:
        posts_count_text_view = self.device.find(
            resourceId=f'{self.device.app_id}:id/row_profile_header_textview_post_count',
            className='android.widget.TextView'
        )

        if posts_count_text_view.exists():
            posts_count_text = posts_count_text_view.get_text()
            if posts_count_text:
                try:
                    return parse(posts_count_text)
                except ValueError:
                    print(COLOR_FAIL + f"Cannot parse \"{posts_count_text}\". "
                                       f"Maybe not English language is set?" + COLOR_ENDC)
                    raise LanguageNotEnglishException()
            else:
                print_timeless(COLOR_FAIL + "Cannot get posts count text" + COLOR_ENDC)
                return None
        else:
            print_timeless(COLOR_FAIL + "Cannot find posts count view" + COLOR_ENDC)
        return None

    def get_profile_info(self, swipe_up_if_needed=False):
        username, followers, following = self._get_profile_info(swipe_up_if_needed)
        if (username is None or followers is None or following is None) and not self.is_visible():
            print(COLOR_FAIL + "Oops, wrong tab was opened accidentally. Let's try again." + COLOR_ENDC)
            TabBarView(self.device).navigate_to_profile()
            username, followers, following = self._get_profile_info(swipe_up_if_needed)
        return username, followers, following

    def _get_profile_info(self, swipe_up_if_needed):
        username = self.get_username()
        followers = self.get_followers_count(swipe_up_if_needed=swipe_up_if_needed) or 0
        following = self.get_following_count(swipe_up_if_needed=swipe_up_if_needed) or 0

        return username, followers, following

    def get_profile_biography(self):
        try:
            biography = self.device.find(
                resourceIdMatches=f"{self.device.app_id}:id/profile_header_bio_text",
                className="android.widget.TextView",
            )
            if biography.exists():
                biography_text = biography.get_text()
                # If the biography is very long, blabla text and end with "...more"
                # click the bottom of the text and get the new text
                is_long_bio = re.compile(
                    r"{0}$".format("… more"), flags=re.IGNORECASE
                ).search(biography_text)
                if is_long_bio is not None:
                    print('Found "… more" in bio - trying to expand')
                    # Clicking the biography is dangerous. Clicking "right" is safest so we can try to avoid hashtags
                    biography.click()
                    # If we do click a hashtag (VERY possible) - let's back out
                    # a short bio is better than no bio
                    try:
                        return biography.get_text()
                    except DeviceFacade.JsonRpcError:
                        print("Can't find biography - did we click a hashtag or link? going back.")
                        print("Failed to expand biography - checking short view.")
                        self.device.back()
                        return biography.get_text()
                return biography_text
        except DeviceFacade.JsonRpcError:
            print_timeless(COLOR_FAIL + "Cannot find biography" + COLOR_ENDC)
        return ""

    def get_full_name(self):
        fullname = ""
        try:
            full_name_view = self.device.find(
                resourceIdMatches=f"{self.device.app_id}:id/profile_header_full_name",
                className="android.widget.TextView",
            )
            if full_name_view.exists():
                fullname_text = full_name_view.get_text()
                if fullname_text is not None:
                    return fullname_text
            return ""
        except DeviceFacade.JsonRpcError:
            print_timeless(COLOR_FAIL + "Cannot find full name" + COLOR_ENDC)
        return fullname

    def has_business_category(self):
        if self.is_own_profile:
            insights_button = self.device.find(
                resourceId=f'{self.device.app_id}:id/button_text',
                classNameMatches=TEXTVIEW_OR_BUTTON_REGEX,
                textMatches=case_insensitive_re("Insights")
            )
            return insights_button.exists()
        else:
            business_category_view = self.device.find(
                resourceId=f'{self.device.app_id}:id/profile_header_business_category',
                className='android.widget.TextView'
            )
            return business_category_view.exists()

    def is_private_account(self):
        private_profile_view = self.device.find(
            resourceIdMatches=case_insensitive_re(
                [
                    f"{self.device.app_id}:id/private_profile_empty_state",
                    f"{self.device.app_id}:id/row_profile_header_empty_profile_notice_title",
                ]
            )
        )
        return private_profile_view.exists(quick=True)

    def is_story_available(self):
        return self.device.find(
            resourceId=f"{self.device.app_id}:id/reel_ring",
            className="android.view.View",
        ).exists(quick=True)

    def navigate_to_followers(self):
        print_debug("Navigate to Followers")
        followers_button = self.device.find(resourceIdMatches=self.FOLLOWERS_BUTTON_ID_REGEX.format(self.device.app_id, self.device.app_id))
        followers_button.click()
        followers_following_list_view = FollowersFollowingListView(self.device)
        followers_following_list_view.switch_to_tab(FollowersFollowingListView.Tab.FOLLOWERS)
        return followers_following_list_view

    def navigate_to_following(self):
        print_debug("Navigate to Followers")
        following_button = self.device.find(resourceIdMatches=self.FOLLOWING_BUTTON_ID_REGEX.format(self.device.app_id, self.device.app_id))
        following_button.click()
        followers_following_list_view = FollowersFollowingListView(self.device)
        followers_following_list_view.switch_to_tab(FollowersFollowingListView.Tab.FOLLOWING)
        return followers_following_list_view

    def open_messages(self):
        message_button = self.device.find(
            classNameMatches=self.MESSAGE_BUTTON_CLASS_NAME_REGEX,
            textMatches=case_insensitive_re('Message')
        )
        if message_button.exists(quick=True):
            message_button.click()
            return True
        return False

    def get_profile_image(self) -> Optional[Image]:
        profile_image_view = self.device.find(resourceId=self.PROFILE_IMAGE_ID_REGEX.format(self.device.app_id),
                                              className=self.PROFILE_IMAGE_CLASS_NAME)
        if profile_image_view.exists(quick=True):
            return profile_image_view.get_image()
        else:
            return None

    def get_visible_posts_rows(self) -> int:
        count = 0
        posts_rows = self.device.find(resourceId=f"{self.device.app_id}:id/media_set_row_content_identifier",
                                      className="android.widget.LinearLayout")
        if posts_rows.exists(quick=True):
            post_width = posts_rows.get_width() / 3
            min_accepted_height = post_width / 3
            for row in posts_rows:
                row_height = row.get_height()
                if row_height >= min_accepted_height:
                    count += 1
        return count


class ProfileActionsView(InstagramView):

    def open_messages(self):
        item = self.device.find(resourceId=f'{self.device.app_id}:id/action_sheet_row_text_view',
                                className='android.widget.Button',
                                textMatches=case_insensitive_re("Send Message"))
        if item.exists(quick=True):
            item.click()
            return True
        return False


class FollowersFollowingListView(InstagramView):

    SEARCH_EDIT_TEXT_ID_REGEX = '{0}:id/row_search_edit_text'
    SEARCH_EDIT_TEXT_CLASS_NAME = 'android.widget.EditText'
    FOLLOW_LIST_ITEM_ID_REGEX = '{0}:id/follow_list_username'
    FOLLOW_LIST_ITEM_CLASS_NAME = 'android.widget.TextView'

    @unique
    class Tab(Enum):
        FOLLOWERS = 0
        FOLLOWING = 1

    def switch_to_tab(self, tab):
        """
        :type tab: FollowersFollowingListView.Tab
        """
        following_tab = self.device.find(className="android.widget.TextView",
                                         clickable=True,
                                         textMatches="(?i).*?following")
        followers_tab = self.device.find(className="android.widget.TextView",
                                         clickable=True,
                                         textMatches="(?i).*?followers")
        if tab == self.Tab.FOLLOWERS:
            followers_tab.click()
        else:
            following_tab.click()

    def search_for_user(self, username) -> bool:
        search_edit_text = self.device.find(resourceId=self.SEARCH_EDIT_TEXT_ID_REGEX.format(self.device.app_id),
                                            className=self.SEARCH_EDIT_TEXT_CLASS_NAME)
        search_edit_text.click()
        search_edit_text.set_text(username)
        sleeper.random_sleep()
        follow_list_item = self.device.find(resourceId=self.FOLLOW_LIST_ITEM_ID_REGEX.format(self.device.app_id),
                                            className=self.FOLLOW_LIST_ITEM_CLASS_NAME,
                                            text=username)
        if follow_list_item.exists(quick=True):
            follow_list_item.click()
            return True
        return False

    def scroll_to_bottom(self):
        print("Scroll to the bottom of the list")

        def is_end_reached():
            see_all_button = self.device.find(resourceId=f'{self.device.app_id}:id/see_all_button',
                                              className='android.widget.TextView')
            return see_all_button.exists()

        list_view = self.device.find(resourceId='android:id/list',
                                     className='android.widget.ListView')
        while not is_end_reached():
            list_view.swipe(DeviceFacade.Direction.BOTTOM)

    def scroll_to_top(self):
        print("Scroll to top of the list")

        def is_at_least_one_follower():
            follower = self.device.find(resourceId=f'{self.device.app_id}:id/follow_list_container',
                                        className='android.widget.LinearLayout')
            return follower.exists()

        list_view = self.device.find(resourceId='android:id/list',
                                     className='android.widget.ListView')

        while not is_at_least_one_follower():
            list_view.scroll(DeviceFacade.Direction.TOP)

    def is_list_empty(self):
        # Looking for any profile in the list, just to make sure its loaded with profiles
        any_username_view = self.device.find(resourceId=f'{self.device.app_id}:id/follow_list_username',
                                             className='android.widget.TextView')
        is_list_empty_from_profiles = not any_username_view.exists(quick=True)
        return is_list_empty_from_profiles

    def iterate_over_followers(self, is_myself, iteration_callback,
                               iteration_callback_pre_conditions, iterate_without_sleep=False):
        FOLLOW_LIST_CONTAINER_ID_REGEX = case_insensitive_re([f"{self.device.app_id}:id/follow_list_container"])
        ROW_SEARCH_ID_REGEX = case_insensitive_re([f"{self.device.app_id}:id/row_search_edit_text"])
        LOAD_MORE_BUTTON_ID_REGEX = case_insensitive_re([f"{self.device.app_id}:id/row_load_more_button"])

        # Wait until list is rendered
        self.device.find(resourceIdMatches=FOLLOW_LIST_CONTAINER_ID_REGEX,
                         className='android.widget.LinearLayout').wait()

        def scrolled_to_top():
            row_search = self.device.find(resourceIdMatches=ROW_SEARCH_ID_REGEX,
                                          className='android.widget.EditText')
            return row_search.exists()

        prev_screen_iterated_followers = []
        scroll_end_detector = ScrollEndDetector()
        while True:
            print("Iterate over visible followers")
            if not iterate_without_sleep:
                sleeper.random_sleep()

            screen_iterated_followers = []
            screen_skipped_followers_count = 0
            scroll_end_detector.notify_new_page()

            try:
                for item in self.device.find(resourceIdMatches=FOLLOW_LIST_CONTAINER_ID_REGEX,
                                             className='android.widget.LinearLayout'):
                    user_info_view = item.child(index=1)
                    user_name_view = user_info_view.child(index=0).child()
                    if not user_name_view.exists(quick=True):
                        print(COLOR_OKGREEN + "Next item not found: probably reached end of the screen." + COLOR_ENDC)
                        break

                    try:
                        username = user_name_view.get_text()
                    except DeviceFacade.JsonRpcError:
                        print(COLOR_OKGREEN + "Next item was found, but its text is half-cutted / invisible, "
                                              "moving on to next row." + COLOR_ENDC)
                        continue

                    screen_iterated_followers.append(username)
                    scroll_end_detector.notify_username_iterated(username)

                    if not iteration_callback_pre_conditions(username, user_name_view):
                        screen_skipped_followers_count += 1
                        continue

                    to_continue = iteration_callback(username, user_name_view)
                    if not to_continue:
                        print(COLOR_OKBLUE + "Stopping followers iteration" + COLOR_ENDC)
                        return

            except IndexError:
                print(COLOR_FAIL + "Cannot get next item: probably reached end of the screen." + COLOR_ENDC)

            if is_myself and scrolled_to_top():
                print(COLOR_OKGREEN + "Scrolled to top, finish." + COLOR_ENDC)
                return
            elif len(screen_iterated_followers) > 0:
                load_more_button = self.device.find(resourceIdMatches=LOAD_MORE_BUTTON_ID_REGEX)
                load_more_button_exists = load_more_button.exists(quick=True)

                if scroll_end_detector.is_the_end():
                    return

                need_swipe = screen_skipped_followers_count == len(screen_iterated_followers)
                list_view = self.device.find(resourceId='android:id/list',
                                             className='android.widget.ListView')
                if not list_view.exists():
                    print(COLOR_FAIL + "Cannot find the list of followers. Trying to press back again." + COLOR_ENDC)
                    self.device.back()
                    list_view = self.device.find(resourceId='android:id/list',
                                                 className='android.widget.ListView')

                if is_myself:
                    print(COLOR_OKGREEN + "Need to scroll now" + COLOR_ENDC)
                    list_view.scroll(DeviceFacade.Direction.TOP)
                else:
                    pressed_retry = False
                    if load_more_button_exists:
                        retry_button = load_more_button.child(className='android.widget.ImageView')
                        if retry_button.exists():
                            print("Press \"Load\" button")
                            retry_button.click()
                            sleeper.random_sleep()
                            pressed_retry = True

                    if need_swipe and not pressed_retry:
                        print(COLOR_OKGREEN + "All followers skipped, let's do a swipe" + COLOR_ENDC)
                        list_view.swipe(DeviceFacade.Direction.BOTTOM)
                    else:
                        print(COLOR_OKGREEN + "Need to scroll now" + COLOR_ENDC)
                        list_view.scroll(DeviceFacade.Direction.BOTTOM)

                prev_screen_iterated_followers.clear()
                prev_screen_iterated_followers += screen_iterated_followers
            else:
                print(COLOR_OKGREEN + "No followers were iterated, finish." + COLOR_ENDC)
                return


class CurrentStoryView(InstagramView):
    def getStoryFrame(self):
        return self.device.find(
            resourceId=f"{self.device.app_id}:id/reel_viewer_image_view",
            className="android.widget.FrameLayout",
        )

    def getUsername(self):
        reel_viewer_title = self.device.find(
            resourceId=f"{self.device.app_id}:id/reel_viewer_title",
            className="android.widget.TextView",
        )
        return "" if not reel_viewer_title.exists() else reel_viewer_title.get_text()

    def getTimestamp(self):
        reel_viewer_timestamp = self.device.find(
            resourceId=f"{self.device.app_id}:id/reel_viewer_timestamp",
            className="android.widget.TextView",
        )
        if reel_viewer_timestamp.exists():
            timestamp = reel_viewer_timestamp.get_text().strip()
            value = int(re.sub("[^0-9]", "", timestamp))
            if timestamp[-1] == "s":
                return datetime.timestamp(
                    datetime.datetime.now() - datetime.timedelta(seconds=value)
                )
            elif timestamp[-1] == "m":
                return datetime.timestamp(
                    datetime.datetime.now() - datetime.timedelta(minutes=value)
                )
            elif timestamp[-1] == "h":
                return datetime.timestamp(
                    datetime.datetime.now() - datetime.timedelta(hours=value)
                )
            else:
                return datetime.timestamp(
                    datetime.datetime.now() - datetime.timedelta(days=value)
                )
        return None


class DialogView(InstagramView):

    UNFOLLOW_BUTTON_ID_REGEX = '{0}:id/follow_sheet_unfollow_row|{1}:id/button_positive|{2}:id/primary_button'
    UNFOLLOW_BUTTON_CLASS_NAME_REGEX = TEXTVIEW_OR_BUTTON_REGEX
    UNFOLLOW_BUTTON_TEXT_REGEX = case_insensitive_re("Unfollow")
    LOCATION_DENY_BUTTON_ID_REGEX = '.*?:id/permission_deny.*?'
    LOCATION_DENY_BUTTON_CLASS_NAME_REGEX = TEXTVIEW_OR_BUTTON_REGEX
    LOCATION_DENY_AND_DONT_ASK_AGAIN_BUTTON_ID_REGEX = '.*?:id/permission_deny_and_dont_ask_again.*?'
    LOCATION_DENY_AND_DONT_ASK_AGAIN_BUTTON_CLASS_NAME_REGEX = TEXTVIEW_OR_BUTTON_REGEX
    LOCATION_CHECKBOX_ID_REGEX = '.*?:id/do_not_ask_checkbox'
    CONTINUE_BUTTON_ID = '{0}:id/primary_button'
    CONTINUE_BUTTON_CLASS_NAME = 'android.widget.Button'
    CONTINUE_BUTTTON_TEXT_REGEX = case_insensitive_re("Continue")
    OK_BUTTON_ID = '{0}:id/primary_button'
    OK_BUTTON_CLASS_NAME = 'android.widget.Button'
    OK_BUTTTON_TEXT_REGEX = case_insensitive_re("OK")
    CLOSE_APP_ID = 'android:id/aerr_close'
    CLOSE_APP_CLASS_NAME = 'android.widget.Button'
    CLOSE_APP_TEXT_REGEX = case_insensitive_re("Close app")
    HUAWEI_UPDATE_TITLE_REGEX = case_insensitive_re("Software update")
    HUAWEI_UPDATE_BUTTON_REGEX = case_insensitive_re("Later")

    def is_visible(self) -> bool:
        dialog_v1 = self.device.find(resourceIdMatches=f'{self.device.app_id}:id/(bottom_sheet_container|dialog_root_view|content)',
                                     className='android.widget.FrameLayout')
        dialog_v2 = self.device.find(resourceId=f'{self.device.app_id}:id/dialog_container',
                                     classNameMatches='android.view.ViewGroup|android.view.View')
        dialog_v3 = self.device.find(resourceIdMatches='com.android.(permissioncontroller|packageinstaller):id/.*?',
                                     className='android.widget.LinearLayout')
        return dialog_v1.exists(quick=True) \
            or dialog_v2.exists(quick=True) \
            or dialog_v3.exists(quick=True)

    def click_unfollow(self) -> bool:
        unfollow_button = self.device.find(
            resourceIdMatches=self.UNFOLLOW_BUTTON_ID_REGEX.format(self.device.app_id, self.device.app_id, self.device.app_id),
            classNameMatches=self.UNFOLLOW_BUTTON_CLASS_NAME_REGEX,
            textMatches=self.UNFOLLOW_BUTTON_TEXT_REGEX
        )
        if unfollow_button.exists():
            unfollow_button.click()
            return True
        return False

    def close_not_responding_dialog_if_visible(self):
        if self._click_close_app():
            print(COLOR_FAIL + "App crashed! Closing \"Isn't responding\" dialog." + COLOR_ENDC)
            save_crash(self.device)

    def _click_close_app(self) -> bool:
        close_app_button = self.device.find(resourceId=self.CLOSE_APP_ID,
                                            className=self.CLOSE_APP_CLASS_NAME,
                                            textMatches=self.CLOSE_APP_TEXT_REGEX)
        if close_app_button.exists():
            close_app_button.click()
            return True
        return False

    def close_location_access_dialog_if_visible(self):
        if not do_location_permission_dialog_checks:
            return

        if self.is_visible():
            if self._click_deny_location_access():
                print("Deny location permission request")

    def _click_deny_location_access(self) -> bool:
        deny_and_dont_ask_button = self.device.find(resourceIdMatches=self.LOCATION_DENY_AND_DONT_ASK_AGAIN_BUTTON_ID_REGEX,
                                                    classNameMatches=self.LOCATION_DENY_AND_DONT_ASK_AGAIN_BUTTON_CLASS_NAME_REGEX)
        deny_button = self.device.find(resourceIdMatches=self.LOCATION_DENY_BUTTON_ID_REGEX,
                                       classNameMatches=self.LOCATION_DENY_BUTTON_CLASS_NAME_REGEX)
        checkbox = self.device.find(resourceIdMatches=self.LOCATION_CHECKBOX_ID_REGEX,
                                    className="android.widget.CheckBox")
        checkbox.click(ignore_if_missing=True)
        if deny_and_dont_ask_button.exists():
            deny_and_dont_ask_button.click()
            return True
        if deny_button.exists():
            deny_button.click()
            return True
        return False

    def click_continue(self) -> bool:
        continue_button = self.device.find(resourceId=self.CONTINUE_BUTTON_ID.format(self.device.app_id),
                                           className=self.CONTINUE_BUTTON_CLASS_NAME,
                                           textMatches=self.CONTINUE_BUTTTON_TEXT_REGEX)
        if continue_button.exists():
            continue_button.click()
            return True
        return False

    def click_ok(self) -> bool:
        continue_button = self.device.find(resourceId=self.OK_BUTTON_ID.format(self.device.app_id),
                                           className=self.OK_BUTTON_CLASS_NAME,
                                           textMatches=self.OK_BUTTTON_TEXT_REGEX)
        if continue_button.exists():
            continue_button.click()
            return True
        return False

    def close_update_dialog_if_visible(self):
        if self.device.get_brand() == 'HUAWEI':
            if self.device.find(textMatches=self.HUAWEI_UPDATE_TITLE_REGEX).exists(quick=True):
                print("Found update dialog for HUAWEI, closing")
                self.device.find(textMatches=self.HUAWEI_UPDATE_BUTTON_REGEX).click(ignore_if_missing=True)
                sleeper.random_sleep()


class LanguageNotEnglishException(Exception):
    pass


class UserSwitchFailedException(Exception):
    pass
