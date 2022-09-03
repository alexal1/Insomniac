<br />
<p align="center">
    <img width="128" height="128" src="https://raw.githubusercontent.com/alexal1/Insomniac/master/res/insomniac.png" alt="Insomniac"/>
    <h1 align="center">Insomniac</h1>
    <p align="center">Simple and friendly automation tool which brings more followers to your Instagram account and engages existing audience. Automatic liking, commenting, following/unfollowing, scraping and sending direct messages. Everything works from your own Android phone/tablet/emulator under your full control. <b>No root required.</b></p>
    <p align="center">
        <a href="https://github.com/alexal1/Insomniac/releases">
            <img src="https://img.shields.io/pypi/v/insomniac?label=latest%20version"/>
        </a>
        <a href="https://www.python.org/downloads/release/python-3106/">
            <img src="https://img.shields.io/pypi/pyversions/insomniac"/>
        </a>
        <a href="https://pypi.org/project/insomniac/">
            <img src="https://img.shields.io/pypi/dm/insomniac"/>
        </a>
        <a href="https://insomniac-bot.com/get_latest_supported_ig_apk/">
            <img src="https://img.shields.io/endpoint?url=https://insomniac-bot.com/get_latest_supported_ig_version/"/>
        </a>
    </p>
</p>

### Why Automating Instagram Activity (Liking, Following, etc.)?
💸 If you want just to _increase_ your followers count or get more likes, there's a bunch of companies that will give you that immediately for a few $$$. But most likely your audience will be merely bots and mass-followers.

🌱 If you want to get engaged followers, that will be interested in your content and probably will pay you for your services, then _automation_ is the right way.

📈 This Instagram bot provides you methods to **target** on the audience that is most likely interested **in you**. Generally these methods are (with growing complexity):
1. Interact with users who follow specific **bloggers** or like posts by specific **hashtags**. _Easiest level, just one Insomniac command._
2. Same, but from those users interact only with your **target audience**. Meaning that you can pick users by specific parameters: by gender, by language, by posts count, etc. _Still one Insomniac command, but you'll have to add a file with "filtering" parameters._
3. **Scrape** your target audience from other accounts and use your main account only to interact. This reduces the app time-spent of your main account and makes the main account significantly less suspicious to Instagram. _You'll have to learn how to use Insomniac "configs" and combine them into an infinite loop – so that everything would work by itself._  

<br />
<p align="center">
    <img src="https://raw.githubusercontent.com/alexal1/Insomniac/master/res/demo.gif">
</p>

### Getting Started
We have an awesome [documentation](https://insomniac-bot.com/docs/) where you will find installation instructions for Windows, macOS, Ubuntu and Raspberry Pi.

Basically all you need is a machine with Python 3 and a connected Android phone. In case you don't have a phone, we have posts explaining how to make it work with a free Android emulator: [Windows](https://www.patreon.com/posts/how-to-install-43543116), [macOS](https://www.patreon.com/posts/how-to-install-43485861), [Ubuntu](https://www.patreon.com/posts/how-to-install-43485861).

Please use a specific Instagram app version which you can find in the header (click on the "IG version" badge). That's because Instagram UI gets changed pretty often, so we guarantee a stable work only on versions up to a specific number.

The simplest Insomniac command to start with would be something like this:
```
python3 start.py --interact @natgeo-followers
```
But better check the docs.

### Filtering
Eventually you will come to the point where you want to avoid accounts with thousands of followings. Or with zero posts. Or with some other red flags which you will choose for yourself. Here's the full list:

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

You can find how to use them in the [documentation](https://insomniac-bot.com/docs/#/?id=filters). But don't tense up, it's as easy as create a file called "filters.json" and put it into a folder.

### Command-Line Arguments vs Configs
At some point we realised that there appeared so many Insomniac command-line arguments that they became difficult to handle.

_Tip: by the way, you can see all available commands by running `python3 start.py` with no arguments._

What we did is we introduced a concept of "configs". So instead of writing a veeeery long command like this:
```
python3 start.py --interact @natgeo-followers @natgeo-following amazingtrips-top-likers amazingtrips-recent-likers P-antartica-top-likers P-antartica-recent-likers amazingtrips-top-posts amazingtrips-recent-posts P-antartica-top-posts P-antartica-recent-posts --speed 4 --wait-for-device --likes-count "1-2" --likes-percentage "75" --interactions-limit-per-source "12-16" --successful-interactions-limit-per-source "6-8" --total-interactions-limit "100-200" --total-successful-interactions-limit "50-60" --total-likes-limit "50-60" --total-get-profile-limit "300-400" --session-length-in-mins-limit "50-60"
```
You can just write this:
```
python3 start.py --config-file interact-likes-only.json
```
Where [interact-likes-only.json](https://github.com/alexal1/Insomniac/blob/master/config-examples/interact/interact-likes-only.json) is a config file which you will just put in the folder where you run the command from.

The interesting thing about configs is that you can add a field `next_config_file` in any config. So a config will launch another config. You can also specify a sleeping time between them using the `repeat` field (in minutes). Using this technique you can create infinite loops of configs, see examples [here](https://github.com/alexal1/Insomniac/tree/master/config-examples/flow-of-actions). Such loops are called _flows_.

### Scraping and Interacting with Targets
Basically to interact with targets you can run
```
python3 start.py --interact-targets
```
This means that Insomniac will search for targets either in [targets.txt](https://github.com/alexal1/Insomniac/blob/master/targets.txt) file (if provided) or in the database. The only way for targets to appear in the database is to use [scraping](https://insomniac-bot.com/docs/#/?id=scraping). Scraping basically means searching for specific accounts to interact with _as the targets for the main account_. So when scraping you always have to specify this main account like this: `--scrape-for-account username`.

See scraping config examples [here](https://github.com/alexal1/Insomniac/tree/master/config-examples-extra/scrape).

### Extra Features
As you can imagine, this project's development and support takes a lot of energy, so in order to continue working we made part of the features paid. These features are called _extra features_, because they are not necessary to run the project. But most likely you'd like to have them.

You can find the full list of extra features in the [documentation](https://insomniac-bot.com/docs/#/?id=extra-features).

As a free bonus you'll get a Telegram bot [@your_insomniac_bot](https://t.me/your_insomniac_bot) which can send you current stats. So you'll be able to monitor your setup health from anywhere. Read more in one of our [Patreon posts](https://www.patreon.com/posts/v3-8-0-update-63591855).

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
