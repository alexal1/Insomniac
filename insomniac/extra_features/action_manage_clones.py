import os
import subprocess
from time import sleep

from insomniac import APP_REOPEN_WARNING, COLOR_FAIL, COLOR_ENDC
from insomniac.device import DeviceWrapper
from insomniac.device_facade import DeviceFacade
from insomniac.extra_features.actions_impl import airplane_mode_on_off
from insomniac.extra_features.management_actions_types import CloneCreationAction, CloneInstallationAction, \
    CloneRemovalAction
from insomniac.extra_features.report import print_short_management_report
from insomniac.extra_features.utils import get_package_by_name
from insomniac.extra_features.views import StartPageView, SystemDialogView
from insomniac.hardban_indicator import HardBanError
from insomniac.navigation import navigate, close_instagram_and_system_dialogs, InstagramOpener
from insomniac.safely_runner import run_safely
from insomniac.sleeper import sleeper
from insomniac.storage import ProfileStatus
from insomniac.utils import print, print_timeless, describe_exception, close_instagram
from insomniac.views import TabBarTabs, ProfileView, ActionBarView, HomeView

TEMPORARY_APK_NAME = "tmp"


def create_clones(app_cloner_device_id, users_list, apk_store_path, session_state, on_action):
    print("Open Appcloner")
    _open_appcloner(app_cloner_device_id)

    sleeper.random_sleep(multiplier=2.0)

    device = DeviceWrapper(device_id=app_cloner_device_id,
                           old_uiautomator=False,
                           wait_for_device=False,
                           app_id=None,
                           app_name=None,
                           dont_set_typewriter=True).get()

    _open_clone_settings(device)

    for username in users_list:
        succeed = False
        while not succeed:
            try:
                succeed = _create_clone(device, username)
            except DeviceFacade.JsonRpcError as e:
                print(COLOR_FAIL + describe_exception(e, with_stacktrace=False) + COLOR_ENDC)
                _close_appcloner(app_cloner_device_id)
                sleeper.random_sleep()
                _open_appcloner(app_cloner_device_id)
                sleeper.random_sleep(multiplier=2.0)
                _open_clone_settings(device)
                continue
        _pull_apk(app_cloner_device_id, apk_store_path, username)
        on_action(CloneCreationAction(user=username, appcloner_host_device=app_cloner_device_id))
        print_short_management_report(session_state)

    _close_appcloner(app_cloner_device_id)


def install_clones(target_device_id, users_passwords_map, apk_store_path, session_state, on_action):
    for username_password_pair in users_passwords_map:
        username = username_password_pair['user']
        password = username_password_pair['password']

        app_id = get_package_by_name(target_device_id, username)

        if app_id is None:
            _install_apk(target_device_id, apk_store_path, username)

        app_id = get_package_by_name(target_device_id, username)

        if app_id is None:
            print(COLOR_FAIL + f'App of profile {username} could not be found on the device, moving to next profile' + COLOR_ENDC)
            continue

        print_timeless(f"\n\n-------- Log in to @{username} --------")

        device_wrapper = DeviceWrapper(device_id=target_device_id,
                                       old_uiautomator=False,
                                       wait_for_device=False,
                                       app_id=app_id,
                                       app_name=None,
                                       dont_set_typewriter=False)
        profile_status = _log_in_and_prepare_account(device_wrapper, username, password)
        on_action(CloneInstallationAction(user=username, target_device=target_device_id, profile_status=profile_status))
        print_short_management_report(session_state)


def remove_clones(target_device_id, users_list, session_state, on_action):
    for username in users_list:
        is_removed = _remove_app(target_device_id, username)
        if is_removed:
            on_action(CloneRemovalAction(user=username, target_device=target_device_id))
            print_short_management_report(session_state)


def _log_in_and_prepare_account(device_wrapper, username, password):
    profile_status = "profile_status"
    job_state = {profile_status: ProfileStatus.UNKNOWN}

    airplane_mode_on_off(device_wrapper)
    device = device_wrapper.get()
    InstagramOpener.INSTANCE.open_instagram()

    @run_safely(device_wrapper)
    def job():
        sleeper.random_sleep(multiplier=4.0)
        try:
            if SystemDialogView(device).close_play_protect():
                # Sleep again because app was actually opened only now
                sleeper.random_sleep(multiplier=4.0)
            home_view = HomeView(device)
            if home_view.is_visible():
                print(f"@{username} is logged in already")
            else:
                start_page_view = StartPageView(device)
                start_page_view.close_terms_dialog()
                print(f"Log in as @{username}")
                start_page_view.go_to_log_in().log_in(username, password)
                sleeper.random_sleep(multiplier=4.0)
                if not home_view.is_visible():
                    print(COLOR_FAIL + "HomeView is not visible after log in, seems we've failed" + COLOR_ENDC)
                    return
        except HardBanError:
            job_state[profile_status] = ProfileStatus.HARD_BAN
            return

        navigate(device, TabBarTabs.PROFILE)
        is_business_account = ProfileView(device, is_own_profile=True).has_business_category()
        if is_business_account:
            print(f"@{username} is already a business account")
        else:
            _switch_to_business_account(device)

        sleeper.random_sleep()
        close_instagram_and_system_dialogs(device)
        sleeper.random_sleep()

        job_state[profile_status] = ProfileStatus.VALID

    for _ in range(3):
        job()
        if job_state[profile_status] != ProfileStatus.UNKNOWN:
            break

    if job_state[profile_status] == ProfileStatus.UNKNOWN:
        job_state[profile_status] = ProfileStatus.CANT_LOGIN

    close_instagram(device.device_id, device.app_id)

    return job_state[profile_status]


def _is_clone_installed(device_id, username):
    app_id = get_package_by_name(device_id, username)
    if app_id is None:
        return False
    cmd = ("adb" + ("" if device_id is None else " -s " + device_id) +
           f" shell pm list {app_id}")
    cmd_res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding="utf8")
    return cmd_res.stdout.strip() != ""


def _open_appcloner(device_id):
    cmd = ("adb" + ("" if device_id is None else " -s " + device_id) +
           f" shell am start -n com.applisto.appcloner/com.applisto.appcloner.activity.MainActivity")

    cmd_res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding="utf8")
    err = cmd_res.stderr.strip()
    if err and err != APP_REOPEN_WARNING:
        print(COLOR_FAIL + err + COLOR_ENDC)


def _close_appcloner(device_id):
    cmd = ("adb" + ("" if device_id is None else " -s " + device_id) +
           f" shell am force-stop com.applisto.appcloner")

    cmd_res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding="utf8")
    err = cmd_res.stderr.strip()
    if err:
        print(COLOR_FAIL + err + COLOR_ENDC)


def _open_clone_settings(device):
    print("Open Instagram clone settings")
    sleeper.random_sleep(multiplier=2.0)
    device.find(className="android.widget.TextView",
                textMatches="Instagram\n.*?").click(ignore_if_missing=True)


def _create_clone(device, username):
    print_timeless(f"\n\n-------- Creating a clone for @{username} --------")
    print("Increment clone number")
    device.find(className="android.widget.TextView",
                textMatches=".*?Clone number.*?").click()
    clone_number_edit_text = device.find(className="android.widget.EditText")
    current_clones_number = int(clone_number_edit_text.get_text())
    clone_number_edit_text.set_text(current_clones_number + 1)
    device.find(className="android.widget.Button",
                text="OK").click()

    print("Set name")
    device.find(className="android.widget.TextView",
                text="Name").click()
    device.find(className="android.widget.EditText").click()
    device.find(className="android.widget.EditText").set_text(username)
    device.find(className="android.widget.Button",
                text="OK").click()

    print("Start cloning")
    device.find(className="android.widget.ImageButton",
                description="Clone app").click()
    try:
        device.find(className="android.widget.Button",
                    text="OK").click()
    except DeviceFacade.JsonRpcError:
        # If we pressed in past on "don't show this dialog again", there wont be any OK button
        pass
    device.find(className="android.widget.Button",
                text="CONTINUE").click()
    while not device.find(className="android.widget.TextView", text="App cloned").exists():
        sleep(5)
    device.find(className="android.widget.Button",
                text="CANCEL").click()

    print("Save apk")
    bottom_view = device.find(resourceId="com.applisto.appcloner:id/l",
                              className="android.view.View")
    bottom_view.click(mode=DeviceFacade.Place.CENTER)
    device.find(className="android.widget.TextView",
                textMatches=".*?Generated APKs.*?").click()
    sleeper.random_sleep()

    cloned_item = device.find(className="android.widget.ListView",
                              resourceId="android:id/list").child(index=1)
    cloned_item.click()
    device.find(className="android.widget.TextView",
                text="Save").click()
    device.find(className="android.widget.EditText").click()
    device.find(className="android.widget.EditText").set_text(f"{TEMPORARY_APK_NAME}.apk")
    sleeper.random_sleep()
    device.find(className="android.widget.Button",
                text="SAVE").click()
    if device.find(className="android.widget.TextView", textStartsWith="Replace").exists():
        device.find(className="android.widget.Button",
                    text="OK").click()

    print("Delete clone")
    cloned_item.click()
    device.find(className="android.widget.TextView",
                text="Delete").click()
    device.find(className="android.widget.Button",
                text="DELETE").click()
    sleeper.random_sleep()

    print("Back to initial state")
    bottom_view.click(mode=DeviceFacade.Place.LEFT)

    return True


def _pull_apk(device_id, apk_store_path, username):
    user_apk_file_name = f"{username}.apk"
    print(f"Pulling {user_apk_file_name}")
    cmd = ("adb" + ("" if device_id is None else " -s " + device_id) +
           f" pull /storage/emulated/0/{TEMPORARY_APK_NAME}.apk {os.path.join(apk_store_path, user_apk_file_name)}")
    cmd_res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding="utf8")
    err = cmd_res.stderr.strip()
    if err:
        print(COLOR_FAIL + err + COLOR_ENDC)


def _install_apk(device_id, apk_store_path, username):
    user_apk_file_name = f"{username}.apk"
    print(f"Installing {user_apk_file_name}")
    cmd = ("adb" + ("" if device_id is None else " -s " + device_id) +
           f" install {os.path.join(apk_store_path, user_apk_file_name)}")
    cmd_res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding="utf8")
    err = cmd_res.stderr.strip()
    if err:
        print(COLOR_FAIL + err + COLOR_ENDC)


def _remove_app(device_id, username):
    app_id = get_package_by_name(device_id, username)

    if app_id is None:
        print(COLOR_FAIL + f"Could not find app id of profile {username}. App wont be uninstalled" + COLOR_ENDC)
        return False

    print(f"Uninstalling {app_id} ({username})")
    cmd = ("adb" + ("" if device_id is None else " -s " + device_id) + f" uninstall {app_id}")
    cmd_res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding="utf8")
    err = cmd_res.stderr.strip()
    if err:
        print(COLOR_FAIL + err + COLOR_ENDC)
        return False

    return True


def _open_clone(device_id, app_name):
    print(f"Open \"{app_name}\" app")
    app_id = get_package_by_name(device_id, app_name)

    cmd = ("adb" + ("" if device_id is None else " -s " + device_id) +
           f" shell am start -n {app_id}/com.instagram.mainactivity.MainActivity")

    cmd_res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding="utf8")
    err = cmd_res.stderr.strip()
    if err and err != APP_REOPEN_WARNING:
        print(COLOR_FAIL + err + COLOR_ENDC)


def _switch_to_business_account(device):
    print("Switching to business account...")
    ActionBarView.create_instance(device)
    ProfileView(device) \
        .navigate_to_options() \
        .navigate_to_settings() \
        .navigate_to_account() \
        .switch_to_business_account()
