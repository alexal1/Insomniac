import json

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.dates import DateFormatter

from src.utils import *

A4_WIDTH_INCHES = 8.27
A4_HEIGHT_INCHES = 11.69


def main():
    username="admishchenko"

    sessions = _load_sessions(username)
    if not sessions:
        return

    followers_count = [session['profile']['followers'] for session in sessions]
    dates = [(datetime.strptime(session['start_time'], '%Y-%m-%d %H:%M:%S.%f')) for session in sessions]
    total_followed = [session['total_followed'] for session in sessions]
    total_unfollowed = [-session['total_unfollowed'] for session in sessions]
    total_likes = [session['total_likes'] for session in sessions]

    with PdfPages('test.pdf') as pdf:
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
                                                                       'Period: whole time.\n',
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


def _load_sessions(username):
    path = username + "/sessions.json"
    if os.path.exists(path):
        with open(path) as json_file:
            json_array = json.load(json_file)
        return json_array
    else:
        print_timeless(COLOR_FAIL + "No sessions.json file found for @" + username)
        return None


if __name__ == "__main__":
    main()
