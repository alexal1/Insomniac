from enum import unique, Enum

from insomniac.actions_impl import open_user_followings, sort_followings_by_date, iterate_over_followings, do_unfollow
from insomniac.actions_runners import ActionState
from insomniac.actions_types import UnfollowAction
from insomniac.storage import FollowingStatus
from insomniac.utils import *

FOLLOWING_BUTTON_ID_REGEX = 'com.instagram.android:id/row_profile_header_following_container' \
                            '|com.instagram.android:id/row_profile_header_container_following'
TEXTVIEW_OR_BUTTON_REGEX = 'android.widget.TextView|android.widget.Button'


def unfollow(device, on_action, storage, unfollow_restriction, session_state, is_limit_reached, action_status):
    if not open_user_followings(device, None):
        return

    sort_followings_by_date(device)
    random_sleep()

    # noinspection PyUnusedLocal
    # following_name_view is a standard callback argument
    def iteration_callback_pre_conditions(following_name, following_name_view):
        """
        :return: True to start unfollowing for given user, False to skip
        """
        if storage.is_user_in_whitelist(following_name):
            print(f"@{following_name} is in whitelist. Skip.")
            return False

        if unfollow_restriction == UnfollowRestriction.FOLLOWED_BY_SCRIPT or \
                unfollow_restriction == UnfollowRestriction.FOLLOWED_BY_SCRIPT_NON_FOLLOWERS:
            following_status = storage.get_following_status(following_name)
            if not following_status == FollowingStatus.FOLLOWED:
                print("Skip @" + following_name + ". Following status: " + following_status.name + ".")
                return False

        if unfollow_restriction == UnfollowRestriction.ANY:
            following_status = storage.get_following_status(following_name)
            if following_status == FollowingStatus.UNFOLLOWED:
                print("Skip @" + following_name + ". Following status: " + following_status.name + ".")
                return False

        return True

    # noinspection PyUnusedLocal
    # following_name_view is a standard callback argument
    def iteration_callback(following_name, following_name_view):
        """
        :return: True to continue unfollowing after given user, False to stop
        """
        print("Unfollow @" + following_name)

        is_interact_limit_reached, interact_reached_source_limit, interact_reached_session_limit = \
            is_limit_reached(UnfollowAction(user=following_name), session_state)

        if is_interact_limit_reached:
            # Reached interaction session limit, stop the action
            if interact_reached_session_limit is not None:
                print(COLOR_OKBLUE + "Unfollowing session-limit {0} has been reached. Stopping activity."
                      .format(interact_reached_session_limit) + COLOR_ENDC)
                action_status.set_limit(ActionState.SESSION_LIMIT_REACHED)
            else:
                print(COLOR_OKBLUE + "Unfollowing source-limit {0} has been reached. Stopping activity."
                      .format(interact_reached_session_limit) + COLOR_ENDC)
                action_status.set_limit(ActionState.SOURCE_LIMIT_REACHED)
            return False

        check_if_is_follower = unfollow_restriction == UnfollowRestriction.FOLLOWED_BY_SCRIPT_NON_FOLLOWERS
        unfollowed = do_unfollow(device, following_name, session_state.my_username, check_if_is_follower)

        if unfollowed:
            storage.add_interacted_user(following_name, unfollowed=True)
            on_action(UnfollowAction(user=following_name))

        return True

    iterate_over_followings(device, iteration_callback, iteration_callback_pre_conditions)


@unique
class UnfollowRestriction(Enum):
    ANY = 0
    FOLLOWED_BY_SCRIPT = 1
    FOLLOWED_BY_SCRIPT_NON_FOLLOWERS = 2
