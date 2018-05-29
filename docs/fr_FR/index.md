Plugin GoogleCast (googlecast)
=============================

![Logo plugin](../images/logoplugin.png "Logo plugin")

Plugin pour commander les équipements compatibles Google Cast.


**Fonctionnalités :**

- Contrôle du son (mute, +/-)
- Contrôle des médias (play/pause/stop...)
- Arrêt appli en cours, reboot
- Diffuser une page web sur un écran
- Lecture de fichier audio et vidéo via url
- Retour d'état sur les principales Fonctionnalités
- Affichage de la lecture en cours
- Text To Speech (TTS)
- Récupération/modification de la configuration


![Logo plugin](../images/chromecast.png "Chromecast")

**Modèle compatibles Google Cast**
- Chromecast Audio/Video
- Android TV, Nexus Player, TV (Vizio, Sharp, Sony, Toshiba, Philips)
- Google Home
- Soundbars and speakers (Vizio, Sony, LG, Philips
B&O Play, Grundig, Polk Audio, Bang & Olufsen, Onkyo, Pioneer...)
- Autres modèles labelisés *Google Cast*

![GoogleCast Logo](../images/googlecast_logo.png "GoogleCast Logo")
![Android TV](../images/tv.png "Android TV")

**Autres liens**
- Wikipedia <a target="_blank" href="https://en.wikipedia.org/wiki/Google_Cast">GoogleCast</a>
- <a target="_blank" href="https://en.wikipedia.org/wiki/List_of_apps_with_Google_Cast_support">Applications</a> pouvant diffuser sur un équipement GoogleCast


Dashboard
=======================

![Visuel du dashboard](../images/dashboard.png "Visuel du dashboard")

Configuration du plugin
=======================

Après téléchargement du plugin :
- Activer le plugin
- Lancer l'installation des dépendances
- Niveau de log recommandé : info
- Lancer le démon.

Les paramêtres de configuration n'ont généralement pas besoin d'être modifiés
- Port du socket interne de communication. Ne modifier que si nécessaire (ex: s'il est déjà pris par un autres plugin)
- Fréquence de rafraîchissement. A ne modifier uniquement si la fréquence normale à un impact important sur les performances globales
- TTS - Utiliser l'adresse Jeedom externe : par défaut utilise l'addresse web Jeedom interne
- TTS - Langue par défaut : langue du moteur TTS utilisé par défaut
- TTS - Moteur par défaut : le moteur TTS utilisé (PicoTTS ou Google Translate)
- TTS - Vitesse de parole : rapidité de prononciation du texte
- TTS - Ne pas utiliser le cache : désactive l'utilisation du cache Jeedom (déconnseillé)
- TTS - Nettoyer cache : nettoie le repertoire temporaire de generation des fichiers sons
- Désactiver notif pour nouveaux GoogleCast : ce sont des notifications lors de la découverte de nouveaux Google Cast non configurés

> **Notes**  
> Pour TTS (Text To Speech)
> - PicoTTS ne nécessite pas de connexion internet, l'API Google Translate nécessite un accès web et le rendu est meilleur.
> - Un mécanisme de cache permet de ne générer le rendu sonore que s'il n'existe pas déjà en memoire. La cache est vidé au redémarrage de Jeedom.

![Configuration Plugin](../images/configuration_plugin.png "Configuration Plugin")

Configuration des équipements
=============================

La configuration des équipements GoogleCast est accessible à partir du menu *Plugins > Multimedia > Google Cast*.

![Configuration](../images/configuration.png "Configuration")

Une fois les équipements branchés, lancer un scan pour les détecter et les ajouter automatiquement. Si aucun équipement apparait, bien vérifier que les équipements sont accessibles et alimentés.

La vue 'Santé'' permet d'avoir une vue synthétique des équipements et de leurs états.

> **Note**    
> Il n'est pas possible d'ajouter manuellement un Google Cast

### Onglet Commandes

Les commandes de bases sont générées automatiquement.

Vous pouvez également ajouter de nouvelles commandes (voir section ci-dessous).

![Alt text](../images/commands.png "Custom command")

Liste des commandes non visibles par défaut :
- *Statut Player* : info affichant l'état de lecture Média (ex: PLAYING/PAUSED) ;
- *Titre* : Titre du média en cours ;
- *Artist* : Artist du média en cours ;
- *Custom Cmd* : Ce composant est destiné à être utilisé via un schénario ou pour test (voir section [Utilisation dans un scénario](#utilisation-dans-un-scénario));
- *Pincode* : pincode pour association rapide (exemple de configuration avancée) 

Pour les voir sur le dashboard, il faut activer 'Afficher' dans l'onglet des commandes.


### Afficheur Lecture en cours (widget)

La commande de type information appelée 'Playing Widget' (visible par défaut) permet d'afficher l'image de la lecture en cours.

L'afficheur se rafraichit toutes les 20 secondes par défaut.

![Display 1](../images/display1.png "Display 1")

Installation / configuration :
- Affiché par défaut après installation. Désactiver l'affichage pour cacher.
- Pour une utilisation dans un dashboard, iL est possible d'utiliser un virtuel en créant une commande de type *info / autres* avec pour valeur la commande *Display* de l'ampli. Appliquer alors le widget dashboard *googlecast_playing* (via onglet *Affichage* de la configuration avancée de la commande)
- Pour une utilisation dans un design, ajouter la commande *Playing Widget* directement dans le design.

Paramêtres CSS optionnels (via '*Paramètres optionnels widget*'):
- *fontSize* (ex: 35px, défaut=25px) : taille de police de base
- *fontColor* (ex: blue, défaut=white) : couleur de l'afficheur
- *fontFamily* (ex: 'Arial') : change la police de l'afficheur
- *backColor* (ex: blue, défaut=black) : couleur du fond de l'afficheur
- *playingSize* (ex: 300px, défaut 250px) : Largeur et hauteur de l'image de lecture en cours
- *contentSize* (ex: 70px,défaut 50px) : Hauteur de la partie textuelle
- *additionalCss* (format css, ex: '.blabla {...}') : pour ajouter/modifier d'autres CSS (utilisateur avancé)

![Configuration CSS](../images/configuration_css.png "Configuration CSS")

> **Notes**   
> Non disponible pour mobile pour le moment


Commandes personnalisées
=============================

### Applications spéciales

- *Web* : afficher une page web sur un google cast. Les paramêtres disponibles sont l'url, forcer, et le délai de recharchement (ex: value='https://google.com',False,0 pour charger Google sans forcer (nécessaire pour certains sites) et sans rechargement)
- *Media* : lire un fichier audio ou vidéo à partir d'une URL
- *YouTube* : afficher une vidéo à artir d'un ID de vidéo (en fin d'url) => Ne fonctionne pas pour le moment
- *Backdrom* : afficher le fond d'écran ou économiseur d'écran Google Cast (selon les modèles)

> **Notes**   
> - Voir les boutons créés par défaut pour un exemple d'utilisation    
> - Youtube est non fontionnel pour le moment


### Commandes avancées

#### Syntaxe des commandes brutes
Elles doivent être séparés par *|*
```
- app : name of application (web/backdrop/youtube/media)
- cmd : name of command (dépend of application)
    * tts : text to speech, use value to pass text
    * refresh
    * reboot
    * volume_up
    * volume_down
    * volume_set : use value (0-100)
    * mute_on
    * muto_off
    * quit_app
    * start_app : use value to pass app id
    * play
    * stop
    * rewind
    * skip
    * seek : use value (seconds)
    * pause
    For application dependant commands
        * web : load_url
        * media : play_media
        * youtube : play_video/add_to_queue/update_screen_id/clear_playlist
        * backdrop : no command
- value : chain of parameters seperated by ','
- vol (optional, entre 1 et 100) : ajuster le volume pour la commande
- sleep (optional) : add a break after end of command (in seconds)

ex web : app=web|cmd=load_url|vol=90|value='http://pictoplasma.sound-creatures.com',True,10
ex TTS : cmd=tts|vol=100|value=Mon text a dire
```

> **Notes**     
> les chaines de caractères pour les commandes sont limitées dans Jeedom à 128 caractères. Utiliser les scénarios (voir plus bas pour passer outre cette limitation)

#### Paramêtres possibles pour *play_video* en mode *media* :
```
- url: str - url of the media.
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

ex short : app=media|cmd=play_video|value='http://contentlink','video/mp4','Video name'

ex long : app=media|cmd=play_video|value='http://contentlink','video/mp4',title:'Video name',
   thumb:'http://imagelink',autoplay:True,
   subtitles:'http://subtitlelink',subtitles_lang:'fr-FR',
   subtitles_mime:'text/vtt'
```

> **Notes**   
> - Les url et chaines de caractères sont entourés de guillements simples ('). Les autres valeurs possibles sont True/False/None ainsi que des valeurs numériques entières.
> - Il est nécessaire de remplacer le signe '=' dans les url par '%3D'

#### Paramêtres possibles pour *load_url* en mode *web* :
```
- url: str - website url.
- force: bool - force mode. To be used if default is not working. (optional, default False).
- reload: int - reload time in seconds. 0 = no reload. (optional, default 0)

ex 1 : app=web|cmd=load_url|value='http://pictoplasma.sound-creatures.com',True,10
ex 2 : app=web|cmd=load_url|value='http://mywebsite/index.php?apikey%3Dmyapikey'
```

> **Notes**   
> - Les url et chaines de caractères sont entourés de guillements simples ('). Les autres valeurs possibles sont True/False/None ainsi que des valeurs numériques entières.
> - Il est nécessaire de remplacer le signe '=' dans les url par '%3D'

#### Paramêtres possibles pour cmd *tts* :
```
- lang: str - fr-FR/en-US or any compatible language (optional)
- engine: str - picotts/gtts. (optional)
- quit: 0/1 - quit app after tts action.
- forcetts: 1 - do not use cache (useful for testing).
- speed: float (default=1.2) - speed of speech (eg: 0.5, 2).

ex : cmd=tts|value=My text|lang=en-US|engine=gtts|quit=1
ex : cmd=tts|value=Mon texte|engine=gtts|speed=0.8|forcetts=1
```

#### Séquence de commandes
Il est possible de lancer plusieurs commandes à la suite en séparant par *$$*

```
ex 1 : cmd=tts|sleep=2|value=Je lance ma vidéo$$app=media|cmd=play_video|value='http://contentlink','video/mp4','Video name'
ex 2 : app=media|cmd=play_video|value='http://contentlink','video/mp4','Video name',current_time:148|sleep=10$$cmd=quit_app
```

#### Configuration avancé des équipements

##### Récupérer une configuration
Certaines configurations peuvent être récupérées dans une commande de type info (*cmd=getconfig*).

Ces commandes de ce type sont rafraichies toutes les 15 minutes ou manuellement via appel de la commande 'refreshconfig' (non visible par défaut)

Une liste est disponible en se connectant sur l'équipement :
http://IP:8008/setup/eureka_info?options=detail

Pour plus d'info voir  https://rithvikvibhu.github.io/GHLocalApi/

###### Paramêtres possibles pour cmd *getconfig* :
```
- value: str - uri base after 'setup/' based on API doc (default is 'eureka_info'). If starts with 'post:', a POST type request will be issued.
- data: str - json path to be returned seperated by '/'. To get several data, seperate by ','.
- sep: str - seperator if several data is set (default = ',').
- format: json/string - output format (default = 'string').
- error: 1 - seperator if several data is set (default = ',').
- reterror: str - value to be returned if connection fails. Default will not change previous state.

Exemples:
- Récupération le Pin code d'une Google Chromecast :
cmd=getconfig|data=opencast_pin_code
- Google Home : Récupération de l'état de la première alarme :
cmd=getconfig|value=assistant/alarms|data=alarm/0/status
```

##### Modifier une configuration
Certaines configurations peuvent être modifiées dans une commande de type action (*cmd=setconfig*).

Voir l'api Google sur ce lien pour ce qui est modifiable : https://rithvikvibhu.github.io/GHLocalApi/

###### Paramêtres possibles pour cmd *setconfig* :
```
- value: str - uri base after 'setup/' based on API doc.
- data: str - json data.

Exemples:
- Disable notification on Google home
cmd=setconfig|value=assistant/notifications|data={'notifications_enabled': false}
- Google Home : Volume au plus bas pour alarme :
cmd=setconfig|value=assistant/alarms/volume|data={'volume': 1}
```

### Utilisation dans un scénario

La commande nommée *Custom Cmd* permet de lancer une commande brute à partir d'un scénario.

Par exemple pour lancer Google sur un Google Cast à partir d'un scénrio, ajouter la commande avec la valeur souhaitée dans le champs 'message'.
```
app=web|cmd=load_url|value='https://google.com',True,10
```

![Scenario](../images/scenario.png "Scenario")


FAQ
=============================

#### Aucune détection lors du scan

- Vérifier que le Google Cast est disponible à partir d'une application permettant la visulisation des appareils compatibles ;
- Jeedom doit se trouver sur le même réseau que les équipements Google Cast    
(pour docker, le container est soit en mode Host, soit est configuré pour être sur le même réseau ; en VM, la machine est en mode bridge) ;
- Vérifier qu'il n'y a pas de blocages au niveau du firewall pour la découverte via le protocol 'Zeroconf' ;

#### Aucune commande ne semble fonctionner

- Vérifier que le Google Cast fonctionne avec d'autres équipements ;
- Vérifier que rien n'a changé depuis le scan ;

#### Certaines commandes ne fonctionnent pas

- Cela peut dépendre du modèle et de l'application l'utilisant ;

#### Les dépendances ne s'installent pas

- Vérifier dans les logs la provenance de l'erreur. Le plugin nécessite l'installation de python3 et pip3.

#### Le Text To Speech (TTS) ne fonctionne pas

- Essayer avec les paramêtres suivants : 'Utiliser l'adresse Jeedom externe' ou 'Ne pas utiliser le cache'
- Si jeedom n'a pas d'accès web, utiliser le moteur picoTTS
- Vérifier dans les logs la nature de l'erreur

#### Diffuser Jeedom sans authentification sur un Google Cast

C'est possible via le mode web. Pour gérer l'authentification automatiquement, utiliser le plugin 'autologin' (voir doc du plugin).

Changelog
=============================

[Voir la page dédiée](changelog.md).
