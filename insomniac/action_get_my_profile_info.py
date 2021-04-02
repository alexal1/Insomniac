from insomniac.navigation import switch_to_english
from insomniac.sleeper import sleeper
from insomniac.utils import *
from insomniac.views import TabBarView, ActionBarView, AccountView, UserSwitchFailedException


def get_my_profile_info(device, username):
    try:
        profile_view = TabBarView(device).navigate_to_profile()
        sleeper.random_sleep()

        if username is not None:
            if not profile_view.change_to_username(username):
                print(COLOR_FAIL + f"Couldn't switch user to {username}, abort!" + COLOR_ENDC)
                device.back()
                raise UserSwitchFailedException()

        print("Refreshing your profile status...")
        profile_view.refresh()
        sleeper.random_sleep()

        ActionBarView.update_interaction_rect(device)

        username, followers, following = profile_view.get_profile_info(swipe_up_if_needed=True)
    except UserSwitchFailedException as e:
        raise e
    except Exception as e:
        print(COLOR_FAIL + f"Exception: {e}" + COLOR_ENDC)
        save_crash(device, e)
        switch_to_english(device)

        # Try again on the correct language
        profile_view = TabBarView(device).navigate_to_profile()
        sleeper.random_sleep()

        if username is not None:
            if not profile_view.change_to_username(username):
                print(COLOR_FAIL + f"Couldn't switch user to {username}, abort!" + COLOR_ENDC)
                device.back()
                raise UserSwitchFailedException()

        print("Refreshing your profile status...")
        profile_view.refresh()
        sleeper.random_sleep()

        ActionBarView.update_interaction_rect(device)

        username, followers, following = profile_view.get_profile_info(swipe_up_if_needed=True)

    report_string = ""
    if username:
        report_string += "Hello, @" + username + "! "
    if followers is not None:
        report_string += "You have " + str(followers) + " followers"
        if following is not None:
            report_string += " and " + str(following) + " followings"
        report_string += " so far."

    if not report_string == "":
        print(report_string)

    return username, followers, following
