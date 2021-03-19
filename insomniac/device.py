from insomniac.device_facade import create_device
from insomniac.typewriter import Typewriter
from insomniac.utils import *


class DeviceWrapper(object):
    device = None

    def __init__(self, device_id, old_uiautomator, wait_for_device, app_id, dont_set_typewriter):
        self.device_id = device_id
        self.app_id = app_id
        self.old_uiautomator = old_uiautomator

        self.create(wait_for_device, dont_set_typewriter)

    def get(self):
        return self.device

    def create(self, wait_for_device, dont_set_typewriter):
        if not check_adb_connection(device_id=self.device_id, wait_for_device=wait_for_device):
            return None

        typewriter = Typewriter(self.device_id)
        if not dont_set_typewriter:
            typewriter.set_adb_keyboard()

        device = create_device(self.old_uiautomator, self.device_id, self.app_id, typewriter)
        if device is None:
            return None

        self.device = device

        return self.device
