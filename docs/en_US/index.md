GoogleCast plugin (googlecast)
=============================

![Logo plugin](../images/logoplugin.png "Logo plugin")

Plugin to control Google Cast enabled devices.


**Features:**

- Sound control (mute, +/-)
- Media control (play/pause/stop ...)
- Stop app in progress, reboot
- Broadcast a web page on a screen
- Play audio and video files via url
- Return of status on the main functionalities
- Display of the current reading
- Text To Speech (TTS)
- Recovery/modification of equipment configuration


![Logo plugin](../images/chromecast.png "Chromecast")

**Google Cast compatible models**
- Chromecast Audio/Video
- Android TV, Nexus Player, TV (Vizio, Sharp, Sony, Toshiba, Philips)
- Google Home
- Soundbars and speakers (Vizio, Sony, LG, Philips
B&O Play, Grundig, Polk Audio, Bang & Olufsen, Onkyo, Pioneer ...)
- Other models labeled *Google Cast*

![GoogleCast Logo](../images/googlecast_logo.png "GoogleCast Logo")
![Android TV](../images/tv.png "Android TV")

**Other links**
- Wikipedia <a target="_blank" href="https://en.wikipedia.org/wiki/Google_Cast">GoogleCast</a>
- List of <a target="_blank" href="https://en.wikipedia.org/wiki/List_of_apps_with_Google_Cast_support">Google Cast enabled applications</a>


Dashboard
=======================

![Dashboard view](../images/dashboard.png "Dashboard view")
![Dashboard view 2](../images/dashboard2.png "Dashboard view 2")

Quick Start
=======================

The plugin is normally functional from the installation with the default setting.

In a few steps:
1. Install the market plugin, the dependencies and start the daemon,
2. Start a scan of Google Cast available on the network,
3. Save the equipment found,
4. Go to the dashboard and test the 'demo' buttons (media, web ...),
5. To change/adapt the setting, read the rest of the documentation.

Toble of Content
=======================

- [GoogleCast plugin (googlecast)](#googlecast-plugin--googlecast-)
- [Dashboard](#dashboard)
- [Quick Start](#quick-start)
- [Toble of Content](#toble-of-content)
- [Plugin Configuration](#plugin-configuration)
- [Configuration des équipements](#configuration-des--quipements)
    + [Onglet Commandes](#onglet-commandes)
    + [Afficheur Lecture en cours (widget)](#afficheur-lecture-en-cours--widget-)
    + [TTS Widget for text entry and volume control](#tts-widget-for-text-entry-and-volume-control)
- [Custom commands](#custom-commands)
    + [Special applications](#special-applications)
    + [Advanced commands](#advanced-commands)
      - [Syntax for raw commands](#syntax-for-raw-commands)
      - [Possible parameters for *play_media* en mode *media* :](#possible-parameters-for--play-media--en-mode--media---)
      - [Possible parameters for *load_url* en mode *web* :](#possible-parameters-for--load-url--en-mode--web---)
      - [Possible parameters for *play_media* en mode *plex* :](#possible-parameters-for--play-media--en-mode--plex---)
      - [Possible parameters for *tts* :](#possible-parameters-for--tts---)
      - [Possible parameters for *notif* :](#possible-parameters-for--notif---)
      - [Command sequences](#command-sequences)
      - [Device advanced configuration](#device-advanced-configuration)
        * [Retreive a configuration](#retreive-a-configuration)
          + [available parameters for *getconfig* cmd :](#available-parameters-for--getconfig--cmd--)
        * [Modify a configuration](#modify-a-configuration)
          + [available parameters for *setconfig* cmd :](#available-parameters-for--setconfig--cmd--)
        * [Pre-defined configuration commands](#pre-defined-configuration-commands)
    + [Adding a command *action* of type *List*](#adding-a-command--action--of-type--list-)
    + [Use in scenarios](#use-in-scenarios)
      - [With dedicated command *Custom Cmd*](#with-dedicated-command--custom-cmd-)
      - [With php bloc code](#with-php-bloc-code)
    + [Use with interactions and IFTTT](#use-with-interactions-and-ifttt)
      - [Interactions](#interactions)
      - [Custom CMD](#custom-cmd)
- [Known limitations and bugs](#known-limitations-and-bugs)
- [FAQ](#faq)
- [Changelog](#changelog)


Plugin Configuration
=======================

After downloading the plugin:
- Activate the plugin
- Start the installation of dependencies
- Recommended log level: info
- Launch the demon.

Configuration settings do not usually need to be changed
- **Demon**
  - Internal communication socket port. Only modify if necessary (ex: if it is already taken by another plugin)
  - Special configuration (eg: Docker, VM). Only change if it does not work without the option.
  - Refresh frequency. Only change if the normal frequency has a significant impact on overall performance
- **TTS**
  - Use the external Jeedom address: by default uses the internal Jeedom web address
  - Default language: TTS engine language used by default
  - Default engine: the TTS engine used (PicoTTS, Google Translate, Speach API, Google Speach API dev)
  - Speech rate: speed of pronunciation of the text
  - Do not use cache: disables use of Jeedom cache (deprecated)
  - Clean cache: cleans the temporary directory for generating sound files
  - Automatic cache deletion of more than X days: deletes unused TTS sound files for X days (daily cron). 0 deletes all the cache.
- **Notifications**
  - Disable notifications for new Google Cast: These are notifications when discovering new Google Cast unconfigured

> **Notes for TTS (Text To Speech)**
> - PicoTTS does not require an internet connection, the Google Translate API requires web access and rendering is better.
> - For Google Speech API, a key is required (see FAQ). Rendering is better than Google Translate API.
> - A cache mechanism makes it possible to generate the sound reproduction only if it does not already exist in memory (RAM). The cache is deleted when the server is restarted.
> - In the event of failure on one of the motors other than picotts (ex: problem of Internet connection), the command will be launched via picotts.

![Configuration Plugin](../images/configuration_plugin.png "Configuration Plugin")

Configuration des équipements
=============================

Google Cast device setup is available from the *Plugins> Multimedia> Google Cast* menu.

![Configuration](../images/configuration.png "Configuration")

Once the devices are connected, run a scan to detect and add them automatically. If no equipment appears, check that the equipment is accessible and powered.

The view 'Health' allows to have a synthetic view of equipment and their current states.

> **Note**    
> It's not possible to manually add a Google Cast

### Onglet Commandes

Basic commands are generated automatically.

You can also add new commands (see section below).

![Alt text](../images/commands.png "Custom command")

List of non-visible commands by default:
- *Player Status*: info displaying the media playback status (eg PLAYING/PAUSED);
- *Title*: Title of the current media;
- *Artist*: Artist of the current media;
- *Custom Cmd*: This component is intended to be used via a scenario or for testing (see section [Use in a scenario] (# use-in-a-scenario));
- *Pincode*: pincode for quick association (example of advanced configuration)

To see them on the dashboard, you have to activate 'Show' in the commands tab.

> **Notes on order info 'Status' (*status_text*)**
> - *status_text* returns the current status of the Google Cast.
> - In case of error when launching an order, *status_text* is at
> 'CMD UNKNOWN' if the command does not exist,
> 'NOT CONNECTED' if offline or
> 'ERROR' for other errors
> - At rest (no action in progress), *status_text* = `& nbsp;`


### Afficheur Lecture en cours (widget)

The information type command called 'Playing Widget' (visible by default) displays the image of the current playback.

The display refreshes every 20 seconds by default.

![Display 1](../images/display1.png "Display 1")

Installation/configuration:
- Displayed by default after installation. Disable the display to hide.
- For use in a dashboard, it is possible to use a virtual by creating a command of the type *info/others* with the command *Playing Widget* (not internal *nowplaying*) of the Google Cast. Then apply the dashboard widget *googlecast_playing* (via tab *View* of the advanced configuration of the command)
- For use in a design, add the *Playing Widget* command directly into the design.

optional CSS settings (via '*Optional Widget Settings'):
- *fontSize* (ex: 35px, default = 25px): basic font size
- *fontColor* (ex: blue, default = white): color of the display
- *fontFamily* (ex: 'Arial'): change the font of the display
- *backColor* (ex: blue, default = black): color of the bottom of the display
- *playingSize* (ex: 300px, default 250px): width and height of the current playback picture
- *contentSize* (ex: 70px, default 50px): height of the textual part
- *additionalCss* (css format, ex: '.blabla {...}'): to add/modify other CSS (advanced user)

![Configuration CSS](../images/configuration_css.png "Configuration CSS")

> **Notes**   
> Not available for mobile

### TTS Widget for text entry and volume control

A widget is available for action type and message subtype commands to allow you to enter text for the TTS and adjust the volume.

![Speak Widget](../images/widget_speak.png "Speak Widget")

Installation/configuration:
- An example is displayed by default after installation to test the TTS function.
- For use in a dashboard, it is possible to use a virtual one by creating a command of the type *action/message* with value the command *Custom Cmd* of Google Cast. Then apply the dashboard widget *googlecast_speak* (via tab *View* of the advanced configuration of the command)
- The contents of the action command (subtype message) can contain the variables *#message#* and *#volume#*

optional CSS settings (via '*Optional Widget Settings'):
- *width* (ex: 35px, default = 150px): size of the widget
- *default_volume* (ex: blue, default = 100): default valume
- *default_message* (ex: 'Test'): default text in the widget
- *additionalCss* (css format, ex: '.blabla {...}'): to add/modify other CSS (advanced user)

> **Notes**   
> Not available for mobile


Custom commands
=============================

### Special applications

- *Web*: Display a web page on a Google Cast. The available parameters are url, force, and reload time (ex: value = 'https://google.com',False,0 to load Google without forcing (necessary for some sites) and without reloading)
- *Media*: play an audio or video file from a URL
- *YouTube*: display a video with a video ID (at the end of the URL) => Does not work at the moment
- *Backdrop*: show the Google Cast wallpaper or screen saver (depending on model)
- *Plex*: play a file or playlist from a Plex server

> **Notes**    
> - See the buttons created by default for an example of use
> - Youtube is not functional at the moment


### Advanced commands

#### Syntax for raw commands
They must be seperated by *|*
```
- app : name of application (web/backdrop/youtube/media)
- cmd : name of command (dépend of application)
    * tts : text to speech, use value to pass text
    * notif : send sound notification based on existing media file (ex: mp3)
    * refresh
    * reboot : reboot the Google Cast
    * volume_up
    * volume_down
    * volume_set : use value (0-100)
    * mute_on
    * mute_off
    * quit_app
    * start_app : use value to pass app id
    * play
    * stop
    * rewind : go back to media start
    * skip : got to next media
    * seek : use value in seconds. Can use +/- to use relative seek (ex: +20 to pass 20 seconds)
    * pause
    For application dependant commands
        * web : load_url (default)
        * media : play_media (default)
        * youtube : play_video (default)/add_to_queue/remove_video/play_next
        * backdrop : no command
        * plex : play_media  (default)/play/stop/pause
- value : chain of parameters separated by ',' (depending of command)
- vol (optional, between 1 et 100) : adjust volume for the command
- sleep (optional, int/float) : add a break after end of command in seconds (eg: 2, 2.5)
- uuid (optional) : redirect to other google cast uuid in new thread (parallel processing). Useful when using sequences on several device.
- nothread (optional) : if uuid provided, disable use of thread for parallel processing. (eg: nothread=1)

ex web : app=web|cmd=load_url|vol=90|value='http://pictoplasma.sound-creatures.com',True,10
ex TTS : cmd=tts|vol=100|value=Mon text a dire
```

> **Notes**     
> String length for commands are limited in Jeedom to 128 characters. Use scenarios (see below to override this limitation)

#### Possible parameters for *play_media* en mode *media* :
```
- url: str - url of the media (mandatory).
- content_type: str - mime type. Example: 'video/mp4' (optional).
   Possible values: 'audio/aac', 'audio/mpeg', 'audio/ogg', 'audio/wav', 'image/bmp',
   'image/gif', 'image/jpeg', 'image/png', 'image/webp','video/mp4', 'video/webm'.
- title: str - title of the media (optional).
- thumb: str - thumbnail image url (optional, default=None).
- current_time: float - seconds from the beginning of the media to start playback (optional, default=0).
- autoplay: bool - whether the media will automatically play (optional, default=True).
- stream_type: str - describes the type of media artifact as one of the following: "NONE", "BUFFERED", "LIVE" (optional, default='BUFFERED').
- subtitles: str - url of subtitle file to be shown on chromecast (optional, default=None).
- subtitles_lang: str - language for subtitles (optional, default='en-US').
- subtitles_mime: str - mimetype of subtitles (optional, default='text/vtt').
   Possible values: 'application/xml+ttml', 'text/vtt'.
- subtitle_id: int - id of subtitle to be loaded (optional, default=1).

ex short : app=media|cmd=play_media|value='http://contentlink','video/mp4','Video name'
ex short : app=media|cmd=play_media|value='http://contentlink',title:'Video name'
ex short : app=media|value='http://contentlink','video/mp4','Video name' (implicit play_media command call)

ex long : app=media|cmd=play_media|value='http://contentlink','video/mp4',title:'Video name',
   thumb:'http://imagelink',autoplay:True,
   subtitles:'http://subtitlelink',subtitles_lang:'fr-FR',
   subtitles_mime:'text/vtt'
```

> **Notes**   
> - Les url et chaînes de caractères sont entourées de guillements simples ('). Les autres valeurs possibles sont True/False/None ainsi que des valeurs numériques entières.
> - Il est nécessaire de remplacer le signe '=' dans les url par '%3D'
> - Un média local situé dans le répertoire *<jeedom>/plugins/googlecast/localmedia/* peux être utilisé en appelant l'url *local://<nomdufichier>* (ex: local://bigben1.mp3)

#### Possible parameters for *load_url* en mode *web* :
```
- url: str - website url.
- force: bool - force mode. To be used if default is not working. (optional, default False).
- reload: int - reload time in seconds. 0 = no reload. (optional, default 0)

ex 1 : app=web|cmd=load_url|value='http://pictoplasma.sound-creatures.com',True,10
ex 2 : app=web|cmd=load_url|value='http://mywebsite/index.php?apikey%3Dmyapikey'
ex 3 : app=web|value='http://mywebsite/index.php?apikey%3Dmyapikey' (implicit load_url command call)
```

> **Notes**   
> - Urls and strings are surrounded by single quotes ('). Other possible values are True/False/None and integer numeric values.
> - It is necessary to replace the sign '=' dans les url par '%3D'

#### Possible parameters for *play_media* en mode *plex* :
```
- value: str - search query. It will play the first element returned.
- type: str - type of content. Example: 'video/audio' (optional, default=video).
- server: str - URL if token is provided, friendly name of Plex server if user & pass provided.
- user: str - account login possibly as an email account (optional if token provided).
- pass: str - account password (optional if token provided).
- token: str - token if any (optional if user & pass provided).
- shuffle: 0/1 - shuffle playlist if several media (optional, default=0).
- repeat: 0/1 - repeat media (optional, default=0).
- offset: int - media offset (optional, default=0).

ex using user & pass :   
   app=plex|cmd=play_media|user=XXXXXX|pass=XXXXXXXXXXX|server=MyPlexServer|value=Playlist Jeedom|shuffle=1|type=audio
ex using token :   
   app=plex|cmd=play_media|token=XXXXXXXXX|server=http://IP:32400|value=Playlist Jeedom
ex using token with implicit play_media command call :   
   app=plex|token=XXXXXXXXX|server=http://IP:32400|value=Playlist Jeedom
```

> **Notes**   
> - When using user & pass, internet access is required
> - Token value is displayed in logs (debug) when user & pass has been used the first time
> - you can simulate result of search query (value) in main search field of Plex web UI

#### Possible parameters for *tts* :
```
- value: str - text
- lang: str - fr-FR/en-US or any compatible language (optional, default is configuration)
- engine: str - picotts/gtts/gttsapi/gttsapidev. (optional, default is configuration)
- quit: 0/1 - quit app after tts action.
- forcetts: 1 - do not use cache (useful for testing).
- speed: float (default=1.2) - speed of speech (eg: 0.5, 2).
- vol: int (default=previous) - set the volume for the time TTS message is broadcast. Previous volume is resumed when done.
- sleep: float (default=0) - add time in seconds after tts is finished (before volume resume)
- silence: int (default=300, 600 for group cast) - add a short silence before the speech to make sure all is audible (in milliseconds)
- generateonly: 1 - only generate speech file in cache (no action on device)
- forcevol: 1 - Set volume also if the current volume is the same (useful for TTS synchronisation in multithreading)
- noresume: 1 - disable recovery of previous state before playing TTS.
- forceapplaunch: 1 - will try to force launch of previous application even if not launched by plugin.
- highquality: 1 - increase tts sound file bitrate and sample rate. Use this setting for test.
- buffered: 1 - stream to google cast as buffered stream instead of live. Use this setting for test.
- voice (gttsapi/gttsapidev only): male/female - chose a male or female voice (default is female)
- usessml (gttsapi/gttsapidev only): 1 - use ssml format insteaf of text. See https://cloud.google.com/text-to-speech/docs/ssml ('=' symbols must be replace by '^')

ex : cmd=tts|value=My text|lang=en-US|engine=gtts|quit=1
ex : cmd=tts|value=Mon texte|engine=gtts|speed=0.8|forcetts=1
ex voice/ssml : cmd=tts|engine=gttsapi|voice=male|value=<speak>Etape 1<break time^"3s"/>Etape 2</speak>
```

> **Notes**   
> - By default, the plugin will try to resume previous app launched (will only work when previous application has been launched by the plugin).
> - You can try to force resume to any application using 'forceapplaunch=1' but there is a good chance that it will not resume correctly.

#### Possible parameters for *notif* :
```
- value: str - local media filename (located in '<jeedom>/plugins/googlecast/localmedia/' folder)
- quit: 0/1 - quit app after notif action.
- vol: int (default=previous) - set the volume for the time notif message is broadcast. Previous volume is resumed when done.
- duration: float (default=file duration) - override play duration of notification.
- sleep: float (default=0) - add time in seconds after notif is finished (before volume resume)
- forcevol: 1 - Set volume also if the current volume is the same (useful for notif synchronisation in multithreading)
- noresume: 1 - disable recovery of previous state before playing notif.
- forceapplaunch: 1 - will try to force launch of previous application even if not launched by plugin.

ex : cmd=notif|value=bigben1.mp3|vol=100
```

> **Notes**   
> - By default, the plugin will try to resume previous app launched (will only work when previous application has been launched by the plugin).
> - You can try to force resume to any application using 'forceapplaunch=1' but there is a good chance of failure.
> - Existing sounds in plugin : house_firealarm.mp3, railroad_crossing_bell.mp3, submarine_diving.mp3, tornado_siren.mp3, bigben1.mp3, bigben2.mp3

#### Command sequences
It's possible to launch several orders afterwards by separating by *$$*

```
ex 1 : cmd=tts|sleep=2|value=Je lance ma vidéo$$app=media|cmd=play_video|value='http://contentlink','video/mp4','Video name'
ex 2 : app=media|cmd=play_video|value='http://contentlink','video/mp4','Video name',current_time:148|sleep=10$$cmd=quit_app
ex TTS command on several google cast in parallel making sure the file is already cached :   
    cmd=tts|value=My TTS message|generateonly=1$$uuid=XXXXXXXXXXX|cmd=tts|value=My TTS message$$uuid=YYYYYYYYYYY|cmd=tts|value=My TTS message
```
> **Note**   
> adding 'uuid' parameter will redirect to this uuid device in new thread. This can be used to send a sequence to several device in one command.

#### Device advanced configuration

##### Retreive a configuration
Some configurations can be retrieved in an info command (*cmd=getconfig*).

These commands are refreshed every 15 minutes or manually via the 'refreshconfig' command (not visible by default)

A list is available by connecting to the equipment:
http://IP:8008/setup/eureka_info?options=detail

For more info, check out https://rithvikvibhu.github.io/GHLocalApi/

###### available parameters for *getconfig* cmd :
```
- value: str - uri base after 'setup/' based on API doc (default is 'eureka_info'). If starts with 'post:', a POST type request will be issued.
- data: str - json path to be returned separated by '/'. To get several data, separate by ','. Alternatively, JsonPath format can be used ( http://goessner.net/articles/JsonPath).
- sep: str - seperator if several data is set (default = ',').
- format: json/string/custom - output format (default = 'string'). 'custom' follows 'sprintf' php function format (ex: %d, %s).
- error: 1 - seperator if several data is set (default = ',').
- reterror: str - value to be returned if connection fails. Default will not change previous state.

Exemples:
- Récupération du pincode d'une Google Chromecast :
cmd=getconfig|data=opencast_pin_code
- Google Home : Récupération de l'état de la première alarme (-1 en cas de problème ou non existant) :
cmd=getconfig|value=assistant/alarms|data=$.alarm.[0].status|reterror=-1
- Google Home : Récupération de la date et heure de la première alarme au format JJ-MM-AAAA HH:MM :
cmd=getconfig|value=assistant/alarms|data=$.alarm.[0].fire_time|fnc=ts2long|reterror=00-00-0000 00:00
- Google Home : Récupération de la date et heure de l'alarme avec id connu au format JJ-MM-AAAA HH:MM :
cmd=getconfig|value=assistant/alarms|data=$.alarm.[?(@.id=alarm/xxxxxx)].fire_time|fnc=ts2long|reterror=00-00-0000 00:00
- Changer le nom du Google cast :
cmd=setconfig|data={"name":"Mon nouveau nom"}
- Google Home : Désactiver le mode nuit :
cmd=setconfig|value=assistant/set_night_mode_params|data={"enabled": false}
- Google Home : Changer luminosité du mode nuit :
cmd=setconfig|value=assistant/set_night_mode_params|data={"led_brightness": 0.2}
```

##### Modify a configuration
Some configurations can be modified in an action type command (* cmd = setconfig *).

See the Google API on this link for what is editable : https://rithvikvibhu.github.io/GHLocalApi/

###### available parameters for *setconfig* cmd :
```
- value: str - uri base after 'setup/' based on API doc.
- data: str - json data.

Exemples:
- Disable notification on Google home :
cmd=setconfig|value=assistant/notifications|data={'notifications_enabled': false}
- Google Home : Volume au plus bas pour alarme :
cmd=setconfig|value=assistant/alarms/volume|data={'volume': 1}
```

##### Pre-defined configuration commands

The following commands can be used in an 'info' or scenario command (via fonction *getInfoHttpSimple()*) :

- *gh_get_alarms_date* : retourne la date de toutes les alarmes.
- *gh_get_alarms_id* : retourne les identifiants uniques de toutes les alarmes et timers.
- *gh_get_alarm_date_#* (#=numéro, commence par 0) : retourne la date de la prochaine alarme au format dd-mm-yyyy HH:mm.
- *gh_get_alarm_datenice_#* (#=numéro, commence par 0) : retourne la date de la prochaine alarme au format {'Today'|'Tomorrow'|dd-mm-yyyy} HH:mm.
- *gh_get_alarm_timestamp_#* (#=numéro, commence par 0) : retourne le timestamp de la prochaine alarme.
- *gh_get_alarm_status_#* (#=numéro, commence par 0) : statut de l'alarme (1 = configuré,  2 = sonne).
- *gh_get_timer_timesec_#* (#=numéro, commence par 0) : retourne le nombre de secondes avant déclenchement du timer.
- *gh_get_timer_time_#* (#=numéro, commence par 0) : retourne la date de déclenchement du timer.
- *gh_get_timer_duration_#* (#=numéro, commence par 0) : retourne la durée originale configurée du timer.
- *gh_get_timer_status_#* (#=numéro, commence par 0) : statut du timer (1 = configuré,  3 = sonne).
- *gh_get_donotdisturb* : retourne l'état de la fonction 'Do Not Disturb'.
- *gh_get_alarms_volume* : récupère le volume des alarmes et timers.
- *conf_pincode* : retourne le code pin d'association.
- *conf_getbonded_bluetooth* : retourne tous les équipements bluetooth enregistrés.
- *conf_getconnected_wifi* : retourne le nom du réseau wifi configuré.

Les commandes suivantes peuvent être utilisé dans une commande 'action' ou scénario (via fonction *setInfoHttpSimple()* ou commande *Custom Cmd*) :

- *gh_set_donotdisturb_on* : active la fonction 'Do Not Disturb'.
- *gh_set_donotdisturb_off* : désactive la fonction 'Do Not Disturb'.
- *gh_set_donotdisturb_#* (#=true/false) : active/désavtive la fonction 'Do Not Disturb'
- *gh_set_alarms_volume_#* (# = entre 0 et 100 (eg: 10)) : configure le volume des alarmes et timers.
- *bt_connectdefault* : connecte l'équipement bluetooth configuré par défaut.
- *bt_connect_X* (#=adresse mac au format xx:xx:xx:xx:xx:xx) : connecte l'équipement bluetooth donné en paramètre.
- *bt_disconnectdefault* : déconnecte l'équipement bluetooth configuré par défaut.

```
Exemples:
- info type command
gh_get_alarm_date_0
- action type command
gh_set_alarms_volume_80
```

### Adding a command *action* of type *List*

To create an *action* command of type *List* whose several parameters change, the command must imperatively be called *cmdlist_XXXX* with XXXX being able to be replaced by a name (example cmdlist_radio).

The *Value List* field must contain the list of commands and follow the format `<commands>|<displayed text>;<commands>|<displayed text>;;...`   
The separator needs to be changed from '|' to '^'.

````
Example for web sites :
app=web^cmd=load_url^value='https://google.com'|Google;
app=web^cmd=load_url^value='https://facebook.com'|Facebook

Example for webradio :
app=media^value='http://urlFluxRadio1/flux.mp3','audio/mpeg','Radio 1'|Radio 1;
app=media^value='http://urlFluxRadio2/flux.mp3','audio/mpeg','Radio 2'|Radio 2;
app=media^value='http://urlFluxRadio3/flux.mp3','audio/mpeg','Radio 3'|Radio 3
````

![Command action of type list](../images/commands_list.png "Command action of type list")

> **Note**   
> For simpler commands (only one parameter changes), it is still possible to use the placeholder *#listValue#* in a command.    
> Example : `app=web|cmd=load_url|value=#listValue#` avec comme liste de valeurs `https://google.com|Google;https://facebook.com|Facebook`


### Use in scenarios

#### With dedicated command *Custom Cmd*
The command called *Custom Cmd* is used to launch a raw command from a scenario.

For example, to launch Google on a Google Cast from a scenario, add the command with the desired value in the 'message' field.
```
app=web|cmd=load_url|value='https://google.com',True,10
```

![Scenario](../images/scenario.png "Scenario")

#### With php bloc code

Examples using php bloc :

```php
$googlecast = googlecast::byLogicalId('XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXX', 'googlecast');
if ( !is_object($googlecast) or $googlecast->getIsEnable()==false ) {
  $scenario->setData("_test", "None");
  // variable _test contains 'None' if google cast does not exist or is disable
}
else {
  // Run a command
  $ret =  $googlecast->helperSendCustomCmd('cmd=tts|value=Test Scénario PHP|vol=100');
  $scenario->setData("_test", $ret);
  // Command launched
  // $ret = true if command has been ran, false if deamon is not running
  // variable _test contains 1 if true, 0 if false

  // Configure a Google Home equipement
  $ret =  $googlecast->setInfoHttpSimple('bt_connect_xx:xx:xx:xx:xx:xx');
  // or $googlecast->helperSendCustomCmd('bt_connect_xx:xx:xx:xx:xx:xx'); (return false if deamon not running, true otherwise)
  // Try to connect a bluetooth device (mac=xx:xx:xx:xx:xx:xx) to Google Home
  // $ret = true if command has been launched, false if failed (Google Home not accessible)

  // Get curent GH alarm time (via long command)
  $ret =  $googlecast->getInfoHttpSimple('cmd=getconfig|value=assistant/alarms|data=$.alarm.[0].fire_time|fnc=ts2long|reterror=Undefined');
  $scenario->setData("_test",$ret);
  // variable _test contains dd-mm-yyyy HH:mm (Undefined if failed)

  // Get curent GH alarm time (via pre-configured command)
  $ret =  $googlecast->getInfoHttpSimple('gh_get_alarm_date_0');
  // or $googlecast->helperSendCustomCmd('gh_get_alarm_date_0'); (return false if deamon not running, true otherwise)
  $scenario->setData("_test",$ret);
  // variable _test contains dd-mm-yyyy HH:mm (Undefined if failed)

 // Get curent GH alarm date only (via long command with formatting)
  $ret =  $googlecast->getInfoHttpSimple('cmd=getconfig|value=assistant/alarms|data=$.alarm.[0].date_pattern|format=%02d%02d%04d|reterror=00000000');
  $scenario->setData("_test",$ret);
  // variable _test contains JJMMAAAA (00000000 if failed)
}
```

Example of TTS or NOTIF command waiting until finished :

```php
// -----------------------
// entire code
$uuid = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXX';
$maxwait = 30;	// 30 sec of max waiting
$retrydelay = 500*1000;	// will retry every 500 ms
$command_string = 'cmd=tts|value=Test Scénario PHP pour gérer le délai !|vol=100';

$googlecast = googlecast::byLogicalId($uuid, 'googlecast');
if ( !is_object($googlecast) or $googlecast->getIsEnable()==false or $googlecast->isOnline()==false ) {
  	return;
}
else {
  $googlecast->helperSendCustomCmd($command_string);
  sleep(2); // make sure command has started
  $status = $googlecast->getInfoValue('status_text');
  $starttime = time();
  while ($status=='Casting: TTS' or $status=='Casting: NOTIF' ) {
    usleep($retrydelay);    // or sleep(1);	// 1 sec
    $status = $googlecast->getInfoValue('status_text');
    if ( (time()-$starttime)>$maxwait ) {
      break;
    }
  }
  return;
}

// -----------------------
// using helper static method
// params: uuid, command, time in second before failing (default 30), retry delay in ms (default 500), initial delay in seconds (default 2)
// return true if success, false if uuid is wrong, disable, offline or delay has passed.
$ret = googlecast::helperSendNotifandWait_static('XXXXXXXX', 'cmd=tts|value=Test Scénario PHP pour gérer le délai', 30, 500);
// with default values : $ret = googlecast::helperSendNotifandWait_static('XXXXXXXX', 'cmd=tts|value=Test Scénario PHP')

// -----------------------
// or using helper instance method
$googlecast = googlecast::byLogicalId($uuid, 'googlecast');
// params: uuid, command, time in second before failing, retry delay in ms, initial delay in seconds (default 2)
// return true if success, false if disable, offline or delay has passed.
$ret = $googlecast->helperSendNotifandWait('XXXXXXXX', 'cmd=tts|value=Test Scénario PHP pour gérer le délai')
```

### Use with interactions and IFTTT

#### Interactions
Compatibility with IFTTT using the following url in the configuration:
```
http(s)://#JEEDOM_DNS#/plugins/googlecast/core/php/googlecast.ifttt.php?apikey=#GCASTPLUGIN_APIKEY#&uuid=#GCAST_UUID#&query=<<{{TextField}}>>
Optional :   
  &vol=X (between 1 and 100)    
  &noresume    
  &quit
  &silence=X (between 1 and 100)
```
Documentation Jeedom et IFTTT : https://jeedom.github.io/plugin-gcast

#### Custom CMD
Send a custom command using webhooks
```
http(s)://#JEEDOM_DNS#/plugins/googlecast/core/php/googlecast.ifttt.php?apikey=#GCASTPLUGIN_APIKEY#&uuid=#GCAST_UUID#&action=customcmd&query=#CUSTOM_CMD#
Notes :   
  #CUSTOM_CMD# : as defined in documentation (eg : app=web|cmd=load_url|value='http://pictoplasma.sound-creatures.com')    
  It may be necessary to encode #CUSTOM_CMD# using https://www.url-encode-decode.com/
```


Known limitations and bugs
=============================

- PicoTTS engine does not handle accented sentences (removed)


FAQ
=============================

#### No detection during the scan

- Check that the Google Cast is available from an application allowing the visualization of compatible devices;
- Jeedom must be on the same network as Google Cast devices
(for Docker, the container must be configured to be on the same network, in VM, the machine is in bridge mode);
- Check that there are no blockages at the firewall for discovery via the 'Zeroconf' protocol;
- To put Docker on the same network, see https://github.com/guirem/plugin-googlecast/issues/8

#### No commands seems to work

- Check that Google Cast works with other devices;
- Check that nothing has changed since the scan;

#### Some commands do not work

- It may depend on the model and the application using it;

#### Dependencies can't install properly

- Check the logs for the source of the error. The plugin requires the installation of python3 and pip3.

#### Text To Speech (TTS) doen't work

- Try with the following parameters: 'Use external Jeedom address' or 'Do not use cache'
- If Jeedom does not have web access, use the picoTTS engine
- Check the logs for the nature of the error

#### Broadcast Jeedom without authentication on a Google Cast

This is possible via the web mode. To manage the authentication automatically, use the plugin 'autologin' (see doc of the plugin).

#### Get an API Key for Google Speech API

The steps to get this key are on this link : http://domotique-home.fr/comment-obtenir-google-speech-api-et-integrer-dans-sarah/

Changelog
=============================

[See dedicated page](changelog.md).
