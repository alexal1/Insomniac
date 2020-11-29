from collections import namedtuple
from enum import unique, Enum

LikeAction = namedtuple('LikeAction', 'source user')
FollowAction = namedtuple('FollowAction', 'source user')
UnfollowAction = namedtuple('UnfollowAction', 'user')
StoryWatchAction = namedtuple('StoryWatchAction', 'user')
InteractAction = namedtuple('InteractAction', 'source user succeed')
GetProfileAction = namedtuple('GetProfileAction', 'user')
ScrapeAction = namedtuple('ScrapeAction', 'source user')
RemoveMassFollowerAction = namedtuple('RemoveMassFollowerAction', 'user')


@unique
class BloggerInteractionType(Enum):
    FOLLOWERS = 'followers'
    FOLLOWING = 'following'


@unique
class HashtagInteractionType(Enum):
    TOP_LIKERS = 'top-likers'
    RECENT_LIKERS = 'recent-likers'
