from enum import Enum, unique


@unique
class Provider(Enum):
    UNKNOWN = 0
    INTERACTION = 1
    SCRAPING = 2
    TARGETS_LIST = 3
