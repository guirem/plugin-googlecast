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
    import pychromecast.pychromecast.controllers.plex as plex
    import pychromecast.pychromecast.controllers.spotify as Spotify
except ImportError:
    logging.error("ERROR: One or several pychromecast controllers are not loaded !")
    print(traceback.format_exc())
    pass

try:
    import pychromecast.pychromecast.customcontrollers.youtube as youtube
except ImportError:
    logging.error("ERROR: Custom controller not loaded !")
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
            self.customplayer = None
            self.customplayername = ""
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
        self._internal_refresh_status(False)
        self.sendNowPlaying(force=True)

    def new_media_status(self, new_mediastatus):
        #logging.debug("JEEDOMCHROMECAST------ New media status " + str(new_mediastatus))
        if self.now_playing==True and new_mediastatus.player_state!="BUFFERING" :
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

    def loadPlayer(self, playername, params=None, token=None) :
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
                    elif playername == 'spotify' :
                        player = spotify.SpotifyController(token)
                        self.gcast.register_handler(player)
                    elif playername == 'plex' :
                        player = plex.PlexController()
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
                except Exception :
                    player = None
                    pass
            self.sendNowPlaying(force=True)
            return self.customplayer
        return None

    def resetPlayer(self) :
        if self.customplayer is not None :
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
            status = {
                "uuid" : uuid,
                "friendly_name" : self.gcast.device.friendly_name,
                "is_active_input" : True if self.gcast.status.is_active_input else False,
                "is_stand_by" :  True if self.gcast.status.is_stand_by else False,
                "volume_level" : int(self.gcast.status.volume_level*100),
                "volume_muted" : self.gcast.status.volume_muted,
                "app_id" : self.gcast.status.app_id,
                "display_name" : self.gcast.status.display_name if self.gcast.status.display_name is not None else globals.DEFAULT_NODISPLAY,
                "status_text" : self.gcast.status.status_text if self.gcast.status.status_text!="" else globals.DEFAULT_NOSTATUS,
                "is_busy" : not self.gcast.is_idle,
            }
            return status
        else :
            return {
                "uuid" : self.uuid,
                "friendly_name" : "", "is_stand_by" :  False, "is_active_input" : False,
                "display_name" : globals.DEFAULT_NODISPLAY, "status_text" : globals.DEFAULT_NOSTATUS,
                "app_id" : "", "is_busy" : False,
            }


    def _internal_status_different(self, new_status):
        prev_status = self.previous_status
        if len(prev_status) != len(new_status) or len(prev_status)==2 or 'volume_level' not in new_status :
            return True
        if prev_status['volume_level'] != new_status['volume_level'] :
            return True
        if prev_status['app_id'] != new_status['app_id'] :
            return True
        if prev_status['is_busy'] != new_status['is_busy'] :
            return True
        if prev_status['volume_level'] != new_status['volume_level'] :
            return True
        if prev_status['volume_muted'] != new_status['volume_muted'] :
            return True
        if prev_status['is_stand_by'] != new_status['is_stand_by'] :
            return True
        if prev_status['status_text'] != new_status['status_text'] :
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
    #name = message['command']['name']
    rootcmd = message['cmd']
    uuid = message['command']['device']['uuid']

    cmd = 'NONE'
    if 'cmd' in message['command'] :
        cmd = message['command']['cmd']
    app = 'media'
    if 'app' in message['command'] :
        app = message['command']['app']
    value = None
    if 'value' in message['command'] :
        value = message['command']['value']

    needSendStatus = True
    logging.debug("ACTION------ " + rootcmd + " - " + cmd + ' - ' + uuid + ' - ' + str(value)+ ' - ' + app)
    if uuid in globals.KNOWN_DEVICES and uuid in globals.GCAST_DEVICES and rootcmd == "action":

        jcast = globals.GCAST_DEVICES[uuid]
        gcast = jcast.gcast
        if cmd == 'refresh':
            logging.debug("ACTION------Refresh action")
        elif cmd == 'reboot':
            logging.debug("ACTION------Reboot action")
            gcast.reboot()
            time.sleep(5)
        elif cmd == 'volume_up':
            logging.debug("ACTION------Volumme up action")
            gcast.volume_up(value if value!=None else 0.1)
        elif cmd == 'volume_down':
            logging.debug("ACTION------Volume down action")
            gcast.volume_down(value if value!=None else 0.1)
        elif cmd == 'volume_set':
            logging.debug("ACTION------Volume set action")
            gcast.set_volume(int(value)/100)
        elif cmd == 'play' and app == 'media':
            logging.debug("ACTION------Play action")
            gcast.media_controller.play()
        elif cmd == 'stop' and app == 'media':
            logging.debug("ACTION------Stop action")
            gcast.media_controller.stop()
        elif cmd == 'rewind':
            logging.debug("ACTION------Rewind action")
            gcast.media_controller.rewind()
        elif cmd == 'skip':
            logging.debug("ACTION------Skip action")
            gcast.media_controller.skip()
        elif cmd == 'seek':
            logging.debug("ACTION------Seek action")
            gcast.media_controller.seek(0 if value is None else value)
        elif cmd == 'start_app':
            logging.debug("ACTION------Stop action")
            gcast.start_app('' if value is None else value)
        elif cmd == 'quit_app':
            logging.debug("ACTION------Stop action")
            gcast.quit_app()
        elif cmd == 'pause' and app == 'media':
            logging.debug("ACTION------Stop action")
            gcast.media_controller.pause()
        elif cmd == 'mute_on':
            logging.debug("ACTION------Mute on action")
            gcast.set_volume_muted(True)
        elif cmd == 'mute_off':
            logging.debug("ACTION------Mute off action")
            gcast.set_volume_muted(False)
        elif app is not None:
            logging.debug("ACTION------Playing action " + cmd + ' for application ' + app)
            try:
                quit_app_before=True
                if 'quit_app_before' in message['command'] :
                    quit_app_before = True if message['command']['quit_app_before'] else False
                force_register=False
                if 'force_register' in message['command'] :
                    force_register = True if message['command']['force_register'] else False
                wait=2
                if 'wait' in message['command'] :
                    wait = message['command']['wait'] if message['command']['wait'].isnumeric() else 1

                if app == 'web':    # app=web|cmd=load_url|value=https://news.google.com,True,5
                    force_register=True
                    possibleCmd = ['load_url']
                    if cmd in possibleCmd :
                        player = jcast.loadPlayer(app, { 'quitapp' : quit_app_before}, None)
                        eval( 'player.' + cmd + '('+ gcast_prepareAppParam(value) +')' )
                elif app == 'youtube':  # app=youtube|cmd=play_video|value=fra4QBLF3GU
                    if gcast.device.cast_type == 'cast' :
                        possibleCmd = ['play_video', 'start_new_session', 'add_to_queue', 'update_screen_id', 'clear_playlist', 'play', 'stop', 'pause']
                        if cmd in possibleCmd :
                            player = jcast.loadPlayer(app, { 'quitapp' : quit_app_before, 'wait': wait}, None)
                            eval( 'player.' + cmd + '('+ gcast_prepareAppParam(value) +')' )
                    else :
                        logging.error("ACTION------ YouTube not availble on Chromecast Audio")
                elif app == 'spotify':  # app=spotify|cmd=launch_app|token=XXXXXX
                    possibleCmd = ['launch_app']
                    if cmd in possibleCmd :
                        if 'token' not in message['command'] :
                            logging.error("ACTION------ Token missing for Spotify")
                        else :
                            player = jcast.loadPlayer(app, { 'quitapp' : quit_app_before, 'wait': wait}, message['command']['token'])
                            player.launch_app()
                elif app == 'backdrop':  # also called backdrop
                    if gcast.device.cast_type == 'cast' :
                        gcast.start_app('E8C28D3C')
                    else :
                        logging.error("ACTION------ Backdrop not availble on Chromecast Audio")
                elif app == 'plex':            # app=plex|cmd=pause
                    quit_app_before=False
                    possibleCmd = ['play', 'stop', 'pause']
                    if cmd in possibleCmd :
                        player = jcast.loadPlayer(app, { 'quitapp' : quit_app_before, 'wait': wait}, None)
                        eval( 'player.' + cmd + '('+ gcast_prepareAppParam(value) +')' )
                else : # media        # app=media|cmd=play_media|value=http://bit.ly/2JzYtfX,video/mp4,Mon film
                    possibleCmd = ['play', 'stop', 'pause', 'play_media']
                    player = jcast.loadPlayer('media', { 'quitapp' : quit_app_before}, None)
                    eval( 'player.' + cmd + '('+ gcast_prepareAppParam(value) +')' )
            except Exception as e:
                logging.error("ACTION------Error while playing "+app+" : %s" % str(e))
                logging.debug(traceback.format_exc())

        else:
            logging.debug("ACTION------NOT IMPLEMENTED : " + cmd)

        if needSendStatus :
            globals.GCAST_DEVICES[uuid].sendDeviceStatus()
    return


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
        elif p == 'True' or p == 'False' or p == 'None' :
            ret = ret + ',' + prefix + p
        else :
            if p.startswith( "'" ) and p.endswith("'") :    # if starts already with simple quote
                withoutQuote = p[1:-1]
                if withoutQuote.isnumeric() :
                    ret = ret + ',' + prefix + withoutQuote
                elif withoutQuote=='True' or withoutQuote=='False' or withoutQuote=='None' :
                    ret = ret + ',' + prefix + withoutQuote
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
                                'friendly_name': message['device']['name'],
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
                elif message['cmd'] == 'refreshall':
                    logging.debug('SOCKET-READ------Attempt a refresh on all devices')
                    for uuid in globals.GCAST_DEVICES :
                        globals.GCAST_DEVICES[uuid].sendDeviceStatus()
                elif message['cmd'] in ['action']:
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
                        "uuid" : known, "friendly_name" : "",
                        "is_stand_by" : False, "is_active_input" : False,
                        "display_name" : globals.DEFAULT_NODISPLAY, "status_text" : globals.DEFAULT_NOSTATUS,
                        "app_id" : "", "is_busy" : False,
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
if args.cycle:
    globals.cycle = float(args.cycle)
if args.cyclemain:
    globals.cycle_main = float(args.cyclemain)
if args.cyclefactor:
    globals.cycle_factor = int(args.cyclefactor)
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

#globals.cycle_factor = int(globals.cycle_factor)

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
logging.info('GLOBAL------Callback : '+str(globals.callback))
logging.info('GLOBAL------Event cycle : '+str(globals.cycle))
logging.info('GLOBAL------Main cycle : '+str(globals.cycle_main))
logging.info('GLOBAL------Default status message : '+str(globals.DEFAULT_NOSTATUS))
logging.info('------------------------------------------------------')

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
