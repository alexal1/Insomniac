from functools import partial

from insomniac.actions_impl import interact_with_user, ScrollEndDetector, open_likers, iterate_over_likers, \
    is_private_account, InteractionStrategy, do_have_story
from insomniac.actions_runners import ActionState
from insomniac.actions_types import InteractAction, LikeAction, FollowAction, GetProfileAction, StoryWatchAction, \
    HashtagInteractionType
from insomniac.device_facade import DeviceFacade
from insomniac.limits import process_limits
from insomniac.navigation import search_for
from insomniac.report import print_short_report, print_interaction_types
from insomniac.sleeper import sleeper
from insomniac.storage import FollowingStatus
from insomniac.utils import *


def extract_hashtag_instructions(source):
    split_idx = source.find('-')
    if split_idx == -1:
        print("There is no special interaction-instructions for " + source + ". Working with " + source + " recent-likers.")
        return source, HashtagInteractionType.RECENT_LIKERS

    selected_instruction = None
    source_profile_name = source[:split_idx]
    interaction_instructions_str = source[split_idx+1:]

    for hashtag_instruction in HashtagInteractionType:
        if hashtag_instruction.value == interaction_instructions_str:
            selected_instruction = hashtag_instruction
            break

    if selected_instruction is None:
        print("Couldn't use interaction-instructions " + interaction_instructions_str +
              ". Working with " + source + " recent-likers.")
        selected_instruction = HashtagInteractionType.RECENT_LIKERS

    return source_profile_name, selected_instruction


def handle_hashtag(device,
                   hashtag,
                   instructions,
                   session_state,
                   likes_count,
                   stories_count,
                   follow_percentage,
                   like_percentage,
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
        elif storage.check_user_was_filtered(liker_username):
            print("@" + liker_username + ": already filtered in past. Skip.")
            return False
        elif storage.check_user_was_interacted(liker_username):
            print("@" + liker_username + ": already interacted. Skip.")
            return False
        elif is_passed_filters is not None:
            if not is_passed_filters(device, liker_username, ['BEFORE_PROFILE_CLICK']):
                storage.add_filtered_user(liker_username)
                return False

        return True

    def interact_with_profile(liker_username, liker_username_view):
        is_interact_limit_reached, interact_reached_source_limit, interact_reached_session_limit = \
            is_limit_reached(InteractAction(source=interaction_source, user=liker_username, succeed=True), session_state)

        if not process_limits(is_interact_limit_reached, interact_reached_session_limit,
                              interact_reached_source_limit, action_status, "Interaction"):
            return False

        is_get_profile_limit_reached, get_profile_reached_source_limit, get_profile_reached_session_limit = \
            is_limit_reached(GetProfileAction(user=liker_username), session_state)

        if not process_limits(is_get_profile_limit_reached, get_profile_reached_session_limit,
                              get_profile_reached_source_limit, action_status, "Get-Profile"):
            return False

        print("@" + liker_username + ": interact")
        liker_username_view.click()
        on_action(GetProfileAction(user=liker_username))

        if is_passed_filters is not None:
            if not is_passed_filters(device, liker_username):
                storage.add_filtered_user(liker_username)
                # Continue to next follower
                print("Back to followers list")
                device.back()
                return True

        is_like_limit_reached, like_reached_source_limit, like_reached_session_limit = \
            is_limit_reached(LikeAction(source=interaction_source, user=liker_username), session_state)

        is_follow_limit_reached, follow_reached_source_limit, follow_reached_session_limit = \
            is_limit_reached(FollowAction(source=interaction_source, user=liker_username), session_state)

        is_watch_limit_reached, watch_reached_source_limit, watch_reached_session_limit = \
            is_limit_reached(StoryWatchAction(user=liker_username), session_state)

        is_private = is_private_account(device)
        if is_private:
            print("@" + liker_username + ": Private account - images wont be liked.")

        do_have_stories = do_have_story(device)
        if not do_have_stories:
            print("@" + liker_username + ": seems there are no stories to be watched.")

        is_likes_enabled = likes_count != '0'
        is_stories_enabled = stories_count != '0'
        is_follow_enabled = follow_percentage != 0

        likes_value = get_value(likes_count, "Likes count: {}", 2, max_count=12)
        stories_value = get_value(stories_count, "Stories to watch: {}", 1)

        can_like = not is_like_limit_reached and not is_private and likes_value > 0
        can_follow = (not is_follow_limit_reached) and storage.get_following_status(liker_username) == FollowingStatus.NONE and follow_percentage > 0
        can_watch = (not is_watch_limit_reached) and do_have_stories and stories_value > 0
        can_interact = can_like or can_follow or can_watch

        if not can_interact:
            print("@" + liker_username + ": Cant be interacted (due to limits / already followed). Skip.")
            storage.add_interacted_user(liker_username, followed=False)
            on_action(InteractAction(source=interaction_source, user=liker_username, succeed=False))
        else:
            print_interaction_types(liker_username, can_like, can_follow, can_watch)
            interaction_strategy = InteractionStrategy(do_like=can_like,
                                                       do_follow=can_follow,
                                                       do_story_watch=can_watch,
                                                       likes_count=likes_value,
                                                       follow_percentage=follow_percentage,
                                                       like_percentage=like_percentage,
                                                       stories_count=stories_value)

            is_liked, is_followed, is_watch = interaction(username=liker_username,
                                                          interaction_strategy=interaction_strategy)
            if is_liked or is_followed or is_watch:
                storage.add_interacted_user(liker_username, followed=is_followed)
                on_action(InteractAction(source=interaction_source, user=liker_username, succeed=True))
                print_short_report(interaction_source, session_state)
            else:
                storage.add_interacted_user(liker_username, followed=False)
                on_action(InteractAction(source=interaction_source, user=liker_username, succeed=False))

        can_continue = True

        if ((is_like_limit_reached and is_likes_enabled) or not is_likes_enabled) and \
                ((is_follow_limit_reached and is_follow_enabled) or not is_follow_enabled) and \
                ((is_watch_limit_reached and is_stories_enabled) or not is_stories_enabled):
            # If one of the limits reached for source-limit, move to next source
            if (like_reached_source_limit is not None and like_reached_session_limit is None) or \
                    (follow_reached_source_limit is not None and follow_reached_session_limit is None):
                can_continue = False
                action_status.set_limit(ActionState.SOURCE_LIMIT_REACHED)

            # If all of the limits reached for session-limit, finish the session
            if ((like_reached_session_limit is not None and is_likes_enabled) or not is_likes_enabled) and \
                    ((follow_reached_session_limit is not None and is_follow_enabled) or not is_follow_enabled):
                can_continue = False
                action_status.set_limit(ActionState.SESSION_LIMIT_REACHED)

        print("Back to followers list")
        device.back()

        return can_continue

    extract_hashtag_profiles_and_interact(device,
                                          hashtag,
                                          instructions,
                                          interact_with_profile,
                                          pre_conditions,
                                          on_action)


def extract_hashtag_profiles_and_interact(device,
                                          hashtag,
                                          instructions,
                                          iteration_callback,
                                          iteration_callback_pre_conditions,
                                          on_action):
    print("Interacting with #{0}-{1}".format(hashtag, instructions.value))

    if not search_for(device, hashtag=hashtag, on_action=on_action):
        return

    # Switch to Recent tab
    if instructions == HashtagInteractionType.RECENT_LIKERS:
        print("Switching to Recent tab")
        tab_layout = device.find(resourceId='com.instagram.android:id/tab_layout',
                                 className='android.widget.LinearLayout')
        if tab_layout.exists():
            tab_layout.child(index=1).click()
        else:
            print("Can't Find recent tab. Interacting with Popular.")

        sleeper.random_sleep()

    # Open first post
    print("Opening the first post")
    first_post_view = device.find(resourceId='com.instagram.android:id/image_button',
                                  className='android.widget.ImageView',
                                  index=1)
    first_post_view.click()
    sleeper.random_sleep()

    posts_list_view = device.find(resourceId='android:id/list',
                                  className='androidx.recyclerview.widget.RecyclerView')
    posts_end_detector = ScrollEndDetector(repeats_to_end=2)

    def pre_conditions(liker_username, liker_username_view):
        posts_end_detector.notify_username_iterated(liker_username)
        return iteration_callback_pre_conditions(liker_username, liker_username_view)

    while True:
        if not open_likers(device):
            print(COLOR_OKGREEN + "No likes, let's scroll down." + COLOR_ENDC)
            posts_list_view.scroll(DeviceFacade.Direction.BOTTOM)
            continue

        print("List of likers is opened.")
        posts_end_detector.notify_new_page()
        sleeper.random_sleep()

        iterate_over_likers(device, iteration_callback, pre_conditions)

        if posts_end_detector.is_the_end():
            break
        else:
            posts_list_view.scroll(DeviceFacade.Direction.BOTTOM)
