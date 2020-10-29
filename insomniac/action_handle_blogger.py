from functools import partial

from insomniac.device_facade import DeviceFacade
from insomniac.interaction import interact_with_user, is_follow_limit_reached_for_source
from insomniac.navigation import search_for
from insomniac.scroll_end_detector import ScrollEndDetector
from insomniac.storage import FollowingStatus
from insomniac.utils import *

FOLLOWERS_BUTTON_ID_REGEX = 'com.instagram.android:id/row_profile_header_followers_container' \
                            '|com.instagram.android:id/row_profile_header_container_followers'


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
    interaction = partial(interact_with_user,
                          my_username=session_state.my_username,
                          likes_count=likes_count,
                          follow_percentage=follow_percentage,
                          on_like=on_like,
                          profile_filter=profile_filter,
                          is_scrapping_session=is_scrapping_session)

    is_follow_limit_reached = partial(is_follow_limit_reached_for_source,
                                      session_state=session_state,
                                      follow_limit=follow_limit,
                                      total_follow_limit=total_follow_limit,
                                      source=username)

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
        if not search_for(device, username=username):
            return False

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
    scroll_end_detector = ScrollEndDetector()
    while True:
        print("Iterate over visible followers")
        if not just_get_list:
            random_sleep()
        screen_iterated_followers = []
        screen_skipped_followers_count = 0
        scroll_end_detector.notify_new_page()

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
                scroll_end_detector.notify_username_iterated(username)

                if just_get_list:
                    continue

                if storage.is_user_in_blacklist(username):
                    print("@" + username + " is in blacklist. Skip.")
                elif not is_myself and storage.check_user_was_interacted(username):
                    print("@" + username + ": already interacted. Skip.")
                    screen_skipped_followers_count += 1
                elif is_myself and storage.check_user_was_interacted_recently(username):
                    print("@" + username + ": already interacted in the last week. Skip.")
                    screen_skipped_followers_count += 1
                elif max_nums_in_username is not None and \
                        get_count_of_nums_in_str(username) > int(max_nums_in_username):
                    print(
                        "@" + username + ": more than " + str(max_nums_in_username) + " numbers in username. Skip.")
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
            load_more_button_exists = load_more_button.exists(quick=True)

            if scroll_end_detector.is_the_end():
                if just_get_list:
                    return all_followers_iterated + screen_iterated_followers

                return

            need_swipe = screen_skipped_followers_count == len(screen_iterated_followers)
            list_view = device.find(resourceId='android:id/list',
                                    className='android.widget.ListView')
            if not list_view.exists():
                print(COLOR_FAIL + "Cannot find the list of followers. Trying to press back again." + COLOR_ENDC)
                device.back()
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
                        print("Press \"Load\" button")
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
