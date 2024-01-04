from typing import Optional

from insomniac.actions_impl import TEXTVIEW_OR_BUTTON_REGEX
from insomniac.extra_features.actions_impl import airplane_mode_on_off
from insomniac.extra_features.utils import new_identity
from insomniac.navigation import close_instagram_and_system_dialogs
from insomniac.sleeper import sleeper
from insomniac.utils import *
from insomniac.views import TabBarView, TabBarTabs, LanguageNotEnglishException
from registration.api import get_phone_number, get_confirmation_code

MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


class UserData:
    full_name = None
    password = None
    username = None


def register_accounts(device_wrapper,
                      users_file_path,
                      session_state,
                      on_action):
    device = device_wrapper.get()
    device_id = device_wrapper.device_id
    app_id = device_wrapper.app_id

    sleeper.random_sleep(multiplier=2.0)

    dialog = device.find(resourceId=f'{app_id}:id/dialog_container',
                         className='android.view.ViewGroup')
    if dialog.exists():
        primary_button = device.find(resourceId=f'{app_id}:id/primary_button',
                                     className='android.widget.Button')
        primary_button.click(ignore_if_missing=True)

    user_data = _get_user_data(users_file_path)
    if user_data is None:
        print(COLOR_FAIL + f"No more not registered users in {users_file_path}!" + COLOR_ENDC)
        return

    print("Press \"Create New Account\"")
    sign_up_button = device.find(resourceId=f'{app_id}:id/sign_up_with_email_or_phone',
                                 classNameMatches=TEXTVIEW_OR_BUTTON_REGEX)
    if sign_up_button.exists():
        sign_up_button.click()
    else:
        clear_instagram_data(device_id, app_id)
        open_instagram(device_id, app_id)
        sign_up_button.click()
    sleeper.random_sleep()

    print("Obtaining and entering a mobile phone...")
    phone_number_data = get_phone_number()
    if phone_number_data is None:
        print(COLOR_FAIL + f"Cannot get phone number!" + COLOR_ENDC)
        return
    country_code_picker = device.find(resourceId=f'{app_id}:id/country_code_picker',
                                      className='android.widget.TextView')
    country_code_picker.click()
    sleeper.random_sleep()

    print("Set country code")
    search_edit_text = device.find(resourceId=f'{app_id}:id/search',
                                   className='android.widget.EditText')
    search_edit_text.set_text(phone_number_data.country_code)
    sleeper.random_sleep()

    country_code_list = device.find(resourceId=f'{app_id}:id/country_code_list',
                                    className='android.widget.ListView')
    country_code_first_item = country_code_list.child(index=0)
    country_code_first_item.click()
    sleeper.random_sleep()

    print("Set phone number")
    phone_field = device.find(resourceId=f'{app_id}:id/phone_field',
                              className='android.widget.EditText')
    phone_field.set_text(phone_number_data.phone_number)
    sleeper.random_sleep()
    print("Go next")
    next_button = device.find(resourceId=f'{app_id}:id/button_text',
                              classNameMatches=TEXTVIEW_OR_BUTTON_REGEX)
    next_button.click()
    sleeper.random_sleep()

    print("Obtaining and entering the confirmation code...")
    confirmation_code = get_confirmation_code(phone_number_data.response_id)
    if confirmation_code is None:
        print(COLOR_FAIL + f"Cannot get confirmation code!" + COLOR_ENDC)
        return
    confirmation_code_edit_text = device.find(resourceId=f'{app_id}:id/confirmation_field',
                                              className='android.widget.EditText')
    confirmation_code_edit_text.set_text(confirmation_code)
    sleeper.random_sleep()
    print("Go next")
    next_button.click()
    sleeper.random_sleep()

    print("Enter full name")
    full_name_edit_text = device.find(resourceId=f'{app_id}:id/full_name',
                                      className='android.widget.EditText')
    full_name_edit_text.set_text(user_data.full_name)
    sleeper.random_sleep()

    password_edit_text = device.find(resourceId=f'{app_id}:id/password',
                                     className='android.widget.EditText')
    if password_edit_text.exists():
        print("Enter password")
        password_edit_text.set_text(user_data.password)
        sleeper.random_sleep()

    print("Continue")
    continue_button = device.find(resourceId=f'{app_id}:id/continue_without_ci',
                                  classNameMatches=TEXTVIEW_OR_BUTTON_REGEX)
    continue_button.click()
    sleeper.random_sleep()

    if password_edit_text.exists():
        print("Enter password")
        password_edit_text.set_text(user_data.password)
        sleeper.random_sleep()
        print("Go next")
        next_button.click()
        sleeper.random_sleep()

    print("Choose random birthday")
    pickers = device.find(resourceId='android:id/pickers',
                          className='android.widget.LinearLayout')
    print("Set day")
    day_picker = pickers.child(index=1).child(index=1)
    day_picker.long_click()
    day_picker.set_text(str(random.randint(1, 31)))
    sleeper.random_sleep()
    print("Set month")
    month_picker = pickers.child(index=0).child(index=1)
    month_picker.long_click()
    month_picker.set_text(random.choice(MONTHS))
    sleeper.random_sleep()
    print("Set year")
    year_picker = pickers.child(index=2).child(index=1)
    year_picker.long_click()
    year_picker.set_text(str(random.randint(1981, 2003)))
    sleeper.random_sleep()
    device.close_keyboard()
    year_picker.click()
    sleeper.random_sleep()
    print("Go next")
    next_button.click()
    sleeper.random_sleep()

    change_username_button = device.find(resourceId=f'{app_id}:id/change_username',
                                         classNameMatches=TEXTVIEW_OR_BUTTON_REGEX)
    if change_username_button.exists(quick=True):
        print("Let's change username")
        change_username_button.click()
        sleeper.random_sleep()

    print("Set username")
    username_edit_text = device.find(resourceId=f'{app_id}:id/username',
                                     className='android.widget.EditText')
    username_edit_text.set_text(user_data.username)
    sleeper.random_sleep()
    print("Go next")
    next_button.click()

    print("Waiting for the registration to complete...")
    sleeper.random_sleep(multiplier=8.0)

    print("Now just skip everything...")
    while _skip(device, app_id):
        pass

    print("Done!")

    if _is_succeed(device):
        print(COLOR_OKGREEN + "Registration successfully completed!" + COLOR_ENDC)
        _set_user_done(users_file_path)
    else:
        print(COLOR_FAIL + "Registration failed!" + COLOR_ENDC)

    new_identity(device_id, app_id)
    sleeper.random_sleep(multiplier=2.0)
    close_instagram_and_system_dialogs(device)  # for the case if New Identity didn't work
    airplane_mode_on_off(device_wrapper)


def _get_user_data(path) -> Optional[UserData]:
    with open(path, "r", encoding="utf-8") as file:
        lines = [line.rstrip() for line in file]

        for i, line in enumerate(lines):
            # Skip comment
            if i == 0:
                continue

            if "DONE" in line:
                continue

            user_data = UserData()
            user_data.full_name, user_data.password, user_data.username = line.split(', ')
            return user_data


def _set_user_done(path):
    with open(path, "r+", encoding="utf-8") as file:
        lines = [line.rstrip() for line in file]

        for i, line in enumerate(lines):
            # Skip comment
            if i == 0:
                continue

            if "DONE" in line:
                continue

            lines[i] += " - DONE"
            break

        file.truncate(0)
        file.seek(0)
        file.write("\n".join(lines))


def _skip(device, app_id) -> bool:
    """
    Skip everything.

    :returns: True if skipped something, False if not
    """
    sleeper.random_sleep()
    skip_button = device.find(resourceId=f'{app_id}:id/skip_button',
                              classNameMatches=TEXTVIEW_OR_BUTTON_REGEX)
    dialog = device.find(resourceId=f'{app_id}:id/dialog_container',
                         className='android.view.ViewGroup')
    dialog_negative_button = dialog.child(resourceId=f'{app_id}:id/negative_button',
                                          className='android.widget.Button')
    action_bar_button = device.find(resourceId=f'{app_id}:id/action_bar_button_action',
                                    className='android.widget.ViewSwitcher')

    if skip_button.exists():
        print("Skip")
        skip_button.click()
        return True

    if dialog_negative_button.exists():
        print("Skip")
        dialog_negative_button.click()
        return True

    if action_bar_button.exists():
        print("Next")
        action_bar_button.click()
        return True

    return False


def _is_succeed(device):
    try:
        TabBarView(device).navigate_to(TabBarTabs.PROFILE)
    except LanguageNotEnglishException:
        print(COLOR_FAIL + "Cannot open newly created profile..." + COLOR_ENDC)
        return False
    return True

