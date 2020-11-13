from croniter import croniter

from insomniac.utils import *


def is_at_working_hour(working_hours):
    start_work_hour, stop_work_hour = 1, 24

    if working_hours:
        start_work_hour, stop_work_hour = get_left_right_values(working_hours, "Working hours {}", (9, 21))

        if not (1 <= start_work_hour <= 24):
            print(COLOR_FAIL + "Working-hours left-boundary ({0}) is not valid. "
                               "Using (9) instead".format(start_work_hour) + COLOR_ENDC)
            start_work_hour = 9

        if not (1 <= stop_work_hour <= 24):
            print(COLOR_FAIL + "Working-hours right-boundary ({0}) is not valid. "
                               "Using (21) instead".format(stop_work_hour) + COLOR_ENDC)
            stop_work_hour = 21

    now = datetime.now()

    if not (start_work_hour <= now.hour <= stop_work_hour):
        print("Current Time: {0} which is out of working-time range ({1}-{2})"
              .format(now.strftime("%H:%M:%S"), start_work_hour, stop_work_hour))
        next_execution = '0 {0} * * *'.format(start_work_hour)

        time_till_next_execution_seconds = (croniter(next_execution, now).get_next(datetime) - now).seconds + 60

        return False, time_till_next_execution_seconds

    return True, 0
