## Installation
See the [Installation](/installation) page.

Looking for a more thorough explanation? Then try our [Udemy Course](https://insomniac-bot.com/udemy_course/). 

## Quick start

Open Command Prompt / Terminal in a folder with [start.py](https://raw.githubusercontent.com/alexal1/Insomniac/master/start.py) file _or_ just open Command Prompt and use `cd path/to/folder`. Then make sure that Android phone / emulator is connected by running `adb devices` (should print one device). Run the script by command
```
python3 start.py --interact @natgeo
```
This is a basic command that will start interaction with @natgeo's followers with default parameters. The script will open Instagram app itself and close it when finished. To stop immediately press _Ctrl+C_ (_control+C_ on Mac).

## How to update

**TL;DR** `python3 -m pip install --upgrade insomniac`

Doesn't work for you or want more details? Please check [How to update](/how-to-update) page.

## Core features
"Core" features means everything you need for basic usage of Insomniac. This is an [open source](https://github.com/alexal1/Insomniac/tree/master/insomniac) part of the project. If you feel that you need more – welcome to the [Extra features](/?id=extra-features) section.

_Note that you can print the list of features by running `python start.py` with no arguments._

### Interaction
"Interaction" is the main job of this bot: we interact with our potential audience to gain its attention.

#### --interact amazingtrips-top-likers [@natgeo-followers ...]
list of hashtags, usernames, or places. Usernames should start with "@" symbol. Places should start with "P-" symbols. You can specify the way of interaction after a "-" sign: @natgeo-followers, @natgeo-following, amazingtrips-top-likers, amazingtrips-recent-likers, P-Paris-top-likers, P-Paris-recent-likers
#### --likes-count 2-4
number of likes for each interacted user, 2 by default. It can be a number (e.g. 2) or a range (e.g. 2-4)
#### --like-percentage 50
likes given percentage of interacted users, 100 by default
#### --follow-percentage 50
follow given percentage of interacted users, 0 by default
#### --stories-count 3-8
number of stories to watch for each user, disabled by default. It can be a number (e.g. 2) or a range (e.g. 2-4)
#### --comments-list WOW! [What a picture! ...]
list of comments you wish to comment on posts during interaction
#### --comment-percentage 50
comment given percentage of interacted users, 0 by default
#### --interaction-users-amount 3-8
add this argument to select an amount of users from the interact-list (users are randomized). It can be a number (e.g. 4) or a range (e.g. 3-8)
#### --reinteract-after 150
set a time (in hours) to wait before re-interact with an already interacted profile, disabled by default (won't interact again). It can be a number (e.g. 48) or a range (e.g. 50-80)
#### --interact-targets True / False
use this argument in order to interact with profiles from targets.txt

### Unfollowing
While interaction lets you follow users, "unfollowing" lets you revert it back after a while.

#### --unfollow 100-200
unfollow at most given number of users. Only users followed by this script will be unfollowed. The order is from oldest to newest followings. It can be a number (e.g. 100) or a range (e.g. 100-200)
#### --unfollow-followed-by-anyone
By default, only profiles that been followed by the bot will be unfollowed. Set this parameter if you want to unfollow any profile (even if not been followed by the bot)
#### --unfollow-non-followers
unfollow only profiles that are not following you
#### --unfollow-source list
you can specify where to take the users to unfollow from. Can be one of the values: profile / list. "profile" means unfollowing your profile\'s followings. "list" means unfollowing from the "unfollow.txt" file (**extra feature**). By default "profile" is used
#### --following-sort-order latest
sort the following-list when unfollowing users from the list. Can be one of values: default / latest / earliest. By default sorting by earliest                   
#### --recheck-follow-status-after 150
set a time (in hours) to wait before re-check follow status of a profile, disabled by default (will check every time when needed). It can be a number (e.g. 48) or a range (e.g. 50-80)

### Limits
"Limits" are our defense against Instagram bots-detection system. Use limits to make your bot behave like a human. There are no strict rules of how to use limits because Instagram can be less or more suspicious depending on your account age, type of network (WiFi/Cellular) and other parameters.

#### --successful-interactions-limit-per-source 40
number of successful-interactions per each
blogger/hashtag, 70 by default. It can be a number
(e.g. 70) or a range (e.g. 60-80)

#### --interactions-limit-per-source 40
number of interactions (successful & non-successful)
per each blogger/hashtag, 140 by default. It can be a
number (e.g. 140) or a range (e.g. 60-80)

#### --total-successful-interactions-limit 60-80
number of total successful interactions per session,
disabled by default. It can be a number (e.g. 70) or a
range (e.g. 60-80)

#### --total-interactions-limit 60-80
number of total interactions (successful &
unsuccessful) per session, disabled by default. It can
be a number (e.g. 70) or a range (e.g. 60-80)

#### --total-likes-limit 300
limit on total amount of likes during the session, 300
by default. It can be a number presenting specific
limit (e.g. 300) or a range (e.g. 100-120)

#### --follow-limit-per-source 7-8
limit on amount of follows during interaction with
each one user's followers, disabled by default. It can
be a number (e.g. 10) or a range (e.g. 6-9)

#### --total-follow-limit 50
limit on total amount of follows during the session,
disabled by default. It can be a number (e.g. 27) or a
range (e.g. 20-30)

#### --total-story-limit 300
limit on total amount of stories watches during the
session, disabled by default. It can be a number (e.g.
27) or a range (e.g. 20-30)

#### --total-comments-limit 300
limit on total amount of comments during the session,
50 by default. It can be a number presenting specific
limit (e.g. 300) or a range (e.g. 100-120)

#### --total-get-profile-limit 1500
limit on total amount of get-profile actions during
the session, disabled by default. It can be a number
(e.g. 600) or a range (e.g. 500-700)

#### --min-following 100
minimum amount of followings, after reaching this
amount unfollow stops

#### --max-following 100
maximum amount of followings, after reaching this
amount follow stops. disabled by default
  
#### --session-length-in-mins-limit 50-60
limit the session length by time (minutes), disabled
by default. It can be a number (e.g. 60) or a range
(e.g. 40-70)

### Sessions Flow
You can setup Insomniac to work infinitely: _interact > sleep > interact > sleep > unfollow > sleep >_ ... etc. That's why we call it a "flow". Read more [in our blogpost](https://www.patreon.com/posts/sessions-flows-45849501).

_Consider using config files even if you don't want an "infinite" work! Config files are the [recommended](https://www.patreon.com/posts/configuration-of-43899836) way for regular users!_

#### --repeat 120-180
repeat the same session again after N minutes after
completion, disabled by default. It can be a number of
minutes (e.g. 180) or a range (e.g. 120-180)

#### --config-file CONFIG_FILE
add this argument if you want to load your
configuration from a config file. Example can be found
in [config-examples](https://github.com/alexal1/Insomniac/tree/master/config-examples) folder
                        
#### --next-config-file CONFIG_FILE
configuration that will be loaded after session is
finished and the bot "sleeps" for time specified by
the "--repeat" argument. You can use this argument to
run multiple Insomniac sessions one by one with
different parameters. E.g. different action (interact
and then unfollow), or different "--username". By
default uses the same config file as been loaded for
the first session. Note that you must use "--repeat"
with this argument!

#### --send-stats
add this flag to send your anonymous statistics to the Telegram bot @your_insomniac_bot. This is useful when insomniac runs infinitely and you want to be able to track progress remotely 

### Advanced
Options for savvy users.

#### --old
add this flag to use an old version of uiautomator.
Use it only if you experience problems with the
default version
                        
#### --device 2443de990e017ece
device identifier. Should be used only when multiple
devices are connected at once

#### --no-speed-check
skip internet speed check at start

#### --no-ig-version-check
skip Instagram version check at start

#### --no-ig-connection-check
skip Instagram connection check at start

#### --speed
manually specify the speed setting, from 1 (slowest) to 4 (fastest). There's also 5 (superfast) but it's not recommended

#### --no-typing
disable "typing" feature (typing symbols one-by-one as a human)

#### --wait-for-device
keep waiting for ADB-device to be ready for connection
(if no device-id is provided using --device flag, will
wait for any available device)

#### --username my_account_name
if you have configured multiple Instagram accounts in
your app, use this parameter in order to switch into a
specific one. Not trying to switch account by default.
If the account does not exist – the session won't
start

#### --app-id com.instagram.android
apk package identifier. Should be used only if you are
using cloned-app. Using 'com.instagram.android' by
default

#### --dont-indicate-softban
by default, Insomniac tries to indicate if there is a
softban on your acoount. Set this flag in order to
ignore those softban indicators

#### --fetch-profiles-from-net
add this flag to fetch profiles from the internet 
instead of opening each user's profile on a device

#### --debug
add this flag to run insomniac in debug mode (more verbose
logs)

## Extra features
Get "extra" features by supporting us via [Patreon $10 tier](https://www.patreon.com/join/insomniac_bot). You'll receive an email with activation code for your [start.py](https://raw.githubusercontent.com/alexal1/Insomniac/master/start.py).

Patreon is our way of monetizing the project. It gives us motivation to constantly improve both "core" and "extra" features.

### Filters
You can skip profiles that don't match your needs. E.g. ignore mass-followers (more than 1000 followings) or ignore too popular accounts (more than 5000 followers). You can do this and more by using **filter.json** file. List of available parameters:

| Parameter                         | Value                                                       | Description                                                                                                  |
| --------------------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------|
| `skip_business`                   | `true/false`                                                | skip business accounts if true                                                                               |
| `skip_non_business`               | `true/false`                                                | skip non-business accounts if true                                                                           |
| `min_followers`                   | 100                                                         | skip accounts with less followers than given value                                                           |
| `max_followers`                   | 5000                                                        | skip accounts with more followers than given value                                                           |
| `min_followings`                  | 10                                                          | skip accounts with less followings than given value                                                          |
| `max_followings`                  | 1000                                                        | skip accounts with more followings than given value                                                          |
| `min_potency_ratio`               | 1                                                           | skip accounts with ratio (followers/followings) less than given value (decimal values can be used too)       |
| `max_potency_ratio`               | 1                                                           | skip accounts with ratio (followers/followings) higher than given value (decimal values can be used too)     |
| `privacy_relation`      `         | `"only_public"` / `"only_private"` / `"private_and_public"` | choose with accounts of which type you want to interact, `"only_public"` by default                          |
| `min_posts`                       | 7                                                           | minimum posts in profile in order to interact                                                                |
| `max_digits_in_profile_name`      | 4                                                           | maximum amount of digits in profile name (more than that - won't be interacted)                              |
| `skip_profiles_without_stories`   | `true/false`                                                | skip accounts that doesnt have updated story (from last 24 hours)                                            |
| `blacklist_words`                 | `["word1", "word2", "word3", ...]`                          | skip accounts that contains one of the words in the list in the profile biography                            |
| `mandatory_words`                 | `["word1", "word2", "word3", ...]`                          | skip accounts that doesn't have one of the words in the list in the profile biography                        |
| `specific_alphabet`               | `["LATIN", "ARABIC", "GREEK", "HEBREW", ...]`               | skip accounts that contains text in their biography/username which different than the provided alphabet list |
| `skip_already_following_profiles` | `true/false`                                                | skip accounts that your profile already followed, even if not followed by the bot                            |
| `only_profiles_with_faces`        | `"male"/"female"/"any"`                                     | analyze profile picture and leave only profiles with male/female/any face on the avatar                      |

Read how to use filters [in our blogpost](https://www.patreon.com/posts/43362005).

#### --refilter-after 150
set a time (in hours) to wait before re-filter an
already filtered profile, disabled by default (will
drop the profile and won't filter again). It can be a
number (e.g. 48) or a range (e.g. 50-80)
                        
#### --filters FILTERS
add this argument if you want to pass filters as an
argument and not from filters.json file

### Scraping
"Scraping" is a technique that lets you interact with much more users per session without being detected by Instagram as "suspiciously active" user. The idea is to use another IG account to filter users and your main IG account to actually interact. Read more about scraping [in our blogpost](https://www.patreon.com/posts/scrapping-what-43902968).

#### --scrape hashtag-top-likers [@username-followers ...]
list of hashtags, usernames, or places. Usernames
should start with "@" symbol. Places should start with
"P-" symbols. You can specify the way of interaction
after a "-" sign: @natgeo-followers, @natgeo-
following, amazingtrips-top-likers, amazingtrips-
recent-likers, P-Paris-top-likers, P-Paris-recent-
likers

#### --scrape-for-account your_profile [your_profile ...]
add this argument in order to just scrape targeted
profiles for an account. The scraped profiles names
will be added to database at target account directory

#### --scrape-users-amount 3-8
add this argument to select an amount of sources from
the scraping-list (sources are randomized). It can be a
number (e.g. 4) or a range (e.g. 3-8)
                        
### Special features
Other features that are unblocked by [joining Patreon $10 tier](https://www.patreon.com/join/insomniac_bot):

#### --warmup-time-before-session 2-6
Set warmup length in minutes, disabled by default. 
It can be a number (e.g. 2) or a range (e.g. 1-3).

#### --remove-mass-followers 10-20
Remove given number of mass followers from the list of
your followers. "Mass followers" are those who has
more than N followings, where N can be set via --max-
following. It can be a number (e.g. 4) or a range
(e.g. 3-8)

#### --mass-follower-min-following 1000
Should be used together with --remove-mass-followers.
Specifies max number of followings for any your
follower, 1000 by default

### Limits
Limits that come together with extra features.

#### --scrape-limit-per-source 40-60
number of profiles-scrapping per each blogger/hashtag,
disabled by default. It can be a number (e.g. 70) or a
range (e.g. 50-80)
                   
#### --total-scrape-limit 150
limit on total amount of profiles-scrapping during the
session, disabled by default. It can be a number (e.g.
100) or a range (e.g. 90-120)

#### --working-hours 9-21
set working hours to the script, disabled by default. 
It can be a number presenting specific hour (e.g. 13)
or a range (e.g. 9-21). Notice that right value must
be higher than the left value.

#### --working-hours-without-sleep 9-21
if you use flow, you maybe don't want to wait for 
working-hours on a specific session, because the 
following session in the flow might be in the working 
hours and you don't want to stop the flow. If that's the 
case, use this parameter

#### --direct-messages-limit 10
limit on total amount of DMs-actions during the current session, disabled by default. It can be a number (e.g. 10) or a range (e.g. 9-12)

### Unfollowing
More unfollowing options will be unblocked.

#### --unfollow-source database
you can specify where to take the users to unfollow from. Can be one of the values: profile / list / database. 
"profile" means unfollowing your profile\'s followings. 
"list" means unfollowing from the "unfollow.txt" file. 
"database" means unfollowing from the database sorted by date of following (older go first). 
"database-global-search" is the same as "database", but searches in global search. 
By default "profile" is used

#### --unfollow-older-than-days
if using "--unfollow-source database", you can specify how long ago an account has to be followed, to unfollow it now. 
Specify number of days. 7 days by default

### Direct Messages
Sending direct messages.

#### --dm-list "Hey bro!" ["What's up bro" ...]
List of messages to pick a random one to send. Spintax supported

#### --dm-to-new-followers
Send direct messages to the given amount of new followers

#### --dm-to-followed-by-bot-only
If true, messages will be sent only to users whom we are following

#### --dm-max-old-followers-in-a-row 30
Stop looking for new followers if seeing this amount of old followers in a row

### Advanced
More options for savvy users!

#### --pre-session-script /path/to/my/script.sh or .bat
use this parameter if you want to run a predefined
script when session starts

#### --post-session-script /path/to/my/script.sh or .bat
use this parameter if you want to run a predefined
script when session ends
