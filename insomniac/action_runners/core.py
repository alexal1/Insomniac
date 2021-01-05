from abc import ABC
from enum import unique, Enum


@unique
class ActionState(Enum):
    PRE_RUN = 0
    RUNNING = 1
    DONE = 2
    SOURCE_LIMIT_REACHED = 3
    SESSION_LIMIT_REACHED = 4


class ActionStatus(object):
    def __init__(self, state):
        self.state = state
        self.limit_state = None

    def set(self, state):
        self.state = state

    def get(self):
        return self.state

    def set_limit(self, limit_state):
        self.limit_state = limit_state

    def get_limit(self):
        return self.limit_state


class ActionsRunner(object):
    """An interface for actions-runner object"""

    ACTION_ID = "OVERRIDE"
    ACTION_ARGS = {"OVERRIDE": "OVERRIDE"}

    action_status = None

    def is_action_selected(self, args):
        raise NotImplementedError()

    def set_params(self, args):
        raise NotImplementedError()

    def reset_params(self):
        raise NotImplementedError()

    def run(self, device_wrapper, storage, session_state, on_action, is_limit_reached, is_passed_filters=None):
        raise NotImplementedError()


class CoreActionsRunner(ActionsRunner, ABC):
    """An interface for extra-actions-runner object"""
