from insomniac.counters_parser import parse
from insomniac.utils import *


def _has_business_category(device):
    business_category_view = device.find(resourceId='com.instagram.android:id/profile_header_business_category',
                                         className='android.widget.TextView')
    return business_category_view.exists()


def _get_posts_count(device):
    posts_count = 0
    posts_count_text_view = device.find(
        resourceId='com.instagram.android:id/row_profile_header_textview_post_count',
        className='android.widget.TextView'
    )
    if posts_count_text_view.exists():
        posts_count_text = posts_count_text_view.get_text()
        if posts_count_text:
            posts_count = parse(device, posts_count_text)
        else:
            print_timeless(COLOR_FAIL + "Cannot get posts count text, default is " + str(posts_count) +
                           COLOR_ENDC)
    else:
        print_timeless(COLOR_FAIL + "Cannot find posts count view, default is " + str(posts_count) + COLOR_ENDC)

    return posts_count


def _get_followers(device):
    followers = 0
    followers_text_view = device.find(
        resourceId='com.instagram.android:id/row_profile_header_textview_followers_count',
        className='android.widget.TextView'
    )
    if followers_text_view.exists():
        followers_text = followers_text_view.get_text()
        if followers_text:
            followers = parse(device, followers_text)
        else:
            print_timeless(COLOR_FAIL + "Cannot get followers count text, default is " + str(followers) +
                           COLOR_ENDC)
    else:
        print_timeless(COLOR_FAIL + "Cannot find followers count view, default is " + str(followers) + COLOR_ENDC)

    return followers


def _get_followings(device):
    followings = 0
    followings_text_view = device.find(
        resourceId='com.instagram.android:id/row_profile_header_textview_following_count',
        className='android.widget.TextView')
    if followings_text_view.exists():
        followings_text = followings_text_view.get_text()
        if followings_text:
            followings = parse(device, followings_text)
        else:
            print_timeless(COLOR_FAIL + "Cannot get followings count text, default is " + str(followings) +
                           COLOR_ENDC)
    else:
        print_timeless(COLOR_FAIL + "Cannot find followings count view, default is " + str(followings) + COLOR_ENDC)

    return followings
