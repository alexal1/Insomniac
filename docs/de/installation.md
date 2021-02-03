[< Zurück zur Dokumentation](/#/de/ ':ignore')

## Installation
Wenn du eine Videoanleitung bevorzugst, freuen wir uns, dich in unserem [Udemy Kurs](https://insomniac-bot.com/udemy_course/) begrüßen zu dürfen. Hier gehen wir alle Installationsschritte gemeinsam durch!

### Windows
1. Downloade und installiere python von [python.org](https://www.python.org/downloads/windows/). Wähle das neuste "stable release".
2. Öffne die Eingabeaufforderung (Win+R)->cmd.
3. Nutze den Befehl `python -m pip install --upgrade pip` um sicherzustellen, dass du die neuste pip-Version benutzt.
4. Nutze den Befehl `python -m pip install insomniac` um das Insomniac-Paket zu installieren.
5. Downloade [start.py](https://raw.githubusercontent.com/alexal1/Insomniac/master/start.py) und speichere es in einem Ordner von dem du Insomniac starten möchtest (Rechtsklick auf den Link -> Link speichern unter...).
6. Downloade [Android platform tools](https://developer.android.com/studio/releases/platform-tools) und entpacke es in einen Ordner, wo du es nicht versehentlich löschst. Standardpfad ist `C:\Benutzer\<dein Benutzername>\Android\sdk\platform-tools\`.
7. [Hinzufügen des platform-tools Pfads zu der PATH-Umgebungsvariable](https://github.com/alexal1/Insomniac/wiki/Adding-platform-tools-to-the-PATH-environment-variable). Wenn du es korrekt gemacht hast, sollte das Kommando `adb devices` in der Eingabeaufforderung `List of devices attached` anzeigen.
8. Verbinde ein Android-Smartphone per USB-Kabel _oder_ benutze einen [Emulator](https://www.patreon.com/posts/how-to-install-43543116).
9. Aktiviere [Entwickleroptionen](https://developer.android.com/studio/debug/dev-options#enable) auf deinem Android-Smartphone/Emulator:
>In Android 4.1 und die Versionen darunter haben die Entwickleroptionen standardmäßig aktiviert. In Android 4.2 höher müssen die Entwickleroptionen erst aktiviert werden. Um die Entwickleroptionen zu aktivieren, tappe 7 mal nacheinander auf die Build-Nummer. Diese findest du an folgenden Orten, abhängig von der Android-Version:
>
> Android 9 (API Level 28) und höher: Einstellungen > Über das Telefon > Build-Nummer
>
> Android 8.0.0 (API Level 26) und Android 8.1.0 (API Level 26): Einstellungen > System > Über das Telefon > Build-Nummer
>
> Android 7.1 (API Level 25) und darunter: Einstellungen > Über das Telefon > Build-Nummer
10. Aktiviere **USB-Debugging** (und **Apps über USB installieren** and **Erlaube ADB-Debugging im "Nur Laden"-Modus** wenn es diese Optionen gibt) in den Entwickleroptionen.
11. Das Android-Gerät wird fragen, ob es die Verbindung mit dem Computer zulassen soll. Klicke "Verbinden".
12. Tippe `adb devices` in die Eingabeaufforderung. Nun wird dein Android-Gerät angezeigt. Es sollte ausschließlich ein Gerät angezeigt werden.

### macOS
1. Downloade und installiere python von [python.org](https://www.python.org/downloads/mac-osx/). Wähle das neuste "stable release".
2. Öffne das Terminal.
3. Nutze den Befehl `python3 -m pip install --upgrade pip` um sicherzustellen, dass du die neuste pip-Version benutzt.
4. Nutze den Befehl `python3 -m pip install insomniac` um das Insomniac-Paket zu installieren.
5. Downloade [start.py](https://raw.githubusercontent.com/alexal1/Insomniac/master/start.py) und speichere es in einem Ordner von dem du Insomniac starten möchtest (Rechtsklick auf den Link -> Link speichern unter...).
6. Downloade [Android platform tools](https://developer.android.com/studio/releases/platform-tools) und entpacke es in einen Ordner, wo du es nicht versehentlich löschst. Standardpfad ist `~/Library/Android/sdk/platform-tools/`.
7. [Hinzufügen des platform-tools Pfads zu der PATH-Umgebungsvariable](https://github.com/alexal1/Insomniac/wiki/Adding-platform-tools-to-the-PATH-environment-variable). Wenn du es korrekt gemacht hast, sollte das Kommando `adb devices` im Terminal `List of devices attached` anzeigen.
8. Verbinde ein Android-Smartphone per USB-Kabel _oder_ benutze einen [Emulator](https://www.patreon.com/posts/how-to-install-43485861).
9. Aktiviere [Entwickleroptionen](https://developer.android.com/studio/debug/dev-options#enable) auf deinem Android-Smartphone/Emulator:
>In Android 4.1 und die Versionen darunter haben die Entwickleroptionen standardmäßig aktiviert. In Android 4.2 höher müssen die Entwickleroptionen erst aktiviert werden. Um die Entwickleroptionen zu aktivieren, tappe 7 mal nacheinander auf die Build-Nummer. Diese findest du an folgenden Orten, abhängig von der Android-Version:
>
> Android 9 (API Level 28) und höher: Einstellungen > Über das Telefon > Build-Nummer
>
> Android 8.0.0 (API Level 26) und Android 8.1.0 (API Level 26): Einstellungen > System > Über das Telefon > Build-Nummer
>
> Android 7.1 (API Level 25) und darunter: Einstellungen > Über das Telefon > Build-Nummer
10. Aktiviere **USB-Debugging** (und **Apps über USB installieren** and **Erlaube ADB-Debugging im "Nur Laden"-Modus** wenn es diese Optionen gibt) in den Entwickleroptionen.
11. Das Android-Gerät wird fragen, ob es die Verbindung mit dem Mac zulassen soll. Klicke "Verbinden".
12. Tippe `adb devices` in die Eingabeaufforderung. Nun wird dein Android-Gerät angezeigt. Es sollte ausschließlich ein Gerät angezeigt werden.

### Ubuntu
1. Öffne das Terminal.
2. Nutze den Befehl `sudo apt-get update && sudo apt-get upgrade` zum updaten und upgraden der aktuellen Pakete.
3. Nutze den Befehl `sudo apt install python3-pip` um pip zu installieren.
4. Nutze den Befehl `python3 -m pip install insomniac` um das Insomniac-Paket zu installieren.
5. Downloade [start.py](https://raw.githubusercontent.com/alexal1/Insomniac/master/start.py) und speichere es in einem Ordner von dem du Insomniac starten möchtest (Rechtsklick auf den Link -> Link speichern unter...).
6. Nutze den Befehl `sudo apt-get install -y android-tools-adb android-tools-fastboot` um Android platform tools zu installieren.
7. Verbinde ein Android-Smartphone per USB-Kabel _oder_ benutze einen [Emulator](https://www.patreon.com/posts/how-to-install-43485861).
8. Aktiviere [Entwickleroptionen](https://developer.android.com/studio/debug/dev-options#enable) auf deinem Android-Smartphone/Emulator:
>In Android 4.1 und die Versionen darunter haben die Entwickleroptionen standardmäßig aktiviert. In Android 4.2 höher müssen die Entwickleroptionen erst aktiviert werden. Um die Entwickleroptionen zu aktivieren, tappe 7 mal nacheinander auf die Build-Nummer. Diese findest du an folgenden Orten, abhängig von der Android-Version:
>
> Android 9 (API Level 28) und höher: Einstellungen > Über das Telefon > Build-Nummer
>
> Android 8.0.0 (API Level 26) und Android 8.1.0 (API Level 26): Einstellungen > System > Über das Telefon > Build-Nummer
>
> Android 7.1 (API Level 25) und darunter: Einstellungen > Über das Telefon > Build-Nummer
10. Aktiviere **USB-Debugging** (und **Apps über USB installieren** and **Erlaube ADB-Debugging im "Nur Laden"-Modus** wenn es diese Optionen gibt) in den Entwickleroptionen.
11. Das Android-Gerät wird fragen, ob es die Verbindung mit dem Computer zulassen soll. Klicke "Verbinden".
12. Tippe `adb devices` in die Eingabeaufforderung. Nun wird dein Android-Gerät angezeigt. Es sollte ausschließlich ein Gerät angezeigt werden.

### Raspberry Pi
1. Öffne das Terminal.
2. Nutze den Befehl `python3 -m pip install --upgrade pip` um sicherzustellen, dass du die neuste pip-Version benutzt.
3. Nutze den Befehl `python3 -m pip install insomniac` um das Insomniac-Paket zu installieren.
4. Downloade [start.py](https://raw.githubusercontent.com/alexal1/Insomniac/master/start.py) und speichere es in einem Ordner von dem du Insomniac starten möchtest (Rechtsklick auf den Link -> Link speichern unter...).
5. Nutze den Befehl `sudo apt-get update && sudo apt-get upgrade` zum updaten und upgraden der aktuellen Pakete.
6. Nutze den Befehl `sudo apt-get install -y android-tools-adb android-tools-fastboot` um Android platform tools zu installieren.
7. Verbinde ein Android-Smartphone per USB-Kabel _oder_ benutze einen [Emulator](https://www.patreon.com/posts/how-to-install-43485861).
8. Aktiviere [Entwickleroptionen](https://developer.android.com/studio/debug/dev-options#enable) auf deinem Android-Smartphone/Emulator:
>In Android 4.1 und die Versionen darunter haben die Entwickleroptionen standardmäßig aktiviert. In Android 4.2 höher müssen die Entwickleroptionen erst aktiviert werden. Um die Entwickleroptionen zu aktivieren, tappe 7 mal nacheinander auf die Build-Nummer. Diese findest du an folgenden Orten, abhängig von der Android-Version:
>
> Android 9 (API Level 28) und höher: Einstellungen > Über das Telefon > Build-Nummer
>
> Android 8.0.0 (API Level 26) und Android 8.1.0 (API Level 26): Einstellungen > System > Über das Telefon > Build-Nummer
>
> Android 7.1 (API Level 25) und darunter: Einstellungen > Über das Telefon > Build-Nummer
10. Aktiviere **USB-Debugging** (und **Apps über USB installieren** and **Erlaube ADB-Debugging im "Nur Laden"-Modus** wenn es diese Optionen gibt) in den Entwickleroptionen.
11. Das Android-Gerät wird fragen, ob es die Verbindung mit dem Computer zulassen soll. Klicke "Verbinden".
12. Tippe `adb devices` in die Eingabeaufforderung. Nun wird dein Android-Gerät angezeigt. Es sollte ausschließlich ein Gerät angezeigt werden.
