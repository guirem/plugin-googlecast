# Changelog

Version list of googlecast plugin.

*[Back to documentation] (index.md)*

## Version of July 04, 2020 (stable) - 2.16

- see beta changelog 2.16 below

## Version of May 29, 2020 (beta) - 2.16

- fix deconnexion de chromecast dans certains cas
- maj des libraries pychromecast et spotipy
- fix partiellement spotify (voir doc)
- configuration page UI

## Version of February 09, 2020 (beta/stable) - 2.15

- added possibility to get alamrs and timers if token is provided
  https://gist.github.com/rithvikvibhu/1a0f4937af957ef6a78453e3be482c1f#the-token
- googlecast detection optimization
- fix volume status control
- added previous playlist song button
- update radio list (75 french) and added slector to widget
- pychromecast library update
- code cleaning

## Version of January 20, 2020 (beta/stable) - 2.14

- fix bug ssml (google cloud ttts)
- fix tts webserver integration
- minor optimizations

## Version du January 11, 2020 (stable)

- push 2.11, 2.12 et 2.13 beta to stable.

## Version of January 08, 2020 (beta) - 2.13

- engine 'TTS Google Speech API' removed and replaced by 'Google Cloud Text-To-Speech' (https://cloud.google.com/text-to-speech/)
  (check doc FAQ if API key doesn't work anymore)
- documentation update

## Version of January 07, 2020 (beta) - 2.12

- optimizations and bug fixes
- fix zeroconf dependency bug
- added androidtv model logo
- removed 'reboot' button from UI (not working anymore)
- documentation update and added debug logs

## Version of December 30, 2019 (beta) - 2.11

- TTS : addition of core Jeedom TTS engine and TTSWebserver
- Jeedom 4 et php7 Compatibility
- added logo for Google Hub
- fix for debian buster installation
- core libraries update

## Version of August 27, 2019 (beta/stable) - 2.10

- Jeedom 4 (php 7.3) basic compatibility

## Version of December 11, 2018 (beta/stable)

- Update of gtts library
- Possible fix for zeronconf dependency installation

## Version of October 14, 2018 (stable)

- beta to stable (see 04 October)

## Version of October 04, 2018 (beta)

- added spanish translation (framirezl)
- updated gtts library (error : 'NoneType' object has no attribute 'group')
- fix log output when set to none
- bug fixes and minor changes
- fix volume param not working for IFTTT
- fix cleanCache not cleaning after expiration
- doc update

## Version of July 11, 2018 (stable)

- compatibility ifttt/ask for google assistant
- doc update for IFTTT

## Version of June 28, 2018 (beta/stable)

- exception management optimization
- bug fix and doc update

## Version of June 20, 2018 (beta/stable)

- Added option 'live' for live stream type such as online radio (fix stream resume issue)
- Added ssml compatibility for gttsapi/gttsapidev tts engine (for advanced tts - see https://cloud.google.com/text-to-speech/docs/ssml)
- Added male voice for gttsapi/gttsapidev tts engine (with voice=male option)
- Added cmd 'warmupnotif' to prepare device for tts message (google cast device sync)
- bug fix and doc update

## Version of June 14, 2018

- Added broadcast option
- fix sequences
- bug fix and doc update

## Version of June 12 juin, 2018 (stable)

- Beta to stable (see below)

## Version of June 12 juin, 2018 (beta)

- IFTTT interactions and webhooks
- Doc update (toc and ifttt)
- English doc translation

## Version of June 11, 2018 (beta)

- Cleaning / optimization of the order configuration page
- Compatibility command action of list type
- New command 'notif' (similar to tts but to play a local mp3)
    Test with `cmd=notif|value=bigben1.mp3|vol=100`
- Possibility to play local files for media app
- fix getconfig (jsonpath compatibility)
- fix update of the command info title / artist / player_state
- Bug fixes and maj doc

## Version of 09 June 2018 (stable)

- Change from beta to stable (see beta changes)
- Resume of the previous stream after TTS when launched via the plugin only
- Default 'speak' widget
- Bug fixes and maj doc

## Version of 09 June 2018 (beta)

- Fix when no volume
- Now 'resume' is the default behavior. You must use noresume = 1 to disable it
- For the summary, a 'play' is forced
- Fix for failover picotts when no internet
- In case of error, 'status_text' is 'ERROR', 'CMD UNKNOWN' is the command does not exist or 'NOT CONNECTED' if offline

## Version of June 08, 2018 (beta)

- Implemention function 'resume' for TTS. Only available for applications launched via the plugin (Google limitation)
- Fix for GH alarm return
- Minor bug fixes
- Plugin icon change (by Alois)
- Doc shift (example php block for scenario)

## Version of June 07, 2018 (beta)

- First version of the 'resume' function for TTS
- Dedicated Widget for TTS
- Minor bug fixes

## Version of June 06, 2018

- Beta to stable (see below)
- Features: TTS (4 engines), Plex, Google Cast config recovery
- Bug fixes and doc maj

## Version of June 04, 2018 (beta)

- Added Google Speech API engine (key needed)
- Added PLEX management
- Bug fixes and doc maj

## Version of May 29, 2018 (beta)

- Added speed of speech management for TTS
- Recovery / modification of equipment configuration (eg: Google Home alarm / timer)
- Bug fixes and doc maj

## Version of May 25, 2018 (beta)

- Added 'info' commands: title, artist, player_state
- Added 'vol' option for each command to modify the volume (see doc)
- Added TextToSpeach (TTS) with Google Translate and PicoTTS engine (see doc)
- Possibility of launching a command sequence (see doc)
- Bug fixes and doc maj

## Version of April 25, 2018

- Fix installation of dependencies for certain systems
- Fix impossibility of (re) connection after a few hours
- Reduction of memory tile (leakage)

## Version of April 23, 2018

- Fix installation of dependencies for raspberry
- Fix impossibility of (re) connection
- Added possibility to adjust the refresh rate

## Version of April 18, 2018

Initial stable release
