# Changelog

Liste des versions du plugin googlecast.

*[Retour à la documentation](index.md)*

## Version du 01 décembre 2021 (beta/stable) - 2.19

- maj librairies pychromecast
- compatibilité jeedom 4.2

## Version du 10 juillet 2021 (beta) - 2.18

- maj librairies pychromecast, gtts, pydub, spotipy
- amelioration de le detection de connexion des équipements chromecast

## Version du 20 décembre 2020 (beta/stable) - 2.17

- maj librairie google translate api
- ajout de nouvelles images d'appareils

## Version du 04 juillet 2020 (stable) - 2.16

- voir changelog version beta

## Version du 29 mai 2020 (beta) - 2.16

- fix deconnexion de chromecast dans certains cas
- maj des libraries pychromecast et spotipy
- fix partiellement spotify (voir doc)
- fix bug de page configuration

## Version du 09 février 2020 (beta/stable) - 2.15

- récupération des alarmes/timers et autres config refonctionne si le jeton est bien renseigné
  https://gist.github.com/rithvikvibhu/1a0f4937af957ef6a78453e3be482c1f#the-token
- optimisation de la detection de googlecast
- correction bug de mise à jour du volume
- ajout d'un bouton pour aller au média précédant d'une playlist
- mise à jour des radios (75) et ajout d'un selecteur sur widget
- mise à jour de la librairie pychromecast
- nettoyage de code

## Version du 20 janvier 2020 (beta/stable) - 2.14

- correction bug ssml (google cloud ttts)
- correction bug intégration tts webserver
- optimisations mineures

## Version du 11 janvier 2020 (stable)

- Passage des versions 2.11, 2.12 et 2.13 beta en stable.

## Version du 08 janvier 2020 (beta) - 2.13

- suppression du moteur 'TTS Google Speech API', remplacé par 'Google Cloud Text-To-Speech' (https://cloud.google.com/text-to-speech/)
  (voir FAQ documentation si la clé API ne fonctionne plus)
- mise à jour de la documentation

## Version du 07 janvier 2020 (beta) - 2.12

- optimisations et corrections de bugs
- fix du bug de dépendance zeroconf
- ajout logo pour modèles androidtv
- suppression du bouton 'reboot' (ne fonctionne plus)
- mise à jour de la documentation et ajout de logs pour debug

## Version du 30 décembre 2019 (beta) - 2.11

- TTS : ajout des moteurs TTS de Jeedom et TTSWebserver
- Compatibilité Jeedom 4 et php7
- Ajout icon pour Google Hub
- Fix installation sur debian buster
- Mise à jour de libraries du plugin

## Version du 27 aout 2019 (beta/stable) - 2.10

- Début de compatibilité avec Jeedom 4 (php 7.3)

## Version du 11 décembre 2018 (beta/stable)

- Mise à jour de la librairie gTTS pour le TTS
- Fix possible pour l'installation de dépendance zeroconf

## Version du 14 octobre 2018 (stable)

- passage beta en stable (voir 04 octobre)

## Version du 04 octobre 2018 (beta)

- ajout traduction espagnol (framirezl)
- maj librairies gtts (erreur : 'NoneType' object has no attribute 'group')
- correction des logs quand configuré sur aucun
- correction de bugs et changements mineurs
- fix param volume qui ne fonctionne pas pour IFTTT
- fix cleanCache qui ne nettoie pas après expiration
- maj doc

## Version du 11 juillet 2018 (stable)

- compatibilité ifttt/ask pour google assistants
- maj doc partie IFTTT

## Version du 28 juin 2018 (beta/stable)

- optimisation de la gestion des exceptions
- bug fix et maj doc

## Version du 20 juin 2018 (beta/stable)

- Ajout option 'live' pour les streams de type radio en ligne (fix problème de resume de stream)
- Ajout compatibilité ssml pour moteur tts gttsapi/gttsapidev (permet de faire du tts avancé - voir https://cloud.google.com/text-to-speech/docs/ssml)
- Ajout option de voix masculine pour moteur tts gttsapi/gttsapidev (avec option voice=male)
- Ajout cmd 'warmupnotif' pour préparer les équipements au tts (synchro des google cast)
- bug fix et maj doc

## Version du 14 juin 2018

- Ajout option broadcast
- fix sequences
- bug fix et maj doc

## Version du 12 juin 2018

- Passage de la beta en stable (voir dessous)

## Version du 12 juin 2018 (beta)

- Interaction IFTTT et webhooks
- Maj doc (toc et ifttt)
- English doc translation

## Version du 11 juin 2018 (beta)

- Nettoyage/optimisation de la page de configuration des commandes
- Compatibilité commande action de type liste
- Nouvelle commande 'notif' (similaire à tts mais pour jouer un mp3 local)
  Tester avec`cmd=notif|value=bigben1.mp3|vol=100`
- Possiblité de jouer des fichiers en local pour app media
- fix getconfig (compatiblité jsonpath)
- fix update des command info title/artist/player_state
- Correction de bugs and maj doc

## Version du 09 juin 2018 (stable)

- Passage de la beta en stable (voir les changements beta)
- Reprise du flux précédant après TTS lorsque lancé via le plugin uniquement
- Widget 'speak' par défaut
- Correction de bugs and maj doc

## Version du 09 juin 2018 (beta)

- Fix quand pas de volume
- Maintenant 'resume' est le comportement par défaut. Il faut utiliser noresume=1 pour le désactiver
- Pour le resume, un 'play' est forcé
- Fix pour failover picotts quand pas d'internet
- En cas d'erreur, 'status_text' est à 'ERROR' , 'CMD UNKNOWN' is la commande n'existe pas ou 'NOT CONNECTED' si offline

## Version du 08 juin 2018 (beta)

- Implémention fonction 'resume' pour TTS. Dsiponible que pour les applications lancées via le plugin (limitation Google)
- Fix pour retour alarme GH
- Correction de bug mineurs
- Changement d'icone du plugin (par Alois)
- Maj doc (exemple de bloc php pour scénario)

## Version du 07 juin 2018 (beta)

- Première version de la fonction 'resume' pour TTS
- Widget dédié pour TTS
- Correction de bug mineurs

## Version du 06 juin 2018

- Passage de la beta en stable (voir dessous)
- Fonctionnalités: TTS (4 moteurs), Plex, récupération config Google Cast
- Correction de bugs et maj doc

## Version du 04 juin 2018 (beta)

- Ajout du moteur Google Speech API (clé nécessaire)
- Ajout gestion PLEX
- Correction de bugs et maj doc

## Version du 29 mai 2018 (beta)

- Ajout de gestion de rapidité de parole pour TTS
- Récupération/modification de la configuration des équipements (ex: alarme/timer Google Home)
- Correction de bugs et maj doc

## Version du 25 mai 2018 (beta)

- Ajout de commandes 'info' : title, artist, player_state
- Ajout de l'option 'vol' pour chaque commande afin de modifier le volume (voir doc)
- Ajout du TextToSpeach (TTS) avec moteur Google Translate et PicoTTS (voir doc)
- Possibilité de lancer une séquence de commande (voir doc)
- Correction de bugs et maj doc

## Version du 25 avril 2018

- Fix installation des dépendances pour certain systèmes
- Fix impossibilité de (re)connection après quelques heures
- Réduction de l'tuilisation mémoire (fuite)

## Version du 23 avril 2018

- Fix installation des dépendances pour raspberry
- Fix impossibilité de (re)connection
- Ajout de possibilité de réglage de la fréquence de rafraîchissement

## Version du 18 avril 2018

Première version stable
