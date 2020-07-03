from functools import partial
from random import shuffle
import random

import uiautomator

from storage import FollowingStatus
from utils import *
from action_handle_blogger import _interact_with_user, _scroll_to_bottom


def handle_hashtag(device,
                   hashtag,
                   likes_count,
                   follow_percentage,
                   storage,
                   on_like,
                   on_interaction):
    interaction = partial(_interact_with_user,
                          likes_count=likes_count,
                          follow_percentage=follow_percentage,
                          on_like=on_like)

    if not _open_post_hashtags(device, hashtag):
        return
    _iterate_over_posts(device, interaction, storage, on_interaction)

def _open_post_hashtags(device, hashtag):
    if hashtag is None:
        print("Enter own hashtag search")
        tab_bar = device(resourceId='com.instagram.android:id/tab_bar', className='android.widget.LinearLayout')
        search_button = tab_bar.child(index=1)

        # Two clicks to reset tab content
        search_button.click.wait()
    else:
        print("Press search")
        tab_bar = device(resourceId='com.instagram.android:id/tab_bar', className='android.widget.LinearLayout')
        search_button = tab_bar.child(index=1)

        # Two clicks to reset tab content
        search_button.click.wait()
        search_button.click.wait()

        print("Open hashtag #" + hashtag)
        search_edit_text = device(resourceId='com.instagram.android:id/action_bar_search_edit_text',
                                  className='android.widget.EditText')
        search_edit_text.set_text(hashtag)

        search_hashtag_button = device(resourceId='com.instagram.android:id/fixed_tabbar_view',
                            className='android.widget.FrameLayout').child(index=2)
        search_hashtag_button.click.wait()

        device.wait.idle()
        hashtag_view = device(resourceId='com.instagram.android:id/row_hashtag_textview_tag_name',
                               className='android.widget.TextView',
                               text="#" + hashtag)

        if not hashtag_view.exists:
            print_timeless(COLOR_FAIL + "Cannot find hashtag #" + hashtag + ", abort." + COLOR_ENDC)
            return False

        hashtag_view.click.wait()

        print("Open #" + hashtag + " recent posts")
        hashtag_type = device(resourceId='com.instagram.android:id/tab_layout',
                                  className='android.widget.LinearLayout').child(index=1)
        hashtag_type.click.wait()

    return True

def open_photo(device,index_ran):
        # recycler_view has a className 'androidx.recyclerview.widget.RecyclerView' on modern Android versions and
        # 'android.view.View' on Android 5.0.1 and probably earlier versions
        recycler_view = device(resourceId='com.instagram.android:id/recycler_view',
                                className='androidx.recyclerview.widget.RecyclerView')
        item_view = recycler_view.child(index=index_ran)
        item_view.click.wait()


def _iterate_over_posts(device, interaction, storage, on_interaction):
    #random up to 12 because min show on screen intially is 12 the max is 20
    interactions_count = 0
    iterations = randint(2,12)
    for x in range(2,iterations):

        open_photo(device,x) 
        profile_check = device(resourceId='com.instagram.android:id/row_feed_photo_profile_imageview',
                                className='android.widget.ImageView')
        profile_check.click.wait()
        
        profile_name = device(resourceId='com.instagram.android:id/action_bar_textview_title',
                                className='android.widget.TextView')
        username = profile_name.text
        if storage.check_user_was_interacted(username):
            print("@" + username + ": already interacted. Skip.")
            device.press.back()
            device.press.back()
        elif storage.check_user_was_interacted_recently(username):
            print("@" + username + ": already interacted in the last week. Skip.")
            device.press.back()
            device.press.back()
        else:
            print("@" + username + ": interact")
            #user_name_view.click.wait()

            can_follow = storage.get_following_status(username) == FollowingStatus.NONE
            interaction_succeed, followed = interaction(device, username=username, can_follow=can_follow)
            storage.add_interacted_user(username, followed=followed)
            interactions_count += 1
            can_continue = on_interaction(succeed=interaction_succeed,
                                            followed=followed,
                                            count=interactions_count)

            if not can_continue:
                return

            print("Back to hashtag list")
            device.press.back()
            device.press.back()
    
