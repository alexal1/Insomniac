from functools import partial

from insomniac.actions_impl import interact_with_user, PostsEndDetector, open_likers, iterate_over_likers, \
    is_private_account, InteractionStrategy
from insomniac.actions_runners import ActionState
from insomniac.actions_types import InteractAction, LikeAction, FollowAction
from insomniac.device_facade import DeviceFacade
from insomniac.navigation import search_for
from insomniac.storage import FollowingStatus
from insomniac.utils import *


def handle_hashtag(device,
                   hashtag,
                   session_state,
                   likes_count,
                   follow_percentage,
                   storage,
                   on_action,
                   is_limit_reached,
                   is_passed_filters,
                   action_status):
    interaction_source = "#{0}".format(hashtag)
    interaction = partial(interact_with_user,
                          device=device,
                          user_source=interaction_source,
                          my_username=session_state.my_username,
                          on_action=on_action)

    def pre_conditions(liker_username, liker_username_view):
        if storage.is_user_in_blacklist(liker_username):
            print("@" + liker_username + " is in blacklist. Skip.")
            return False
        elif storage.check_user_was_interacted(liker_username):
            print("@" + liker_username + ": already interacted. Skip.")
            return False
        elif is_passed_filters is not None:
            if not is_passed_filters(device, liker_username, ['NO_DEVICE']):
                return False

        return True

    def interact_with_liker(liker_username, liker_username_view):
        is_interact_limit_reached, interact_reached_source_limit, interact_reached_session_limit = \
            is_limit_reached(InteractAction(source=interaction_source, user=liker_username, succeed=True), session_state)

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

        print("@" + liker_username + ": interact")
        liker_username_view.click()

        if is_passed_filters is not None:
            if not is_passed_filters(device, liker_username):
                return False

        is_like_limit_reached, like_reached_source_limit, like_reached_session_limit = \
            is_limit_reached(LikeAction(source=interaction_source, user=liker_username), session_state)

        is_follow_limit_reached, follow_reached_source_limit, follow_reached_session_limit = \
            is_limit_reached(FollowAction(source=interaction_source, user=liker_username), session_state)

        is_private = is_private_account(device)
        if is_private:
            print("@" + liker_username + ": Private account - images wont be liked.")

        can_like = not is_like_limit_reached and not is_private
        can_follow = (not is_follow_limit_reached) and storage.get_following_status(liker_username) == FollowingStatus.NONE
        can_interact = can_like or can_follow

        if not can_interact:
            print("@" + liker_username + ": Cant be interacted (due to limits / already followed). Skip.")
        else:
            print("@" + liker_username + "interaction: going to {}{}{}.".format("like" if can_like else "",
                                                                                " and " if can_like and can_follow else "",
                                                                                "follow" if can_follow else ""))

            interaction_strategy = InteractionStrategy(do_like=can_like,
                                                       do_follow=can_follow,
                                                       likes_count=likes_count,
                                                       follow_percentage=follow_percentage)

            is_liked, is_followed = interaction(username=liker_username, interaction_strategy=interaction_strategy)
            if is_liked or is_followed:
                storage.add_interacted_user(liker_username, followed=is_followed)
                on_action(InteractAction(source=interaction_source, user=liker_username, succeed=True))
            else:
                on_action(InteractAction(source=interaction_source, user=liker_username, succeed=False))

        can_continue = True

        if is_like_limit_reached and is_follow_limit_reached:
            # If ont of the limits reached for source-limit, move to next source
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

    extract_hashtag_likers_and_interact(device, hashtag, interact_with_liker, pre_conditions)


def extract_hashtag_likers_and_interact(device, hashtag, iteration_callback, iteration_callback_pre_conditions):
    print("Interacting with #{0} recent-likers".format(hashtag))

    if not search_for(device, hashtag=hashtag):
        return

    # Switch to Recent tab
    print("Switching to Recent tab")
    tab_layout = device.find(resourceId='com.instagram.android:id/tab_layout',
                             className='android.widget.LinearLayout')
    tab_layout.child(index=1).click()
    random_sleep()

    # Open first post
    print("Opening the first post")
    first_post_view = device.find(resourceId='com.instagram.android:id/image_button',
                                  className='android.widget.ImageView',
                                  index=1)
    first_post_view.click()
    random_sleep()

    posts_list_view = device.find(resourceId='android:id/list',
                                  className='androidx.recyclerview.widget.RecyclerView')
    posts_end_detector = PostsEndDetector()

    def pre_conditions(liker_username, liker_username_view):
        posts_end_detector.notify_username_iterated(liker_username)
        return iteration_callback_pre_conditions(liker_username, liker_username_view)

    while True:
        if not open_likers(device):
            print(COLOR_OKGREEN + "No likes, let's scroll down." + COLOR_ENDC)
            posts_list_view.scroll(DeviceFacade.Direction.BOTTOM)
            continue

        print("List of likers is opened.")
        posts_end_detector.notify_likers_opened()
        random_sleep()

        iterate_over_likers(device, iteration_callback, pre_conditions)

        if posts_end_detector.are_posts_ended():
            print(COLOR_OKGREEN + f"Scrolled #{hashtag} to the end, finish." + COLOR_ENDC)
            break
        else:
            posts_list_view.scroll(DeviceFacade.Direction.BOTTOM)
