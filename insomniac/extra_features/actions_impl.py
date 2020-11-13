from insomniac import *


def remove_mass_follower(device, follower_name_view):
    """
    :return: True if successfully removed, False if cannot remove
    """
    remove_button = follower_name_view.right(resourceId='com.instagram.android:id/media_option_button',
                                             className='android.widget.ImageView')
    if not remove_button.exists():
        print(COLOR_OKGREEN + "Next item not found: probably reached end of the screen." + COLOR_ENDC)
        return False
    remove_button.click()
    random_sleep()
    _close_dialog_if_shown(device)
    _close_bottom_sheet_if_shown(device)
    return True


def _close_dialog_if_shown(device):
    dialog_root_view = device.find(resourceId='com.instagram.android:id/dialog_root_view',
                                   className='android.widget.FrameLayout')
    if not dialog_root_view.exists():
        return

    print(COLOR_OKGREEN + "Dialog shown, confirm removing..." + COLOR_ENDC)
    random_sleep()
    remove_button = dialog_root_view.child(index=0).child(resourceId='com.instagram.android:id/primary_button',
                                                          className='android.widget.TextView')
    remove_button.click()
    print("Removing confirmed!")
    random_sleep()


def _close_bottom_sheet_if_shown(device):
    bottom_sheet_view = device.find(resourceId='com.instagram.android:id/bottom_sheet_container',
                                    className='android.view.ViewGroup')
    if not bottom_sheet_view.exists():
        return

    print(COLOR_OKGREEN + "Bottom sheet shown, confirm removing..." + COLOR_ENDC)
    random_sleep()
    remove_button = bottom_sheet_view.child(resourceId='com.instagram.android:id/action_sheet_row_text_view',
                                            className='android.widget.TextView')
    remove_button.click()
    print("Removing confirmed!")
    random_sleep()
