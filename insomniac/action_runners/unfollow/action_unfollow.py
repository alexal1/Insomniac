from enum import unique, Enum

from insomniac.actions_impl import open_user_followings, sort_followings_by_date, iterate_over_my_followings, \
    do_unfollow, FOLLOW_REGEX
from insomniac.actions_types import UnfollowAction, GetProfileAction
from insomniac.limits import process_limits
from insomniac.report import print_short_unfollow_report
from insomniac.sleeper import sleeper
from insomniac.storage import FollowingStatus
from insomniac.utils import *


def unfollow(device, on_action, storage, unfollow_restriction, sort_order, session_state, is_limit_reached, action_status):
    if not open_user_followings(device=device, username=None, on_action=on_action):
        return
    sleeper.random_sleep()
    sort_followings_by_date(device, sort_order)
    sleeper.random_sleep()

    # noinspection PyUnusedLocal
    # following_name_view is a standard callback argument
    def iteration_callback_pre_conditions(following_name, following_name_view, follow_status_button_view):
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
                print("Skip @" + following_name + ". Following status: " + following_status.name +
                      " (probably not followed by the bot...)")
                return False

        if follow_status_button_view is not None:
            following_status = storage.get_following_status(following_name)
            follow_status_from_row = follow_status_button_view.get_text()
            print("Follow-status-button text: " + follow_status_from_row + ".")
            if follow_status_from_row in FOLLOW_REGEX.split('|') or following_status == FollowingStatus.UNFOLLOWED:
                print("Skip @" + following_name + ". Following status: " + FollowingStatus.UNFOLLOWED.name
                      + "(already been unfollowed by the bot...)")
                return False

        if unfollow_restriction == UnfollowRestriction.FOLLOWED_BY_SCRIPT_NON_FOLLOWERS or \
                unfollow_restriction == UnfollowRestriction.ANY_NON_FOLLOWERS:
            if storage.is_profile_follows_me_by_cache(following_name):
                print("Skip @" + following_name + ". Following status (according to cache): "
                      + FollowingStatus.FOLLOWED.name)
                return False

        return True

    # noinspection PyUnusedLocal
    # following_name_view is a standard callback argument
    def iteration_callback(following_name, following_name_view, follow_status_button_view):
        """
        :return: True to continue unfollowing after given user, False to stop
        """
        print("Running Unfollow-action on @" + following_name)

        is_unfollow_limit_reached, unfollow_reached_source_limit, unfollow_reached_session_limit = \
            is_limit_reached(UnfollowAction(user=following_name), session_state)

        if not process_limits(is_unfollow_limit_reached, unfollow_reached_session_limit,
                              unfollow_reached_source_limit, action_status, "Unfollowing"):
            return False

        is_get_profile_limit_reached, get_profile_reached_source_limit, get_profile_reached_session_limit = \
            is_limit_reached(GetProfileAction(user=following_name), session_state)

        if not process_limits(is_get_profile_limit_reached, get_profile_reached_session_limit,
                              get_profile_reached_source_limit, action_status, "Get-Profile"):
            return False

        check_if_is_follower = unfollow_restriction == UnfollowRestriction.FOLLOWED_BY_SCRIPT_NON_FOLLOWERS or \
                               unfollow_restriction == UnfollowRestriction.ANY_NON_FOLLOWERS

        unfollowed = do_unfollow(device, session_state.my_username, following_name, storage, check_if_is_follower,
                                 following_name_view, follow_status_button_view, on_action)

        if unfollowed:
            on_action(UnfollowAction(user=following_name))
            print(COLOR_OKGREEN + f"Unfollowed @{following_name}" + COLOR_ENDC)
            print_short_unfollow_report(session_state)

        return True

    iterate_over_my_followings(device, iteration_callback, iteration_callback_pre_conditions)


@unique
class UnfollowRestriction(Enum):
    ANY = "profiles"
    FOLLOWED_BY_SCRIPT = "followed-by-bot profiles"
    FOLLOWED_BY_SCRIPT_NON_FOLLOWERS = "followed-by-bot non-followers-profiles"
    ANY_NON_FOLLOWERS = "non-followers-profiles"


def get_unfollow_restriction(followed_by_anyone, unfollow_non_followers):
    # followed_by_anyone -> unfollow_non_followers -> restriction
    unfollow_restriction_matrix = {
        True:  {True: UnfollowRestriction.ANY_NON_FOLLOWERS,
                False: UnfollowRestriction.ANY},
        False: {True: UnfollowRestriction.FOLLOWED_BY_SCRIPT_NON_FOLLOWERS,
                False: UnfollowRestriction.FOLLOWED_BY_SCRIPT}
    }
    return unfollow_restriction_matrix[followed_by_anyone][unfollow_non_followers]
