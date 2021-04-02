import datetime
from enum import Enum
from typing import Optional

from insomniac.actions_types import GetProfileAction
from insomniac.device_facade import DeviceFacade
from insomniac.scroll_end_detector import ScrollEndDetector
from insomniac.sleeper import sleeper
from insomniac.utils import *


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

    def __init__(self, device: DeviceFacade):
        self.device = device

    def is_visible(self) -> bool:
        raise NotImplemented(f"is_visible() is not implemented for {self.__class__.__name__}")

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
            self.device.back()
        return self.on_back_pressed()

    def on_back_pressed(self) -> 'InstagramView':
        # Override this method to return a view after press_back_arrow()
        pass

    def is_block_dialog_present(self) -> bool:
        block_dialog_v1 = self.device.find(resourceId=f'{self.device.app_id}:id/dialog_root_view',
                                           className='android.widget.FrameLayout')
        block_dialog_v2 = self.device.find(resourceId=f'{self.device.app_id}:id/dialog_container',
                                           className='android.view.ViewGroup')
        return block_dialog_v1.exists(quick=True) or block_dialog_v2.exists(quick=True)


class TabBarView(InstagramView):
    HOME_CONTENT_DESC = "Home"
    SEARCH_CONTENT_DESC = "[Ss]earch and [Ee]xplore"
    REELS_CONTENT_DESC = "Reels"
    ORDERS_CONTENT_DESC = "Orders"
    ACTIVITY_CONTENT_DESC = "Activity"
    PROFILE_CONTENT_DESC = "Profile"

    def _get_tab_bar(self):
        self.device.close_keyboard()

        tab_bar = self.device.find(
            resourceIdMatches=case_insensitive_re(f"{self.device.app_id}:id/tab_bar"),
            className="android.widget.LinearLayout",
        )
        return tab_bar

    def navigate_to_home(self):
        self._navigate_to(TabBarTabs.HOME)
        return HomeView(self.device)

    def navigate_to_search(self):
        self._navigate_to(TabBarTabs.SEARCH)
        return SearchView(self.device)

    def navigate_to_reels(self):
        self._navigate_to(TabBarTabs.REELS)

    def navigate_to_orders(self):
        self._navigate_to(TabBarTabs.ORDERS)

    def navigate_to_activity(self):
        self._navigate_to(TabBarTabs.ACTIVITY)

    def navigate_to_profile(self):
        self._navigate_to(TabBarTabs.PROFILE)
        return ProfileView(self.device, is_own_profile=True)

    def _navigate_to(self, tab: TabBarTabs):
        tab_name = tab.name
        print_debug(f"Navigate to {tab_name}")
        button = None
        tab_bar_view = self._get_tab_bar()
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

        if button.exists():
            # Two clicks to reset tab content
            button.click()
            button.click()

            return

        print(COLOR_FAIL + f"Didn't find tab {tab_name} in the tab bar... "
                           f"Maybe English language is not set!?" + COLOR_ENDC)

        raise LanguageNotEnglishException()


class ActionBarView(InstagramView):
    action_bar_bottom = None
    tab_bar_top = None

    def __init__(self, device: DeviceFacade):
        super().__init__(device)
        self.action_bar = self._get_action_bar()

    def _get_action_bar(self):
        tab_bar = self.device.find(
            resourceIdMatches=case_insensitive_re(f"{self.device.app_id}:id/action_bar_container"),
            className="android.widget.FrameLayout")
        return tab_bar

    @staticmethod
    def update_interaction_rect(device):
        action_bar = device.find(resourceId=f'{device.app_id}:id/action_bar_container',
                                 className='android.widget.FrameLayout')
        if action_bar.exists():
            ActionBarView.action_bar_bottom = action_bar.get_bounds()['bottom']

        device.close_keyboard()

        tab_bar = device.find(resourceId=f'{device.app_id}:id/tab_bar',
                              className='android.widget.LinearLayout')
        if tab_bar.exists():
            ActionBarView.tab_bar_top = tab_bar.get_bounds()['top']

    @staticmethod
    def is_in_interaction_rect(view):
        if ActionBarView.action_bar_bottom is None or ActionBarView.tab_bar_top is None:
            print(COLOR_FAIL + "Interaction rect is not specified." + COLOR_ENDC)
            return True

        view_top = view.get_bounds()['top']
        view_bottom = view.get_bounds()['bottom']
        return ActionBarView.action_bar_bottom <= view_top and view_bottom <= ActionBarView.tab_bar_top


class HomeView(ActionBarView):
    def __init__(self, device: DeviceFacade):
        super().__init__(device)

    def navigate_to_search(self):
        print_debug("Navigate to Search")
        search_btn = self.action_bar.child(
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
    def _get_search_edit_text(self):
        return self.device.find(
            resourceIdMatches=case_insensitive_re(
                f"{self.device.app_id}:id/action_bar_search_edit_text"
            ),
            className="android.widget.EditText",
        )

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
        return self.device.find(
            resourceIdMatches=case_insensitive_re(
                f"{self.device.app_id}:id/row_place_title"
            ),
            className="android.widget.TextView",
            textMatches=case_insensitive_re(place)
        )

    def _get_tab_text_view(self, tab: SearchTabs):
        tab_layout = self.device.find(
            resourceIdMatches=case_insensitive_re(
                f"{self.device.app_id}:id/fixed_tabbar_tabs_container"
            ),
            className="android.widget.LinearLayout",
        )

        tab_text_view = tab_layout.child(
            resourceIdMatches=case_insensitive_re(
                f"{self.device.app_id}:id/tab_button_name_text"
            ),
            className="android.widget.TextView",
            textMatches=case_insensitive_re(tab.name),
        )
        return tab_text_view

    def _search_tab_with_text_placeholder(self, tab: SearchTabs):
        tab_layout = self.device.find(
            resourceIdMatches=case_insensitive_re(
                f"{self.device.app_id}:id/fixed_tabbar_tabs_container"
            ),
            className="android.widget.LinearLayout",
        )
        search_edit_text = self._get_search_edit_text()

        fixed_text = "Search {}".format(tab.name if tab.name != "TAGS" else "hashtags")
        print_debug(
            "Going to check if the search bar have as placeholder: {}".format(
                fixed_text
            )
        )

        for item in tab_layout.child(
            resourceId=f"{self.device.app_id}:id/tab_button_fallback_icon",
            className="android.widget.ImageView",
        ):
            item.click()
            # random_sleep()

            # Little trick for force-update the ui and placeholder text
            search_edit_text.click()
            self.device.back()

            if self.device.find(
                className="android.widget.TextView",
                textMatches=case_insensitive_re(fixed_text),
            ).exists():
                return item
        return None

    def navigate_to_username(self, username, on_action):
        print_debug(f"Navigate to profile @{username}")
        search_edit_text = self._get_search_edit_text()
        search_edit_text.click()
        self._handle_permission_request()
        sleeper.random_sleep()

        accounts_tab = self._get_tab_text_view(SearchTabs.ACCOUNTS)
        if not accounts_tab.exists():
            print_debug("Cannot find tab: Accounts. Going to attempt to search for placeholder in all tabs")
            accounts_tab = self._search_tab_with_text_placeholder(SearchTabs.ACCOUNTS)
            if accounts_tab is None:
                print(COLOR_FAIL + "Cannot find tab: Accounts." + COLOR_ENDC)
                save_crash(self.device)
                return None
        accounts_tab.click()

        # Check if username already exists in the recent search list -> act as human
        username_view_recent = self._get_username_row(username)
        if username_view_recent.exists():
            username_view_recent.click()
            on_action(GetProfileAction(user=username))
            return ProfileView(self.device, is_own_profile=False)

        print(f"@{username} is not in recent searching history...")
        search_edit_text.set_text(username)
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
        sleeper.random_sleep()

        hashtag_tab = self._get_tab_text_view(SearchTabs.TAGS)
        if not hashtag_tab.exists():
            print_debug("Cannot find tab: Tags. Going to attempt to search for placeholder in all tabs")
            hashtag_tab = self._search_tab_with_text_placeholder(SearchTabs.TAGS)
            if hashtag_tab is None:
                print(COLOR_FAIL + "Cannot find tab: Tags." + COLOR_ENDC)
                save_crash(self.device)
                return None
        hashtag_tab.click()

        # Check if hashtag already exists in the recent search list -> act as human
        hashtag_view_recent = self._get_hashtag_row(hashtag)
        if hashtag_view_recent.exists():
            hashtag_view_recent.click()
            sleeper.random_sleep()
            return HashTagView(self.device)

        print(f"#{hashtag} is not in recent searching history...")
        search_edit_text.set_text(hashtag)
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
        sleeper.random_sleep()

        places_tab = self._get_tab_text_view(SearchTabs.PLACES)
        if not places_tab.exists():
            print_debug("Cannot find tab: Places. Going to attempt to search for placeholder in all tabs")
            places_tab = self._search_tab_with_text_placeholder(SearchTabs.PLACES)
            if places_tab is None:
                print(COLOR_FAIL + "Cannot find tab: Places." + COLOR_ENDC)
                save_crash(self.device)
                return None
        places_tab.click()

        # Check if place already exists in the recent search list -> act as human
        place_view_recent = self._get_place_row(place)
        if place_view_recent.exists():
            place_view_recent.click()
            sleeper.random_sleep()
            return PlacesView(self.device)

        print(f"{place} is not in recent searching history...")
        search_edit_text.set_text(place)
        place_view = self._get_place_row(place)

        if not place_view.exists():
            print(COLOR_FAIL + f"Cannot find place {place}, abort." + COLOR_ENDC)
            save_crash(self.device)
            return None

        place_view.click()
        return PlacesView(self.device)

    def _handle_permission_request(self):
        dialog_container = self.device.find(resourceId="com.android.packageinstaller:id/dialog_container",
                                            className="android.widget.LinearLayout")
        deny_button = dialog_container.child(resourceId="com.android.packageinstaller:id/permission_deny_button",
                                             className="android.widget.Button")
        checkbox = dialog_container.child(resourceId="com.android.packageinstaller:id/do_not_ask_checkbox",
                                          className="android.widget.CheckBox")
        if dialog_container.exists():
            print("Deny Instagram permission request")
            checkbox.click(ignore_if_missing=True)
            deny_button.click(ignore_if_missing=True)


class PostsViewList(InstagramView):

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
        recycler_view = self.device.find(resourceId='android:id/list',
                                         className='androidx.recyclerview.widget.RecyclerView')
        recycler_view.scroll(DeviceFacade.Direction.BOTTOM)

    def swipe_to_fit_posts(self, first_post):
        """calculate the right swipe amount necessary to swipe to next post in hashtag post view"""
        POST_CONTAINER = f"{self.device.app_id}:id/zoomable_view_container|{self.device.app_id}:id/carousel_media_group"
        displayWidth = self.device.get_info()["displayWidth"]
        if first_post:
            zoomable_view_container = self.device.find(
                resourceIdMatches=POST_CONTAINER
            ).get_bounds()["bottom"]

            print("Scrolled down to see more posts.")
            self.device.swipe_points(
                displayWidth / 2,
                zoomable_view_container - 1,
                displayWidth / 2,
                zoomable_view_container * 2 / 3,
            )
        else:

            gap_view = self.device.find(
                resourceIdMatches=f"{self.device.app_id}:id/gap_view"
            ).get_bounds()["top"]

            self.device.swipe_points(displayWidth / 2, gap_view, displayWidth / 2, 10)
            zoomable_view_container = self.device.find(resourceIdMatches=(POST_CONTAINER))

            zoomable_view_container = self.device.find(
                resourceIdMatches=POST_CONTAINER
            ).get_bounds()["bottom"]

            self.device.swipe_points(
                displayWidth / 2,
                zoomable_view_container - 1,
                displayWidth / 2,
                zoomable_view_container * 2 / 3,
            )
        return

    def check_if_last_post(self, last_description):
        """check if that post has been just interacted"""
        post_description = self.device.find(
            resourceId=f"{self.device.app_id}:id/row_feed_comment_textview_layout"
        )
        if post_description.exists(True):
            new_description = post_description.get_text().upper()
            if new_description == last_description:
                print("This is the last post for this hashtag")
                return True, new_description
            else:
                return False, new_description


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
    def navigate_to_language(self):
        print_debug("Navigate to Language")
        button = self.device.find(
            textMatches=case_insensitive_re("Language"),
            resourceId=f"{self.device.app_id}:id/row_simple_text_textview",
            className="android.widget.TextView",
        )
        button.click()

        return LanguageView(self.device)


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
                                           className='android.widget.TextView')
        settings_button.click()
        return SettingsView(self.device)


class OpenedPostView(InstagramView):
    POST_VIEW_ID_REGEX = '{0}:id/zoomable_view_container|{1}:id/carousel_image|{2}:id/layout_container_main'

    def is_visible(self) -> bool:
        return self.device.find(
            resourceIdMatches=self.POST_VIEW_ID_REGEX.format(self.device.app_id,
                                                             self.device.app_id,
                                                             self.device.app_id),
            className='android.widget.FrameLayout'
        ).exists(quick=True)

    def _get_post_like_button(self, scroll_to_find=True):
        """Find the like button right bellow a post.
        Note: sometimes the like button from the post above or bellow are
        dumped as well, so we need handle that situation.

        scroll_to_find: if the like button is not found, scroll a bit down
                        to try to find it. Default: True
        """
        BTN_LIKE_RES_ID = f"{self.device.app_id}:id/row_feed_button_like"
        MEDIA_GROUP_RE = case_insensitive_re(
            [
                f"{self.device.app_id}:id/zoomable_view_container",
                f"{self.device.app_id}:id/carousel_media_group",
            ]
        )

        post_view_area = self.device.find(
            resourceIdMatches=case_insensitive_re("android:id/list")
        )

        if not post_view_area.exists(quick=True):
            print("Cannot find post recycler view area")
            save_crash(self.device)
            return None

        post_media_view = self.device.find(
            resourceIdMatches=MEDIA_GROUP_RE
        )

        if not post_media_view.exists(quick=True):
            print("Cannot find post media view area")
            save_crash(self.device)
            return None

        like_btn_view = post_media_view.down(
            resourceIdMatches=case_insensitive_re(BTN_LIKE_RES_ID)
        )

        should_scroll = False

        if like_btn_view.exists(quick=True):
            # threshold of 30% of the display height
            threshold = int((0.3) * self.device.get_info()["displayHeight"])

            like_btn_top_bound = like_btn_view.get_bounds()["top"]
            is_like_btn_in_the_bottom = like_btn_top_bound > threshold

            if not is_like_btn_in_the_bottom:
                print_debug(f"Like button is to high ({like_btn_top_bound} px). Threshold is {threshold} px")

            post_view_area_bottom_bound = post_view_area.get_bounds()["bottom"]
            is_like_btn_visible = like_btn_top_bound <= post_view_area_bottom_bound

            if not is_like_btn_visible:
                print_debug(f"Like btn out of current clickable area. Like btn top ({like_btn_top_bound}) "
                            f"recycler_view bottom ({post_view_area_bottom_bound})")

            should_scroll = not is_like_btn_in_the_bottom or not is_like_btn_visible

        else:
            print_debug("Like button not found bellow the post.")
            should_scroll = True

        if should_scroll:
            if scroll_to_find:
                print_debug("Try to scroll tiny bit down...")
                # Remember: to scroll down we need to swipe up :)
                for _ in range(3):
                    self.device.swipe(DeviceFacade.Direction.TOP, scale=0.25)
                    like_btn_view = self.device.find(
                        resourceIdMatches=case_insensitive_re(BTN_LIKE_RES_ID)
                    )

                    if like_btn_view.exists(quick=True):
                        break

            if not scroll_to_find or not like_btn_view.exists(quick=True):
                print(COLOR_FAIL + "Could not find like button bellow the post" + COLOR_ENDC)
                return None

        return like_btn_view

    def _is_post_liked(self):

        like_btn_view = self._get_post_like_button()
        if like_btn_view is None:
            return False

        return like_btn_view.get_selected()

    def like_post(self, click_btn_like=False):
        if self._is_post_liked():
            print(COLOR_FAIL + "Post already been liked" + COLOR_ENDC)
            return False

        MEDIA_GROUP_RE = case_insensitive_re(
            [
                f"{self.device.app_id}:id/zoomable_view_container",
                f"{self.device.app_id}:id/carousel_media_group",
            ]
        )

        post_media_view = self.device.find(
            resourceIdMatches=MEDIA_GROUP_RE
        )

        if click_btn_like:
            like_btn_view = self._get_post_like_button()
            if like_btn_view is None:
                return False
            like_btn_view.click()
        else:
            if post_media_view.exists(quick=True):
                post_media_view.double_click()
            else:
                print(COLOR_FAIL + "Could not find post area to double click" + COLOR_ENDC)
                return False

        sleeper.random_sleep()

        return self._is_post_liked()

    def get_user_name(self):
        user_name_view = self.device.find(resourceId=f"{self.device.app_id}:id/row_feed_photo_profile_name")
        if user_name_view.exists(quick=True):
            return user_name_view.get_text()
        return None


class PostsGridView(InstagramView):

    def open_random_post(self) -> Optional['PostsViewList']:
        # Scroll down several times to pick random post
        scroll_times = randint(0, 5)
        posts_grid = self.device.find(resourceId=f'{self.device.app_id}:id/recycler_view',
                                      className='androidx.recyclerview.widget.RecyclerView')
        print(f"Scroll down {scroll_times} times.")
        for _ in range(0, scroll_times):
            posts_grid.scroll(DeviceFacade.Direction.BOTTOM)
            sleeper.random_sleep()

        # Scan for available posts' coordinates
        available_posts_coords = []
        print("Choosing a random post from those on the screen")
        for post_view in posts_grid.child(resourceId=f'{self.device.app_id}:id/image_button',
                                          className='android.widget.ImageView'):
            bounds = post_view.get_bounds()
            left = bounds["left"]
            top = bounds["top"]
            right = bounds["right"]
            bottom = bounds["bottom"]
            coords = (left + (right - left) / 2, top + (bottom - top) / 2)
            available_posts_coords.append(coords)
        if len(available_posts_coords) == 0:
            print(COLOR_FAIL + f"No posts for this hashtag. Abort." + COLOR_ENDC)
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


class ProfileView(ActionBarView):
    def __init__(self, device: DeviceFacade, is_own_profile=False):
        super().__init__(device)
        self.is_own_profile = is_own_profile

    def is_visible(self):
        return self.device.find(resourceId=f"{self.device.app_id}:id/row_profile_header",
                                className="android.view.ViewGroup").exists(quick=True)

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
        for options_view in self.action_bar.child(clickable=True):
            pass
        if options_view is None or not options_view.exists():
            print(COLOR_FAIL + "No idea how to open menu..." + COLOR_ENDC)
            return None
        options_view.click()
        return OptionsView(self.device)

    def change_to_username(self, username):
        action_bar = self._get_action_bar_title_btn()
        current_profile_name = action_bar.get_text().upper()
        if current_profile_name == username.upper():
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
            current_profile_name = action_bar.get_text().upper()
            if current_profile_name == username.upper():
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
        return self.action_bar.child(
            resourceIdMatches=re_case_insensitive, className="android.widget.TextView"
        )

    def get_username(self, error=True):
        title_view = self._get_action_bar_title_btn()
        if title_view.exists():
            return title_view.get_text()
        if error:
            print(COLOR_FAIL + "Cannot get username" + COLOR_ENDC)
        return None

    def _parse_counter(self, text):
        multiplier = 1
        text = text.replace(",", "")
        is_dot_in_text = False
        if '.' in text:
            text = text.replace(".", "")
            is_dot_in_text = True
        if "K" in text:
            text = text.replace("K", "")
            multiplier = 1000

            if is_dot_in_text:
                multiplier = 100

        if "M" in text:
            text = text.replace("M", "")
            multiplier = 1000000

            if is_dot_in_text:
                multiplier = 100000
        try:
            count = int(float(text) * multiplier)
        except ValueError:
            print(COLOR_FAIL + f"Cannot parse {text}. Probably wrong language ?!" + COLOR_ENDC)
            raise LanguageNotEnglishException()
        return count

    def _get_followers_text_view(self):
        followers_text_view = self.device.find(
            resourceIdMatches=case_insensitive_re(
                f"{self.device.app_id}:id/row_profile_header_textview_followers_count"
            ),
            className="android.widget.TextView",
        )
        return followers_text_view

    def get_followers_count(self, should_parse=True, swipe_up_if_needed=False):
        followers = None
        followers_text_view = self._get_followers_text_view()
        if swipe_up_if_needed and not followers_text_view.exists(quick=True):
            print("Cannot find followers count text, maybe its a little bit upper.")
            print("Swiping up a bit.")
            self.device.swipe(DeviceFacade.Direction.BOTTOM)

        if followers_text_view.exists(quick=True):
            followers_text = followers_text_view.get_text()
            if followers_text:
                if should_parse:
                    followers = self._parse_counter(followers_text)
                else:
                    followers = followers_text
            else:
                print(COLOR_FAIL + "Cannot get followers count text" + COLOR_ENDC)
        else:
            print(COLOR_FAIL + "Cannot find followers count view" + COLOR_ENDC)

        return followers

    def _get_following_text_view(self):
        following_text_view = self.device.find(
            resourceIdMatches=case_insensitive_re(
                f"{self.device.app_id}:id/row_profile_header_textview_following_count"
            ),
            className="android.widget.TextView",
        )
        return following_text_view

    def get_following_count(self, swipe_up_if_needed=False):
        following = None
        following_text_view = self._get_following_text_view()
        if swipe_up_if_needed and not following_text_view.exists(quick=True):
            print("Cannot find following count text, maybe its a little bit upper.")
            print("Swiping up a bit.")
            self.device.swipe(DeviceFacade.Direction.BOTTOM)

        if following_text_view.exists():
            following_text = following_text_view.get_text()
            if following_text:
                following = self._parse_counter(following_text)
            else:
                print(COLOR_FAIL + "Cannot get following count text" + COLOR_ENDC)
        else:
            print(COLOR_FAIL + "Cannot find following count view" + COLOR_ENDC)

        return following

    def get_posts_count(self):
        post_count_view = self.device.find(
            resourceIdMatches=case_insensitive_re(
                f"{self.device.app_id}:id/row_profile_header_textview_post_count"
            ),
            className="android.widget.TextView",
        )
        if post_count_view.exists():
            count = post_count_view.get_text()
            if count != None:
                return self._parse_counter(count)
            else:
                print(COLOR_FAIL + "Cannot get posts count text" + COLOR_ENDC)
                return 0
        else:
            print(COLOR_FAIL + "Cannot get posts count text" + COLOR_ENDC)
            return 0

    def count_photo_in_view(self):
        """return rows filled and the number of post in the last row"""
        RECYCLER_VIEW = "androidx.recyclerview.widget.RecyclerView"
        grid_post = self.device.find(
            className=RECYCLER_VIEW, resourceIdMatches="android:id/list"
        )
        if grid_post.exists():  # max 4 rows supported
            for i in range(2, 5):
                lin_layout = grid_post.child(
                    index=i, className="android.widget.LinearLayout"
                )
                if i == 4 or not lin_layout.exists(True):
                    last_index = i - 1
                    last_lin_layout = grid_post.child(index=last_index)
                    for n in range(1, 4):
                        if n == 3 or not last_lin_layout.child(index=n).exists(True):
                            if n == 3:
                                return last_index, 0
                            else:
                                return last_index - 1, n
        else:
            return 0, 0

    def get_profile_info(self, swipe_up_if_needed=False):

        username = self.get_username()
        followers = self.get_followers_count(swipe_up_if_needed=swipe_up_if_needed)
        following = self.get_following_count(swipe_up_if_needed=swipe_up_if_needed)

        return username, followers, following

    def get_profile_biography(self):
        biography = self.device.find(
            resourceIdMatches=case_insensitive_re(
                f"{self.device.app_id}:id/profile_header_bio_text"
            ),
            className="android.widget.TextView",
        )
        if biography.exists():
            biography_text = biography.get_text()
            # If the biography is very long, blabla text and end with "...more" click the bottom of the text and get the new text
            is_long_bio = re.compile(
                r"{0}$".format("… more"), flags=re.IGNORECASE
            ).search(biography_text)
            if is_long_bio is not None:
                biography.click(biography.Location.BOTTOM)
                return biography.get_text()
            return biography_text
        return ""

    def get_full_name(self):
        full_name_view = self.device.find(
            resourceIdMatches=case_insensitive_re(
                f"{self.device.app_id}:id/profile_header_full_name"
            ),
            className="android.widget.TextView",
        )
        if full_name_view.exists():
            fullname_text = full_name_view.get_text()
            if fullname_text is not None:
                return fullname_text
        return ""

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

    def profile_image(self):
        return self.device.find(
            resourceId=f"{self.device.app_id}:id/row_profile_header_imageview",
            className="android.widget.ImageView",
        )

    def navigate_to_followers(self):
        print_debug("Navigate to Followers")
        FOLLOWERS_BUTTON_ID_REGEX = case_insensitive_re(
            [
                f"{self.device.app_id}:id/row_profile_header_followers_container",
                f"{self.device.app_id}:id/row_profile_header_container_followers",
            ]
        )
        followers_button = self.device.find(resourceIdMatches=FOLLOWERS_BUTTON_ID_REGEX)
        followers_button.click()

        return FollowersFollowingListView(self.device)

    def navigate_to_following(self):
        print_debug("Navigate to Followers")
        FOLLOWING_BUTTON_ID_REGEX = case_insensitive_re(
            [
                f"{self.device.app_id}:id/row_profile_header_following_container",
                f"{self.device.app_id}:id/row_profile_header_container_following",
            ]
        )
        following_button = self.device.find(resourceIdMatches=FOLLOWING_BUTTON_ID_REGEX)
        following_button.click()

        return FollowersFollowingListView(self.device)

    def swipe_to_fit_posts(self):
        """calculate the right swipe amount necessary to see 12 photos"""
        displayWidth = self.device.get_info()["displayWidth"]
        element_to_swipe_over = self.device.find(
            resourceIdMatches=f"{self.device.app_id}:id/profile_tabs_container"
        ).get_bounds()["top"]
        bar_countainer = self.device.find(
            resourceIdMatches=f"{self.device.app_id}:id/action_bar_container"
        ).get_bounds()["bottom"]

        print("Scrolled down to see more posts.")
        self.device.swipe_points(
            displayWidth / 2, element_to_swipe_over, displayWidth / 2, bar_countainer
        )
        return

    def navigate_to_posts_tab(self):
        self._navigate_to_tab(ProfileTabs.POSTS)
        return PostsGridView(self.device)

    def navigate_to_igtv_tab(self):
        self._navigate_to_tab(ProfileTabs.IGTV)
        raise Exception("Not implemented")

    def navigate_to_reels_tab(self):
        self._navigate_to_tab(ProfileTabs.REELS)
        raise Exception("Not implemented")

    def navigate_to_effects_tab(self):
        self._navigate_to_tab(ProfileTabs.EFFECTS)
        raise Exception("Not implemented")

    def navigate_to_photos_of_you_tab(self):
        self._navigate_to_tab(ProfileTabs.PHOTOS_OF_YOU)
        raise Exception("Not implemented")

    def _navigate_to_tab(self, tab: ProfileTabs):
        TABS_RES_ID = f"{self.device.app_id}:id/profile_tab_layout"
        TABS_CLASS_NAME = "android.widget.HorizontalScrollView"
        tabs_view = self.device.find(
            resourceIdMatches=case_insensitive_re(TABS_RES_ID),
            className=TABS_CLASS_NAME,
        )

        TAB_RES_ID = f"{self.device.app_id}:id/profile_tab_icon_view"
        TAB_CLASS_NAME = "android.widget.ImageView"
        description = ""
        if tab == ProfileTabs.POSTS:
            description = "Grid View"
        elif tab == ProfileTabs.IGTV:
            description = "IGTV"
        elif tab == ProfileTabs.REELS:
            description = "Reels"
        elif tab == ProfileTabs.EFFECTS:
            description = "Effects"
        elif tab == ProfileTabs.PHOTOS_OF_YOU:
            description = "Photos of You"

        button = tabs_view.child(
            descriptionMatches=case_insensitive_re(description),
            resourceIdMatches=case_insensitive_re(TAB_RES_ID),
            className=TAB_CLASS_NAME,
        )

        attempts = 0
        while not button.exists():
            attempts += 1
            self.device.swipe(DeviceFacade.Direction.TOP, scale=0.1)
            if attempts > 2:
                print(COLOR_FAIL + f"Cannot navigate to tab '{description}'" + COLOR_ENDC)
                save_crash(self.device)
                return

        button.click()

    def _get_recycler_view(self):
        CLASSNAME = "(androidx.recyclerview.widget.RecyclerView|android.view.View)"

        return self.device.find(classNameMatches=CLASSNAME)


class FollowersFollowingListView(InstagramView):
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


class LanguageNotEnglishException(Exception):
    pass


class UserSwitchFailedException(Exception):
    pass
