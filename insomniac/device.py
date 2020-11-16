from insomniac.device_facade import create_device
from insomniac.utils import *


class DeviceWrapper(object):
    device = None

    def __init__(self, device_id, old_uiautomator):
        self.device_id = device_id
        self.old_uiautomator = old_uiautomator

        self.create()

    def get(self):
        return self.device

    def create(self):
        if not check_adb_connection(is_device_id_provided=(self.device_id is not None)):
            return None

        device = create_device(self.old_uiautomator, self.device_id)
        if device is None:
            return None

        self.device = device

        return self.device
