from enum import unique, Enum

from insomniac.actions_impl import open_user_followings, sort_followings_by_date, iterate_over_followings, do_unfollow
from insomniac.actions_types import UnfollowAction, GetProfileAction
from insomniac.limits import process_limits
from insomniac.sleeper import sleeper
from insomniac.storage import FollowingStatus
from insomniac.utils import *


def unfollow(device, on_action, storage, unfollow_restriction, session_state, is_limit_reached, action_status):
    if not open_user_followings(device=device, username=None, on_action=on_action):
        return
    sleeper.random_sleep()
    sort_followings_by_date(device)
    sleeper.random_sleep()

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

        if unfollow_restriction == UnfollowRestriction.ANY or \
                unfollow_restriction == UnfollowRestriction.ANY_NON_FOLLOWERS:
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
        unfollowed = do_unfollow(device, following_name, session_state.my_username, check_if_is_follower, on_action)

        if unfollowed:
            storage.add_interacted_user(following_name, unfollowed=True)
            on_action(UnfollowAction(user=following_name))

        return True

    iterate_over_followings(device, iteration_callback, iteration_callback_pre_conditions)


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
