## Installation
Siehe auch [Installation](/installation.de.md).

Suchst du nach einer detaillierten Beschreibung? Dann schau in unserem [Udemy-Kurs](https://insomniac-bot.com/udemy_course/). 

## Schnellstart

Öffne die Eingabeaufforderung / Terminal in einem Ordner mit der [start.py](https://raw.githubusercontent.com/alexal1/Insomniac/master/start.py)-Datei _oder_ öffne die Eingabeaufforderung irgendwo und navigiere mittels `cd pfad/zum/ordner`. Stelle sicher, dass dein Android-Smartphone oder dein Emulator verbunden ist. Das machst du, indem du den Befehl `adb devices` in die Eingabeaufforderung eingibst. Hier sollte nur ein Gerät gelistet werden.

Starte das insomniac-Script mit Parametern:
```
python3 start.py --interact @natgeo
```
Dieses simple Kommando startet den Bot. Dieser interagiert darauf hin in den Standardeinstellungen mit Followern des Accounts @natgeo. Insomniac öffnet und schließt die Instagram-App selbstständig. Um den Insomniac-Bot vorzeitig zu unterbrechen drücke _Strg+C_ (_control+C_ auf Mac).

## Grundfunktionen
Die Grundfunktionen beinhalten alles, was du für die einfache Nutzung brauchst. Diese sind [open source](https://github.com/alexal1/Insomniac/tree/master/insomniac) und gehören zu dem Projekt Insomniac. Wenn du mehr Funktionen haben möchtest, probiere unsere [Zusatzfunktionen](/?id=zusatzfunktionen) aus.

_Bedenke, dass du dir alle Funktionen anzeigen lassen kannst, wenn du `python start.py` ohne Parameter startest._

### Interaktionen
"Interaktionen" sind die Hauptaufgabe dieses Bots: Wir interagieren mit unserem potenziellen Publikum, um dessen Aufmerksamkeit zu gewinnen.

#### --interact amazingtrips-top-likers [@natgeo-followers ...]
Liste von Hashtags, Usernamen oder Orten. Usernamen müssen mit einem "@"-Zeichen beginnen. Orte müssen mit "P-" beginnen. Du kannst die potenzielles Publikum spezifizieren, indem du das "-"-Zeichen benutzt: @natgeo-followers, @natgeo-following, amazingtrips-top-likers, amazingtrips-recent-likers, P-Paris-top-likers, P-Paris-recent-likers

#### --likes-count 2-4
Anzahl der Likes die pro Instagram-Account verteilt werden, Standardeinstellung ist 2. Es kann eine Zahl angegeben werden (z.B. 2) oder ein Zufallswert zwischen zwei Zahlen (z.B. 2-4).

#### --like-percentage 50
Die Prozentzahl, zu der Content eines Users geliked wird. Standardeinstellung ist 100.

#### --follow-percentage 50
Die Prozentzahl, zu der ein Account gefollowed wird. Standardeinstellung ist 0.

#### --stories-count 3-8
Anzahl der Stories, die von einem User angeschaut werden. Diese Option ist in der Standardeinstellung deaktiviert. Ein kann eine Zahl angegeben werden (z.B. 2) oder ein Zufallswert zwischen zwei Zahlen (z.B. 2-4).

#### --comments-list WOW! [What a picture! ...]
Liste von Kommentaren, die innerhalb der Interaktion mit einem User gepostet werden.

#### --comment-percentage 50
Die Prozentzahl, zu der Kommentare hinterlassen werden. Standardeinstellung ist 0.

#### --interaction-users-amount 3-8
Dieser Parameter gibt gibt an, mit wie vielen Usern von der Interaktionsliste interagiert werden soll (die Accounts werden zufällig ausgewählt). Es kann eine Zahl angegeben werden (z.B. 4) oder ein Zufallswert zwischen zwei Zahlen (z.B. 3-8).

#### --reinteract-after 150
Anzahl der Stunden, die gewartet werden sollen, bevor mit einem bereits interagierten Account erneut interagiert werden soll. Diese Option ist in der Standardeinstellung deaktiviert (mit bereits interagierten Benutzern wird nicht erneut interagiert). Es kann eine Zahl angegeben werden (z.B. 48) oder ein Zufallswert zwischen zwei Zahlen (z.B. 50-80).

#### --interact-targets True / False
Nutze diesen Parameter, wenn mit den Accounts interagiert werden soll, die im **targets.txt**-Dokument angegeben sind.

### Unfollowing
Während das normale Interagieren Unsern followed, kann man mit "unfollow" Usern unfollowen.

#### --unfollow 100-200
Gibt die maximale Anzahl an, wie vielen Users unfollowed werden sollen. Es werden nur Accounts geunfollowed, die vom Insomniac-Bot gefollowed wurden. Die Standardreihenfolge ist hierbei vom Ältesten nach Neusten. Es kann eine Zahl angegeben werden (z.B. 100) oder ein Zufallswert zwischen zwei Zahlen (z.B. 100-200).

#### --unfollow-followed-by-anyone
Standardmäßig werden wird nur Leuten unfollowed, die vom Insomniac-Bot gefollowed wurden. Setze diesen Parameter, wenn alle gefolgten Accounts geunfollowed werden soll.

#### --unfollow-non-followers
Setze diesen Parameter, wenn nur Accounts geunfollowed werden sollen, die dir nicht folgen.

#### --following-sort-order latest
Setzt die Reihenfolge in der die Accounts unfollowed werden. Mögliche Werte: `default` / `latest` / `earliest`. Standardeinstellung ist `earliest`.                   

#### --recheck-follow-status-after 150
Gibt die Anzahl der Stunden an, die gewartet werden soll, bevor überprüft wird, ob ein Account dir auch folgt. Diese Option ist in der Standardeinstellung deaktiviert (die Überprüfung findet immer statt, wenn sie gebraucht wird). Es kann eine Zahl angegeben werden (z.B. 48) oder ein Zufallswert zwischen zwei Zahlen (z.B. 50-80).

### Limits
Limits sind unsere Abwehr gegen das Instagram Bot-Erkennungs-System. Benutze diese Limits, damit der Bot wie ein Mensch wirkt. Es gibt keine strikten Regeln nachdenen Limits eingesetzt werden sollten, da Instagram je nach Account variiert. Accountalter, Art des Netzwerks (WiFi oder mobiles Internet) und anderen Faktoren bestimmen deine Limits.

#### --successful-interactions-limit-per-source 40
Maximale Anzahl der erfolgreichen Interaktionen pro User/Hashtag/Ort. Standardeinstellung ist 70. Es kann eine Zahl angegeben werden (z.B. 70) oder ein Zufallswert zwischen zwei Zahlen (z.B. 60-80).

#### --interactions-limit-per-source 40
Maximale Anzahl der Interaktionen (erfolgreich oder nicht erfolgreich) pro User/Hashtag/Ort. Standardeinstellung ist 140. Es kann eine Zahl angegeben werden (z.B. 70) oder ein Zufallswert zwischen zwei Zahlen (z.B. 60-80).

#### --total-successful-interactions-limit 60-80
Maximale Anzahl der erfolgreichen Interaktionen pro Session. Diese Option ist in der Standardeinstellung deaktiviert. Es kann eine Zahl angegeben werden (z.B. 70) oder ein Zufallswert zwischen zwei Zahlen (z.B. 60-80).

#### --total-interactions-limit 60-80
Maximale Anzahl der Interaktionen (erfolgreich oder nicht erfolgreich) pro Session. Diese Option ist in der Standardeinstellung deaktiviert. Es kann eine Zahl angegeben werden (z.B. 70) oder ein Zufallswert zwischen zwei Zahlen (z.B. 60-80).

#### --total-likes-limit 300
Maximale Anzahl der Likes pro Session. Standardeinstellung ist 300. Es kann eine Zahl angegeben werden (z.B. 300) oder ein Zufallswert zwischen zwei Zahlen (z.B. 100-120).

#### --follow-limit-per-source 7-8
Maximale Anzahl der Follower eines Accounts, mit denen mit einem Follow interagiert werden soll. Diese Option ist in der Standardeinstellung deaktiviert. Es kann eine Zahl angegeben werden (z.B. 10) oder ein Zufallswert zwischen zwei Zahlen (z.B. 6-9).

#### --total-follow-limit 50
Maximale Anzahl der Follows pro Session. Diese Option ist in der Standardeinstellung deaktiviert. Es kann eine Zahl angegeben werden (z.B. 27) oder ein Zufallswert zwischen zwei Zahlen (z.B. 20-30).

#### --total-story-limit 300
Maximale Anzahl von angeschauten Stories pro Session. Diese Option ist in der Standardeinstellung deaktiviert. Es kann eine Zahl angegeben werden (z.B. 27) oder ein Zufallswert zwischen zwei Zahlen (z.B. 20-30).

#### --total-comments-limit 300
Maximale Anzahl von Kommentaren pro Session. Standardeinstellung ist 50. Es kann eine Zahl angegeben werden (z.B. 300) oder ein Zufallswert zwischen zwei Zahlen (z.B. 100-120).

#### --total-get-profile-limit 1500
Maximale Anzahl der Profilaufrufe pro Session. Diese Option ist in der Standardeinstellung deaktiviert. Es kann eine Zahl angegeben werden (z.B. 600) oder ein Zufallswert zwischen zwei Zahlen (z.B. 500-700).

#### --min-following 100
Minimale Anzahl an gefolgten Accounts. Ist das Minimum erreicht, wird nicht weiter geunfollowed. Diese Option ist in der Standardeinstellung deaktiviert.

#### --max-following 100
Maximale Anzahl an gefolgten Accounts. Ist das Maximum erreicht, wir nicht weiter gefollowed. Diese Option ist in der Standardeinstellung deaktiviert.

#### --session-length-in-mins-limit 50-60
Maximale Zeit in Minuten, die eine Session dauern soll. Diese Option ist in der Standardeinstellung deaktiviert. Es kann eine Zahl angegeben werden (z.B. 60) oder ein Zufallswert zwischen zwei Zahlen (z.B. 40-70).

### Sessionabfolge
Du kannst Insomniac so konfigurieren, dass der Bot dauerhaft läuft: _Interagieren > Warten > Interagieren > Warten > Unfollow > Warten > ..._. Das ist der Grund weswegen wir es als "Abfolge" bezeichnen. Erfahre mehr [in unserem Blogpost](https://www.patreon.com/posts/sessions-flows-45849501).

_Ziehe in Erwägung Konfigurationsdateien zu benutzen, auch wenn du ohne Sessionabfolge arbeitest! Die [Benutzung von Konfigurationsdateien](https://www.patreon.com/posts/configuration-of-43899836) wird empfohlen!_

#### --repeat 120-180
Minuten nach denen die gleiche Session wiederholt werden soll. Diese Option ist in der Standardeinstellung deaktiviert. Es kann eine Zahl angegeben werden (z.B. 180) oder ein Zufallswert zwischen zwei Zahlen (z.B. 120-180).

#### --config-file KONFIGURATIONSDATEI
Füge diesen Parameter hinzu um eine Konfigurationsdatei zu laden. Beispiele für Konfigurationsdateien findest du im Order [config-examples](https://github.com/alexal1/Insomniac/tree/master/config-examples).
                        
#### --next-config-file KONFIGURATIONSDATEI
Gibt die Konfigurationsdatei an, die geladen werden soll, nachdem der Bot die Session beendet hat und für die, mittels `--repeat`-Parameter angegebenen Zeit, gewartet hat. Dieser Parameter kann dafür genutzt werden, verschiedene Sessions mit unterschiedlichen Parametern in einer Laufzeit zu starten. Zum Beispiel kann erst interagiert werden und dann geunfollowed oder unterschiedliche Accounts benutzt werden. Nutze dafür den `--username`-Parameter. In der Standardeinstellung wird die gleiche Konfigurationsdatei erneut geladen. Dieser Parameter funktioniert nur, wenn der `--repeat`-Parameter gesetzt ist.

### Fortgeschrittene
Parameter für versierte Benutzer.

#### --old
Benutze diesen Parameter, um die alte Version von uiautomater zu benutzen. Benutze diesen Parameter nur, wenn du Probleme mit der aktuellen Version haben solltest.
                        
#### --device 2443de990e017ece
Gibt die Geräte-ID an. device identifier. Sollte nur verwendet werden, wenn mehrere Geräte angeschlossen sind.

#### --no-speed-check
Überspringt den Test der Internetgeschwindigkeit bei Beginn.

#### --wait-for-device
Warte bis ein ADB-Gerät bereit ist für die Verbindung. (Wenn der `--device`-Parameter nicht gesetzt ist, wird das nächste verfügbare Gerät für die Verbindung benutzt.)

#### --username ACCOUNTNAME
Wenn du mit mehreren Instagram-Accounts eingeloggt bist, kannst du diesen Parameter nutzen um zu einem spezifischen Account zu wechseln. In der Standardeinstellung wird der Account nicht gewechselt. Sollte der angegebene Account nicht existieren, startet der Bot nicht.

#### --app-id com.instagram.android
Gibt die apk-package-id an. Dieser Parameter sollte nur benutzt werden, wenn du den Bot mit einer geklonten App benutzen möchtest. Die Standardeinstellung ist `com.instagram.android`.

#### --dont-indicate-softban
Standardmäßig versucht Insomniac Softbans von Instagram zu erkennen. Setze diesen Parameter, wenn du keine Softban-Erkennung wünschst.

#### --debug
Startet Insomniac im Debug-Modus (ausführliche Logs).

## Zusatzfunktionen
Schalte die Zusatzfunktionen frei, indem du uns unterstützt. Mache dies mittels [Patreon € 9,50-Stufe](https://www.patreon.com/join/insomniac_bot). Du wirst eine E-Mail mit einem Aktivierungscode für dein [start.py](https://raw.githubusercontent.com/alexal1/Insomniac/master/start.py) bekommen.

Patreon ist der von uns gewählte Weg, dieses Projekt zu monetarisieren. Es gibt uns die Motivation zur kontinuierlichen Weiterentwicklung der "Grund-" und "Zusatzfunktionen".

### Filter
Mit Filtern kannst du beim interagieren Instagram-Accounts überspringen. Zum Beispiel kannst du Accounts mit mehr als 1000 Followern oder die mehr als 500 Accounts follown überspringen.
Dies uns noch viel mehr, kannst du mit der **filter.json**-Datei umsetzen. Liste der verfügbaren Parameter:

| Parameter                         | Value                                                       | Description                                                                                                                                 |
| --------------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------|
| `skip_business`                   | `true/false`                                                | Überspringe Firmen-Accounts wenn `true`                                                                                                     |
| `skip_non_business`               | `true/false`                                                | Überspringe Nicht-Firmen-Accounts wenn `true`                                                                                               |
| `min_followers`                   | 100                                                         | Überspringe Accounts mit weniger Followern als der angegebene Wert                                                                          |
| `max_followers`                   | 5000                                                        | Überspringe Accounts mit mehr Followern als der angegebene Wert                                                                             |
| `min_followings`                  | 10                                                          | Überspringe Accounts, die weniger Accounts follown als der angegebene Wert                                                                  |
| `max_followings`                  | 1000                                                        | Überspringe Accounts, die mehr Accounts follown als der angegebene Wert                                                                     |
| `min_potency_ratio`               | 1                                                           | Überspringe Accounts mit einem kleineren (Follower/Follow)-Verhältnis als dem angegebenen Wert (Dezimalzahlen können genutzt werden)        |
| `max_potency_ratio`               | 1                                                           | Überspringe Accounts mit einem größeren (Follower/Follow)-Verhältnis als dem angegebenen Wert (Dezimalzahlen können genutzt werden)         |
| `privacy_relation`                | `"only_public"` / `"only_private"` / `"private_and_public"` | Wähle die Account-Art aus, mit der du interagieren willst interact, `"only_public"` ist die Standardeinstellung                             |
| `min_posts`                       | 7                                                           | Minimale Anzahl der Posts, die ein Instagram-Account haben muss, damit der Bot interagiert                                                  |
| `max_digits_in_profile_name`      | 4                                                           | Maximale Anzahl an Ziffern im Accountnamen - Accounts mit mehr Ziffern im Accountnamen werden ignoriert                                     |
| `skip_profiles_without_stories`   | `true/false`                                                | Überspringe Accounts, die keine aktuelle Story haben (maximal 24 Stunden alt)                                                               |
| `blacklist_words`                 | `["wort1", "wort2", "wort3", ...]`                          | Überspringe Accounts, die eines der angegebenen Wörter in der Profil-Biografie haben                                                        |
| `mandatory_words`                 | `["wort1", "wort2", "wort3", ...]`                          | Überspringe Accounts, die keines der angegebenen Wörter in der Profil-Biografie haben                                                       |
| `specific_alphabet`               | `["LATIN", "ARABIC", "GREEK", "HEBREW", ...]`               | Überspringe Accounts, die Text im Profilnamen/der Biografie haben, welcher nicht in den Zeichensätzen, der angegebenen Liste, enthalten ist |
| `skip_already_following_profiles` | `true/false`                                                | Überspringe Accounts, denen du bereits folgst, unabhängig ob der Bot ihnen gefolgt hat                                                      |

Erfahre wie du Filter benutzt [in unserem Blogpost](https://www.patreon.com/posts/43362005).

#### --refilter-after 150
Gibt eine Zeit in Stunden an, nach der bereits rausgefilterte Accounts erneut überprüft werden sollen. Diese Option ist in der Standardeinstellung deaktiviert (rausgefilterte Accounts werden nicht erneut überprüft). Es kann eine Zahl angegeben werden (z.B. 48) oder ein Zufallswert zwischen zwei Zahlen (z.B. 50-80).
                        
#### --filters FILTER
Gebe diesen Parameter mit an, wenn du Filter als Parameter übergeben willst und nicht in der **filters.json**-Datei.

### Scraping
"Scraping" ist eine Technik um mit noch mehr Accounts zu interagieren ohne dabei aufzufallen und von Instagram als "auffällig aktiver" User eingestuft zu werden. Die Idee ist es, einen anderen Instagram-Account zu nutzen um Accounts zu filtern. Dein Hauptaccount geht im Anschluss nur noch hin und interagiert mit den gefilterten Accounts. Erfahre mehr über Scraping [in unserem Blogpost](https://www.patreon.com/posts/scrapping-what-43902968).

#### --scrape hashtag-top-likers [@username-followers ...]
Liste von Hashtags, Usernamen oder Orten mit denen interagiert werden soll. Usernamen müssen mit einem "@"-Zeichen starten. Orte müssen mit einem "P-" starten. Die potenzielle Zielgruppe kann mittels des "-"-Zeichen verfeinert werden. Zum Beispiel: @natgeo-followers, @natgeo-following, amazingtrips-top-likers, amazingtrips-recent-likers, P-Paris-top-likers, P-Paris-recent-likers

#### --scrape-for-account account1 [account2 ...]
Ist dieser Paramter gesetzt, werden nur die angegebenen Accounts gescraped. Die gescrapeten Accounts werden in der Datenbank gespeichert.

#### --scrape-users-amount 3-8
Dieser Parameter gibt die Anzahl der Accounts von der Scraping-Liste an, mit denen interagiert werden soll (Die Accounts werden zufällig aus der Liste ausgewählt). Es kann eine Zahl angegeben werden (z.B. 4) oder ein Zufallswert zwischen zwei Zahlen (z.B. 3-8).

#### --scrapping-main-db-directory-name haupt-db-ordner-name
Wenn dieser Parameter gesetzt ist, wird für das Scraping die Datenbank benutzt, die in dem angegebenen Verzeichnis zu finden ist. Nutze diesen Parameter, wenn du mehrere Scrapper-Accounts nutzt und diese synchronisiert arbeiten sollen, damit keine Accounts mehrfach gescrapt werden. In der Standardeinstellung wird das Account-Verzeichnis benutzt um den Scraping-Verlauf zu speichern.
                        
### Spezialfunktionen
Andere Funktionen, die freigeschaltet werden, sobald du dich für die [Patreon € 9,50-Stufe](https://www.patreon.com/join/insomniac_bot) entscheidest:

#### --remove-mass-followers 10-20
"Mass Followers" sind Instagram-Accounts, die vielen Accounts follown. Der Parameter definiert die Anzahl an "Mass Followern" denen unfollowed werden soll. Die Anzahl an Follows der "Mass Follower" kann über den Parameter `--max-follower` definiert werden. Es kann eine Zahl angegeben werden (z.B. 4) oder ein Zufallswert zwischen zwei Zahlen (z.B. 3-8).

#### --mass-follower-min-following 1000
Gibt die Anzahl an maximalen Follows an, die ein von dir gefollowter Account haben darf. Der Parameter muss im Zusammenspiel mit `--remove-mass-followers` verwendet werden. Die Standardeinstellung ist 1000.

### Limits
Limits die mit den Zusatzfunktionen mitgeliefert werden.

#### --scrape-limit-per-source 40-60
Gibt die Anzahl der Accounts an, die pro Username/Hashtag gescraped werden sollen. Diese Option ist in der Standardeinstellung deaktiviert. Es kann eine Zahl angegeben werden (z.B. 70) oder ein Zufallswert zwischen zwei Zahlen (z.B. 50-80).
                   
#### --total-scrape-limit 150
Gibt die Anzahl an Accounts an, die maximal pro Session gescraped werden sollen. Diese Option ist in der Standardeinstellung deaktiviert. Es kann eine Zahl angegeben werden (z.B. 100) oder ein Zufallswert zwischen zwei Zahlen (z.B. 90-120).

#### --working-hours 9-21
Dieser Parameter gibt eine Arbeitszeit an, während der Wert eine Stunde repräsentiert. Diese Option ist in der Standardeinstellung deaktiviert. Es kann eine Zahl als Stunde angegeben werden (z.B. 13) oder ein Zufallswert zwischen zwei Zahlen (z.B. 9-21). Beachte, dass die rechte Zahl größer sein muss, als die linke.

### Advanced
Mehr Parameter für versierte Benutzer.

#### --pre-session-script /pfad/zu/meinem/skript.sh oder .bat
Benutze diesen Parameter, wenn du ein vordefiniertes Skript starten willst, wenn eine Session startet.

#### --post-session-script /pfad/zu/meinem/skript.sh oder .bat
Benutze diesen Parameter, wenn du ein vordefiniertes Skript starten willst, wenn eine Session endet.
