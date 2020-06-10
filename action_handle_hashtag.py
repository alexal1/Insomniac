from functools import partial
from utils import *


def handle_hashtag(device,
                   hashtag,
                   likes_count,
                   on_like,
                   on_interaction):
    # Need help here
    # interaction = partial(_interact_with_user, likes_count=likes_count, on_like=on_like)

    _open_hashtag(device, hashtag, likes_count)

    # Need help here
    # _iterate_over_followers(device, interaction, storage, on_interaction)


def _open_hashtag(device, hashtag, likes_count):
    print("Press search")
    tab_bar = device(resourceId='com.instagram.android:id/tab_bar', className='android.widget.LinearLayout')
    search_button = tab_bar.child(index=1)
    search_button.click.wait()

    print("Open hashtag " + hashtag)
    search_edit_text = device(resourceId='com.instagram.android:id/action_bar_search_edit_text',
                              className='android.widget.EditText')
    search_edit_text.set_text(hashtag)
    search_results_list = device(resourceId='android:id/list',
                                 className='android.widget.ListView')
    search_first_result = search_results_list.child(index=0)
    search_first_result.click.wait()

    # Go to Recent - Should be replaced
    x = "822"
    y = "752"
    os.system("adb shell input tap " + x + " " + y)
    random_sleep()

    # Click the first picture - Should be replaced
    x = "150"
    y = "1060"
    os.system("adb shell input tap " + x + " " + y)
    random_sleep()

    for i in range(0, likes_count):
        print("Double click!")
        double_click(device,
                     resourceId='com.instagram.android:id/layout_container_main',
                     className='android.widget.FrameLayout')
        random_sleep()

        _scroll_(device)

    return True


def _scroll_(device):
    tab_bar = device(resourceId='com.instagram.android:id/tab_bar',
                     className='android.widget.LinearLayout')

    x1 = (tab_bar.bounds['right'] - tab_bar.bounds['left']) / 2
    y1 = tab_bar.bounds['top'] - 1

    vertical_offset = tab_bar.bounds['right'] - tab_bar.bounds['left']

    x2 = x1
    y2 = y1 - vertical_offset

    device.swipe(x1, y1, x2, y2)

