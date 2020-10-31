<img align="left" width="80" height="80" src="https://raw.githubusercontent.com/alexal1/Insomniac/master/res/icon.jpg" alt="Insomniac">

# Insomniac
![PyPI](https://img.shields.io/pypi/v/insomniac?label=latest%20version)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/insomniac)
![PyPI - Downloads](https://img.shields.io/pypi/dm/insomniac)

Liking and following automatically on your Android phone/tablet. No root required: it works on [UI Automator](https://developer.android.com/training/testing/ui-automator), which is an official Android UI testing framework.

<img src="https://raw.githubusercontent.com/alexal1/Insomniac/master/res/demo.gif">

### Table of contents
- [Why you should automate Instagram activity (liking, following, etc.)?](#why-you-should-automate-instagram-activity-liking-following-etc)
- [How to install](#how-to-install)
    * [How to install on Raspberry Pi OS](#how-to-install-on-raspberry-pi-os)
- [Get started](#get-started)
    * [Usage example](#usage-example)
    * [Full list of command line arguments](#full-list-of-command-line-arguments)
    * [FAQ](#faq)
- [Extra features](#extra-features)
- [Source code](#source-code)
- [Filtering](#filtering)
- [Whitelist and Blacklist](#whitelist-and-blacklist)
- [Analytics](#analytics)
- [Features in progress](#features-in-progress)
- [Why Insomniac?](#why-insomniac)
- [Community](#community)

### Why you should automate Instagram activity (liking, following, etc.)?
💸 If you want just to _increase_ your followers count or get more likes, there's a bunch of companies that will give you that immediately for a few $$$. But most likely your audience will be bots and mass-followers.

🌱 If you want to get engaged followers, that will be interested in your content and probably will pay you for your services, then _automation_ is the right way.

🎯 This Instagram bot provides you methods to **target** on the audience that is most likely interested **in you**. These methods are:
1. Interact with followers of **bloggers** with similar content
2. Interact with likers of **hashtags** that you use
3. **Filter** accounts to avoid bots and mass-followers

📈 Using these methods altogether gives the best result.

### How to install
1. Run `python3 -m pip install insomniac` in Terminal / Command Prompt<br/><sub><sup>Provided **python** and **pip** are installed already. Learn <a href="https://github.com/alexal1/Insomniac/wiki/Install-Python">how to check it</a>.</sup></sub>
2. Save [start.py](https://raw.githubusercontent.com/alexal1/Insomniac/master/start.py) file which launches the script
2. Download and unzip [Android platform tools](https://developer.android.com/studio/releases/platform-tools), move them to a folder where you won't delete them accidentally, e.g.
```
mkdir -p ~/Library/Android/sdk
mv <path-to-downloads>/platform-tools/ ~/Library/Android/sdk
```
3. [Add platform-tools path to the PATH environment variable](https://github.com/alexal1/Insomniac/wiki/Adding-platform-tools-to-the-PATH-environment-variable). If you do it correctly, Terminal / Command Prompt command `adb devices` will print `List of devices attached`

### How to install on Raspberry Pi OS
1. Update apt-get: `sudo apt-get update`
2. Install ADB and Fastboot: `sudo apt-get install -y android-tools-adb android-tools-fastboot`
3. Install insomniac: `python3 -m pip install insomniac`
4. Save [start.py](https://raw.githubusercontent.com/alexal1/Insomniac/master/start.py) file

### Get started
1. Connect Android device to your computer with a USB cable
2. Enable [Developer options](https://developer.android.com/studio/debug/dev-options#enable) on the device
>On Android 4.1 and lower, the Developer options screen is available by default. On Android 4.2 and higher, you must enable this screen. To enable developer options, tap the Build Number option 7 times. You can find this option in one of the following locations, depending on your Android version:
>
> Android 9 (API level 28) and higher: Settings > About Phone > Build Number
>
> Android 8.0.0 (API level 26) and Android 8.1.0 (API level 26): Settings > System > About Phone > Build Number
>
> Android 7.1 (API level 25) and lower: Settings > About Phone > Build Number
3. Switch on **USB debugging** (and also **Install apps via USB** and **Allow ADB debugging in charge only mode** if there are such options) on the Developer options screen.
4. Device will ask you to allow computer connection. Press "Connect"
5. Type `adb devices` in terminal. It will display attached devices. There should be exactly one device. Then run the script (it works on Python 3):
6. Open Terminal / Command Prompt in the folder with downloaded [start.py](https://raw.githubusercontent.com/alexal1/Insomniac/master/start.py) (or type `cd <path-to-start.py>`) and run
```
python3 start.py --interact @natgeo
```
Make sure that the screen is turned on and device is unblocked. You don't have to open Instagram app, script opens it and closes when it's finished. Just make sure that Instagram app is installed. If everything's fine, script will open `@natgeo`'s followers and like their posts.

### Usage example
Let's say you have a travel blog. Then you may want to use such setup:
```
python3 start.py --interact @natgeo amazingtrips beautifuldestinations --interactions-count 20-30 --likes-count 1-3 --follow-percentage 20 --repeat 120-180
```
The script will sequentially interact with 20-30 `@natgeo`'s followers, 20-30 `#amazingtrips` posts likers, and 20-30 `#beautifuldestinations` posts likers. During each interaction it will like 1-3 random posts and also follow 20% of interacted users. After finished it will close Instagram app and wait for 120-180 minutes. Then the script will repeat the same (and will repeat infinitely), but already interacted users will be ignored. The list of sources (`@natgeo`, `#amazingtrips` and `#beutifuldestinations`) will be shuffled each time.

All this randomness makes it very hard for Instagram to detect that you're using a bot. However, be careful with number of interactions, because even a human can be banned for violating limits.

### Full list of command line arguments
You can also see this list by running with no arguments: `python3 start.py`.
```
  --interact hashtag [@username ...]
                        list of hashtags and usernames. Usernames should start
                        with "@" symbol. The script will interact with
                        hashtags' posts likers and with users' followers
  --likes-count 2-4     number of likes for each interacted user, 2 by
                        default. It can be a number (e.g. 2) or a range (e.g.
                        2-4)
  --total-likes-limit 300
                        limit on total amount of likes during the session, 300
                        by default
  --interactions-count 60-80
                        number of interactions per each blogger, 70 by
                        default. It can be a number (e.g. 70) or a range (e.g.
                        60-80). Only successful interactions count
  --repeat 120-180      repeat the same session again after N minutes after
                        completion, disabled by default. It can be a number of
                        minutes (e.g. 180) or a range (e.g. 120-180)
  --follow-percentage 50
                        follow given percentage of interacted users, 0 by
                        default
  --follow-limit 50     limit on amount of follows during interaction with
                        each one user's followers, disabled by default
  --unfollow 100-200    unfollow at most given number of users. Only users
                        followed by this script will be unfollowed. The order
                        is from oldest to newest followings. It can be a
                        number (e.g. 100) or a range (e.g. 100-200)
  --unfollow-non-followers 100-200
                        unfollow at most given number of users, that don't
                        follow you back. Only users followed by this script
                        will be unfollowed. The order is from oldest to newest
                        followings. It can be a number (e.g. 100) or a range
                        (e.g. 100-200)
  --unfollow-any 100-200
                        unfollow at most given number of users. The order is
                        from oldest to newest followings. It can be a number
                        (e.g. 100) or a range (e.g. 100-200)
  --min-following 100   minimum amount of followings, after reaching this
                        amount unfollow stops
  --device 2443de990e017ece
                        device identifier. Should be used only when multiple
                        devices are connected at once
  --old                 add this flag to use an old version of uiautomator.
                        Use it only if you experience problems with the
                        default version
  --remove-mass-followers 10
                        Remove given number of mass followers from the list of
                        your followers. "Mass followers" are those who has
                        more than N followings, where N can be set via --max-
                        following
  --max-following 1000  Should be used together with --remove-mass-followers.
                        Specifies max number of followings for any your
                        follower, 1000 by default
```

### FAQ
- How to stop the script?<br/>_Ctrl+C (control+C for Mac)_

- Can I prevent my phone from falling asleep while the script is working?<br/>_Yes. Settings -> Developer Options -> Stay awake._

- What to do if I got soft ban (cannot like/follow/comment)?<br/>_Clear Instagram application data. You'll have to login again and then it will work as usual. But it's **highly recommended** to lower your interactions count for the future and take a pause with the script._

- [How to connect Android phone via WiFi?](https://www.patreon.com/posts/connect-android-43141956)

- [How to run on 2 or more devices at once?](https://www.patreon.com/posts/running-script-43143021)

- [Script crashes with **OSError: RPC server not started!** or **ReadTimeoutError**](https://www.patreon.com/posts/problems-with-to-43143682)

### Extra features
All core features in this project are free to use. But you may want to get more fine grained control over the bot via these features:
- **Filtering** - skip unwanted accounts by various parameters, [more here](#filtering)
- **Removing mass followers** - automate "cleaning" your account
- **Analytics tool** - build presentation that shows your growth, [more here](#analytics)
- **Scrapping (next release)** - will make interactions significantly safer and faster

Activate these features by supporting our small team on Patreon: [https://insomniac-bot.com/activate/](https://insomniac-bot.com/activate/).

### Source code
Since core features are free to use, their code is right here in the [src folder](https://github.com/alexal1/Insomniac/tree/master/src). You can help the community by making a pull request. It will be added to the packaged version after successful review. To work with sources, please
1. Clone the project: `git clone https://github.com/alexal1/Insomniac.git`
2. Go to Insomniac folder: `cd Insomniac`
3. Install required libraries: `python3 -m pip install -r requirements.txt`
4. Launch the script via `python3 -m src.insomniac`

Note that [src](https://github.com/alexal1/Insomniac/tree/master/src) code may differ from the packaged code. Generally, the packaged code is more stable.

_2020-10-31: Right now there's quite big difference, but we will synchronize packaged and opensource version ASAP._

### Filtering
You may want to ignore mass-followers (e.g. > 1000 followings) because they are most likely interested only in growing their audience. Or ignore too popular accounts (e.g. > 5000 followers) because they won't notice you. You can do this (and more) by using the filter:

| Parameter                 | Value         | Description                                                                                            |
| ------------------------- | ------------- | ------------------------------------------------------------------------------------------------------ |
| `skip_business`           | `true/false`  | skip business accounts if true                                                                         |
| `skip_non_business`       | `true/false`  | skip non-business accounts if true                                                                     |
| `min_followers`           | 100           | skip accounts with less followers than given value                                                     |
| `max_followers`           | 5000          | skip accounts with more followers than given value                                                     |
| `min_followings`          | 10            | skip accounts with less followings than given value                                                    |
| `max_followings`          | 1000          | skip accounts with more followings than given value                                                    |
| `min_potency_ratio`       | 1             | skip accounts with ratio (followers/followings) less than given value (decimal values can be used too) |
| `follow_private_or_empty` | `true/false`  | private/empty accounts also have a chance to be followed if true                                       |

You can read detailed explanation and instructions how to use it [in the Patreon post](https://www.patreon.com/posts/43362005) **(you'll have to join $10 tier)**.

### Whitelist and Blacklist
**Whitelist** – affects `--remove-mass-followers`, `--unfollow` and all other unfollow actions. Users from this list will _never_ be removed from your followers or unfollowed.

**Blacklist** - affects _all other actions_. Users from this list will be skipped immediately: no interactions and no following.

Go to Insomniac folder and create a folder named as your Instagram nickname (or open an existing one, as Insomniac creates such folder when launched). Create there a file `whitelist.txt` or `blacklist.txt` (or both of them). Write usernames in these files, one username per line, no `@`'s, no commas. Don't forget to save. That's it! 

### Analytics
There also is an analytics tool for this bot. It is a script that builds a report in PDF format. The report contains account's followers growth graphs for different periods. Liking, following and unfollowing actions' amounts are on the same axis to determine bot effectiveness. The report also contains stats of sessions length for different configurations that you've used. All data is taken from `sessions.json` file that's generated during bot's execution.
<img src="https://raw.githubusercontent.com/alexal1/Insomniac/master/res/analytics_sample.png">

To get access to the analytics tool you have to [join Patreon $10 tier](https://www.patreon.com/insomniac_bot).

### Features in progress
- [x] Follow given percentage of interacted users by `--follow-percentage 50`
- [x] Unfollow given number of users (only those who were followed by the script) by `--unfollow 100`
- [x] Unfollow given number of non-followers (only those who were followed by the script) by `--unfollow-non-followers 100`
- [x] Support intervals for likes and interactions count like `--likes-count 2-3`
- [x] Interaction by hashtags
- [ ] Add random actions to behave more like a human (watch your own feed, stories, etc.)
- [ ] Commenting during interaction

### Why Insomniac?
There already are Instagram automation tools that work either on Instagram web version or via Instagram private API. Unfortunately, both ways have become dangerous to use. Instagram bots detection system is very suspicious to browser actions now. And as for private API – you will be blocked forever if Instagram detects that you're using it.

That's why need arised in a solution for mobile devices. Instagram can't distinguish bot from a human when it comes to your phone. However, even a human can reach limits when using the app, so don't fail to be careful. Always set `--total-likes-limit` to 300 or less. Also it's better to use `--repeat` to act periodically for 2-3 hours, because Instagram keeps track of how long the app works.

### Community
We have a [Discord server](https://discord.gg/59pUYCw) which is the most convenient place to discuss all bugs, new features, Instagram limits, etc. If you're not familiar with Discord, you can also join our [Telegram chat](https://t.me/insomniac_chat). And finally, all useful info is posted on our [Patreon page](https://www.patreon.com/insomniac_bot).

<p>
  <a href="https://discord.gg/59pUYCw">
    <img hspace="3" alt="Discord Server" src="https://raw.githubusercontent.com/alexal1/Insomniac/master/res/discord.png" height=84/>
  </a>
  <a href="https://t.me/insomniac_chat">
    <img hspace="3" alt="Telegram Chat" src="https://raw.githubusercontent.com/alexal1/Insomniac/master/res/telegram.png" height=84/>
  </a>
  <a href="https://www.patreon.com/insomniac_bot">
    <img hspace="3" alt="Patreon Page" src="https://raw.githubusercontent.com/alexal1/Insomniac/master/res/patreon.png" height=84/>
  </a>
</p>
