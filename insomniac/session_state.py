import uuid
from datetime import datetime

from insomniac.actions_types import LikeAction, InteractAction, FollowAction, GetProfileAction, ScrapeAction, \
    UnfollowAction, RemoveMassFollowerAction, StoryWatchAction, CommentAction


class SessionState:
    id = None
    args = {}
    app_version = None
    my_username = None
    my_followers_count = None
    my_following_count = None
    totalInteractions = {}
    successfulInteractions = {}
    totalFollowed = {}
    totalComments = 0
    totalLikes = 0
    totalUnfollowed = 0
    totalStoriesWatched = 0
    removedMassFollowers = []
    startTime = None
    finishTime = None

    def __init__(self):
        self.id = str(uuid.uuid4())
        self.args = {}
        self.app_version = None
        self.my_username = None
        self.my_followers_count = None
        self.my_following_count = None
        self.totalInteractions = {}
        self.successfulInteractions = {}
        self.totalFollowed = {}
        self.totalScraped = {}
        self.totalComments = 0
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

        if type(action) == CommentAction:
            self.totalComments += 1

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
