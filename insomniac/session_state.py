import uuid
from datetime import datetime
from json import JSONEncoder

from insomniac.actions_types import LikeAction, InteractAction, FollowAction, GetProfileAction, ScrapeAction, \
    UnfollowAction, RemoveMassFollowerAction, StoryWatchAction


class SessionState:
    id = None
    args = {}
    my_username = None
    my_followers_count = None
    my_following_count = None
    totalInteractions = {}
    successfulInteractions = {}
    totalFollowed = {}
    totalLikes = 0
    totalUnfollowed = 0
    totalStoriesWatched = 0
    removedMassFollowers = []
    startTime = None
    finishTime = None

    def __init__(self):
        self.id = str(uuid.uuid4())
        self.args = {}
        self.my_username = None
        self.my_followers_count = None
        self.my_following_count = None
        self.totalInteractions = {}
        self.successfulInteractions = {}
        self.totalFollowed = {}
        self.totalScraped = {}
        self.totalLikes = 0
        self.totalGetProfile = 0
        self.totalUnfollowed = 0
        self.totalStoriesWatched = 0
        self.removedMassFollowers = []
        self.startTime = datetime.now()
        self.finishTime = None

    def add_action(self, action):
        if type(action) == LikeAction:
            self.totalLikes += 1

        if type(action) == GetProfileAction:
            self.totalGetProfile += 1

        if type(action) == StoryWatchAction:
            self.totalStoriesWatched += 1

        if type(action) == InteractAction:
            if self.totalInteractions.get(action.source) is None:
                self.totalInteractions[action.source] = 1
            else:
                self.totalInteractions[action.source] += 1

            if self.successfulInteractions.get(action.source) is None:
                self.successfulInteractions[action.source] = 1 if action.succeed else 0
            else:
                if action.succeed:
                    self.successfulInteractions[action.source] += 1

        if type(action) == FollowAction:
            if self.totalFollowed.get(action.source) is None:
                self.totalFollowed[action.source] = 1
            else:
                self.totalFollowed[action.source] += 1

        if type(action) == ScrapeAction:
            if self.totalScraped.get(action.source) is None:
                self.totalScraped[action.source] = 1
            else:
                self.totalScraped[action.source] += 1

        if type(action) == UnfollowAction:
            self.totalUnfollowed += 1

        if type(action) == RemoveMassFollowerAction:
            self.removedMassFollowers.append(action.user)

    def is_finished(self):
        return self.finishTime is not None


class SessionStateEncoder(JSONEncoder):

    def default(self, session_state: SessionState):
        return {
            "id": session_state.id,
            "total_interactions": sum(session_state.totalInteractions.values()),
            "successful_interactions": sum(session_state.successfulInteractions.values()),
            "total_followed": sum(session_state.totalFollowed.values()),
            "total_likes": session_state.totalLikes,
            "total_unfollowed": session_state.totalUnfollowed,
            "total_stories_watched": session_state.totalStoriesWatched,
            "total_get_profile": session_state.totalGetProfile,
            "total_scraped": session_state.totalScraped,
            "removed_mass_followers": session_state.removedMassFollowers,
            "start_time": str(session_state.startTime),
            "finish_time": str(session_state.finishTime),
            "args": session_state.args,
            "profile": {
                "followers": str(session_state.my_followers_count),
                "following": str(session_state.my_following_count)
            }
        }
