from functools import partial
from random import shuffle

import uiautomator

from utils import *


def handle_blogger(device,
                   username,
                   likes_count,
                   storage,
                   on_like,
                   on_interaction):
    interaction = partial(_interact_with_user, likes_count=likes_count, on_like=on_like)

    _open_user_followers(device, username)
    _iterate_over_followers(device, interaction, storage, on_interaction)


def _open_user_followers(device, username):
    print("Press search")
    tab_bar = device(resourceId='com.instagram.android:id/tab_bar', className='android.widget.LinearLayout')
    search_button = tab_bar.child(index=1)
    search_button.click.wait()

    print("Open user @" + username)
    search_edit_text = device(resourceId='com.instagram.android:id/action_bar_search_edit_text',
                              className='android.widget.EditText')
    search_edit_text.set_text(username)
    search_results_list = device(resourceId='android:id/list',
                                 className='android.widget.ListView')
    search_first_result = search_results_list.child(index=0)
    search_first_result.click.wait()

    print("Open @" + username + " followers")
    followers_button = device(resourceId='com.instagram.android:id/row_profile_header_followers_container',
                              className='android.widget.LinearLayout')
    followers_button.click.wait()


def _iterate_over_followers(device, interaction, storage, on_interaction):
    interactions_count = 0
    full_interacted_screens_count = 0

    while True:
        print("Iterate over visible followers")
        screen_iterated_followers = 0
        screen_interacted_followers = 0

        for item in device(resourceId='com.instagram.android:id/follow_list_container',
                           className='android.widget.LinearLayout'):
            try:
                user_info_view = item.child(index=1)
                user_name_view = user_info_view.child(index=0).child()
                username = user_name_view.text
            except uiautomator.JsonRPCError:
                print(COLOR_OKBLUE + "Probably reached end of the screen." + COLOR_ENDC)
                break

            screen_iterated_followers += 1
            if storage.check_user_was_interacted(username):
                print("@" + username + ": already interacted. Skip.")
            else:
                print("@" + username + ": interact")
                screen_interacted_followers += 1
                item.click.wait()

                interaction_succeed = interaction(device)
                storage.add_interacted_user(username)
                interactions_count += 1
                can_continue = on_interaction(succeed=interaction_succeed, count=interactions_count)

                if not can_continue:
                    return

                print("Back to followers list")
                device.press.back()

        if screen_iterated_followers == 0:
            print(COLOR_OKBLUE + "No followers were iterated, finish." + COLOR_ENDC)
            return

        list_view = device(resourceId='android:id/list',
                           className='android.widget.ListView')

        if screen_interacted_followers > 0:
            full_interacted_screens_count = 0
            print(COLOR_OKBLUE + "Need to scroll now" + COLOR_ENDC)
            list_view.scroll.toEnd(max_swipes=1)
        else:
            full_interacted_screens_count += 1
            swipes_count = full_interacted_screens_count**2
            print(COLOR_OKBLUE + "All followers on the screen were interacted already." + COLOR_ENDC)
            print(COLOR_OKBLUE + "Scrolling " + str(swipes_count) + " times." + COLOR_ENDC)
            for i in range(full_interacted_screens_count):
                list_view.scroll.toEnd(max_swipes=1)


def _interact_with_user(device, likes_count, on_like):
    if likes_count > 6:
        print(COLOR_FAIL + "Max number of likes per user is 6" + COLOR_ENDC)
        likes_count = 6

    random_sleep()
    photos_indices = [0, 1, 2, 3, 4, 5]
    shuffle(photos_indices)
    for i in range(0, likes_count):
        photo_index = photos_indices[i]
        row = photo_index // 3
        column = photo_index - row * 3

        print("Open and like photo #" + str(i + 1) + " (" + str(row + 1) + " row, " + str(column + 1) + " column)")
        if not _open_photo_and_like(device, row, column, on_like):
            return False

    return True


def _open_photo_and_like(device, row, column, on_like):
    def open_photo():
        recycler_view = device(resourceId='android:id/list',
                               className='androidx.recyclerview.widget.RecyclerView')
        row_view = recycler_view.child(index=row + 1)
        item_view = row_view.child(index=column)
        item_view.click.wait()

    try:
        open_photo()
    except uiautomator.JsonRPCError:
        print(COLOR_WARNING + "Probably need to scroll." + COLOR_ENDC)
        _scroll_profile(device)
        try:
            open_photo()
        except uiautomator.JsonRPCError:
            print(COLOR_WARNING + "Less than 6 photos / account is private. Skip user." + COLOR_ENDC)
            return False

    random_sleep()
    print("Double click!")
    double_click(device,
                 resourceId='com.instagram.android:id/layout_container_main',
                 className='android.widget.FrameLayout')
    random_sleep()

    action_bar = device(resourceId='com.instagram.android:id/action_bar_container',
                        className='android.widget.FrameLayout')
    action_bar_bottom = action_bar.bounds['bottom']

    # If double click didn't work, set like by icon click
    try:
        # Click only button which is under the action bar. It fixes bug with accidental back icon click
        for like_button in device(resourceId='com.instagram.android:id/row_feed_button_like',
                                  className='android.widget.ImageView',
                                  selected=False):
            like_button_top = like_button.bounds['top']
            if like_button_top > action_bar_bottom:
                print("Double click didn't work, click on icon.")
                like_button.click()
                random_sleep()
    except uiautomator.JsonRPCError:
        print("Double click worked successfully.")

    on_like()
    print("Back to profile")
    device.press.back()
    return True


def _scroll_profile(device):
    tab_bar = device(resourceId='com.instagram.android:id/tab_bar',
                     className='android.widget.LinearLayout')

    x1 = (tab_bar.bounds['right'] - tab_bar.bounds['left']) / 2
    y1 = tab_bar.bounds['top'] - 1

    vertical_offset = tab_bar.bounds['right'] - tab_bar.bounds['left']

    x2 = x1
    y2 = y1 - vertical_offset

    device.swipe(x1, y1, x2, y2)
