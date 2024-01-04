from insomniac import *
from insomniac.actions_impl import TEXTVIEW_OR_BUTTON_REGEX, open_user
from insomniac.navigation import switch_to_english, LanguageChangedException
from insomniac.safely_runner import run_safely, RestartJobRequiredException
from insomniac.sleeper import sleeper
from insomniac.views import ProfileView

DELAY_IN_AIRPLANE_MODE = 30
DELAY_AFTER_AIRPLANE_MODE = 10


def airplane_mode_on_off(device_wrapper):
    device = device_wrapper.get()
    if airplane_mode_on_off_programmatically(device):
        return

    done = "done"
    job_state = {done: False}

    def is_airplane_mode_on():
        stream = os.popen("adb" + ("" if device.device_id is None else " -s " + device.device_id) +
                          f" shell settings get global airplane_mode_on")
        output = stream.read()
        stream.close()
        return '1' in output

    def switch_airplane_mode(to_value: bool) -> bool:
        if is_airplane_mode_on() == to_value:
            return True

        # FIRST WAY
        # Try to click on "Airplane mode" text and see if airplane mode is actually on.
        airplane_mode_text = device.find(textMatches="(?i).*?(air|aero)plane.*?")
        if airplane_mode_text.exists():
            # Use loop because there may be expandable block with "Airplane mode" text so we'll have to click twice.
            max_attempts = 2
            attempts = 0
            while attempts < max_attempts:
                airplane_mode_text.click()
                attempts += 1
                if is_airplane_mode_on() == to_value:
                    return True

        # SECOND WAY
        # Just try to click all switches one by one.
        print(COLOR_OKGREEN + "Cannot find \"Airplane mode\" text, fallback to testing switches" + COLOR_ENDC)
        for switch in device.find(className="android.widget.Switch"):
            switch.click()
            sleeper.random_sleep()
            if is_airplane_mode_on() == to_value:
                return True
            else:
                print(COLOR_OKGREEN + "Wrong switch, going to the next one..." + COLOR_ENDC)
                switch.click()

        print(COLOR_FAIL + "Cannot turn on \"Airplane mode\"" + COLOR_ENDC)
        device.back()
        return False

    @run_safely(device_wrapper)
    def job():
        # Open settings
        print("Opening Airplane mode settings...")
        os.popen("adb" + ("" if device.device_id is None else " -s " + device.device_id) +
                 f" shell am start -a android.settings.AIRPLANE_MODE_SETTINGS").close()
        sleeper.random_sleep()

        switch_airplane_mode(True)
        print("Airplane mode ON")
        print(f"Sleep for {DELAY_IN_AIRPLANE_MODE} seconds")
        sleep(DELAY_IN_AIRPLANE_MODE)

        switch_airplane_mode(False)
        print("Airplane mode OFF")
        print(f"Sleep for {DELAY_AFTER_AIRPLANE_MODE} seconds")
        sleep(DELAY_AFTER_AIRPLANE_MODE)

        device.back()

        # Check that airplane mode is turned off and restart if not
        if is_airplane_mode_on():
            raise RestartJobRequiredException("Airplane mode was not turned off!")

        return True

    while not job_state[done]:
        result = job()
        job_state[done] = result


def airplane_mode_on_off_programmatically(device) -> bool:
    """
    Try to switch airplane mode via adb commands. Requires root access.
    """
    print_debug("Trying to switch airplane mode programmatically...")

    output = execute_command("adb" + ("" if device.device_id is None else " -s " + device.device_id) + " root")
    if output is not None and "adbd cannot run as root" in output:
        print_debug(COLOR_FAIL + "Cannot switch airplane mode programmatically." + COLOR_ENDC)
        return False
    execute_command("adb" + ("" if device.device_id is None else " -s " + device.device_id) + " shell settings put global airplane_mode_on 1")
    execute_command("adb" + ("" if device.device_id is None else " -s " + device.device_id) + " shell am broadcast -a android.intent.action.AIRPLANE_MODE --es \"state\" \"true\"")

    print("Airplane mode ON")
    print(f"Sleep for {DELAY_IN_AIRPLANE_MODE} seconds")
    sleep(DELAY_IN_AIRPLANE_MODE)

    execute_command("adb" + ("" if device.device_id is None else " -s " + device.device_id) + " shell settings put global airplane_mode_on 0")
    execute_command("adb" + ("" if device.device_id is None else " -s " + device.device_id) + " shell am broadcast -a android.intent.action.AIRPLANE_MODE --es \"state\" \"false\"")

    # Sleep for a while to let the device connect to a network
    print(f"Sleep for {DELAY_AFTER_AIRPLANE_MODE} seconds")
    sleep(DELAY_AFTER_AIRPLANE_MODE)
    return True


def remove_mass_follower(device, follower_name_view):
    """
    :return: True if successfully removed, False if cannot remove
    """
    remove_button = follower_name_view.right(resourceId=f'{device.app_id}:id/button',
                                             className='android.widget.Button',
                                             text='Remove')
    if remove_button is None or not remove_button.exists():
        print(COLOR_FAIL + 'Cannot find "Remove" button. Maybe not English language is set?' + COLOR_ENDC)
        save_crash(device)
        switch_to_english(device)
        raise LanguageChangedException()
    remove_button.click()
    sleeper.random_sleep()
    _close_dialog_if_shown(device)
    _close_bottom_sheet_if_shown(device)
    return True


def unfollow_from_list(device, storage, on_action, iteration_callback, iteration_callback_pre_conditions):
    while True:
        username = storage.get_unfollow_target()
        if username is None:
            print(COLOR_OKGREEN + "No unfollow targets left in the list" + COLOR_ENDC)
            if activation_controller.is_activated:
                from insomniac.extra_features.report_sender import notify_unfollow_targets_finished
                notify_unfollow_targets_finished(storage.my_username)
            break

        if not iteration_callback_pre_conditions(username, None, None):
            continue

        # Open username's profile
        open_user(device, username, refresh=False, deep_link_usage_percentage=50, on_action=on_action)

        to_continue = iteration_callback(username, None, None)
        if to_continue:
            sleeper.random_sleep()
        else:
            print(COLOR_OKBLUE + f"Stopping iteration over list of profiles" + COLOR_ENDC)
            return


def unfollow_from_database(device, storage, unfollow_older_than_days, is_using_global_search, on_action, iteration_callback, iteration_callback_pre_conditions):
    unfollow_navigation = UnfollowNavigation(device, on_action, is_using_global_search)
    unfollow_navigation.prepare()

    while True:
        username, follow_date = storage.get_unfollow_target_from_database()
        if username is None:
            print(COLOR_OKGREEN + "No unfollow targets left in the database" + COLOR_ENDC)
            if activation_controller.is_activated:
                from insomniac.extra_features.report_sender import notify_unfollow_targets_finished
                notify_unfollow_targets_finished(storage.my_username)
            break

        if follow_date > datetime.now() - timedelta(days=unfollow_older_than_days):
            print(COLOR_OKGREEN + f"There are unfollow targets in the database, "
                                  f"but follows were made less than {unfollow_older_than_days} days ago" + COLOR_ENDC)
            break

        if not iteration_callback_pre_conditions(username, None, None):
            continue

        user_found = unfollow_navigation.open_user(username)
        if not user_found:
            storage.update_follow_status(username, do_i_follow_him=False)
            print(f"User @{username} not found, saving that we don't follow him and continuing...")
            continue

        to_continue = iteration_callback(username, None, None)
        if to_continue:
            sleeper.random_sleep()
        else:
            print(COLOR_OKBLUE + f"Stopping unfollowing from the database" + COLOR_ENDC)
            return


def _close_dialog_if_shown(device):
    dialog_root_view = device.find(resourceId=f'{device.app_id}:id/dialog_root_view',
                                   className='android.widget.FrameLayout')
    if not dialog_root_view.exists():
        dialog_root_view = device.find(resourceId=f'{device.app_id}:id/dialog_container',
                                       className='android.view.ViewGroup')
        if not dialog_root_view.exists():
            return

    print(COLOR_OKGREEN + "Dialog shown, confirm removing..." + COLOR_ENDC)
    sleeper.random_sleep()
    remove_button = dialog_root_view.child(index=0).child(resourceId=f'{device.app_id}:id/primary_button',
                                                          classNameMatches=TEXTVIEW_OR_BUTTON_REGEX)
    remove_button.click()
    print("Removing confirmed!")
    sleeper.random_sleep()


def _close_bottom_sheet_if_shown(device):
    bottom_sheet_view = device.find(resourceId=f'{device.app_id}:id/bottom_sheet_container',
                                    className='android.view.ViewGroup')
    if not bottom_sheet_view.exists():
        return

    print(COLOR_OKGREEN + "Bottom sheet shown, confirm removing..." + COLOR_ENDC)
    sleeper.random_sleep()
    remove_button = bottom_sheet_view.child(resourceId=f'{device.app_id}:id/action_sheet_row_text_view',
                                            classNameMatches=TEXTVIEW_OR_BUTTON_REGEX)
    remove_button.click()
    print("Removing confirmed!")
    sleeper.random_sleep()


class UnfollowNavigation:

    device = None
    on_action = None
    is_using_global_search = False
    followers_following_list_view = None

    def __init__(self, device, on_action, is_using_global_search):
        self.device = device
        self.on_action = on_action
        self.is_using_global_search = is_using_global_search

    def prepare(self):
        if not self.is_using_global_search:
            self.followers_following_list_view = ProfileView(self.device, is_own_profile=True).navigate_to_following()

    def open_user(self, username) -> bool:
        if self.is_using_global_search:
            return open_user(device=self.device,
                             username=username,
                             refresh=False,
                             deep_link_usage_percentage=0,
                             on_action=self.on_action)
        else:
            return self.followers_following_list_view.search_for_user(username)
