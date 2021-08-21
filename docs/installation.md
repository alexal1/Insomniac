[< Back to the documentation](/#)

## Installation
If you prefer video lessons, welcome to the [Udemy Course](https://insomniac-bot.com/udemy_course/). We'll go through all installation steps together!

### Windows
1. Download and install python from [python.org](https://www.python.org/downloads/windows/). Better choose latest stable release.
2. Open Command Prompt.
3. Run `python -m pip install --upgrade pip` to make sure you've got the latest pip version.
4. Run `python -m pip install insomniac` to install insomniac package.
5. Download [start.py](https://raw.githubusercontent.com/alexal1/Insomniac/master/start.py) to a directory where you're going to launch the script from (right-click on the link, then Save As).
6. Download and unzip [Android platform tools](https://developer.android.com/studio/releases/platform-tools), move them to a folder where you won't delete them accidentally. Standard place is `C:\Users\<your username>\Android\sdk\platform-tools\`.
7. [Add platform-tools path to the PATH environment variable](https://github.com/alexal1/Insomniac/wiki/Adding-platform-tools-to-the-PATH-environment-variable). If you do it correctly, Command Prompt command `adb devices` will print `List of devices attached`.
8. Connect your Android phone via USB cable _or_ use [emulator](https://www.patreon.com/posts/how-to-install-43543116).
9. Enable [Developer options](https://developer.android.com/studio/debug/dev-options#enable) on the Android phone/emulator:
>On Android 4.1 and lower, the Developer options screen is available by default. On Android 4.2 and higher, you must enable this screen. To enable developer options, tap the Build Number option 7 times. You can find this option in one of the following locations, depending on your Android version:
>
> Android 9 (API level 28) and higher: Settings > About Phone > Build Number
>
> Android 8.0.0 (API level 26) and Android 8.1.0 (API level 26): Settings > System > About Phone > Build Number
>
> Android 7.1 (API level 25) and lower: Settings > About Phone > Build Number
10. Switch on **USB debugging** (and also **Install apps via USB** and **Allow ADB debugging in charge only mode** if there are such options) on the Developer options screen. You may also want to enable **Stay awake while charging**.
11. Android device will ask you to allow computer connection. Press "Connect".
12. Type `adb devices` in Command Prompt. It will display attached devices. There should be exactly one device.

### macOS
1. Download and install python from [python.org](https://www.python.org/downloads/mac-osx/). Better choose latest stable release.
2. Open Terminal.
3. Run `python3 -m pip install --upgrade pip` to make sure you've got the latest pip version.
4. Run `python3 -m pip install insomniac` to install insomniac package.
5. Download [start.py](https://raw.githubusercontent.com/alexal1/Insomniac/master/start.py) to a directory where you're going to launch the script from (right-click on the link, then Download Linked File As).
6. Download and unzip [Android platform tools](https://developer.android.com/studio/releases/platform-tools), move them to a folder where you won't delete them accidentally. Standard place is `~/Library/Android/sdk/platform-tools/`.
7. [Add platform-tools path to the PATH environment variable](https://github.com/alexal1/Insomniac/wiki/Adding-platform-tools-to-the-PATH-environment-variable). If you do it correctly, Terminal command `adb devices` will print `List of devices attached`.
8. Connect your Android phone via USB cable _or_ use [emulator](https://www.patreon.com/posts/how-to-install-43485861).
9. Enable [Developer options](https://developer.android.com/studio/debug/dev-options#enable) on the Android phone/emulator:
>On Android 4.1 and lower, the Developer options screen is available by default. On Android 4.2 and higher, you must enable this screen. To enable developer options, tap the Build Number option 7 times. You can find this option in one of the following locations, depending on your Android version:
>
> Android 9 (API level 28) and higher: Settings > About Phone > Build Number
>
> Android 8.0.0 (API level 26) and Android 8.1.0 (API level 26): Settings > System > About Phone > Build Number
>
> Android 7.1 (API level 25) and lower: Settings > About Phone > Build Number
10. Switch on **USB debugging** (and also **Install apps via USB** and **Allow ADB debugging in charge only mode** if there are such options) on the Developer options screen. You may also want to enable **Stay awake while charging**.
11. Android device will ask you to allow computer connection. Press "Connect".
12. Type `adb devices` in Terminal. It will display attached devices. There should be exactly one device.

### Ubuntu
1. Open Terminal.
2. Run `sudo apt-get update && sudo apt-get upgrade` to update & upgrade current packages.
3. Run `sudo apt install python3-pip` to install pip.
4. Run `python3 -m pip install insomniac` to install insomniac package.
5. Download [start.py](https://raw.githubusercontent.com/alexal1/Insomniac/master/start.py) to a directory where you're going to launch the script from (right-click on the link, then Save Link As).
6. Run `sudo apt-get install -y android-tools-adb android-tools-fastboot` to install Android platform tools.
7. Connect your Android phone via USB cable _or_ use [emulator](https://www.patreon.com/posts/how-to-install-43485861).
8. Enable [Developer options](https://developer.android.com/studio/debug/dev-options#enable) on the Android phone/emulator:
>On Android 4.1 and lower, the Developer options screen is available by default. On Android 4.2 and higher, you must enable this screen. To enable developer options, tap the Build Number option 7 times. You can find this option in one of the following locations, depending on your Android version:
>
> Android 9 (API level 28) and higher: Settings > About Phone > Build Number
>
> Android 8.0.0 (API level 26) and Android 8.1.0 (API level 26): Settings > System > About Phone > Build Number
>
> Android 7.1 (API level 25) and lower: Settings > About Phone > Build Number
9. Switch on **USB debugging** (and also **Install apps via USB** and **Allow ADB debugging in charge only mode** if there are such options) on the Developer options screen. You may also want to enable **Stay awake while charging**.
10. Android device will ask you to allow computer connection. Press "Connect".
11. Type `adb devices` in Terminal. It will display attached devices. There should be exactly one device.

### Raspberry Pi
1. Open Terminal.
2. Run `python3 -m pip install --upgrade pip` to make sure you've got the latest pip version.
3. Run `python3 -m pip install insomniac` to install insomniac package.
4. Download [start.py](https://raw.githubusercontent.com/alexal1/Insomniac/master/start.py) to a directory where you're going to launch the script from (right-click on the link, then Save link as).
5. Run `sudo apt-get update && sudo apt-get upgrade` to update & upgrade current packages.
6. Run `sudo apt-get install -y android-tools-adb android-tools-fastboot libopenjp2-7` to install Android platform tools.
7. Connect your Android phone via USB cable _or_ use [emulator](https://www.patreon.com/posts/how-to-install-43485861).
8. Enable [Developer options](https://developer.android.com/studio/debug/dev-options#enable) on the Android phone/emulator:
>On Android 4.1 and lower, the Developer options screen is available by default. On Android 4.2 and higher, you must enable this screen. To enable developer options, tap the Build Number option 7 times. You can find this option in one of the following locations, depending on your Android version:
>
> Android 9 (API level 28) and higher: Settings > About Phone > Build Number
>
> Android 8.0.0 (API level 26) and Android 8.1.0 (API level 26): Settings > System > About Phone > Build Number
>
> Android 7.1 (API level 25) and lower: Settings > About Phone > Build Number
9. Switch on **USB debugging** (and also **Install apps via USB** and **Allow ADB debugging in charge only mode** if there are such options) on the Developer options screen. You may also want to enable **Stay awake while charging**.
10. Android device will ask you to allow computer connection. Press "Connect".
11. Type `adb devices` in Terminal. It will display attached devices. There should be exactly one device.