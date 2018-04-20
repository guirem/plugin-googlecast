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
- <a target="_blank" href="https://en.wikipedia.org/wiki/List_of_apps_with_Google_Cast_support">Applications</a> pouvant diffuser sur un équipement GoogleCast :


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
- Désactiver notif pour nouveaux GoogleCast : ce sont des notifications lors de la découverte de nouveaux Google Cast non configurés

Configuration des équipements
=============================

La configuration des équipements GoogleCast est accessible à partir du menu *Plugins > Multimedia > Google Cast*.

![Configuration](../images/configuration.png "Configuration")

Une fois les équipements alimentés, lancer un scan pour détecter et ajouter automatiquement. Si aucun équipement apparait, bien vérifier que les équipements sont accessibles et alimentés.

La vue santé permet d'avoir une vue synthétique des équipements et de leurs états.


### Onglet Commandes

Les commandes de bases sont générées automatiquement.

Vous pouvez également ajouter de nouvelles commandes (voir section ci-dessous).

![Alt text](../images/commands.png "Custom command")

Liste des commandes non visibles par défaut :
- *Statut Player* : info affichant l'état de lecture Média (ex: PLAYING/PAUSED) ;
- *Custom Cmd* : Ce composant est destiné à être utilisé via un schénario ou pour test ;

Pour les voir sur le dashboard, il faut activer 'Afficher' dans l'onglet des commandes.

> **Notes**
>
> - La commande de volume se fait sur des valeurs entre 0 et 98 et non pas sur des valeurs en db.

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

- *Backdrom* afficher le fond d'écran ou économiseur d'écran Google Cast (selon les modèles)
- *Web* afficher une page web sur un google cast. Les paramêtres disponibles sont l'url, forcer, et le délai de recharchement (ex: value='https://google.com',False,0 pour charger Google sans forcer (nécessaire pour certains sites) et sans rechargement)
- *Media* lire un fichier audio ou vidéo à partir d'une URL

```
- url: str - url of the media.
- content_type: str - mime type. Example: 'video/mp4' (optional).
- title: str - title of the media (optional).
- thumb: str - thumbnail image url (optional, default=None).
- current_time: float - seconds from the beginning of the media to start playback (optional, default=0).
- autoplay: bool - whether the media will automatically play (optional, default=True).
- stream_type: str - describes the type of media artifact as one of the following: "NONE", "BUFFERED", "LIVE" (optional, default='BUFFERED').
- subtitles: str - url of subtitle file to be shown on chromecast (optional, default=None).
- subtitles_lang: str - language for subtitles (optional, default='en-US').
- subtitles_mime: str - mimetype of subtitles (optional, default='text/vtt').
- subtitle_id: int - id of subtitle to be loaded (optional, default=1).

ex : value='http://bit.ly/2JzYtfX,video/mp4','video/mp4',title='Video',
   thumb=None,current_time=0,autoplay=True,
   stream_type=BUFFERED,metadata=None,
   subtitles=None,subtitles_lang='fr-FR',
   subtitles_mime='text/vtt',subtitle_id=1
```
- *YouTube* afficher une vidéo à artir d'un ID de vidéo (en fin d'url)

> **Notes**   
> Voir les boutons créés par défaut pour un exemple d'utilisation


### Commandes avancées

Syntaxe des commandes brutes (séparés par des *|*)
```
- app : name of application (web/backdrop/youtube/media)
- cmd : name of command (dépend of application)
    * web : load_url
    * youtube : play_video/add_to_queue/update_screen_id/clear_playlist
    * backdrop : no command
    * media : play_media/play/stop/pause
- value : chain of paramteres seperated by ','

app=web|cmd=load_url|value='http://pictoplasma.sound-creatures.com',True,10
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

Changelog
=============================

[Voir la page dédiée](changelog.md).
