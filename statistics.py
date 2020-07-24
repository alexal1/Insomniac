import json
from datetime import timedelta
from enum import Enum, unique

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.dates import DateFormatter

from src.utils import *

A4_WIDTH_INCHES = 8.27
A4_HEIGHT_INCHES = 11.69


def main():
    username = "admishchenko"

    sessions = _load_sessions(username)
    if not sessions:
        return

    with PdfPages('statistics_' + username + '.pdf') as pdf:
        sessions_week = filter_sessions(sessions, Period.LAST_WEEK)
        plot_followers_growth(sessions_week, pdf, username, Period.LAST_WEEK)

        sessions_month = filter_sessions(sessions, Period.LAST_MONTH)
        plot_followers_growth(sessions_month, pdf, username, Period.LAST_MONTH)

        plot_followers_growth(sessions, pdf, username, Period.ALL_TIME)


def _load_sessions(username):
    path = username + "/sessions.json"
    if os.path.exists(path):
        with open(path) as json_file:
            json_array = json.load(json_file)
        return json_array
    else:
        print_timeless(COLOR_FAIL + "No sessions.json file found for @" + username)
        return None


def plot_followers_growth(sessions, pdf, username, period):
    followers_count = [session['profile']['followers'] for session in sessions]
    dates = [get_start_time(session) for session in sessions]
    total_followed = [session['total_followed'] for session in sessions]
    total_unfollowed = [-session['total_unfollowed'] for session in sessions]
    total_likes = [session['total_likes'] for session in sessions]

    fig, (axes1, axes2, axes3) = plt.subplots(ncols=1,
                                              nrows=3,
                                              sharex='row',
                                              figsize=(A4_WIDTH_INCHES, A4_HEIGHT_INCHES),
                                              gridspec_kw={
                                                  'height_ratios': [4, 1, 1]
                                              })

    fig.subplots_adjust(top=0.8, hspace=0.05)

    formatter = DateFormatter('%B %dth')
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_formatter(formatter)

    axes1.plot(dates, followers_count, marker='o')
    axes1.set_ylabel('Followers')
    axes1.xaxis.grid(True, linestyle='--')
    axes1.set_title('Followers growth for account "@' + username + '".\nThis page shows correlation between '
                                                                   'followers count and Insomniac actions:\n'
                                                                   'follows, unfollows, and likes.\n\n'
                                                                   'Period: ' + period.value + '.\n',
                    fontsize=12,
                    x=0,
                    horizontalalignment='left')

    axes2.fill_between(dates, total_followed, 0, color='#00CCFF', alpha=0.4)
    axes2.fill_between(dates, total_unfollowed, 0, color='#F94949', alpha=0.4)
    axes2.set_ylabel('Follows / unfollows')
    axes2.xaxis.grid(True, linestyle='--')

    axes3.fill_between(dates, total_likes, 0, color='#78EF7B', alpha=0.4)
    axes3.set_ylabel('Likes')
    axes3.set_xlabel('Date')
    axes3.xaxis.grid(True, linestyle='--')

    pdf.savefig()
    plt.close()


def filter_sessions(sessions, period):
    if period == Period.LAST_WEEK:
        week_ago = datetime.now() - timedelta(weeks=1)
        return list(filter(lambda session: get_start_time(session) > week_ago, sessions))
    if period == Period.LAST_MONTH:
        month_ago = datetime.now() - timedelta(days=30)
        return list(filter(lambda session: get_start_time(session) > month_ago, sessions))
    if period == Period.ALL_TIME:
        return sessions


def get_start_time(session):
    return datetime.strptime(session['start_time'], '%Y-%m-%d %H:%M:%S.%f')


@unique
class Period(Enum):
    LAST_WEEK = "last week"
    LAST_MONTH = "last month"
    ALL_TIME = "all time"


if __name__ == "__main__":
    main()
