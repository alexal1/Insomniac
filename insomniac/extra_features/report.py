from insomniac.utils import *


def print_full_management_report(sessions):
    print_timeless("\n")

    completed_sessions = [session for session in sessions if session.is_finished()]
    print_timeless(COLOR_REPORT + "Completed sessions: " + str(len(completed_sessions)) + COLOR_ENDC)

    duration = timedelta(0)
    for session in sessions:
        finish_time = session.finishTime or datetime.now()
        duration += finish_time - session.startTime
    print_timeless(COLOR_REPORT + "Total duration: " + str(duration) + COLOR_ENDC)

    total_clones_created = 0
    total_clones_installed = 0
    total_clones_removed = 0
    total_app_data_cleanup = 0
    total_profiles_registered = 0
    for session in sessions:
        total_clones_created += len(session.totalClonesCreation)
        total_clones_installed += len(session.totalClonesInstallation)
        total_clones_removed += len(session.totalClonesDeletion)
        total_app_data_cleanup += len(session.totalAppDataCleanups)
        total_profiles_registered += len(session.totalRegisteredAccounts)

    print_timeless(COLOR_REPORT + "Total clones created: " + str(total_clones_created) + COLOR_ENDC)
    print_timeless(COLOR_REPORT + "Total clones installed: " + str(total_clones_installed) + COLOR_ENDC)
    print_timeless(COLOR_REPORT + "Total clones removed: " + str(total_clones_removed) + COLOR_ENDC)
    print_timeless(COLOR_REPORT + "Total app-data cleanup: " + str(total_app_data_cleanup) + COLOR_ENDC)
    print_timeless(COLOR_REPORT + "Total profiles registered: " + str(total_profiles_registered) + COLOR_ENDC)


def print_short_management_report(session_state):
    total_clones_created = len(session_state.totalClonesCreation)
    total_clones_installed = len(session_state.totalClonesInstallation)
    total_clones_removed = len(session_state.totalClonesDeletion)
    total_app_data_cleanup = len(session_state.totalAppDataCleanups)
    total_profiles_registered = len(session_state.totalRegisteredAccounts)

    print(COLOR_REPORT + "Session progress: " +
          str(total_clones_created) + " clones created, " +
          str(total_clones_installed) + " clones installed, " +
          str(total_clones_removed) + " clones removed, " +
          str(total_app_data_cleanup) + " app-data cleaned-up, " +
          str(total_profiles_registered) + " new profiles registered" + COLOR_ENDC)
