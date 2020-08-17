from src.utils import *

_action_bar_bottom = None
_tab_bar_top = None


def update_interaction_rect(device):
    action_bar = device(resourceId='com.instagram.android:id/action_bar_container',
                        className='android.widget.FrameLayout')
    if action_bar.exists:
        global _action_bar_bottom
        _action_bar_bottom = action_bar.info['bounds']['bottom']
    else:
        print(COLOR_FAIL + "Cannot find action bar. This can lead to crashes, but script will continue working."
              + COLOR_ENDC)

    tab_bar = device(resourceId='com.instagram.android:id/tab_bar',
                     className='android.widget.LinearLayout')
    if tab_bar.exists:
        global _tab_bar_top
        _tab_bar_top = tab_bar.info['bounds']['top']
    else:
        print(COLOR_FAIL + "Cannot find tab bar. This can lead to crashes, but script will continue working."
              + COLOR_ENDC)


def is_in_interaction_rect(view):
    if _action_bar_bottom is None or _tab_bar_top is None:
        print(COLOR_FAIL + "Interaction rect is not specified in interaction_rect_checker.py" + COLOR_ENDC)

    view_top = view.info['bounds']['top']
    view_bottom = view.info['bounds']['bottom']

    if _action_bar_bottom is not None and view_top > _action_bar_bottom:
        return False

    if _tab_bar_top is not None and view_bottom < _tab_bar_top:
        return False

    return True
