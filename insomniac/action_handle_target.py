from functools import partial

from insomniac.actions_impl import interact_with_user, InteractionStrategy, is_private_account, open_user
from insomniac.actions_runners import ActionState
from insomniac.actions_types import LikeAction, FollowAction, InteractAction, GetProfileAction
from insomniac.limits import process_limits
from insomniac.storage import FollowingStatus
from insomniac.utils import *


def handle_target(device,
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

    def pre_conditions(target_name, target_name_view):
        if storage.is_user_in_blacklist(target_name):
            print("@" + target_name + " is in blacklist. Skip.")
            return False
        elif storage.check_user_was_interacted(target_name):
            print("@" + target_name + ": already interacted. Skip.")
            return False
        elif is_passed_filters is not None:
            if not is_passed_filters(device, target_name, ['BEFORE_PROFILE_CLICK']):
                return False

        return True

    def interact_with_target(target_name, target_name_view):
        is_interact_limit_reached, interact_reached_source_limit, interact_reached_session_limit = \
            is_limit_reached(InteractAction(source=target_name, user=target_name, succeed=True), session_state)

        if not process_limits(is_interact_limit_reached, interact_reached_session_limit,
                              interact_reached_source_limit, action_status, "Interaction"):
            return

        is_get_profile_limit_reached, get_profile_reached_source_limit, get_profile_reached_session_limit = \
            is_limit_reached(GetProfileAction(user=target_name), session_state)

        if not process_limits(is_get_profile_limit_reached, get_profile_reached_session_limit,
                              get_profile_reached_source_limit, action_status, "Get-Profile"):
            return

        print("@" + target_name + ": interact")

        if is_passed_filters is not None:
            if not is_passed_filters(device, target_name):
                print("Moving to next target")
                return

        is_like_limit_reached, like_reached_source_limit, like_reached_session_limit = \
            is_limit_reached(LikeAction(source=target_name, user=target_name), session_state)

        is_follow_limit_reached, follow_reached_source_limit, follow_reached_session_limit = \
            is_limit_reached(FollowAction(source=target_name, user=target_name), session_state)

        is_private = is_private_account(device)
        if is_private:
            print("@" + target_name + ": Private account - images wont be liked.")

        can_like = not is_like_limit_reached and not is_private
        can_follow = (not is_follow_limit_reached) and storage.get_following_status(username) == FollowingStatus.NONE
        can_interact = can_like or can_follow

        if not can_interact:
            print("@" + target_name + ": Cant be interacted (due to limits / already followed). Skip.")
            storage.add_interacted_user(target_name, followed=False)
            on_action(InteractAction(source=target_name, user=target_name, succeed=False))
        else:
            print("@" + target_name + "interaction: going to {}{}{}.".format("like" if can_like else "",
                                                                             " and " if can_like and can_follow else "",
                                                                             "follow" if can_follow else ""))

            interaction_strategy = InteractionStrategy(do_like=can_like,
                                                       do_follow=can_follow,
                                                       likes_count=likes_count,
                                                       follow_percentage=follow_percentage)

            is_liked, is_followed = interaction(username=target_name, interaction_strategy=interaction_strategy)
            if is_liked or is_followed:
                storage.add_interacted_user(target_name, followed=is_followed)
                on_action(InteractAction(source=target_name, user=target_name, succeed=True))
            else:
                storage.add_interacted_user(target_name, followed=False)
                on_action(InteractAction(source=target_name, user=target_name, succeed=False))

        if is_like_limit_reached and is_follow_limit_reached:
            # If one of the limits reached for source-limit, move to next source
            if like_reached_source_limit is not None or follow_reached_source_limit is not None:
                action_status.set_limit(ActionState.SOURCE_LIMIT_REACHED)

            # If both of the limits reached for session-limit, finish the session
            if like_reached_session_limit is not None and follow_reached_session_limit is not None:
                action_status.set_limit(ActionState.SESSION_LIMIT_REACHED)

        print("Moving to next target")
        return

    if is_myself:
        return

    if pre_conditions(username, None):
        if open_user(device=device, username=username, refresh=False, on_action=on_action):
            interact_with_target(username, None)
