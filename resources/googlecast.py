# This file is part of Jeedom.
#
# Jeedom is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Jeedom is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Jeedom. If not, see <http://www.gnu.org/licenses/>.
#
# pylint: disable=C
# pylint: disable=R
# pylint: disable=W
# pylint: disable=E

import os,re
import os.path
import shutil
import logging
import sys
import argparse
import time
from datetime import datetime
import signal
import json
import traceback
import _thread as thread
import socket
import resource
from pydub import AudioSegment
import hashlib
from gtts import gTTS

import globals

# check imports
try:
    import pychromecast.pychromecast as pychromecast
except ImportError:
    logging.error("ERROR: Main pychromecast module not loaded !")
    logging.error(traceback.format_exc())
    sys.exit(1)

try:
    import pychromecast.pychromecast.controllers.dashcast as dashcast
    import pychromecast.pychromecast.controllers.spotify as Spotify
    import pychromecast.pychromecast.controllers.youtube as youtube
except ImportError:
    logging.error("ERROR: One or several pychromecast controllers are not loaded !")
    print(traceback.format_exc())
    pass

try:
    #import pychromecast.pychromecast.customcontrollers.youtube as youtube
    import pychromecast.pychromecast.customcontrollers.plex2 as plex
except ImportError:
    logging.error("ERROR: Custom controller not loaded !")
    logging.error(traceback.format_exc())
    pass

try:
    from plexapi.myplex import MyPlexAccount
    from plexapi.server import PlexServer
except ImportError:
    logging.error("ERROR: Plex API not loaded !")
    logging.error(traceback.format_exc())
    pass

try:
    import spotipy.spotify_token as stoken
    import spotipy
except ImportError:
    logging.error("ERROR: Spotify API not loaded !")
    logging.error(traceback.format_exc())
    pass

try:
    from jeedom.jeedom import *
except ImportError:
    print("Error: importing module from jeedom folder")
    sys.exit(1)

# ------------------------

# class JeedomChromeCast
class JeedomChromeCast :
    def __init__(self, gcast, options=None, scan_mode=False):
        self.uuid = str(gcast.device.uuid)
        self.friendly_name = gcast.device.friendly_name
        self.gcast = gcast
        self.previous_status = {"uuid" : self.uuid, "online" : False}
        self.now_playing = False
        self.online = True
        self.scan_mode = scan_mode
        if scan_mode == False :
            self.being_shutdown = False
            self.is_recovering = False
            self.disable_notif = False
            self.customplayer = None
            self.customplayername = ""
            self.previous_playercmd =  {}
            self.sessionid_storenext = False
            self.sessionid_current = ''
            self.nowplaying_lastupdated = 0
            self.gcast.media_controller.register_status_listener(self)
            self.gcast.register_status_listener(self)
            self.gcast.register_connection_listener(self)
            self.options = options
            # manage CEC exception
            if options and 'ignore_CEC' in options :
                if options['ignore_CEC'] == "1" and self.friendly_name not in pychromecast.IGNORE_CEC :
                    pychromecast.IGNORE_CEC.append(self.gcast.device.friendly_name)
            # CEC always disable for audio chromecast
            if self.gcast.device.cast_type != 'cast' and self.friendly_name not in pychromecast.IGNORE_CEC:
                pychromecast.IGNORE_CEC.append(self.gcast.device.friendly_name)

            if self.gcast.socket_client :
                self.gcast.socket_client.tries = int(round(globals.SCAN_FREQUENCY)/10/2)
                self.gcast.socket_client.retry_wait = 5
                self.gcast.socket_client.timeout = 5

    @property
    def device(self):
        return self.gcast.device

    @property
    def is_connected(self):
        try :
            if self.gcast.socket_client is not None or self.gcast.status is not None or self.online==True or self.is_recovering==True :
                return True
        except Exception :
            return False

    @property
    def is_castgroup(self):
        if self.gcast.device.cast_type != 'group' :
            return False
        return True

    @property
    def support_video(self):
        if self.gcast.device.cast_type == 'cast' :
            return True
        return False

    def getCurrentVolume(self):
        return int(self.gcast.status.volume_level*100)

    def startNowPlaying(self):
        if self.now_playing == False and self.online == True :
            logging.debug("JEEDOMCHROMECAST------ Starting monitoring of " + self.uuid)
            self.now_playing = True
            self.sendNowPlaying(force=True)

    def stopNowPlaying(self):
        logging.debug("JEEDOMCHROMECAST------ Stopping monitoring of " + self.uuid)
        self.now_playing = False

    def new_cast_status(self, new_status):
        #logging.debug("JEEDOMCHROMECAST------ Status " + str(new_status))
        self._manage_previous_status(new_status)
        if not self.disable_notif :
            self._internal_refresh_status(False)
            self.sendNowPlaying(force=True)

    def new_media_status(self, new_mediastatus):
        #logging.debug("JEEDOMCHROMECAST------ New media status " + str(new_mediastatus))
        if self.now_playing==True and new_mediastatus.player_state!="BUFFERING" and not self.disable_notif :
            self._internal_send_now_playing()

    def new_connection_status(self, new_status):
        # CONNECTING / CONNECTED / DISCONNECTED / FAILED / LOST
        logging.debug("JEEDOMCHROMECAST------ Connexion change event " + str(new_status.status))
        self.online = False
        if new_status.status == "DISCONNECTED" and self.being_shutdown==False:
            self.disconnect()
            logging.info("JEEDOMCHROMECAST------ Chromecast has beend disconnected : " + self.friendly_name)
        if new_status.status == "LOST" :
            self.is_recovering = True
            self._internal_refresh_status(True)
        if new_status.status == "CONNECTING" or new_status.status == "FAILED" :
            self.is_recovering = True
        if new_status.status == "CONNECTED" :    # is reborn...
            self.online = True
            self.is_recovering = False
            if self.uuid not in globals.GCAST_DEVICES :
                globals.GCAST_DEVICES[self.uuid] = self
            self._internal_refresh_status(True)
            if self.now_playing == True :
                self._internal_trigger_now_playing_update()

    def _manage_previous_status(self, new_status):
        logging.debug("JEEDOMCHROMECAST------ Manage previous status " + str(new_status))
        if self.sessionid_storenext and new_status.session_id is not None :
            self.sessionid_current = new_status.session_id
            self.sessionid_storenext = False
        appid = new_status.app_id
        if appid is not None and new_status.status_text not in ['Casting: TTS', 'Default Media Receiver'] and self.sessionid_current != new_status.session_id :
            self.previous_playercmd = {}
            logging.debug("JEEDOMCHROMECAST------ Manage previous status : Removing previous playercmd!")

    def savePreviousPlayerCmd(self, params):
        #logging.debug("JEEDOMCHROMECAST------ Manage previous player cmd " + str(params))
        self.previous_playercmd['params'] = params
        self.previous_playercmd['time'] = int(time.time())
        self.previous_playercmd['appid'] = self.getAppId(params['app'] if 'app' in params else None)
        self.previous_playercmd['appname'] = params['app'] if 'app' in params else None
        self.sessionid_storenext = True
        self.sessionid_current = ''

    def resetPreviousPlayerCmd(self):
        self.previous_playercmd = {}
        self.sessionid_storenext = False
        self.sessionid_current = ''

    def getPreviousPlayerCmd(self):
        logging.debug("JEEDOMCHROMECAST------ getPreviousPlayerCmd " + str(self.previous_playercmd))
        ret = None
        beforeTTSappid = (self.previous_playercmd['current_appid'] if 'current_appid' in self.previous_playercmd else None)
        if 'params' in self.previous_playercmd :
            if self.previous_playercmd['appid']==beforeTTSappid :
                self.previous_playercmd['params']
                if 'current_time' in self.previous_playercmd :
                    self.previous_playercmd['params']['offset'] = self.previous_playercmd['current_time']
                ret = self.previous_playercmd['params']
        elif beforeTTSappid is not None :
            ret = {'cmd': 'start_app', 'appid' : beforeTTSappid}
        return ret

    def prepareTTSplay(self):
        retval = 0
        try :
            self.previous_playercmd['current_appid'] = self.gcast.status.app_id
            self.previous_playercmd['current_sessionid'] = self.gcast.status.session_id
            retval = self.gcast.media_controller.status.adjusted_current_time
        except Exception :
            pass
        self.previous_playercmd['current_time'] = retval
        return retval

    def getAppId(self, appname):
        retval = None
        if appname=='plex' :
            retval = '9AC194DC'
        elif appname=='media' :
            retval = 'CC1AD845';
        elif appname=='backdrop' :
            retval = 'E8C28D3C';
        elif appname=='web' :
            retval = '84912283';
        return retval

    def sendDeviceStatus(self, _force=True):
        try :
            self.gcast.media_controller.update_status()
            time.sleep(0.2)
        except Exception :
            pass
        self._internal_refresh_status(_force)

    def sendDeviceStatusIfNew(self):
        self.sendDeviceStatus(False)

    def disconnect(self):
        if self.scan_mode==False :
            self.is_recovering = False
            self.being_shutdown = True
            self._internal_refresh_status(True)
            if self.now_playing == True :
                self._internal_send_now_playing()
                self.now_playing = False
            if self.uuid in globals.GCAST_DEVICES :
                del globals.GCAST_DEVICES[self.uuid]
            logging.debug("JEEDOMCHROMECAST------ Chromecast disconnected : " + self.friendly_name)
        self.gcast.disconnect()
        self.free_memory()

    def free_memory(self):
        try :
            self.gcast.socket_client.socket.shutdown(socket.SHUT_RDWR)
            self.gcast.socket_client.socket.close()
        except Exception :
            pass
        del self.gcast
        del self

    def loadPlayer(self, playername, params=None) :
        if self.gcast.socket_client :
            forceReload = False
            if params and 'forcereload' in params :
                forceReload = True
            if not self.customplayer or self.customplayername != playername or forceReload==True :
                try:
                    if playername == 'web' :
                        player = dashcast.DashCastController()
                        self.gcast.register_handler(player)
                    elif playername == 'youtube' :
                        player = youtube.YouTubeController()
                        self.gcast.register_handler(player)
                        time.sleep(5)
                    elif playername == 'spotify' :
                        player = spotify.SpotifyController()
                        self.gcast.register_handler(player)
                        time.sleep(2)
                    elif playername == 'plex' :
                        player = plex.PlexController()
                        self.gcast.register_handler(player)
                        time.sleep(2)
                    else :
                        player = self.gcast.media_controller
                    logging.debug("JEEDOMCHROMECAST------ Initiating player " + str(player.namespace))
                    self.customplayer = player
                    self.customplayername = playername
                    if params and 'waitbeforequit' in params :
                        time.sleep(params['waitbeforequit'])
                    if params and 'quitapp' in params :
                        self.gcast.quit_app()
                    if params and 'wait' in params :
                        time.sleep(params['wait'])
                except Exception as e:
                    logging.error("JEEDOMCHROMECAST------ Error while initiating player " +playername+ " on low level commands : %s" % str(e))
                    logging.debug(traceback.format_exc())
                    player = None
                    pass
            #else:
            #    time.sleep(0.2)
            if not self.disable_notif :
                self.sendNowPlaying(force=True)
            return self.customplayer
        return None

    def resetPlayer(self) :
        self.resetPreviousPlayerCmd()
        if self.customplayer is not None and self.customplayername != 'media' :
            if self.gcast.socket_client and self.customplayer.namespace in self.gcast.socket_client._handlers :
                del self.gcast.socket_client._handlers[self.customplayer.namespace]
            self.customplayer = None
            self.sendNowPlaying(force=True)

    def _internal_refresh_status(self,_force = False):
        uuid = self.uuid
        status = self._internal_get_status()
        if _force or self._internal_status_different(status) :
            logging.debug("Detected changes in status of " +self.device.friendly_name)
            globals.KNOWN_DEVICES[uuid]['status'] = status
            self.previous_status = status
            globals.KNOWN_DEVICES[uuid]['online'] = self.online
            if self.online == False :
                globals.KNOWN_DEVICES[uuid]['lastOfflineSent'] = int(time.time())
            globals.JEEDOM_COM.add_changes('devices::'+uuid,globals.KNOWN_DEVICES[uuid])
            globals.KNOWN_DEVICES[uuid]['lastSent'] = int(time.time())


    def _internal_get_status(self):
        if self.gcast.status is not None and self.online == True:
            uuid = self.uuid
            playStatus = self.gcast.media_controller.status
            status = {
                "uuid" : uuid, "uri" : self.gcast.uri, "friendly_name" : self.gcast.device.friendly_name,
                "friendly_name" : self.gcast.device.friendly_name,
                "is_active_input" : True if self.gcast.status.is_active_input else False,
                "is_stand_by" :  True if self.gcast.status.is_stand_by else False,
                "volume_level" : int(self.gcast.status.volume_level*100),
                "volume_muted" : self.gcast.status.volume_muted,
                "app_id" : self.gcast.status.app_id,
                "display_name" : self.gcast.status.display_name if self.gcast.status.display_name is not None else globals.DEFAULT_NODISPLAY,
                "status_text" : self.gcast.status.status_text if self.gcast.status.status_text!="" else globals.DEFAULT_NOSTATUS,
                "is_busy" : not self.gcast.is_idle,
                "title" : "" if playStatus is None else playStatus.title,
                "artist" : "" if playStatus is None else playStatus.artist,
                'series_title': "" if playStatus is None else playStatus.series_title,
                "stream_type" : "" if playStatus is None else playStatus.stream_type,
                "player_state" : "" if playStatus is None else playStatus.player_state,
            }
            return status
        else :
            return {
                "uuid" : self.uuid,
                "is_stand_by" :  False, "is_active_input" : False,
                "display_name" : globals.DEFAULT_NODISPLAY, "status_text" : globals.DEFAULT_NOSTATUS,
                "app_id" : "", "is_busy" : False,
                "title" : "", "artist" : "", 'series_title': "", "stream_type" : "", "player_state" : "",
            }


    def _internal_status_different(self, new_status):
        prev_status = self.previous_status
        if len(prev_status) != len(new_status) or len(prev_status)==2 or 'volume_level' not in new_status :
            return True
        if prev_status['status_text'] != new_status['status_text'] :
            return True
        if prev_status['volume_level'] != new_status['volume_level'] :
            return True
        if prev_status['is_busy'] != new_status['is_busy'] :
            return True
        if prev_status['volume_muted'] != new_status['volume_muted'] :
            return True
        if prev_status['is_stand_by'] != new_status['is_stand_by'] :
            return True
        if prev_status['app_id'] != new_status['app_id'] :
            return True
        if prev_status['player_state'] != new_status['player_state'] :
            return True
        return False

    def getDefinition(self):
        status = {
            "friendly_name" : self.gcast.device.friendly_name,
            "model_name" : self.gcast.device.model_name,
            "manufacturer" : self.gcast.device.manufacturer,
            "cast_type" : self.gcast.device.cast_type,
            "uri" : self.gcast.uri
        }
        return status

    def getStatus(self):
        return self._internal_get_status()

    def _internal_trigger_now_playing_update(self) :
        try :
            self.gcast.media_controller.update_status()
        except Exception :
            pass

    def sendNowPlaying(self, force=False):
        if force==True :
            self._internal_send_now_playing()
        elif self.now_playing==True:
            logging.debug("JEEDOMCHROMECAST------ NOW PLAYING " + str(int(time.time())-self.nowplaying_lastupdated))
            if (int(time.time())-self.nowplaying_lastupdated)>=globals.NOWPLAYING_FREQUENCY :
                self._internal_trigger_now_playing_update()

    def sendNowPlaying_heartbeat(self):
        if self.now_playing==True:
            if (int(datetime.utcnow().timestamp())-self.nowplaying_lastupdated)>=globals.NOWPLAYING_FREQUENCY :
                logging.debug("JEEDOMCHROMECAST------ NOW PLAYING heartbeat " + str(int(datetime.utcnow().timestamp())-self.nowplaying_lastupdated))
                self._internal_trigger_now_playing_update()

    def _internal_send_now_playing(self):
        uuid = self.uuid
        if self.gcast.status and self.online == True :
            playStatus = self.gcast.media_controller.status
            if self.gcast.media_controller.status.last_updated:
                self.nowplaying_lastupdated = int(self.gcast.media_controller.status.last_updated.timestamp())
            else:
                self.nowplaying_lastupdated = int(time.time())
            if len(playStatus.images) > 0 :
                img = str(playStatus.images[0].url)
            else:
                img = None
            data = {
                "uuid" : uuid,
                "online" : True,
                "friendly_name" : self.gcast.device.friendly_name,
                "is_active_input" : True if self.gcast.status.is_active_input else False,
                "is_stand_by" :  True if self.gcast.status.is_stand_by else False,
                "volume_level" :  int(self.gcast.status.volume_level*100),     #"{0:.2f}".format(cast.status.volume_level),
                "volume_muted" : self.gcast.status.volume_muted,
                "app_id" : self.gcast.status.app_id,
                "display_name" : self.gcast.status.display_name if self.gcast.status.display_name is not None else globals.DEFAULT_NODISPLAY,
                "status_text" : self.gcast.status.status_text if self.gcast.status.status_text!="" else globals.DEFAULT_NOSTATUS,
                "is_busy" : not self.gcast.is_idle,
                "title" : playStatus.title,
                "album_artist" : playStatus.album_artist,
                "metadata_type" : playStatus.metadata_type,
                "album_name" : playStatus.album_name,
                #"current_time" : '{0:.0f}'.format(playStatus.current_time),
                "current_time" : '{0:.0f}'.format(playStatus.adjusted_current_time),
                "artist" : playStatus.artist,
                'series_title': playStatus.series_title,
                'season': playStatus.season,
                'episode': playStatus.episode,
                "image" : img,
                "stream_type" : playStatus.stream_type,
                "track" : playStatus.track,
                "player_state" : playStatus.player_state,
                "supported_media_commands" : playStatus.supported_media_commands,
                "supports_pause" : playStatus.supports_pause,
                "duration": playStatus.duration, #'{0:.0f}'.format(playStatus.duration),
                "content_type": playStatus.content_type,
                "idle_reason": playStatus.idle_reason
            }
            globals.JEEDOM_COM.send_change_immediate({'uuid' :  uuid, 'nowplaying':data});
        else :
            data = {
                "uuid" : uuid,
                "online" : False, "friendly_name" : "",
                "is_active_input" : False, "is_stand_by" :  False,
                "app_id" : "", "display_name" : globals.DEFAULT_NODISPLAY, "status_text" : globals.DEFAULT_NOSTATUS,
                "is_busy" : False, "title" : "",
                "album_artist" : "","metadata_type" : "",
                "album_name" : "", "current_time" : 0,
                "artist" : "", "image" : None,
                "series_title": "", "season": "", "episode": "",
                "stream_type" : "", "track" : "",
                "player_state" : "", "supported_media_commands" : 0,
                "supports_pause" : "", "duration": 0,
                'content_type': "", "idle_reason": ""
            }
            globals.JEEDOM_COM.send_change_immediate({'uuid' :  uuid, 'nowplaying':data});


# -------------------------------
# main method to manage actions
# -------------------------------
def action_handler(message):
    rootcmd = message['cmd']
    uuid = message['device']['uuid']
    srcuuid = uuid

    if uuid in globals.KNOWN_DEVICES and uuid in globals.GCAST_DEVICES and rootcmd == "action":
        hascallback=False
        callback=''
        if 'callback' in message['device'] :
            hascallback=message['device']['callback'] if True is not None else False
            callback=message['device']['callback'] if message['device']['callback'] is not None else ''

        source=''
        if 'source' in message['device'] :
            source=message['device']['source']

        commandlist = message['command']
        if not isinstance(commandlist, list) :
            commandlist = [commandlist]

        for command in commandlist :
            uuid = srcuuid
            if 'uuid' in command :
                if 'nothread' in command and command['uuid'] in globals.GCAST_DEVICES:
                    uuid = command['uuid']
                    logging.debug("ACTION------Changing uuid to run in sequence in this tread : " + uuid)
                else :
                    newUuid = command['uuid']
                    del command['uuid']
                    newMessage = {
                        'cmd' : 'action',
                        'delegated' : True,
                        'device' : {'uuid' : newUuid, 'source' : message['device']['source'] },
                        'command' : command
                    }
                    logging.debug("ACTION------DELEGATED command to other uuid : " + newUuid)
                    thread.start_new_thread( action_handler, (newMessage,))
                    continue

            app = 'media'
            cmd = 'NONE'
            if 'cmd' in command :
                cmd = command['cmd']
            app = 'media'
            if 'app' in command :
                app = command['app']
            appid = ''
            if 'appid' in command :
                appid = command['appid']
            value = None
            if 'value' in command :
                value = command['value']
            sleep=0
            if 'sleep' in command :
                sleep = float(command['sleep'])
            vol = None
            if 'vol' in command :
                try:
                    vol = int(command['vol'])
                    if not (0 < vol <= 100) or command['vol'] == '':
                        vol = None
                except:
                    vol = None

            # specific parameters for apps
            quit_app_before=True
            if 'quit_app_before' in command :
                quit_app_before = True if command['quit_app_before'] else False
            quit=False
            if 'quit' in command :
                quit = True if command['quit'] else False
            force_register=False
            if 'force_register' in command :
                force_register = True if command['force_register'] else False
            wait=2
            if 'wait' in command :
                wait = int(command['wait']) if command['wait'].isnumeric() else 2

            if app == 'tts' :
                cmd = 'tts'
                app = 'media'

            needSendStatus = True
            fallbackMode = True
            logging.debug("ACTION------ " + rootcmd + " - " + cmd + ' - ' + uuid + ' - ' + str(value)+ ' - ' + app)

            jcast = globals.GCAST_DEVICES[uuid]
            gcast = jcast.gcast
            try:
                if app == 'media' :    # app=media|cmd=play_media|value=http://bit.ly/2JzYtfX,video/mp4,Mon film
                    possibleCmd = ['play_media']
                    if cmd in possibleCmd :
                        if 'offset' in command and float(command['offset'])>0 and 'current_time' not in value :
                            value = value + ',current_time:'+ str(command['offset'])

                        fallbackMode=False
                        player = jcast.loadPlayer('media', { 'quitapp' : quit_app_before})
                        eval( 'player.' + cmd + '('+ gcast_prepareAppParam(value) +')' )
                        jcast.savePreviousPlayerCmd(command)

                elif app == 'web':    # app=web|cmd=load_url|value=https://news.google.com,True,5
                    force_register=True
                    possibleCmd = ['load_url']
                    if cmd in possibleCmd :
                        fallbackMode=False
                        player = jcast.loadPlayer(app, { 'quitapp' : quit_app_before})
                        eval( 'player.' + cmd + '('+ gcast_prepareAppParam(value) +')' )
                        jcast.savePreviousPlayerCmd(command)

                elif app == 'youtube':  # app=youtube|cmd=play_video|value=fra4QBLF3GU
                    #possibleCmd = ['play_video', 'start_new_session', 'add_to_queue', 'update_screen_id', 'clear_playlist', 'play', 'stop', 'pause']
                    possibleCmd = ['play_video', 'add_to_queue', 'play_next', 'remove_video']
                    if cmd in possibleCmd :
                        fallbackMode=False
                        if jcast.support_video == True :
                            player = jcast.loadPlayer(app, { 'quitapp' : quit_app_before, 'wait': wait})
                            eval( 'player.' + cmd + '('+ gcast_prepareAppParam(value) +')' )
                            jcast.savePreviousPlayerCmd(command)
                        else :
                            logging.error("ACTION------ YouTube not availble on Google Cast Audio")

                elif app == 'spotify':  # app=spotify|cmd=launch_app|user=XXXXXX|pass=YYYY|value
                    possibleCmd = ['play_media']
                    if cmd == 'play_media' :
                        fallbackMode=False

                        if 'user' in command and 'pass' in command :
                            username = command['user']
                            password = command['pass']
                        token = None
                        if 'token' in command :
                            token = command['token']

                        if username is not None and password is not None and token is None :
                            data = stoken.start_session(username, password)
                            token = data[0]

                        keepGoing = True
                        if value is None :
                            logging.error("ACTION------ Missing content id for spotify")
                            keepGoing = False
                        if token is None and (username is None or password is None) :
                            logging.error("ACTION------ Missing token or user/pass paramaters for spotify")
                            keepGoing = False

                        if keepGoing == True :
                            player = jcast.loadPlayer(app, { 'quitapp' : quit_app_before, 'wait': wait})
                            player.launch_app(token)
                            spotifyClient = spotipy.Spotify(auth=token)

                            devices_available = spotifyClient.devices()
                            device_id = None
                            for device in devices_available['devices']:
                                if device['name'] == jcast.device.friendly_name :
                                    device_id = device['id']
                                    break
                            if device_id is not None :
                                out = spotifyClient.start_playback(device_id=device_id, uris=[value])
                                jcast.savePreviousPlayerCmd(command)

                elif app == 'backdrop':  # also called backdrop
                    if jcast.support_video == True :
                        fallbackMode=False
                        gcast.start_app('E8C28D3C')
                        jcast.savePreviousPlayerCmd(command)
                    else :
                        logging.error("ACTION------ Backdrop not availble on Google Cast Audio")

                elif app == 'plex':            # app=plex|cmd=pause
                    quit_app_before=False
                    possibleCmd = ['play_media','play', 'stop', 'pause', 'next', 'previous']
                    if cmd in possibleCmd :
                        fallbackMode=False

                        player = jcast.loadPlayer(app, { 'quitapp' : quit_app_before, 'wait': wait})
                        #player.namespace = 'urn:x-cast:com.google.cast.sse'

                        if cmd == 'play_media' :
                            serverurl = None
                            if 'server' in command :
                                serverurl = command['server']
                            username = None
                            password = None
                            if 'user' in command and 'pass' in command :
                                username = command['user']
                                password = command['pass']
                            token = None
                            if 'token' in command :
                                token = command['token']
                            type = 'audio'
                            if 'type' in command :
                                type = command['type']
                            if jcast.support_video==False and type=='video' :
                                type = 'audio'
                            offset = 0
                            if 'offset' in command :
                                offset = int(command['offset'])
                            shuffle = 0
                            if 'shuffle' in command :
                                shuffle = int(command['shuffle'])
                            repeat = 0
                            if 'repeat' in command :
                                repeat = int(command['repeat'])

                            keepGoing = True
                            if serverurl is None :
                                logging.error("ACTION------ Missing server paramater for plex")
                                keepGoing = False
                            if token is None and (username is None or password is None) :
                                logging.error("ACTION------ Missing token or user/pass paramaters for plex")
                                keepGoing = False

                            if keepGoing==True :
                                is_resume = False
                                if 'resume_plexitem' in command :
                                    is_resume = True

                                if not is_resume :
                                    if username is not None and password is not None and token is None :
                                        account = MyPlexAccount(username, password)
                                        for res in account.resources() :
                                            logging.debug("PLEX------ Resource available : " +str(res.name))
                                        plexServer = account.resource(serverurl).connect()
                                        logging.debug("PLEX------ Token for reuse : " +str(account._token))
                                    else :
                                        plexServer = PlexServer(serverurl, token)
                                    plexmedia = plexServer.search(value, limit=1)
                                    if len(plexmedia)>0 :
                                        command['resume_plexitem'] = plexmedia[0]
                                        command['resume_plexserver'] = plexServer
                                        player.play_media(plexmedia[0], plexServer, {'offset':offset, 'type':type, 'shuffle':shuffle, 'repeat':repeat} )
                                        jcast.savePreviousPlayerCmd(command)
                                    else :
                                        logging.debug("PLEX------No media found for query " + value)

                                else :
                                    logging.debug("PLEX------Restoring from previous call")
                                    player.play_media(command['resume_plexitem'], command['resume_plexserver'], {'offset':offset, 'type':type, 'shuffle':shuffle, 'repeat':repeat} )
                                    jcast.savePreviousPlayerCmd(command)

                        else :
                            eval( 'player.' + cmd + '()' )

                if fallbackMode==False :
                    logging.debug("ACTION------Playing action " + cmd + ' for application ' + app)
            except Exception as e:
                logging.error("ACTION------Error while playing action " +cmd+ " on app " +app+" : %s" % str(e))
                logging.debug(traceback.format_exc())

            # low level google cast actions
            if fallbackMode==True :
                try:
                    if cmd == 'refresh':
                        logging.debug("ACTION------Refresh action")
                        time.sleep(1)
                        fallbackMode=False
                    elif cmd == 'reboot':
                        logging.debug("ACTION------Reboot action")
                        gcast.reboot()
                        time.sleep(5)
                        fallbackMode=False
                    elif cmd == 'volume_up':
                        logging.debug("ACTION------Volumme up action")
                        gcast.volume_up(value if value is not None else 0.1)
                        fallbackMode=False
                    elif cmd == 'volume_down':
                        logging.debug("ACTION------Volume down action")
                        gcast.volume_down(value if value is not None else 0.1)
                        fallbackMode=False
                    elif cmd == 'volume_set':
                        logging.debug("ACTION------Volume set action")
                        gcast.set_volume(int(value)/100)
                        fallbackMode=False
                    elif cmd == 'start_app':
                        logging.debug("ACTION------Start app action")
                        appToLaunch = '' if value is None else value
                        if appid != '':
                            appToLaunch=appid
                        gcast.start_app(appToLaunch)
                        fallbackMode=False
                    elif cmd == 'quit_app':
                        logging.debug("ACTION------Stop action")
                        gcast.quit_app()
                        jcast.resetPlayer()
                        fallbackMode=False
                    elif cmd == 'mute_on':
                        logging.debug("ACTION------Mute on action")
                        gcast.set_volume_muted(True)
                        fallbackMode=False
                    elif cmd == 'mute_off':
                        logging.debug("ACTION------Mute off action")
                        gcast.set_volume_muted(False)
                        fallbackMode=False
                    elif cmd == 'tts':
                        logging.debug("ACTION------TTS action")
                        lang = globals.tts_language
                        if 'lang' in command :
                            lang = command['lang']
                        engine = globals.tts_engine
                        if 'engine' in command :
                            engine = command['engine']
                        speed = globals.tts_speed
                        if 'speed' in command :
                            speed = float(command['speed'])
                        forcetts = False
                        if 'forcetts' in command :
                            forcetts = True
                        silence = 300
                        if 'silence' in command :
                            silence = int(command['silence'])
                        elif jcast.is_castgroup==True :
                            silence = 1000
                        generateonly = False
                        if 'generateonly' in command :
                            generateonly = True
                        forcevol = False
                        if 'forcevol' in command :
                            forcevol = True
                        resume = False
                        if 'resume' in command :
                            resume = True

                        curvol = jcast.getCurrentVolume()
                        if curvol == vol and not forcevol :
                            vol = None
                        need_duration=False
                        if vol is not None or quit==True or resume==True :
                            need_duration=True

                        if generateonly == False :
                            url,duration,mp3filename=get_tts_data(value, lang, engine, speed, forcetts, need_duration, silence)
                            if vol is not None :
                                gcast.set_volume(vol/100)
                                time.sleep(0.1)
                            thumb=globals.JEEDOM_WEB + '/plugins/googlecast/desktop/images/tts.png'
                            jcast.disable_notif = True
                            if resume:
                                jcast.prepareTTSplay()
                            player = jcast.loadPlayer(app, { 'quitapp' : False, 'wait': wait})
                            player.play_media(url, 'audio/mp3', 'TTS', thumb=thumb, add_delay=0.1, stream_type="LIVE");
                            player.block_until_active(timeout=2);
                            jcast.disable_notif = False
                            if vol is not None :
                                time.sleep(duration+(silence/1000)+1)
                                if sleep>0 :
                                    time.sleep(sleep)
                                    sleep=0
                                gcast.set_volume(curvol/100)
                                vol = None
                            if quit:
                                if vol is None :
                                    time.sleep(duration+(silence/1000)+1)
                                gcast.quit_app()
                            if resume:
                                prevcommand = jcast.getPreviousPlayerCmd()
                                if prevcommand is not None :
                                    newMessage = {
                                        'cmd' : 'action',
                                        'delegated' : True,
                                        'resume' : True,
                                        'device' : {'uuid' : uuid, 'source' : message['device']['source'] },
                                        'command' : prevcommand
                                    }
                                    logging.debug("TTS------DELEGATED RESUME AFTER TTS for uuid : " + uuid)
                                    time.sleep(0.3)
                                    jcast.resetPreviousPlayerCmd()
                                    thread.start_new_thread( action_handler, (newMessage,))
                                else :
                                    logging.debug("TTS------Resume is not possible!")
                        else :
                            logging.error("TTS------Only generating TTS file without playing")
                            get_tts_data(value, lang, engine, speed, forcetts, False, silence)
                            needSendStatus = False

                        fallbackMode=False
                except Exception as e:
                    logging.error("ACTION------Error while playing action " +cmd+ " on low level commands : %s" % str(e))
                    logging.debug(traceback.format_exc())

            # media/application controler level Google Cast actions
            if fallbackMode==True :
                try:
                    player=gcast.media_controller
                    if cmd == 'play':
                        logging.debug("ACTION------Play action")
                        player.play()
                        fallbackMode=False
                    elif cmd == 'stop':
                        logging.debug("ACTION------Stop action")
                        player.stop()
                        fallbackMode=False
                    elif cmd == 'rewind':
                        logging.debug("ACTION------Rewind action")
                        player.rewind()
                        fallbackMode=False
                    elif cmd == 'skip':
                        logging.debug("ACTION------Skip action")
                        player.skip()
                        fallbackMode=False
                    elif cmd == 'seek':
                        logging.debug("ACTION------Seek action")
                        player.seek(0 if value is None else value)
                        fallbackMode=False
                    elif cmd == 'pause':
                        logging.debug("ACTION------Stop action")
                        player.pause()
                        fallbackMode=False
                    elif cmd == 'sleep':
                        logging.debug("ACTION------Sleep")
                        time.sleep(float(value))
                        fallbackMode=False
                except Exception as e:
                    logging.error("ACTION------Error while playing action " +cmd+ " on default media controler : %s" % str(e))
                    logging.debug(traceback.format_exc())

            if vol is not None :
                logging.debug("ACTION------SET VOLUME OPTION")
                time.sleep(0.1)
                gcast.set_volume(vol/100)

            if fallbackMode==True :
                logging.debug("ACTION------Action " + cmd + " not implemented !")

            if sleep>0 :
                time.sleep(sleep)

            if needSendStatus :
                time.sleep(0.1)
                globals.GCAST_DEVICES[uuid].sendDeviceStatus()

        if hascallback :
            callbackret=manage_callback(uuid, callback)
            callbackmsg={'callback' : 1,'source' : source, 'uuid' : uuid, 'result': callbackret}
            globals.JEEDOM_COM.send_change_immediate(callbackmsg);

    else :
        logging.error("ACTION------ Device not connected !")
        return False

    return True

def manage_callback(uuid, callback_type):
    # todo things for callback before returning value
    return True

def get_tts_data(text, language, engine, speed, forcetts, calcduration, silence=300):
    srclanguage = language
    if not globals.tts_gapi_haskey and (engine=='gttsapi' or engine=='gttsapidev') :
        logging.error("CMD-TTS------No key provided, fallback to picotts engine")
        engine = 'picotts'
        speed = 1

    if globals.tts_cacheenabled==False :
        try :
            if os.path.exists(globals.tts_cachefoldertmp) :
                shutil.rmtree(globals.tts_cachefoldertmp)
        except :
            pass
    cachepath=globals.tts_cachefolderweb
    # manage cache in ram memory
    symlinkpath=globals.tts_cachefoldertmp
    ttstext = text
    try:
        os.stat(symlinkpath)
    except:
        os.mkdir(symlinkpath)
    try:
        os.stat(cachepath)
    except:
        os.symlink(symlinkpath, cachepath)
    try:
        rawfilename = text+engine+language+str(silence)
        file = hashlib.md5(rawfilename.encode('utf-8')).hexdigest()
        filenamemp3=os.path.join(cachepath,file+'.mp3')
        logging.debug("CMD-TTS------TTS Filename hexdigest : " + file + "  ("+rawfilename+")")
        if not os.path.isfile(filenamemp3) or forcetts==True :
            logging.debug("CMD-TTS------Generating file")

            if engine == 'gtts':
                speed = float(speed)
                language=language.split('-')[0]
                try:
                    tts = gTTS(text=ttstext, lang=language)
                    tts.save(filenamemp3)
                    if speed!=1:
                        try:
                            os.system('sox '+filenamemp3+' '+filenamemp3+ 'tmp.mp3 tempo ' +str(speed))
                            os.remove(filenamemp3)
                            os.rename(filenamemp3+'tmp.mp3', filenamemp3);
                        except OSError:
                            pass
                    speech = AudioSegment.from_mp3(filenamemp3)
                    if silence > 0 :
                        start_silence = AudioSegment.silent(duration=silence)
                        speech = start_silence + speech
                    speech.export(filenamemp3, format="mp3", bitrate="128k", tags={'albumartist': 'Jeedom', 'title': 'TTS', 'artist':'Jeedom'}, parameters=["-ar", "44100","-vol", "200"])
                    duration_seconds = speech.duration_seconds
                except Exception as e:
                    logging.error("CMD-TTS------Google Translate API : Cannot connect to API - failover to picotts  (%s)" % str(e))
                    logging.debug(traceback.format_exc())
                    engine = 'picotts'
                    filenamemp3 = filenamemp3.replace(".mp3", "_failover.mp3")
                    file = file + '_failover'
                    language = srclanguage
                    speed = 1.2

            elif engine == 'gttsapi':
                speed = float(speed) - 0.7
                ttsurl = globals.tts_gapi_url + 'v1/synthesize?enc=mpeg&client=chromium&key='+globals.tts_gapi_key+'&text='+ttstext+'&lang='+language+'&speed='+"{0:.2f}".format(speed)+'&pitch=0.5'
                r = requests.get(ttsurl)
                if r.status_code == requests.codes.ok :
                    with open(filenamemp3 , 'wb') as f:
                        f.write(r.content)
                    speech = AudioSegment.from_mp3(filenamemp3)
                    if silence > 0 :
                        start_silence = AudioSegment.silent(duration=silence)
                        speech = start_silence + speech
                    speech.export(filenamemp3, format="mp3", bitrate="128k", tags={'albumartist': 'Jeedom', 'title': 'TTS', 'artist':'Jeedom'}, parameters=["-ar", "44100","-vol", "200"])
                    duration_seconds = speech.duration_seconds
                else :
                    logging.debug("CMD-TTS------Google Speech API : Cannot connect to API - failover to picotts")
                    engine = 'picotts'
                    filenamemp3 = filenamemp3.replace(".mp3", "_failover.mp3")
                    file = file + '_failover'
                    language = srclanguage
                    speed = 1.2

            elif engine == 'gttsapidev':
                speed = float(speed) - 0.7
                ttsurl = globals.tts_gapi_url + 'v2/synthesize?enc=mpeg&client=chromium&key='+globals.tts_gapi_key+'&text='+ttstext+'&lang='+language+'&speed='+"{0:.2f}".format(speed)+'&pitch=0.5'
                r = requests.get(ttsurl)
                if r.status_code == requests.codes.ok :
                    with open(filenamemp3 , 'wb') as f:
                        f.write(r.content)
                    speech = AudioSegment.from_mp3(filenamemp3)
                    if silence > 0 :
                        start_silence = AudioSegment.silent(duration=silence)
                        speech = start_silence + speech
                    speech.export(filenamemp3, format="mp3", bitrate="128k", tags={'albumartist': 'Jeedom', 'title': 'TTS', 'artist':'Jeedom'}, parameters=["-ar", "44100","-vol", "200"])
                    duration_seconds = speech.duration_seconds
                else :
                    logging.debug("CMD-TTS------Google Speech API : Cannot connect to API - failover to picotts")
                    engine = 'picotts'
                    filenamemp3 = filenamemp3.replace(".mp3", "_failover.mp3")
                    file = file + '_failover'
                    language = srclanguage
                    speed = 1.2

            if engine == 'picotts':
                speed = float(speed) - 0.2
                filename=os.path.join(cachepath,file+'.wav')
                # fix accent issue for picotts
                ttstext = ttstext.encode('utf-8').decode('ascii','ignore')
                os.system('pico2wave -l '+language+' -w '+filename+ ' "' +ttstext+ '"')
                speech = AudioSegment.from_wav(filename)
                if silence > 0 :
                    start_silence = AudioSegment.silent(duration=silence)
                    speech = start_silence + speech
                speech.export(filenamemp3, format="mp3", bitrate="128k", tags={'albumartist': 'Jeedom', 'title': 'TTS', 'artist':'Jeedom'}, parameters=["-ar", "44100","-vol", "200"])
                duration_seconds = speech.duration_seconds
                if speed!=1:
                    try:
                        os.system('sox '+filenamemp3+' '+filenamemp3+ 'tmp.mp3 tempo ' +str(speed))
                        os.remove(filenamemp3)
                        os.rename(filenamemp3+'tmp.mp3', filenamemp3);
                    except OSError:
                        pass
                try :
                    os.remove(filename)
                except OSError:
                    pass

            logging.debug("CMD-TTS------Sentence: '" +ttstext+ "' ("+engine+","+language+",speed:"+"{0:.2f}".format(speed)+")")

        else:
            logging.debug("CMD-TTS------Using from cache")
            if calcduration == True:
                speech = AudioSegment.from_mp3(filenamemp3)
                duration_seconds = speech.duration_seconds
            else:
                duration_seconds=0
            logging.debug("CMD-TTS------Sentence: '" +ttstext+ "' ("+engine+","+language+")")

        try :   # touch file so cleaning can be done later based on date
            os.utime(filenamemp3, None)
        except :
            pass
        urltoplay=globals.JEEDOM_WEB+'/plugins/googlecast/tmp/'+file+'.mp3'
    except Exception as e:
        logging.error("CMD-TTS------Exception while generating tts file : %s" % str(e))
        logging.debug(traceback.format_exc())
    return urltoplay, duration_seconds, filenamemp3

def logByTTS(text_id):
    lang = globals.tts_language
    engine = globals.tts_engine
    speed = globals.tts_speed
    if text_id == 'CMD_ERROR' :
        text = "La commande n'a pas pu être lancée !"
    else :
        text = "Un erreur s'est produite !"
    url,duration,mp3filename=get_tts_data(text, language, engine, speed, False, False, 300)
    thumb=globals.JEEDOM_WEB + '/plugins/googlecast/desktop/images/tts.png'
    player = jcast.loadPlayer('media', { 'quitapp' : False, 'wait': 0})
    player.play_media(url, 'audio/mp3', 'TTS', thumb=thumb, add_delay=0.1, stream_type="LIVE");
    player.block_until_active(timeout=2);


def gcast_prepareAppParam(params):
    if params is None or params == '':
        return ''
    ret = ''
    s = [k for k in re.split("(,|\w*?:'.*?'|'.*?')", params) if k.strip() and k!=',']
    for p in s :
        p = p.strip()
        s2 = [k for k in re.split("(:|'.*?'|http:.*)", p) if k.strip() and k!=':']
        prefix = ''
        if len(s2)==2 :
            prefix = s2[0].strip() + '='
            p = s2[1].strip()
        if p.isnumeric() :
            ret = ret + ',' + prefix + p
        elif p.lower() == 'true' or p.lower() == 'false' or p.lower() == 'none' :
            ret = ret + ',' + prefix + p[0].upper()+p[1:]
        else :
            if p.startswith( "'" ) and p.endswith("'") :    # if starts already with simple quote
                withoutQuote = p[1:-1].lower()
                if withoutQuote.isnumeric() :
                    ret = ret + ',' + prefix + withoutQuote
                elif withoutQuote=='true' or withoutQuote=='false' or withoutQuote=='none' :
                    ret = ret + ',' + prefix + withoutQuote[0].upper()+withoutQuote[1:]
                else :
                    ret = ret + ',' + prefix + p
            else :
                ret = ret + ',' + prefix + '"'+ p +'"'    # else add quotes
    retval=ret[1:].replace(')', '')
    logging.debug("PARAMPARSER---- Returned: " + str(retval))
    return retval


def start(cycle=2):
    jeedom_socket.open()
    logging.info("GLOBAL------Socket started...")
    logging.info("GLOBAL------Waiting for messages...")
    thread.start_new_thread( read_socket, (globals.cycle,))
    globals.JEEDOM_COM.send_change_immediate({'started' : 1,'source' : globals.daemonname});

    try:
        while True :
            try:
                current_time = int(time.time())
                if globals.LEARN_MODE and (globals.LEARN_BEGIN+globals.LEARN_TIMEOUT)  < current_time :
                    globals.LEARN_MODE = False
                    logging.info('HEARTBEAT------Quitting learn mode (60s elapsed)')
                    globals.JEEDOM_COM.send_change_immediate({'learn_mode' : 0,'source' : globals.daemonname})

                if (globals.LAST_BEAT + globals.HEARTBEAT_FREQUENCY/2)  < current_time :
                    globals.JEEDOM_COM.send_change_immediate({'heartbeat' : 1,'source' : globals.daemonname})
                    globals.LAST_BEAT = current_time

                if globals.LEARN_MODE and not globals.SCAN_PENDING :
                    thread.start_new_thread( scanner, ('learn',))

                if not globals.SCAN_PENDING and (current_time - globals.SCAN_LAST) > globals.SCAN_FREQUENCY :
                    thread.start_new_thread( scanner, ('scanner',))

                if (current_time - globals.NOWPLAYING_LAST)>globals.NOWPLAYING_FREQUENCY/2 and not globals.LEARN_MODE:
                    for uuid in globals.GCAST_DEVICES :
                        globals.GCAST_DEVICES[uuid].sendNowPlaying_heartbeat()
                    globals.NOWPLAYING_LAST = current_time

                time.sleep(cycle)

            except Exception as e:
                logging.error("GLOBAL------Exception on scanner")

    except KeyboardInterrupt:
        logging.error("GLOBAL------KeyboardInterrupt, shutdown")
        shutdown()


def read_socket(cycle):
    while True :
        try:
            global JEEDOM_SOCKET_MESSAGE
            if not JEEDOM_SOCKET_MESSAGE.empty():
                logging.debug("SOCKET-READ------Message received in socket JEEDOM_SOCKET_MESSAGE")
                message = json.loads(JEEDOM_SOCKET_MESSAGE.get())
                if message['apikey'] != globals.apikey:
                    logging.error("SOCKET-READ------Invalid apikey from socket : " + str(message))
                    return
                logging.debug('SOCKET-READ------Received command from jeedom : '+str(message['cmd']))
                if message['cmd'] == 'add':
                    logging.debug('SOCKET-READ------Add device : '+str(message['device']))
                    if 'uuid' in message['device']:
                        uuid = message['device']['uuid']
                        if uuid not in globals.KNOWN_DEVICES :
                            globals.KNOWN_DEVICES[uuid] = {
                                'uuid': uuid, 'status': {},
                                #'friendly_name': message['device']['name'],
                                'lastOnline':0, 'online':False,
                                'lastSent': 0, 'lastOfflineSent': 0,
                                'options' : message['device']['options']
                            }
                            globals.SCAN_LAST = 0
                elif message['cmd'] == 'remove':
                    logging.debug('SOCKET-READ------Remove device : '+str(message['device']))
                    if 'uuid' in message['device']:
                        uuid = message['device']['uuid']
                        if uuid in globals.NOWPLAYING_DEVICES :
                            del globals.NOWPLAYING_DEVICES[uuid]
                        if uuid in globals.GCAST_DEVICES :
                            globals.GCAST_DEVICES[uuid].disconnect()
                        if uuid in globals.KNOWN_DEVICES :
                            del globals.KNOWN_DEVICES[uuid]
                        globals.SCAN_LAST = 0
                elif message['cmd'] == 'nowplaying':
                    if 'uuid' in message:
                        uuid = message['uuid']
                        globals.NOWPLAYING_DEVICES[uuid] = int(time.time())
                        if uuid in globals.GCAST_DEVICES :
                            logging.debug('SOCKET-READ------Now playing activated for '+uuid)
                            globals.GCAST_DEVICES[uuid].startNowPlaying()
                        else :
                            logging.debug('SOCKET-READ------Now playing for ' +uuid+ ' not activated because is offline')
                elif message['cmd'] == 'learnin':
                    logging.debug('SOCKET-READ------Enter in learn mode')
                    globals.LEARN_MODE = True
                    globals.LEARN_BEGIN = int(time.time())
                    globals.JEEDOM_COM.send_change_immediate({'learn_mode' : 1,'source' : globals.daemonname});
                elif message['cmd'] == 'learnout':
                    logging.debug('SOCKET-READ------Leave learn mode')
                    globals.LEARN_MODE = False
                    globals.JEEDOM_COM.send_change_immediate({'learn_mode' : 0,'source' : globals.daemonname});
                elif message['cmd'] == 'refresh':
                    logging.debug('SOCKET-READ------Attempt a refresh on a device')
                    uuid = message['device']['uuid']
                    if uuid in globals.GCAST_DEVICES :
                        globals.GCAST_DEVICES[uuid].sendDeviceStatus()
                elif message['cmd'] == 'cleanttscache':
                    logging.debug('SOCKET-READ------Clean TTS cache')
                    if 'days' in message :
                        cleanCache(int(message['days']))
                    else :
                        cleanCache()
                elif message['cmd'] == 'refreshall':
                    logging.debug('SOCKET-READ------Attempt a refresh on all devices')
                    for uuid in globals.GCAST_DEVICES :
                        globals.GCAST_DEVICES[uuid].sendDeviceStatus()
                elif message['cmd'] == 'action':
                    logging.debug('SOCKET-READ------Attempt an action on a device')
                    thread.start_new_thread( action_handler, (message,))
                    logging.debug('SOCKET-READ------Action Thread Launched')
                elif message['cmd'] == 'logdebug':
                    logging.info('SOCKET-READ------Passage du demon en mode debug force')
                    log = logging.getLogger()
                    for hdlr in log.handlers[:]:
                        log.removeHandler(hdlr)
                    jeedom_utils.set_log_level('debug')
                    logging.debug('SOCKET-READ------<----- La preuve ;)')
                elif message['cmd'] == 'lognormal':
                    logging.info('SOCKET-READ------Passage du demon en mode de log initial')
                    log = logging.getLogger()
                    for hdlr in log.handlers[:]:
                        log.removeHandler(hdlr)
                    jeedom_utils.set_log_level(globals.log_level)
                elif message['cmd'] == 'stop':
                    logging.info('SOCKET-READ------Arret du demon sur demande socket')
                    globals.JEEDOM_COM.send_change_immediate({'learn_mode' : 0,'source' : globals.daemonname});
                    time.sleep(2)
                    shutdown()
        except Exception as e:
            logging.error("SOCKET-READ------Exception on socket : %s" % str(e))
            logging.debug(traceback.format_exc())
        time.sleep(cycle)

def scanner(name):
    try:
        logging.debug("SCANNER------ Start scanning...")
        globals.SCAN_PENDING = True
        show_memory_usage()

        rawcasts = None
        scanForced = False
        if (int(time.time())-globals.DISCOVERY_LAST)>globals.DISCOVERY_FREQUENCY :
            scanForced = True
        else :
            for known in globals.KNOWN_DEVICES :
                if known not in globals.GCAST_DEVICES :
                    scanForced = scanForced or True

        if scanForced==True or globals.LEARN_MODE==True:
            logging.debug("SCANNER------ Looking for chromecasts on network...")
            rawcasts = pychromecast.get_chromecasts(tries=1, retry_wait=2, timeout=globals.SCAN_TIMEOUT)
            casts = []
            for cast in rawcasts :
                casts.append( JeedomChromeCast(cast, scan_mode=True) )
        else :
            logging.debug("SCANNER------ No need to scan network, all devices are present")
            casts = list(globals.GCAST_DEVICES.values())

        uuid_newlyadded = []
        for cast in casts :
            uuid = cast.uuid
            current_time = int(time.time())

            if uuid in globals.KNOWN_DEVICES :
                globals.KNOWN_DEVICES[uuid]['online'] = True
                globals.KNOWN_DEVICES[uuid]['lastScan'] = current_time
                globals.KNOWN_DEVICES[uuid]["lastOnline"] = current_time

                if uuid not in globals.GCAST_DEVICES :
                    logging.info("SCANNER------ Detected chromecast : " + cast.friendly_name)
                    uuid_newlyadded.append(uuid)
                    globals.GCAST_DEVICES[uuid] = JeedomChromeCast(cast.gcast, globals.KNOWN_DEVICES[uuid]["options"])

                if uuid in globals.NOWPLAYING_DEVICES :
                    if (current_time-globals.NOWPLAYING_DEVICES[uuid]) > globals.NOWPLAYING_TIMEOUT :
                        del globals.NOWPLAYING_DEVICES[uuid]
                        globals.GCAST_DEVICES[uuid].stopNowPlaying()
                    else :
                        globals.GCAST_DEVICES[uuid].startNowPlaying()

                globals.GCAST_DEVICES[uuid].sendDeviceStatusIfNew()

            else :
                if globals.LEARN_MODE :
                    data = {'friendly_name':cast.friendly_name, 'uuid': uuid, 'lastScan': current_time }
                    data['def'] = cast.getDefinition()
                    data['status'] = cast.getStatus()
                    data['learn'] = 1;
                    logging.info("SCANNER------ LEARN MODE : New device : " + uuid + ' (' + data["friendly_name"] + ')')
                    globals.JEEDOM_COM.add_changes('devices::'+uuid,data)

                elif (current_time-globals.DISCOVERY_LAST)>globals.DISCOVERY_FREQUENCY :
                    logging.debug("SCANNER------ DISCOVERY MODE : New device : " + uuid + ' (' + cast.friendly_name + ')')
                    globals.JEEDOM_COM.send_change_immediate({'discovery' : 1, 'uuid' : uuid, 'friendly_name' : cast.friendly_name})
                    globals.DISCOVERY_LAST = current_time

        # memory cleaning
        if rawcasts is not None :
            for cast in casts :
                if cast.uuid not in uuid_newlyadded :
                    cast.disconnect()
        del rawcasts, casts
        del uuid_newlyadded

        # loop through all known devices to find those not connected
        for known in globals.KNOWN_DEVICES :
            current_time = int(time.time())
            is_not_available = True

            if known in globals.GCAST_DEVICES :
                if globals.GCAST_DEVICES[known].is_connected==True :
                    is_not_available = False
                else :
                    # something went wrong so disconnect completely
                    globals.GCAST_DEVICES[known].disconnect()

            if is_not_available==True :
                logging.debug("SCANNER------No connection to device " + known)
                if globals.KNOWN_DEVICES[known]['online']==True :
                    logging.info("SCANNER------Connection lost to device " + known)

                globals.KNOWN_DEVICES[known]['lastScan'] = current_time
                if ( globals.KNOWN_DEVICES[known]['online']==True or (current_time-globals.KNOWN_DEVICES[known]['lastOfflineSent'])>globals.LOSTDEVICE_RESENDNOTIFDELAY ) :
                    globals.KNOWN_DEVICES[known]['online'] = False
                    globals.KNOWN_DEVICES[known]['lastOfflineSent'] = current_time
                    globals.KNOWN_DEVICES[known]['status'] = status = {
                        "uuid" : known,
                        "is_stand_by" : False, "is_active_input" : False,
                        "display_name" : globals.DEFAULT_NODISPLAY, "status_text" : globals.DEFAULT_NOSTATUS,
                        "app_id" : "", "is_busy" : False,
                        "title" : "", "artist" : "", 'series_title': "", "stream_type" : "", "player_state" : "",
                    }
                    #globals.JEEDOM_COM.add_changes('devices::'+known, globals.KNOWN_DEVICES[known])
                    globals.JEEDOM_COM.send_change_immediate_device(known, globals.KNOWN_DEVICES[known])
                    globals.KNOWN_DEVICES[known]['lastSent'] = current_time
                    if known in globals.NOWPLAYING_DEVICES:
                        del globals.NOWPLAYING_DEVICES[known]
                        data = {
                            "uuid" : known,
                            "online" : False, "friendly_name" : "",
                            "is_active_input" : False, "is_stand_by" : False,
                            "display_name" : globals.DEFAULT_NODISPLAY, "status_text" : globals.DEFAULT_NOSTATUS,
                            "app_id" : "", "is_busy" : False, "title" : "",
                            "album_artist" : "", "metadata_type" : "",
                            "album_name" : "", "current_time" : 0,
                            "artist" : "", "image" : None,
                            'series_title': "", 'season': "", 'episode': "",
                            "stream_type" : "", "track" : "",
                            "player_state" : "", "supported_media_commands" : 0,
                            "supports_pause" : "", "duration": 0,
                            "content_type": "", "idle_reason": ""
                        }
                        globals.JEEDOM_COM.send_change_immediate({'uuid' :  known, 'nowplaying':data});

            else :
                globals.KNOWN_DEVICES[known]["lastScan"] = current_time

    except Exception as e:
        logging.error("SCANNER------Exception on scanner : %s" % str(e))
        logging.debug(traceback.format_exc())

    globals.SCAN_LAST = int(time.time())
    globals.SCAN_PENDING = False

memory_last_use=0
memory_last_time=int(time.time())
memory_first_time=int(time.time())
def show_memory_usage():
    if logging.getLogger().isEnabledFor(logging.DEBUG) :
        usage = resource.getrusage(resource.RUSAGE_SELF)
        try:
            global memory_last_use, memory_last_time, memory_first_time
            ru_utime = getattr(usage, 'ru_utime')
            ru_stime = getattr(usage, 'ru_stime')
            ru_maxrss = getattr(usage, 'ru_maxrss')
            total=ru_utime+ru_stime
            curtime=int(time.time())
            timedif=curtime-memory_last_time
            timediftotal=curtime-memory_first_time
            logging.warning(' MEMORY---- Total CPU time used : %.3fs (%.2f%%)  |  Last %i sec : %.3fs (%.2f%%)  | Memory : %s Mo' % (total, total/timediftotal*100, timedif, total-memory_last_use, (total-memory_last_use)/timedif*100, int(round(ru_maxrss/1000))))
            memory_last_use=total
            memory_last_time=curtime
        except:
            pass

def cleanCache(nbDays=0):
    if nbDays == 0 :    # clean entire directory including containing folder
        try:
            if os.path.exists(globals.tts_cachefoldertmp):
                shutil.rmtree(globals.tts_cachefoldertmp)
        except:
            pass
    else :              # clean only files older than X days
        now = time.time()
        path = globals.tts_cachefoldertmp
        try:
            for f in os.listdir(path):
                if os.stat(os.path.join(path,f)).st_mtime < now - nbDays * 86400 :
                    if os.path.isfile(f):
                        os.remove(os.path.join(path, f))
        except:
            pass

def handler(signum=None, frame=None):
    logging.debug("GLOBAL------Signal %i caught, exiting..." % int(signum))
    shutdown()

def shutdown():
    logging.debug("GLOBAL------Shutdown")
    logging.debug("GLOBAL------Removing PID file " + str(globals.pidfile))
    try:
        os.remove(globals.pidfile)
    except:
        pass
    try:
        for uuid in globals.GCAST_DEVICES :
            globals.GCAST_DEVICES[uuid].disconnect()
        globals.JEEDOM_COM.send_change_immediate({'stopped' : 1,'source' : globals.daemonname});
        time.sleep(1)
        jeedom_socket.close()
    except:
        pass
    logging.debug("Exit 0")
    sys.stdout.flush()
    os._exit(0)

# -------------------------------------------
# ------ PROGRAM STARTS HERE ----------------
# -------------------------------------------
parser = argparse.ArgumentParser(description='GoogleCast Daemon for Jeedom plugin')
parser.add_argument("--loglevel", help="Log Level for the daemon", type=str)
parser.add_argument("--pidfile", help="PID filname", type=str)
parser.add_argument("--callback", help="Callback url", type=str)
parser.add_argument("--apikey", help="Jeedom API key", type=str)
parser.add_argument("--ttsweb", help="Jeedom Web server (for TTS)", type=str)
parser.add_argument("--ttslang", help="Default TTS language", type=str)
parser.add_argument("--ttsengine", help="Default TTS engine", type=str)
parser.add_argument("--ttscache", help="Use cache", type=str)
parser.add_argument("--ttsspeed", help="TTS speech speed", type=str)
parser.add_argument("--ttsgapikey", help="TTS Google API Key", type=str)
parser.add_argument("--socketport", help="Socket Port", type=str)
parser.add_argument("--sockethost", help="Socket Host", type=str)
parser.add_argument("--daemonname", help="Daemon Name", type=str)
parser.add_argument("--scantimeout", help="GoogleCast scan timeout", type=str)
parser.add_argument("--scanfrequency", help="Frequency for scan", type=str)
parser.add_argument("--cycle", help="Cycle to send/receive event", type=str)
parser.add_argument("--cyclemain", help="Cycle for main loop", type=str)
parser.add_argument("--cyclefactor", help="Factor for event cycles (default=1)", type=str)
parser.add_argument("--defaultstatus", help="Returned display string", type=str)
args = parser.parse_args()


if args.scantimeout:
    globals.SCAN_TIMEOUT = int(args.scantimeout)
if args.scanfrequency:
    globals.SCAN_FREQUENCY = int(args.scanfrequency)
if args.loglevel:
    globals.log_level = args.loglevel
if args.pidfile:
    globals.pidfile = args.pidfile
if args.callback:
    globals.callback = args.callback
if args.apikey:
    globals.apikey = args.apikey
if args.ttsweb:
    globals.JEEDOM_WEB = args.ttsweb
if args.ttslang:
    globals.tts_language = args.ttslang
if args.ttsengine:
    globals.tts_engine = args.ttsengine
if args.ttsspeed:
    globals.tts_speed = args.ttsspeed
if args.ttscache:
    globals.tts_cacheenabled = False if int(args.ttscache)==0 else True
if args.ttsgapikey:
    globals.tts_gapi_key = args.ttsgapikey
    if globals.tts_gapi_key != 'none' :
        globals.tts_gapi_haskey = True
if args.cycle:
    globals.cycle = float(args.cycle)
if args.cyclemain:
    globals.cycle_main = float(args.cyclemain)
if args.cyclefactor:
    globals.cycle_factor = float(args.cyclefactor)
if args.socketport:
    globals.socketport = args.socketport
if args.sockethost:
    globals.sockethost = args.sockethost
if args.daemonname:
    globals.daemonname = args.daemonname
if args.defaultstatus:
    globals.DEFAULT_NOSTATUS = args.defaultstatus

if globals.cycle_factor==0:
    globals.cycle_factor=1
globals.NOWPLAYING_FREQUENCY = int(globals.NOWPLAYING_FREQUENCY*globals.cycle_factor)
globals.SCAN_FREQUENCY = int(globals.SCAN_FREQUENCY*globals.cycle_factor)

globals.socketport = int(globals.socketport)
globals.cycle = float(globals.cycle*globals.cycle_factor)
globals.cycle_main = float(globals.cycle_main*globals.cycle_factor)

jeedom_utils.set_log_level(globals.log_level)
logging.info('------------------------------------------------------')
logging.info('------------------------------------------------------')
logging.info('GLOBAL------STARTING googlecast')
logging.info('GLOBAL------Scan Timeout : '+str(globals.SCAN_TIMEOUT))
logging.info('GLOBAL------Scan Frequency : '+str(globals.SCAN_FREQUENCY))
logging.info('GLOBAL------Log level : '+str(globals.log_level))
logging.info('GLOBAL------Socket port : '+str(globals.socketport))
logging.info('GLOBAL------Socket host : '+str(globals.sockethost))
logging.info('GLOBAL------PID file : '+str(globals.pidfile))
logging.info('GLOBAL------Apikey : '+str(globals.apikey))
logging.info('GLOBAL------TTS Jeedom server : '+str(globals.JEEDOM_WEB))
logging.info('GLOBAL------TTS default language : '+str(globals.tts_language))
logging.info('GLOBAL------TTS default engine : '+str(globals.tts_engine))
logging.info('GLOBAL------TTS default speech speed : '+str(globals.tts_speed))
if globals.tts_gapi_haskey :
    logging.info('GLOBAL------TTS Google API Key (optional) : OK')
else :
    logging.info('GLOBAL------TTS Google API Key (optional) : NOK')
logging.info('GLOBAL------Cache status : '+str(globals.tts_cacheenabled))
logging.info('GLOBAL------Callback : '+str(globals.callback))
logging.info('GLOBAL------Event cycle : '+str(globals.cycle))
logging.info('GLOBAL------Main cycle : '+str(globals.cycle_main))
logging.info('GLOBAL------Default status message : '+str(globals.DEFAULT_NOSTATUS))
logging.info('-----------------------------------------------------')

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)

try:
    jeedom_utils.write_pid(str(globals.pidfile))
    globals.JEEDOM_COM = jeedom_com(apikey = globals.apikey,url = globals.callback,cycle=globals.cycle)
    if not globals.JEEDOM_COM.test():
        logging.error('GLOBAL------Network communication issues. Please fix your Jeedom network configuration.')
        shutdown()
    else :
        logging.info('GLOBAL------Network communication to jeedom OK.')
    jeedom_socket = jeedom_socket(port=globals.socketport,address=globals.sockethost)
    start(globals.cycle_main)

except Exception as e:
    logging.error('GLOBAL------Fatal error : '+str(e))
    logging.debug(traceback.format_exc())
    shutdown()
