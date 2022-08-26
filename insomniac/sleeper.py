from random import uniform

from insomniac.utils import *

MEGABIT = 1000000
SPEED_SUPERFAST = 1000 * MEGABIT  # not recommended
SPEED_GOOD = 25 * MEGABIT
SPEED_BAD = 10 * MEGABIT
SPEED_UGLY = 1 * MEGABIT
SPEED_ZERO = 0

# Dict of sleep ranges by Internet speed
SLEEP_RANGE_BY_SPEED = {
    SPEED_SUPERFAST: (0, 1),
    SPEED_GOOD: (1, 3),
    SPEED_BAD: (2, 5),
    SPEED_UGLY: (4, 8),
    SPEED_ZERO: (7, 12)
}


class Sleeper:
    sleep_range_start = 1.0
    sleep_range_end = 4.0

    def __init__(self):
        pass

    def random_sleep(self, multiplier=1.0):
        delay = uniform(self.sleep_range_start, self.sleep_range_end) * multiplier
        print(f"Sleep for {delay:.2f} seconds")
        sleep(delay)

    def _set_random_sleep_range(self, speed, s1, s2):
        start1, end1 = SLEEP_RANGE_BY_SPEED[s1]
        start2, end2 = SLEEP_RANGE_BY_SPEED[s2]
        x = (speed - s1) / (s2 - s1) if s2 != s1 else 1  # x is a value between [0, 1]

        self.sleep_range_start = start1 + x * (start2 - start1)
        self.sleep_range_end = end1 + x * (end2 - end1)

        print(f"Sleep range will be from {self.sleep_range_start:.2f} to {self.sleep_range_end:.2f} seconds")

    def set_random_sleep_range(self, speed_1_to_5):
        if speed_1_to_5 == 1:
            s1 = SPEED_ZERO
            s2 = SPEED_UGLY
            speed = SPEED_ZERO
        elif speed_1_to_5 == 2:
            s1 = SPEED_UGLY
            s2 = SPEED_BAD
            speed = SPEED_UGLY
        elif speed_1_to_5 == 3:
            s1 = SPEED_BAD
            s2 = SPEED_GOOD
            speed = SPEED_BAD
        elif speed_1_to_5 == 4:
            s1 = SPEED_GOOD
            s2 = SPEED_GOOD
            speed = SPEED_GOOD
        elif speed_1_to_5 == 5:
            s1 = SPEED_SUPERFAST
            s2 = SPEED_SUPERFAST
            speed = SPEED_SUPERFAST
        else:
            print(COLOR_FAIL + f"Unexpected speed value: {speed_1_to_5}" + COLOR_ENDC)
            self.set_random_sleep_range(4)
            return

        self._set_random_sleep_range(speed, s1, s2)

    def update_random_sleep_range(self):
        try:
            speed = _get_internet_speed()
            if SPEED_ZERO <= speed <= SPEED_UGLY:
                s1 = SPEED_ZERO
                s2 = SPEED_UGLY
            elif SPEED_UGLY <= speed <= SPEED_BAD:
                s1 = SPEED_UGLY
                s2 = SPEED_BAD
            elif SPEED_BAD <= speed <= SPEED_GOOD:
                s1 = SPEED_BAD
                s2 = SPEED_GOOD
            else:
                s1 = SPEED_GOOD
                s2 = SPEED_GOOD

            self._set_random_sleep_range(speed, s1, s2)
        except Exception as ex:
            print(COLOR_FAIL + "Got an error while trying to measure the internet speed" + COLOR_ENDC)
            print(COLOR_FAIL + describe_exception(ex) + COLOR_ENDC)
            print(f"Sleep range will remain as default to be from {self.sleep_range_start:.2f} to {self.sleep_range_end:.2f} seconds")


def _get_internet_speed():
    from insomniac.tools import speedtest

    # Catch all possible exceptions from speedtest (e.g. crashed with TypeError)
    # noinspection PyBroadException
    try:
        s = speedtest.Speedtest()
        s.get_best_server()
        s.download(threads=1)
        s.upload(threads=1)
        results_dict = s.results.dict()
    except Exception as ex:
        print(COLOR_FAIL + "Failed to determine Internet speed, supposing it's zero" + COLOR_ENDC)
        print(COLOR_FAIL + describe_exception(ex) + COLOR_ENDC)
        return SPEED_ZERO

    download_speed = results_dict['download']
    upload_speed = results_dict['upload']
    print(f"Download speed {(download_speed / MEGABIT):.2f} Mbit/s, upload speed {(upload_speed / MEGABIT):.2f} Mbit/s")
    return (download_speed + upload_speed) / 2


sleeper = Sleeper()
