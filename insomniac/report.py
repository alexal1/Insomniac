from datetime import timedelta

from insomniac.utils import *


def print_full_report(sessions):
    if len(sessions) > 1:
        for index, session in enumerate(sessions):
            finish_time = session.finishTime or datetime.now()
            print_timeless("\n")
            print_timeless(COLOR_REPORT + "SESSION #" + str(index + 1) + f" - {session.my_username}" + COLOR_ENDC)
            print_timeless(COLOR_REPORT + "Start time: " + str(session.startTime) + COLOR_ENDC)
            print_timeless(COLOR_REPORT + "Finish time: " + str(finish_time) + COLOR_ENDC)
            print_timeless(COLOR_REPORT + "Duration: " + str(finish_time - session.startTime) + COLOR_ENDC)
            print_timeless(COLOR_REPORT + "Total interactions: " + _stringify_interactions(session.totalInteractions)
                           + COLOR_ENDC)
            print_timeless(COLOR_REPORT + "Successful interactions: "
                           + _stringify_interactions(session.successfulInteractions) + COLOR_ENDC)
            print_timeless(COLOR_REPORT + "Total followed: "
                           + _stringify_interactions(session.totalFollowed) + COLOR_ENDC)
            print_timeless(COLOR_REPORT + "Total likes: " + str(session.totalLikes) + COLOR_ENDC)
            print_timeless(COLOR_REPORT + "Total comments: " + str(session.totalComments) + COLOR_ENDC)
            print_timeless(COLOR_REPORT + "Total unfollowed: " + str(session.totalUnfollowed) + COLOR_ENDC)
            print_timeless(COLOR_REPORT + "Total get-profile: " + str(session.totalGetProfile) + COLOR_ENDC)
            print_timeless(COLOR_REPORT + "Removed mass followers: "
                           + _stringify_removed_mass_followers(session.removedMassFollowers) + COLOR_ENDC)

    print_timeless("\n")
    print_timeless(COLOR_REPORT + "TOTAL" + COLOR_ENDC)

    completed_sessions = [session for session in sessions if session.is_finished()]
    print_timeless(COLOR_REPORT + "Completed sessions: " + str(len(completed_sessions)) + COLOR_ENDC)

    duration = timedelta(0)
    for session in sessions:
        finish_time = session.finishTime or datetime.now()
        duration += finish_time - session.startTime
    print_timeless(COLOR_REPORT + "Total duration: " + str(duration) + COLOR_ENDC)

    total_interactions = {}
    successful_interactions = {}
    total_followed = {}
    total_removed_mass_followers = []
    for session in sessions:
        for source, count in session.totalInteractions.items():
            if total_interactions.get(source) is None:
                total_interactions[source] = count
            else:
                total_interactions[source] += count

        for source, count in session.successfulInteractions.items():
            if successful_interactions.get(source) is None:
                successful_interactions[source] = count
            else:
                successful_interactions[source] += count

        for source, count in session.totalFollowed.items():
            if total_followed.get(source) is None:
                total_followed[source] = count
            else:
                total_followed[source] += count

        for username in session.removedMassFollowers:
            total_removed_mass_followers.append(username)

    print_timeless(COLOR_REPORT + "Total interactions: " + _stringify_interactions(total_interactions) + COLOR_ENDC)
    print_timeless(COLOR_REPORT + "Successful interactions: " + _stringify_interactions(successful_interactions)
                   + COLOR_ENDC)
    print_timeless(COLOR_REPORT + "Total followed : " + _stringify_interactions(total_followed)
                   + COLOR_ENDC)

    total_likes = sum(session.totalLikes for session in sessions)
    print_timeless(COLOR_REPORT + "Total likes: " + str(total_likes) + COLOR_ENDC)

    total_unfollowed = sum(session.totalUnfollowed for session in sessions)
    print_timeless(COLOR_REPORT + "Total unfollowed: " + str(total_unfollowed) + COLOR_ENDC)

    total_story_watches = sum(session.totalStoriesWatched for session in sessions)
    print_timeless(COLOR_REPORT + "Total stories watches: " + str(total_story_watches) + COLOR_ENDC)

    total_comments = sum(session.totalComments for session in sessions)
    print_timeless(COLOR_REPORT + "Total comments: " + str(total_comments) + COLOR_ENDC)

    total_get_profile = sum(session.totalGetProfile for session in sessions)
    print_timeless(COLOR_REPORT + "Total get-profile: " + str(total_get_profile) + COLOR_ENDC)

    print_timeless(COLOR_REPORT + "Removed mass followers: "
                   + _stringify_removed_mass_followers(total_removed_mass_followers) + COLOR_ENDC)


def print_short_report(source, session_state):
    total_likes = session_state.totalLikes
    total_comments = session_state.totalComments
    total_followed = sum(session_state.totalFollowed.values())
    interactions = session_state.successfulInteractions.get(source, 0)
    total_successful_interactions = sum(session_state.successfulInteractions.values())
    total_story_views = session_state.totalStoriesWatched
    print(COLOR_REPORT + "Session progress: " + str(total_likes) + " likes, " + str(total_followed) + " followed, " +
          str(total_story_views) + " stories watched, " + str(total_comments) + " comments, " +
          str(interactions) + " successful " + ("interaction" if interactions == 1 else "interactions") +
          " for " + source + "," +
          " " + str(total_successful_interactions) + " successful interactions for the entire session" + COLOR_ENDC)

    
def print_short_unfollow_report(session_state):
    total_unfollowed = session_state.totalUnfollowed
    print(COLOR_REPORT + "Session progress: " + str(total_unfollowed) + " unfollowed for the entire session" + COLOR_ENDC)

    
def print_short_scrape_report(session_state):
    total_scraped = sum(session_state.totalScraped.values())
    print(COLOR_REPORT + "Session progress: " + str(total_scraped) +
          " profiles scraped for the entire session" + COLOR_ENDC)

    
def print_interaction_types(username, can_like, can_follow, can_watch, can_comment):
    interaction_types = []
    if can_like:
        interaction_types.append("like")
    if can_follow:
        interaction_types.append("follow")
    if can_watch:
        interaction_types.append("watch stories")
    if can_comment:
        interaction_types.append("comment")
    print(f"@{username} interaction: going to {', '.join(interaction_types)}")


def _stringify_interactions(interactions):
    if len(interactions) == 0:
        return "0"

    result = ""
    total = sum(interactions.values())
    for source, count in interactions.items():
        result += str(count) + " for " + source + ", "
    result = result[:-2]
    return "({0}) {1}".format(total, result)


def _stringify_removed_mass_followers(removed_mass_followers):
    if len(removed_mass_followers) == 0:
        return "none"
    else:
        return "@" + ", @".join(removed_mass_followers)
