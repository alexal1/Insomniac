from functools import partial
from random import shuffle

from src.device_facade import DeviceFacade
from src.interaction_rect_checker import is_in_interaction_rect
from src.navigation import navigate, Tabs, switch_to_english, LanguageChangedException
from src.storage import FollowingStatus
from src.utils import *

FOLLOWERS_BUTTON_ID_REGEX = 'com.instagram.android:id/row_profile_header_followers_container' \
                            '|com.instagram.android:id/row_profile_header_container_followers'
TEXTVIEW_OR_BUTTON_REGEX = 'android.widget.TextView|android.widget.Button'
FOLLOW_REGEX = 'Follow|Follow Back'
UNFOLLOW_REGEX = 'Following|Requested'


def handle_blogger(device,
                   username,
                   is_scrapping_session,
                   is_targeted_session,
                   session_state,
                   likes_count,
                   follow_percentage,
                   follow_limit,
                   total_follow_limit,
                   storage,
                   profile_filter,
                   on_like,
                   on_interaction):
    is_myself = username == session_state.my_username
    interaction = partial(_interact_with_user,
                          my_username=session_state.my_username,
                          likes_count=likes_count,
                          follow_percentage=follow_percentage,
                          on_like=on_like,
                          profile_filter=profile_filter,
                          is_scrapping_session=is_scrapping_session)

    is_follow_limit_reached = partial(_is_follow_limit_reached,
                                      session_state=session_state,
                                      follow_limit=follow_limit,
                                      total_follow_limit=total_follow_limit,
                                      blogger=username)

    if is_targeted_session:
        if is_myself:
            return

        if storage.check_user_was_interacted(username):
            print("@" + username + ": already interacted. Skip.")
            return

        if not _open_user(device, username):
            return

        _interact_single_user(device, username, interaction, is_follow_limit_reached, storage,
                              on_interaction, is_myself, is_scrapping_session)

    else:
        if not _open_user_followers(device, username):
            return
        if is_myself:
            _scroll_to_bottom(device)
        _iterate_over_followers(device, interaction, is_follow_limit_reached, storage, on_interaction, is_myself,
                                is_scrapping_session, profile_filter.get_max_numbers_in_profile_name())


def get_user_followers_list(device, username):
    if not _open_user_followers(device, username, True):
        print(COLOR_FAIL + "Could not open {0} profile followers list. It wont be grabbed this session.".format(username) + COLOR_ENDC)
        return []

    full_list = _iterate_over_followers(device, None, None, None, None, False, True, None, True)
    return list(dict.fromkeys(full_list))


def _open_user_followers(device, username, refresh=False):
    return _open_user(device, username, True, refresh)


def _open_user(device, username, open_followers=False, refresh=False):
    if username is None:
        print("Open your followers")
        followers_button = device.find(resourceIdMatches=FOLLOWERS_BUTTON_ID_REGEX)
        followers_button.click()
    else:
        navigate(device, Tabs.SEARCH)

        print("Open user @" + username)
        search_edit_text = device.find(resourceId='com.instagram.android:id/action_bar_search_edit_text',
                                       className='android.widget.EditText')
        search_edit_text.set_text(username)
        username_view = device.find(resourceId='com.instagram.android:id/row_search_user_username',
                                    className='android.widget.TextView',
                                    text=username)
                                    
        random_sleep()
        if not username_view.exists():
            print_timeless(COLOR_FAIL + "Cannot find user @" + username + ", abort." + COLOR_ENDC)
            return False

        username_view.click()

        if refresh:
            print("Refreshing profile status...")
            coordinator_layout = device.find(resourceId='com.instagram.android:id/coordinator_root_layout')
            if coordinator_layout.exists():
                coordinator_layout.scroll(DeviceFacade.Direction.TOP)

        if open_followers:
            print("Open @" + username + " followers")
            followers_button = device.find(resourceIdMatches=FOLLOWERS_BUTTON_ID_REGEX)
            followers_button.click()

    return True


def _scroll_to_bottom(device):
    print("Scroll to bottom")

    def is_end_reached():
        see_all_button = device.find(resourceId='com.instagram.android:id/see_all_button',
                                     className='android.widget.TextView')
        return see_all_button.exists()

    list_view = device.find(resourceId='android:id/list',
                            className='android.widget.ListView')
    while not is_end_reached():
        list_view.swipe(DeviceFacade.Direction.BOTTOM)

    print("Scroll back to the first follower")

    def is_at_least_one_follower():
        follower = device.find(resourceId='com.instagram.android:id/follow_list_container',
                               className='android.widget.LinearLayout')
        return follower.exists()

    while not is_at_least_one_follower():
        list_view.scroll(DeviceFacade.Direction.TOP)


def _interact_single_user(device, username, interaction, is_follow_limit_reached, storage,
                          on_interaction, is_myself, is_scrapping_session):
    if is_myself:
        print("Cant interact your-self. Skip.")
        return

    if storage.check_user_was_interacted(username):
        print("@" + username + ": already interacted. Skip.")
        return

    print("@" + username + ": interact")

    can_follow = not is_myself \
                 and not is_follow_limit_reached() \
                 and storage.get_following_status(username) == FollowingStatus.NONE

    interaction_succeed, followed = interaction(device, username=username, can_follow=can_follow)

    if is_scrapping_session and interaction_succeed:
        storage.add_target_user(username)

    storage.add_interacted_user(username, followed=followed)
    on_interaction(succeed=interaction_succeed, followed=followed)

    print("Back to search view")
    device.back()


def _iterate_over_followers(device, interaction, is_follow_limit_reached, storage, on_interaction,
                            is_myself, is_scrapping_session, max_nums_in_username=None, just_get_list=False):
    # Wait until list is rendered
    device.find(resourceId='com.instagram.android:id/follow_list_container',
                className='android.widget.LinearLayout').wait()

    def scrolled_to_top():
        row_search = device.find(resourceId='com.instagram.android:id/row_search_edit_text',
                                 className='android.widget.EditText')
        return row_search.exists()

    def showing_suggestions():
        row_search = device.find(resourceId='com.instagram.android:id/row_header_textview',
                                 className='android.widget.TextView')
        return row_search.exists()

    all_followers_iterated = []
    prev_screen_iterated_followers = []
    while True:
        print("Iterate over visible followers")
        if not just_get_list:
            random_sleep()
        screen_iterated_followers = []
        screen_skipped_followers_count = 0

        try:
            for item in device.find(resourceId='com.instagram.android:id/follow_list_container',
                                    className='android.widget.LinearLayout'):
                user_info_view = item.child(index=1)
                user_name_view = user_info_view.child(index=0).child()
                if not user_name_view.exists(quick=True):
                    print(COLOR_OKGREEN + "Next item not found: probably reached end of the screen." + COLOR_ENDC)
                    break

                username = user_name_view.get_text()
                screen_iterated_followers.append(username)

                if not just_get_list:
                    if not is_myself and storage.check_user_was_interacted(username):
                        print("@" + username + ": already interacted. Skip.")
                        screen_skipped_followers_count += 1
                    elif is_myself and storage.check_user_was_interacted_recently(username):
                        print("@" + username + ": already interacted in the last week. Skip.")
                        screen_skipped_followers_count += 1
                    elif max_nums_in_username is not None and \
                            get_count_of_nums_in_str(username) > int(max_nums_in_username):
                        print("@" + username + ": more than " + str(max_nums_in_username) + " numbers in username. Skip.")
                        screen_skipped_followers_count += 1
                    else:
                        print("@" + username + ": interact")
                        user_name_view.click()

                        can_follow = not is_myself \
                            and not is_follow_limit_reached() \
                            and storage.get_following_status(username) == FollowingStatus.NONE

                        interaction_succeed, followed = interaction(device, username=username, can_follow=can_follow)

                        if is_scrapping_session and interaction_succeed:
                            storage.add_target_user(username)

                        storage.add_interacted_user(username, followed=followed)
                        can_continue = on_interaction(succeed=interaction_succeed,
                                                      followed=followed)

                        if not can_continue:
                            return

                        print("Back to followers list")
                        device.back()
        except IndexError:
            print(COLOR_FAIL + "Cannot get next item: probably reached end of the screen." + COLOR_ENDC)

        if is_myself and scrolled_to_top():
            print(COLOR_OKGREEN + "Scrolled to top, finish." + COLOR_ENDC)

            if just_get_list:
                return all_followers_iterated + screen_iterated_followers

            return
        elif len(screen_iterated_followers) > 0:
            load_more_button = device.find(resourceId='com.instagram.android:id/row_load_more_button')
            load_more_button_exists = load_more_button.exists()

            if not load_more_button_exists and screen_iterated_followers == prev_screen_iterated_followers:
                print(COLOR_OKGREEN + "Iterated exactly the same followers twice, finish." + COLOR_ENDC)

                if just_get_list:
                    return all_followers_iterated + screen_iterated_followers

                return

            need_swipe = screen_skipped_followers_count == len(screen_iterated_followers)
            list_view = device.find(resourceId='android:id/list',
                                    className='android.widget.ListView')
            if is_myself:
                print(COLOR_OKGREEN + "Need to scroll now" + COLOR_ENDC)
                list_view.scroll(DeviceFacade.Direction.TOP)
            else:
                pressed_retry = False
                if load_more_button_exists:
                    retry_button = load_more_button.child(className='android.widget.ImageView')
                    if retry_button.exists():
                        retry_button.click()
                        random_sleep()
                        pressed_retry = True

                if need_swipe and not pressed_retry:
                    print(COLOR_OKGREEN + "All followers skipped, let's do a swipe" + COLOR_ENDC)
                    list_view.swipe(DeviceFacade.Direction.BOTTOM)
                else:
                    print(COLOR_OKGREEN + "Need to scroll now" + COLOR_ENDC)
                    list_view.scroll(DeviceFacade.Direction.BOTTOM)

            all_followers_iterated += screen_iterated_followers
            prev_screen_iterated_followers.clear()
            prev_screen_iterated_followers += screen_iterated_followers
        else:
            print(COLOR_OKGREEN + "No followers were iterated, finish." + COLOR_ENDC)

            if just_get_list:
                return all_followers_iterated

            return


def _is_private_account(device):
    recycler_view = device.find(resourceId='android:id/list')
    return not recycler_view.exists()


def _interact_with_user(device,
                        is_scrapping_session,
                        username,
                        my_username,
                        likes_count,
                        on_like,
                        can_follow,
                        follow_percentage,
                        profile_filter) -> (bool, bool):
    """
    :return: (whether interaction succeed, whether @username was followed during the interaction)
    """
    if username == my_username:
        print("It's you, skip.")
        return False, False

    random_sleep()

    if not profile_filter.check_profile(device, username):
        return False, False

    if is_scrapping_session:
        if (not profile_filter.can_follow_private_or_empty()) and _is_private_account(device):
            return False, False

        return True, False

    likes_value = get_value(likes_count, "Likes count: {}", 2)
    if likes_value > 12:
        print(COLOR_FAIL + "Max number of likes per user is 12" + COLOR_ENDC)
        likes_value = 12

    coordinator_layout = device.find(resourceId='com.instagram.android:id/coordinator_root_layout')
    if coordinator_layout.exists():
        print("Scroll down to see more photos.")
        coordinator_layout.scroll(DeviceFacade.Direction.BOTTOM)

    if _is_private_account(device):
        print(COLOR_OKGREEN + "Private / empty account." + COLOR_ENDC)
        if can_follow and profile_filter.can_follow_private_or_empty():
            followed = _follow(device,
                               username,
                               follow_percentage)
        else:
            followed = False
            print(COLOR_OKGREEN + "Skip user." + COLOR_ENDC)
        return False, followed

    number_of_rows_to_use = min((likes_value * 2) // 3 + 1, 4)
    photos_indices = list(range(0, number_of_rows_to_use * 3))
    shuffle(photos_indices)
    photos_indices = photos_indices[:likes_value]
    photos_indices = sorted(photos_indices)
    for i in range(0, likes_value):
        photo_index = photos_indices[i]
        row = photo_index // 3
        column = photo_index - row * 3

        random_sleep()
        print("Open and like photo #" + str(i + 1) + " (" + str(row + 1) + " row, " + str(column + 1) + " column)")
        if not _open_photo_and_like(device, row, column, on_like):
            print(COLOR_OKGREEN + "Less than " + str(number_of_rows_to_use * 3) + " photos." + COLOR_ENDC)
            if can_follow and profile_filter.can_follow_private_or_empty():
                followed = _follow(device,
                                   username,
                                   follow_percentage)
            else:
                followed = False

            if not followed:
                print(COLOR_OKGREEN + "Skip user." + COLOR_ENDC)
            return False, followed

    if can_follow:
        return True, _follow(device, username, follow_percentage)

    return True, False


def _open_photo_and_like(device, row, column, on_like):
    def open_photo():
        # recycler_view has a className 'androidx.recyclerview.widget.RecyclerView' on modern Android versions and
        # 'android.view.View' on Android 5.0.1 and probably earlier versions
        recycler_view = device.find(resourceId='android:id/list')
        row_view = recycler_view.child(index=row + 1)
        if not row_view.exists():
            return False
        item_view = row_view.child(index=column)
        if not item_view.exists():
            return False
        item_view.click()
        return True

    if not open_photo():
        return False

    random_sleep()
    print("Double click!")
    photo_view = device.find(resourceId='com.instagram.android:id/layout_container_main',
                             className='android.widget.FrameLayout')
    photo_view.double_click()
    random_sleep()

    # If double click didn't work, set like by icon click
    try:
        # Click only button which is under the action bar and above the tab bar.
        # It fixes bugs with accidental back / home clicks.
        for like_button in device.find(resourceId='com.instagram.android:id/row_feed_button_like',
                                       className='android.widget.ImageView',
                                       selected=False):
            if is_in_interaction_rect(like_button):
                print("Double click didn't work, click on icon.")
                like_button.click()
                random_sleep()
                break
    except DeviceFacade.JsonRpcError:
        print("Double click worked successfully.")

    detect_block(device)
    on_like()
    print("Back to profile")
    device.back()
    return True


def _follow(device, username, follow_percentage):
    follow_chance = randint(1, 100)
    if follow_chance > follow_percentage:
        return False

    print("Following...")
    coordinator_layout = device.find(resourceId='com.instagram.android:id/coordinator_root_layout')
    if coordinator_layout.exists():
        coordinator_layout.scroll(DeviceFacade.Direction.TOP)

    random_sleep()

    profile_header_actions_layout = device.find(resourceId='com.instagram.android:id/profile_header_actions_top_row',
                                                className='android.widget.LinearLayout')
    if not profile_header_actions_layout.exists():
        print(COLOR_FAIL + "Cannot find profile actions." + COLOR_ENDC)
        return False

    follow_button = profile_header_actions_layout.child(classNameMatches=TEXTVIEW_OR_BUTTON_REGEX,
                                                        clickable=True,
                                                        textMatches=FOLLOW_REGEX)
    if not follow_button.exists():
        unfollow_button = profile_header_actions_layout.child(classNameMatches=TEXTVIEW_OR_BUTTON_REGEX,
                                                              clickable=True,
                                                              textMatches=UNFOLLOW_REGEX)
        if unfollow_button.exists():
            print(COLOR_OKGREEN + "You already follow @" + username + "." + COLOR_ENDC)
            return False
        else:
            print(COLOR_FAIL + "Cannot find neither Follow button, nor Unfollow button. Maybe not "
                               "English language is set?" + COLOR_ENDC)
            save_crash(device)
            switch_to_english(device)
            raise LanguageChangedException()

    follow_button.click()
    detect_block(device)
    print(COLOR_OKGREEN + "Followed @" + username + COLOR_ENDC)
    random_sleep()
    return True


def _is_follow_limit_reached(session_state, follow_limit, total_follow_limit, blogger):
    if total_follow_limit is not None:
        total_followed_count = sum(session_state.totalFollowed.values())
        if total_followed_count >= total_follow_limit:
            return True

    if follow_limit is None:
        return False

    followed_count = session_state.totalFollowed.get(blogger)
    return followed_count is not None and followed_count >= follow_limit
