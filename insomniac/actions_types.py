from collections import namedtuple

LikeAction = namedtuple('LikeAction', 'source user')
FollowAction = namedtuple('FollowAction', 'source user')
UnfollowAction = namedtuple('UnfollowAction', 'user')
StoryWatchAction = namedtuple('StoryWatchAction', 'user')
InteractAction = namedtuple('InteractAction', 'source user succeed')
GetProfileAction = namedtuple('GetProfileAction', 'user')
ScrapeAction = namedtuple('ScrapeAction', 'source user')
RemoveMassFollowerAction = namedtuple('RemoveMassFollowerAction', 'user')
