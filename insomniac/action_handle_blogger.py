from functools import partial

from insomniac.actions_impl import interact_with_user, open_user_followers, \
    scroll_to_bottom, iterate_over_followers, InteractionStrategy, is_private_account
from insomniac.actions_runners import ActionState
from insomniac.actions_types import LikeAction, FollowAction, InteractAction
from insomniac.storage import FollowingStatus
from insomniac.utils import *

FOLLOWERS_BUTTON_ID_REGEX = 'com.instagram.android:id/row_profile_header_followers_container' \
                            '|com.instagram.android:id/row_profile_header_container_followers'


def handle_blogger(device,
                   username,
                   session_state,
                   likes_count,
                   follow_percentage,
                   storage,
                   on_action,
                   is_limit_reached,
                   is_passed_filters,
                   action_status):
    is_myself = username == session_state.my_username
    interaction = partial(interact_with_user,
                          device=device,
                          user_source=username,
                          my_username=session_state.my_username,
                          on_action=on_action)

    if not open_user_followers(device, username):
        return

    if is_myself:
        scroll_to_bottom(device)

    def pre_conditions(follower_name, follower_name_view):
        if storage.is_user_in_blacklist(follower_name):
            print("@" + follower_name + " is in blacklist. Skip.")
            return False
        elif not is_myself and storage.check_user_was_interacted(follower_name):
            print("@" + follower_name + ": already interacted. Skip.")
            return False
        elif is_myself and storage.check_user_was_interacted_recently(follower_name):
            print("@" + follower_name + ": already interacted in the last week. Skip.")
            return False
        elif is_passed_filters is not None:
            if not is_passed_filters(device, follower_name, ['BEFORE_PROFILE_CLICK']):
                return False

        return True

    def interact_with_follower(follower_name, follower_name_view):
        is_interact_limit_reached, interact_reached_source_limit, interact_reached_session_limit = \
            is_limit_reached(InteractAction(source=username, user=follower_name, succeed=True), session_state)

        if is_interact_limit_reached:
            # Reached interaction session limit, stop the action
            if interact_reached_session_limit is not None:
                print(COLOR_OKBLUE + "Interaction session-limit {0} has been reached. Stopping activity."
                      .format(interact_reached_session_limit) + COLOR_ENDC)
                action_status.set_limit(ActionState.SESSION_LIMIT_REACHED)
            else:
                print(COLOR_OKBLUE + "Interaction source-limit {0} has been reached. Moving to next source."
                      .format(interact_reached_session_limit) + COLOR_ENDC)
                action_status.set_limit(ActionState.SOURCE_LIMIT_REACHED)

            return False

        print("@" + follower_name + ": interact")
        follower_name_view.click()

        if is_passed_filters is not None:
            if not is_passed_filters(device, follower_name):
                return False

        is_like_limit_reached, like_reached_source_limit, like_reached_session_limit = \
            is_limit_reached(LikeAction(source=username, user=follower_name), session_state)

        is_follow_limit_reached, follow_reached_source_limit, follow_reached_session_limit = \
            is_limit_reached(FollowAction(source=username, user=follower_name), session_state)

        is_private = is_private_account(device)
        if is_private:
            print("@" + follower_name + ": Private account - images wont be liked.")

        can_like = not is_like_limit_reached and not is_private
        can_follow = (not is_follow_limit_reached) and storage.get_following_status(username) == FollowingStatus.NONE
        can_interact = can_like or can_follow

        if not can_interact:
            print("@" + follower_name + ": Cant be interacted (due to limits / already followed). Skip.")
        else:
            print("@" + follower_name + "interaction: going to {}{}{}.".format("like" if can_like else "",
                                                                               " and " if can_like and can_follow else "",
                                                                               "follow" if can_follow else ""))

            interaction_strategy = InteractionStrategy(do_like=can_like,
                                                       do_follow=can_follow,
                                                       likes_count=likes_count,
                                                       follow_percentage=follow_percentage)

            is_liked, is_followed = interaction(username=follower_name, interaction_strategy=interaction_strategy)
            if is_liked or is_followed:
                storage.add_interacted_user(follower_name, followed=is_followed)
                on_action(InteractAction(source=username, user=follower_name, succeed=True))
            else:
                on_action(InteractAction(source=username, user=follower_name, succeed=False))

        can_continue = True

        if is_like_limit_reached and is_follow_limit_reached:
            # If one of the limits reached for source-limit, move to next source
            if like_reached_source_limit is not None or follow_reached_source_limit is not None:
                can_continue = False
                action_status.set_limit(ActionState.SOURCE_LIMIT_REACHED)

            # If both of the limits reached for session-limit, finish the session
            if like_reached_session_limit is not None and follow_reached_session_limit is not None:
                can_continue = False
                action_status.set_limit(ActionState.SESSION_LIMIT_REACHED)

        print("Back to followers list")
        device.back()

        return can_continue

    iterate_over_followers(device, is_myself, interact_with_follower, pre_conditions)
