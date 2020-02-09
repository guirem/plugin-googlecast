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

import os
import re
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
from gcloudtts import gcloudTTS, gcloudTTSError

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
    import pychromecast.pychromecast.controllers.spotify as spotify
except ImportError:
    logging.error(
        "ERROR: One or several pychromecast controllers are not loaded !")
    print(traceback.format_exc())
    sys.exit(1)
    pass

try:
    import pychromecast.pychromecast.customcontrollers.plex2 as plex
    import pychromecast.pychromecast.customcontrollers.youtube as youtube
except ImportError:
    logging.error("ERROR: Custom controllers not loaded !")
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
    from jeedom.jeedom import jeedom_com, jeedom_socket, jeedom_utils, JEEDOM_SOCKET_MESSAGE
except ImportError:
    print("Error: importing module from jeedom folder")
    sys.exit(1)

# ------------------------

# class JeedomChromeCast


class JeedomChromeCast:
    def __init__(self, gcast, options=None, scan_mode=False):
        self.uuid = str(gcast.device.uuid)
        self.friendly_name = gcast.device.friendly_name
        self.gcast = gcast
        self.previous_status = {"uuid": self.uuid, "online": False}
        self.now_playing = False
        self.online = True
        self.scan_mode = scan_mode
        self.error_count = 0
        if scan_mode is False:
            self.gcast.wait(timeout=globals.SCAN_TIMEOUT)
            self.being_shutdown = False
            self.is_recovering = False
            self.disable_notif = False
            self.customplayer = None
            self.customplayername = ""
            self.previous_playercmd = {}
            self.sessionid_storenext = False
            self.sessionid_current = ''
            self.previous_nowplaying = {}
            self.previous_usewarmup = False
            self.nowplaying_lastupdated = 0
            self.has_apperror = False
            self.apperror_type = 'NONE'
            self.gcast.media_controller.register_status_listener(self)
            self.gcast.register_launch_error_listener(self)
            self.gcast.register_status_listener(self)
            self.gcast.register_connection_listener(self)
            self.options = options
            # manage CEC exception
            if options and 'ignore_CEC' in options:
                if options['ignore_CEC'] == "1" and self.friendly_name not in pychromecast.IGNORE_CEC:
                    pychromecast.IGNORE_CEC.append(
                        self.gcast.device.friendly_name)
            # CEC always disable for audio chromecast
            if self.gcast.device.cast_type != 'cast' and self.friendly_name not in pychromecast.IGNORE_CEC:
                pychromecast.IGNORE_CEC.append(self.gcast.device.friendly_name)

            if self.gcast.socket_client:
                self.gcast.socket_client.tries = int(
                    round(globals.SCAN_FREQUENCY)/10/2)
                self.gcast.socket_client.retry_wait = 5
                self.gcast.socket_client.timeout = 5

    @property
    def device(self):
        return self.gcast.device

    @property
    def is_connected(self):
        try:
            if self.gcast.socket_client is not None or self.gcast.status is not None or self.online is True or self.is_recovering is True:
                return True
        except Exception:
            return False

    @property
    def is_castgroup(self):
        if self.gcast.device.cast_type != 'group':
            return False
        return True

    @property
    def support_video(self):
        if self.gcast.device.cast_type == 'cast':
            return True
        return False

    @property
    def media_current_time(self):
        ret = 0
        try:
            ret = self.gcast.media_controller.status.adjusted_current_time
            ret = 0 if ret is None else float(ret)
        except Exception:
            pass
        return ret

    def reset_exceptioncount(self):
        self.error_count = 0

    def manage_exceptions(self, message_string=''):
        self.error_count = self.error_count + 1
        if self.error_count >= 3:
            logging.debug(
                "JEEDOMCHROMECAST------ Forced disconnection after 3 exceptions for " + self.uuid)
            self.disconnect()
        elif 'Chromecast is connecting...' in message_string:
            logging.debug(
                "JEEDOMCHROMECAST------ Forced disconnection due to connection fatal error for " + self.uuid)
            self.disconnect()
        else:
            logging.debug(
                "JEEDOMCHROMECAST------ Managed exception but no forced disconnection for " + self.uuid)

    def applaunch_callback_reset(self):
        self.has_apperror = False
        self.apperror_type = 'NONE'

    def applaunch_callback_haserror(self):
        retbol = self.has_apperror
        rettype = self.apperror_type
        self.manage_callback_reset()
        return retbol, rettype

    def getCurrentVolume(self):
        return int(self.gcast.status.volume_level*100)

    def startNowPlaying(self):
        if self.now_playing is False and self.online is True:
            logging.debug(
                "JEEDOMCHROMECAST------ Starting monitoring of " + self.uuid)
            self.now_playing = True
            self.sendNowPlaying(force=True)

    def stopNowPlaying(self):
        logging.debug(
            "JEEDOMCHROMECAST------ Stopping monitoring of " + self.uuid)
        self.now_playing = False

    def new_cast_status(self, new_status):
        # logging.debug("JEEDOMCHROMECAST------ Status " + str(new_status))
        self._manage_previous_status(new_status)
        if not self.disable_notif:
            self._internal_refresh_status(False)
            self.sendNowPlaying(force=True)

    def new_media_status(self, new_mediastatus):
        # logging.debug("JEEDOMCHROMECAST------ New media status " + str(new_mediastatus))
        if new_mediastatus.player_state != "BUFFERING" and not self.disable_notif:
            if not globals.disable_mediastatus:
                self._internal_send_now_playing_statusupdate(new_mediastatus)
            if self.now_playing is True:
                self._internal_send_now_playing()

    def new_launch_error(self, launch_failure):
        logging.debug(
            "JEEDOMCHROMECAST------ New launch error " + str(launch_failure))
        if launch_failure.reason == "CANCELLED":
            # self.manage_exceptions('Launch error : CANCELLED')
            try:
                self.gcast.quit_app()
            except Exception:
                self.manage_exceptions('Launch error : CANCELLED')
                pass
        self.has_apperror = True
        self.apperror_type = launch_failure.reason
        sendErrorDeviceStatus(self.uuid, 'APP ERROR')

    def new_connection_status(self, new_status):
        # CONNECTING / CONNECTED / DISCONNECTED / FAILED / LOST
        logging.debug(
            "JEEDOMCHROMECAST------ Connexion change event " + str(new_status.status))
        self.online = False
        if new_status.status == "DISCONNECTED" and self.being_shutdown is False:
            self.disconnect()
            logging.info(
                "JEEDOMCHROMECAST------ Chromecast has beend disconnected : " + self.friendly_name)
        if new_status.status == "LOST":
            self.is_recovering = True
            self._internal_refresh_status(True)
        if new_status.status == "CONNECTING" or new_status.status == "FAILED":
            self.is_recovering = True
        if new_status.status == "CONNECTED":    # is reborn...
            self.online = True
            self.error_count = 0
            self.is_recovering = False
            if self.uuid not in globals.GCAST_DEVICES:
                globals.GCAST_DEVICES[self.uuid] = self
            self._internal_refresh_status(True)
            if self.now_playing is True:
                self._internal_trigger_now_playing_update()

    def _manage_previous_status(self, new_status):
        # logging.debug("JEEDOMCHROMECAST------ Manage previous status " + str(new_status))
        if self.sessionid_storenext and new_status.session_id is not None:
            self.sessionid_current = new_status.session_id
            self.sessionid_storenext = False
        appid = new_status.app_id
        if appid is not None and new_status.status_text not in ['Casting: TTS', 'Default Media Receiver'] and self.sessionid_current != new_status.session_id:
            self.previous_playercmd = {}
            logging.debug(
                "JEEDOMCHROMECAST------ Manage previous status : Removing previous playercmd!")

    def savePreviousPlayerCmd(self, params):
        # logging.debug("JEEDOMCHROMECAST------ Manage previous player cmd " + str(params))
        self.previous_playercmd['params'] = params
        self.previous_playercmd['time'] = int(time.time())
        self.previous_playercmd['appid'] = self.getAppId(
            params['app'] if 'app' in params else None)
        self.previous_playercmd['appname'] = params['app'] if 'app' in params else None
        self.sessionid_storenext = True
        self.previous_usewarmup = False
        self.sessionid_current = ''

    def resetPreviousPlayerCmd(self):
        self.previous_playercmd = {}
        self.sessionid_storenext = False
        self.sessionid_current = ''

    def getPreviousPlayerCmd(self, forceapplaunch=False, notifMode=True):
        logging.debug(
            "JEEDOMCHROMECAST------ getPreviousPlayerCmd " + str(self.previous_playercmd))
        ret = None
        beforeTTSappid = (self.previous_playercmd['current_appid']
                          if 'current_appid' in self.previous_playercmd else None)
        if 'params' in self.previous_playercmd:
            if self.previous_playercmd['appid'] == beforeTTSappid or notifMode is False:
                self.previous_playercmd['params']
                if 'current_time' in self.previous_playercmd and self.previous_playercmd['current_time'] > 0:
                    if 'current_stream_type' in self.previous_playercmd and self.previous_playercmd['current_stream_type'] != 'LIVE':
                        self.previous_playercmd['params']['offset'] = self.previous_playercmd['current_time']
                    if 'live' in self.previous_playercmd['params']:
                        self.previous_playercmd['params']['offset'] = 0
                playerstate = self.previous_playercmd[
                    'current_player_state'] if 'current_player_state' in self.previous_playercmd else 'PLAYING'
                if playerstate == 'PAUSED':
                    ret = [self.previous_playercmd['params'], {'cmd': 'pause'}]
                elif playerstate == 'IDLE':
                    ret = [self.previous_playercmd['params'], {'cmd': 'stop'}]
                else:
                    ret = [self.previous_playercmd['params'], {'cmd': 'play'}]

        elif beforeTTSappid is not None and forceapplaunch:
            ret = {'cmd': 'start_app', 'appid': beforeTTSappid}
        return ret

    def prepareTTSplay(self):
        retval = 0
        if self.previous_usewarmup is False:
            try:
                self.previous_playercmd['current_appid'] = self.gcast.status.app_id
                self.previous_playercmd['current_sessionid'] = self.gcast.status.session_id
                self.previous_playercmd['current_player_state'] = self.gcast.media_controller.status.player_state
                self.previous_playercmd['current_stream_type'] = self.gcast.media_controller.status.stream_type
                retval = self.media_current_time
            except Exception:
                pass
            self.previous_playercmd['current_time'] = retval
        else:
            self.previous_usewarmup = False
        return retval

    def prepareForceResume(self, player_state, current_time):
        if player_state is not None:
            self.previous_playercmd['current_player_state'] = player_state
        if current_time is not None:
            self.previous_playercmd['current_time'] = current_time

    def prepareWarumplay(self):
        retval = 0
        try:
            self.previous_usewarmup = True
            self.previous_playercmd['current_appid'] = self.gcast.status.app_id
            self.previous_playercmd['current_sessionid'] = self.gcast.status.session_id
            self.previous_playercmd['current_player_state'] = self.gcast.media_controller.status.player_state
            self.previous_playercmd['current_stream_type'] = self.gcast.media_controller.status.stream_type
            retval = self.media_current_time
        except Exception:
            pass
        self.previous_playercmd['current_time'] = retval
        return retval

    def getAppId(self, appname):
        retval = None
        if appname == 'plex':
            retval = '9AC194DC'
        elif appname == 'media':
            retval = 'CC1AD845'
        elif appname == 'backdrop':
            retval = 'E8C28D3C'
        elif appname == 'web':
            retval = '84912283'
        return retval

    def sendDeviceStatus(self, _force=True):
        try:
            self.gcast.media_controller.update_status()
            time.sleep(0.2)
        except Exception:
            pass
        self._internal_refresh_status(_force)

    def sendDeviceStatusIfNew(self):
        self.sendDeviceStatus(False)

    def disconnect(self):
        if self.scan_mode is False:
            self.is_recovering = False
            self.being_shutdown = True
            self._internal_refresh_status(True)
            if self.now_playing is True:
                self._internal_send_now_playing()
                self.now_playing = False
            if self.uuid in globals.GCAST_DEVICES:
                del globals.GCAST_DEVICES[self.uuid]
            logging.debug(
                "JEEDOMCHROMECAST------ Chromecast disconnected : " + self.friendly_name)
        try:
            self.gcast.disconnect()
        except Exception:
            pass
        self.free_memory()

    def free_memory(self):
        try:
            self.gcast.socket_client.socket.shutdown(socket.SHUT_RDWR)
            self.gcast.socket_client.socket.close()
            del self.gcast
        except Exception:
            pass
        del self

    def loadPlayer(self, playername, params=None):
        if self.gcast.socket_client:
            forceReload = False
            if params and 'forcereload' in params:
                forceReload = True
            if not self.customplayer or self.customplayername != playername or forceReload is True:
                try:
                    if playername == 'web':
                        player = dashcast.DashCastController()
                        self.gcast.register_handler(player)
                    elif playername == 'youtube':
                        player = youtube.YouTubeController()
                        self.gcast.register_handler(player)
                        time.sleep(5)
                    elif playername == 'spotify':
                        player = spotify.SpotifyController()
                        self.gcast.register_handler(player)
                        time.sleep(2)
                    elif playername == 'plex':
                        player = plex.PlexController()
                        self.gcast.register_handler(player)
                        time.sleep(2)
                    else:
                        player = self.gcast.media_controller
                    logging.debug(
                        "JEEDOMCHROMECAST------ Initiating player " + str(player.namespace))
                    self.customplayer = player
                    self.customplayername = playername
                    if params and 'waitbeforequit' in params:
                        time.sleep(params['waitbeforequit'])
                    if params and 'quitapp' in params:
                        self.gcast.quit_app()
                    if params and 'wait' in params:
                        time.sleep(params['wait'])
                except Exception as e:
                    logging.error("JEEDOMCHROMECAST------ Error while initiating player " +
                                  playername + " on low level commands : %s" % str(e))
                    logging.debug(traceback.format_exc())
                    player = None
                    pass
            # else:
            #    time.sleep(0.2)
            if not self.disable_notif:
                self.sendNowPlaying(force=True)
            return self.customplayer
        return None

    def resetPlayer(self):
        self.resetPreviousPlayerCmd()
        if self.customplayer is not None and self.customplayername != 'media':
            if self.gcast.socket_client and self.customplayer.namespace in self.gcast.socket_client._handlers:
                del self.gcast.socket_client._handlers[self.customplayer.namespace]
            self.customplayer = None
            self.sendNowPlaying(force=True)

    def _internal_refresh_status(self, _force=False):
        uuid = self.uuid
        status = self._internal_get_status()
        if _force or self._internal_status_different(status):
            logging.debug(
                "JEEDOMCHROMECAST------ Detected changes in status of " + self.device.friendly_name)
            globals.KNOWN_DEVICES[uuid]['status'] = status
            self.previous_status = status
            globals.KNOWN_DEVICES[uuid]['online'] = self.online
            if self.online is False:
                globals.KNOWN_DEVICES[uuid]['lastOfflineSent'] = int(
                    time.time())
            globals.JEEDOM_COM.add_changes(
                'devices::'+uuid, globals.KNOWN_DEVICES[uuid])
            globals.KNOWN_DEVICES[uuid]['lastSent'] = int(time.time())

    def _internal_get_status(self):
        if self.gcast.status is not None and self.online is True:
            uuid = self.uuid
            playStatus = self.gcast.media_controller.status
            status = {
                "uuid": uuid, "uri": self.gcast.uri,
                "friendly_name": self.gcast.device.friendly_name,
                "is_active_input": True if self.gcast.status.is_active_input else False,
                "is_stand_by":  True if self.gcast.status.is_stand_by else False,
                "volume_level": int(self.gcast.status.volume_level*100),
                "volume_muted": self.gcast.status.volume_muted,
                "app_id": self.gcast.status.app_id,
                "icon_url": self.gcast.status.icon_url,
                "display_name": self.gcast.status.display_name if self.gcast.status.display_name is not None else globals.DEFAULT_NODISPLAY,
                "status_text": self.gcast.status.status_text if self.gcast.status.status_text != "" else globals.DEFAULT_NOSTATUS,
                "is_busy": not self.gcast.is_idle,
                "title": "" if playStatus.title is None else playStatus.title,
                "artist": "" if playStatus.artist is None else playStatus.artist,
                "series_title": "" if playStatus.series_title is None else playStatus.series_title,
                "stream_type": "" if playStatus.stream_type is None else playStatus.stream_type,
                "player_state": "" if playStatus.player_state is None else playStatus.player_state,
            }
            return status
        else:
            return {
                "uuid": self.uuid,
                "is_stand_by":  False, "is_active_input": False,
                "display_name": globals.DEFAULT_NODISPLAY, "status_text": globals.DEFAULT_NOSTATUS,
                "app_id": "", "icon_url": "", "is_busy": False,
                "title": "", "artist": "", 'series_title': "", "stream_type": "", "player_state": "",
            }

    def _internal_status_different(self, new_status):
        prev_status = self.previous_status
        if len(prev_status) != len(new_status) or len(prev_status) == 2 or 'volume_level' not in new_status:
            return True
        if prev_status['status_text'] != new_status['status_text']:
            return True
        if prev_status['volume_level'] != new_status['volume_level']:
            return True
        if prev_status['is_busy'] != new_status['is_busy']:
            return True
        if prev_status['volume_muted'] != new_status['volume_muted']:
            return True
        if prev_status['is_stand_by'] != new_status['is_stand_by']:
            return True
        if prev_status['app_id'] != new_status['app_id']:
            return True
        if prev_status['player_state'] != new_status['player_state']:
            return True
        return False

    def _internal_send_now_playing_statusupdate(self, new_nowplaying):
        prev_nowplaying = self.previous_nowplaying
        test_dif = False
        if 'title' not in prev_nowplaying:
            test_dif = True
        elif prev_nowplaying['title'] != new_nowplaying.title:
            test_dif = True
        elif prev_nowplaying['player_state'] != new_nowplaying.player_state and new_nowplaying.player_state != ['UNKNOWN']:
            test_dif = True

        if test_dif is True:
            mediastatus = {
                "uuid": self.uuid,
                "title": '' if new_nowplaying.title is None else new_nowplaying.title,
                "artist": '' if new_nowplaying.artist is None else new_nowplaying.artist,
                "series_title": '' if new_nowplaying.series_title is None else new_nowplaying.series_title,
                "player_state": '' if new_nowplaying.player_state is None else new_nowplaying.player_state,
            }
            logging.debug(
                "JEEDOMCHROMECAST------ NOW PLAYING STATUS SEND " + str(mediastatus))
            self.previous_nowplaying = mediastatus
            globals.JEEDOM_COM.add_changes(
                'devices::'+self.uuid, {'uuid': self.uuid, 'typemsg': 'info', 'status': mediastatus})

    def getDefinition(self):
        status = {
            "friendly_name": self.gcast.device.friendly_name,
            "model_name": self.gcast.device.model_name,
            "manufacturer": self.gcast.device.manufacturer,
            "cast_type": self.gcast.device.cast_type,
            "uri": self.gcast.uri
        }
        return status

    def getStatus(self):
        return self._internal_get_status()

    def _internal_trigger_now_playing_update(self):
        try:
            self.gcast.media_controller.update_status()
        except Exception:
            pass

    def sendNowPlaying(self, force=False):
        if force is True:
            self._internal_send_now_playing()
        elif self.now_playing is True:
            logging.debug("JEEDOMCHROMECAST------ NOW PLAYING " + self.uuid +
                          " in seconds : " + str(int(time.time())-self.nowplaying_lastupdated))
            if (int(time.time())-self.nowplaying_lastupdated) >= globals.NOWPLAYING_FREQUENCY:
                self._internal_trigger_now_playing_update()

    def sendNowPlaying_heartbeat(self):
        if self.now_playing is True:
            if (int(datetime.utcnow().timestamp())-self.nowplaying_lastupdated) >= globals.NOWPLAYING_FREQUENCY:
                logging.debug("JEEDOMCHROMECAST------ NOW PLAYING heartbeat for " + self.uuid +
                              " in seconds : " + str(int(datetime.utcnow().timestamp())-self.nowplaying_lastupdated))
                self._internal_trigger_now_playing_update()
            if (int(datetime.utcnow().timestamp())-self.nowplaying_lastupdated) >= globals.NOWPLAYING_FREQUENCY_MAX:
                logging.debug("JEEDOMCHROMECAST------ NOW PLAYING heartbeat for " + self.uuid +
                              " : force to resend data after " + str(globals.NOWPLAYING_FREQUENCY_MAX) + " seconds")
                self._internal_send_now_playing()

    def _internal_send_now_playing(self):
        uuid = self.uuid
        if self.gcast.status and self.online is True:
            playStatus = self.gcast.media_controller.status
            if self.gcast.media_controller.status.last_updated:
                self.nowplaying_lastupdated = int(
                    self.gcast.media_controller.status.last_updated.timestamp())
            else:
                self.nowplaying_lastupdated = int(time.time())
            if len(playStatus.images) > 0:
                img = str(playStatus.images[0].url)
            else:
                img = None
            data = {
                "uuid": uuid,
                "online": True,
                "friendly_name": self.gcast.device.friendly_name,
                "is_active_input": True if self.gcast.status.is_active_input else False,
                "is_stand_by":  True if self.gcast.status.is_stand_by else False,
                # "{0:.2f}".format(cast.status.volume_level),
                "volume_level":  int(self.gcast.status.volume_level*100),
                "volume_muted": self.gcast.status.volume_muted,
                "app_id": self.gcast.status.app_id,
                "icon_url": self.gcast.status.icon_url,
                "display_name": self.gcast.status.display_name if self.gcast.status.display_name is not None else globals.DEFAULT_NODISPLAY,
                "status_text": self.gcast.status.status_text if self.gcast.status.status_text != "" else globals.DEFAULT_NOSTATUS,
                "is_busy": not self.gcast.is_idle,
                "title": playStatus.title,
                "album_artist": playStatus.album_artist,
                "metadata_type": playStatus.metadata_type,
                "album_name": playStatus.album_name,
                # "current_time" : '{0:.0f}'.format(playStatus.current_time),
                "current_time": '{0:.0f}'.format(playStatus.adjusted_current_time),
                "artist": playStatus.artist,
                'series_title': playStatus.series_title,
                'season': playStatus.season,
                'episode': playStatus.episode,
                "image": img,
                "stream_type": playStatus.stream_type,
                "track": playStatus.track,
                "player_state": playStatus.player_state,
                "supported_media_commands": playStatus.supported_media_commands,
                "supports_pause": playStatus.supports_pause,
                # '{0:.0f}'.format(playStatus.duration),
                "duration": playStatus.duration,
                "content_type": playStatus.content_type,
                "idle_reason": playStatus.idle_reason
            }
            globals.JEEDOM_COM.send_change_immediate(
                {'uuid':  uuid, 'nowplaying': data})
        else:
            data = {
                "uuid": uuid,
                "online": False, "friendly_name": "",
                "is_active_input": False, "is_stand_by":  False,
                "app_id": "", "icon_url": "",
                "display_name": globals.DEFAULT_NODISPLAY,
                "status_text": globals.DEFAULT_NOSTATUS,
                "is_busy": False, "title": "",
                "album_artist": "", "metadata_type": "",
                "album_name": "", "current_time": 0,
                "artist": "", "image": None,
                "series_title": "", "season": "", "episode": "",
                "stream_type": "", "track": "",
                "player_state": "", "supported_media_commands": 0,
                "supports_pause": "", "duration": 0,
                'content_type': "", "idle_reason": ""
            }
            globals.JEEDOM_COM.send_change_immediate(
                {'uuid':  uuid, 'nowplaying': data})


# -------------------------------
# main method to manage actions
# -------------------------------
def action_handler(message):
    rootcmd = message['cmd']
    uuid = message['device']['uuid']
    srcuuid = uuid

    if uuid in globals.KNOWN_DEVICES and uuid in globals.GCAST_DEVICES and rootcmd == "action":
        hascallback = False
        callback = ''
        if 'callback' in message['device']:
            hascallback = message['device']['callback'] if True is not None else False
            callback = message['device']['callback'] if message['device']['callback'] is not None else ''

        source = ''
        if 'source' in message['device']:
            source = message['device']['source']

        commandlist = message['command']
        if not isinstance(commandlist, list):
            commandlist = [commandlist]

        for command in commandlist:
            uuid = srcuuid

            if 'broadcast' in command:
                broadcastList = command['broadcast']
                if broadcastList == 'all':
                    uuidlist = []
                    for broadcastuuid in globals.GCAST_DEVICES:
                        if not globals.GCAST_DEVICES[broadcastuuid].is_castgroup:
                            uuidlist.append(broadcastuuid)
                else:
                    uuidlist = broadcastList.split(',')
                for newUuid in uuidlist:
                    newcmd = command.copy()
                    del newcmd['broadcast']
                    newMessage = {
                        'cmd': 'action',
                        'delegated': True,
                        'device': {'uuid': newUuid, 'source': message['device']['source']},
                        'command': newcmd
                    }
                    logging.debug(
                        "ACTION------DELEGATED command to other uuid : " + newUuid)
                    thread.start_new_thread(action_handler, (newMessage,))
                continue

            if 'uuid' in command:
                if 'nothread' in command and command['uuid'] in globals.GCAST_DEVICES:
                    uuid = command['uuid']
                    logging.debug(
                        "ACTION------Changing uuid to run in sequence in this tread : " + uuid)
                else:
                    newUuid = command['uuid']
                    del command['uuid']
                    newMessage = {
                        'cmd': 'action',
                        'delegated': True,
                        'device': {'uuid': newUuid, 'source': message['device']['source']},
                        'command': command
                    }
                    logging.debug(
                        "ACTION------DELEGATED command to other uuid : " + newUuid)
                    thread.start_new_thread(action_handler, (newMessage,))
                    continue

            if 'storecmd' in command:
                storecmd = command.copy()
                del storecmd['storecmd']
                jcast = globals.GCAST_DEVICES[uuid]
                if jcast.is_castgroup is False:
                    if 'app' in command and command['app'] in ['media', 'plex', 'web', 'backdrop', 'spotify', 'youtube']:
                        jcast.savePreviousPlayerCmd(storecmd)
                        logging.debug(
                            "ACTION STORECMD------Storing command for later resume.")
                    else:
                        logging.debug(
                            "ACTION STORECMD------Not possible for this kind of action !")
                else:
                    logging.debug(
                        "ACTION STORECMD------Not possible for cast group !:")
                continue

            cmd = 'NONE'
            if 'cmd' in command:
                cmd = command['cmd']
            app = 'none'
            if 'app' in command:
                app = command['app']
            appid = ''
            if 'appid' in command:
                appid = command['appid']
            value = None
            if 'value' in command:
                value = command['value']
            if 'v' in command:
                value = command['v']
            sleep = 0
            if 'sleep' in command:
                sleep = float(command['sleep'])
            sleepbefore = 0
            if 'sleepbefore' in command:
                sleepbefore = float(command['sleepbefore'])
            vol = None
            if 'vol' in command:
                try:
                    vol = int(command['vol'])
                    if not (0 < vol <= 100) or command['vol'] == '':
                        vol = None
                except Exception:
                    vol = None

            # specific parameters for apps
            quit_app_before = True
            if 'quit_app_before' in command:
                quit_app_before = True if command['quit_app_before'] else False
            quit = False
            if 'quit' in command:
                quit = True if command['quit'] else False
            # force_register = False
            # if 'force_register' in command:
            #     force_register = True if command['force_register'] else False
            wait = 2
            if 'wait' in command:
                wait = int(command['wait']
                           ) if command['wait'].isnumeric() else 2

            if app == 'tts':
                cmd = 'tts'
                app = 'media'

            needSendStatus = True
            fallbackMode = True
            logging.debug("ACTION------ " + rootcmd + " - " +
                          cmd + ' - ' + uuid + ' - ' + str(value) + ' - ' + app)

            if sleepbefore > 0:
                time.sleep(sleepbefore)

            jcast = globals.GCAST_DEVICES[uuid]
            gcast = jcast.gcast
            try:
                jcast.applaunch_callback_reset()
                if app == 'media':    # app=media|cmd=play_media|value=http://bit.ly/2JzYtfX,video/mp4,Mon film
                    if cmd == 'NONE':
                        cmd = 'play_media'
                    possibleCmd = ['play_media']
                    if cmd in possibleCmd and value is not None:
                        if 'offset' in command and float(command['offset']) > 0 and 'current_time' not in value:
                            value = value + ',current_time:' + \
                                str(command['offset'])
                        if 'live' in command and 'stream_type' not in value:
                            if int(command['live']) == 1:
                                value = value + ",stream_type:'LIVE'"
                            else:
                                del command['live']
                        forceplay = 0
                        if 'forceplay' in command:
                            try:
                                forceplay = float(command['forceplay'])
                            except Exception:
                                forceplay = 2.0
                            del command['forceplay']

                        value = value.replace('h:/', 'http://')
                        value = value.replace('hs:/', 'https://')
                        value = value.replace(
                            'local://', globals.JEEDOM_WEB+'/plugins/googlecast/'+globals.localmedia_folder+'/')
                        value = value.replace(
                            'logo://', globals.JEEDOM_WEB+'/plugins/googlecast/desktop/images/')
                        fallbackMode = False
                        player = jcast.loadPlayer(
                            'media', {'quitapp': quit_app_before})
                        eval('player.' + cmd +
                             '(' + gcast_prepareAppParam(value) + ')')
                        jcast.savePreviousPlayerCmd(command)
                        if forceplay > 0.0:
                            time.sleep(forceplay)
                            # logging.debug("FORCEPLAY------ ")
                            player.play()

                elif app == 'web':    # app=web|cmd=load_url|value=https://news.google.com,True,5
                    if cmd == 'NONE':
                        cmd = 'load_url'
                    possibleCmd = ['load_url']
                    if cmd in possibleCmd:
                        fallbackMode = False
                        player = jcast.loadPlayer(
                            app, {'quitapp': quit_app_before})
                        value = value.replace('h:/', 'http://')
                        value = value.replace('hs:/', 'https://')
                        eval('player.' + cmd +
                             '(' + gcast_prepareAppParam(value) + ')')
                        jcast.savePreviousPlayerCmd(command)

                elif app == 'youtube':  # app=youtube|cmd=play_video|value=fra4QBLF3GU
                    # possibleCmd = ['play_video', 'start_new_session', 'add_to_queue', 'update_screen_id', 'clear_playlist', 'play', 'stop', 'pause']
                    possibleCmd = ['play_video', 'add_to_queue',
                                   'play_next', 'remove_video']
                    if cmd in possibleCmd:
                        fallbackMode = False
                        if jcast.support_video is True:
                            player = jcast.loadPlayer(
                                app, {'quitapp': quit_app_before, 'wait': wait})
                            eval('player.' + cmd +
                                 '(' + gcast_prepareAppParam(value) + ')')
                            if cmd == 'play_video':
                                jcast.savePreviousPlayerCmd(command)
                        else:
                            logging.error(
                                "ACTION------ YouTube not availble on Google Cast Audio")

                elif app == 'spotify':  # app=spotify|cmd=launch_app|user=XXXXXX|pass=YYYY|value
                    if cmd == 'NONE':
                        cmd = 'play_media'
                    possibleCmd = ['play_media']
                    if cmd == 'play_media':
                        fallbackMode = False

                        wptoken = None
                        if 'user' in command and 'pass' in command:
                            username = command['user']
                            password = command['pass']
                            wptoken = stoken.SpotifyWpToken(username, password)

                        if 'token' in command:
                            token = command['token']

                        keepGoing = True
                        if value is None:
                            logging.error(
                                "ACTION------ Missing content id for spotify")
                            keepGoing = False
                        if token is None:
                            logging.error(
                                "ACTION------ Missing token paramaters for spotify")
                            keepGoing = False

                        if keepGoing is True:
                            player = jcast.loadPlayer(
                                app, {'quitapp': quit_app_before, 'wait': wait})
                            if wptoken is None:
                                player.launch_app(token)
                            else:
                                time.sleep(1)
                                player.launch_app(wptoken.value)

                            spotifyClient = spotipy.Spotify(auth=token)
                            time.sleep(1)

                            value = value.replace('spotify:', '')
                            trycount = 0
                            success = False
                            devicefound = False
                            while trycount < 4:
                                if devicefound is False:
                                    devices_available = spotifyClient.devices()
                                    device_id = None
                                    for device in devices_available['devices']:
                                        logging.debug(
                                            "ACTION------Spotify registered device : " + str(device['name']))
                                        if device['name'] == jcast.device.friendly_name:
                                            device_id = device['id']
                                            break

                                if device_id is not None:
                                    devicefound = True
                                    try:
                                        logging.debug(
                                            "ACTION------Spotify device found !")

                                        if value == 'recent':
                                            recentlyPlayed = spotifyClient.current_user_recently_played(
                                                limit=1)
                                            if len(recentlyPlayed['items']) > 0:
                                                value = recentlyPlayed['items'][0]['track']['uri']
                                                value = value.replace(
                                                    'spotify:', '')
                                                logging.debug(
                                                    "ACTION------Spotify recently played : " + value)
                                            # logging.debug("ACTION------Spotify recently played : " + str(recentlyPlayed))
                                        elif 'track' not in value:   # album or playlist
                                            spotifyClient.start_playback(
                                                device_id=device_id, context_uri='spotify:'+value)
                                        else:  # track
                                            spotifyClient.start_playback(
                                                device_id=device_id, uris=['spotify:'+value])
                                        success = True
                                        break
                                    except Exception as e:
                                        trycount = trycount+1
                                        logging.debug(
                                            "ACTION------Spotify error : %s" % str(e))
                                        # logging.debug(traceback.format_exc())
                                        gcast.media_controller.stop()
                                        time.sleep(1)
                                else:
                                    logging.debug(
                                        "ACTION------Spotify : device not found, wait for spotify to set an id...")
                                    device_id = player.wait()
                                    logging.debug(
                                        "ACTION------Spotify : device not found, returned this new id : " + str(device_id))
                                    trycount = trycount+1

                            if success is True:
                                jcast.savePreviousPlayerCmd(command)
                            else:
                                if devicefound is False:
                                    logging.error(
                                        "ACTION------ Spotify : device not found ! Have you added the cast device using Spotify phone application ?")
                                else:
                                    logging.error(
                                        "ACTION------ Spotify : Starting spotify failed !")
                                break

                elif app == 'backdrop':  # also called backdrop
                    if jcast.support_video is True:
                        fallbackMode = False
                        gcast.start_app('E8C28D3C')
                        jcast.savePreviousPlayerCmd(command)
                    else:
                        logging.error(
                            "ACTION------ Backdrop not availble on Google Cast Audio")

                elif app == 'plex':            # app=plex|cmd=pause
                    quit_app_before = False
                    if cmd == 'NONE':
                        cmd = 'play_media'
                    possibleCmd = ['play_media', 'play',
                                   'stop', 'pause', 'next', 'previous']
                    if cmd in possibleCmd:
                        fallbackMode = False

                        player = jcast.loadPlayer(
                            app, {'quitapp': quit_app_before, 'wait': wait})
                        # player.namespace = 'urn:x-cast:com.google.cast.sse'

                        if cmd == 'play_media':
                            serverurl = None
                            if 'server' in command:
                                serverurl = command['server']
                            username = None
                            password = None
                            if 'user' in command and 'pass' in command:
                                username = command['user']
                                password = command['pass']
                            token = None
                            if 'token' in command:
                                token = command['token']
                            type = 'audio'
                            if 'type' in command:
                                type = command['type']
                            if jcast.support_video is False and type == 'video':
                                type = 'audio'
                            offset = 0
                            if 'offset' in command:
                                offset = int(command['offset'])
                            shuffle = 0
                            if 'shuffle' in command:
                                shuffle = int(command['shuffle'])
                            repeat = 0
                            if 'repeat' in command:
                                repeat = int(command['repeat'])

                            keepGoing = True
                            if serverurl is None:
                                logging.error(
                                    "ACTION------ Missing server paramater for plex")
                                keepGoing = False
                            if token is None and (username is None or password is None):
                                logging.error(
                                    "ACTION------ Missing token or user/pass paramaters for plex")
                                keepGoing = False

                            if keepGoing is True:
                                is_resume = False
                                if 'resume_plexitem' in command:
                                    is_resume = True

                                if not is_resume:
                                    if username is not None and password is not None and token is None:
                                        account = MyPlexAccount(
                                            username, password)
                                        for res in account.resources():
                                            logging.debug(
                                                "PLEX------ Resource available : " + str(res.name))
                                        plexServer = account.resource(
                                            serverurl).connect()
                                        logging.debug(
                                            "PLEX------ Token for reuse : " + str(account._token))
                                    else:
                                        plexServer = PlexServer(
                                            serverurl, token)
                                    plexmedia = plexServer.search(
                                        value, limit=1)
                                    if len(plexmedia) > 0:
                                        command['resume_plexitem'] = plexmedia[0]
                                        command['resume_plexserver'] = plexServer
                                        player.play_media(plexmedia[0], plexServer, {
                                                          'offset': offset, 'type': type, 'shuffle': shuffle, 'repeat': repeat})
                                        jcast.savePreviousPlayerCmd(command)
                                    else:
                                        logging.debug(
                                            "PLEX------No media found for query " + value)

                                else:
                                    logging.debug(
                                        "PLEX------Restoring from previous call")
                                    player.play_media(command['resume_plexitem'], command['resume_plexserver'], {
                                                      'offset': offset, 'type': type, 'shuffle': shuffle, 'repeat': repeat})
                                    jcast.savePreviousPlayerCmd(command)

                        else:
                            eval('player.' + cmd + '()')

                if fallbackMode is False:
                    logging.debug("ACTION------Playing action " +
                                  cmd + ' for application ' + app)
            except Exception as e:
                logging.error("ACTION------Error while playing action " +
                              cmd + " on app " + app+" : %s" % str(e))
                logging.debug(traceback.format_exc())
                jcast.manage_exceptions(str(e))

            # low level google cast actions
            if fallbackMode is True:
                try:
                    if cmd == 'refresh':
                        logging.debug("ACTION------Refresh action")
                        time.sleep(1)
                        fallbackMode = False
                    elif cmd == 'reboot':
                        logging.debug("ACTION------Reboot action")
                        gcast.reboot()
                        time.sleep(5)
                        fallbackMode = False
                    elif cmd == 'volume_up':
                        logging.debug("ACTION------Volumme up action")
                        gcast.volume_up(value if value is not None else 0.1)
                        fallbackMode = False
                    elif cmd == 'volume_down':
                        logging.debug("ACTION------Volume down action")
                        gcast.volume_down(value if value is not None else 0.1)
                        fallbackMode = False
                    elif cmd == 'volume_set':
                        logging.debug("ACTION------Volume set action")
                        gcast.set_volume(int(value)/100)
                        fallbackMode = False
                    elif cmd == 'start_app':
                        logging.debug("ACTION------Start app action")
                        appToLaunch = '' if value is None else value
                        if appid != '':
                            appToLaunch = appid
                        gcast.start_app(appToLaunch)
                        fallbackMode = False
                    elif cmd == 'quit_app':
                        logging.debug("ACTION------Quit app action")
                        gcast.quit_app()
                        jcast.resetPlayer()
                        fallbackMode = False
                    elif cmd == 'mute_on':
                        logging.debug("ACTION------Mute on action")
                        gcast.set_volume_muted(True)
                        fallbackMode = False
                    elif cmd == 'mute_off':
                        logging.debug("ACTION------Mute off action")
                        gcast.set_volume_muted(False)
                        fallbackMode = False
                    elif cmd == 'turn_on':
                        logging.debug("ACTION------Turn on action")
                        if gcast.is_idle:
                            if gcast.app_id is not None:
                                # Quit the previous app before starting splash screen
                                gcast.quit_app()
                            # The only way we can turn the Chromecast is on is by launching an app
                            url = generate_warmupnotif()
                            gcast.play_media(url, "BUFFERED")
                        fallbackMode = False
                    elif cmd == 'turn_off':
                        logging.debug("ACTION------Turn off action")
                        gcast.quit_app()
                        jcast.resetPlayer()
                        fallbackMode = False

                    elif cmd == 'notif':
                        logging.debug("ACTION------NOTIF action")
                        forcevol = False
                        if 'forcevol' in command:
                            forcevol = True
                        type = 'audio'
                        if 'type' in command:
                            type = command['type']
                        resume = True
                        if 'noresume' in command:
                            resume = False
                        streamtype = 'LIVE'
                        if 'buffered' in command and command['buffered'] == '1':
                            streamtype = 'BUFFERED'
                        durationparam = 0
                        if 'duration' in command:
                            durationparam = float(command['duration'])
                        curvol = jcast.getCurrentVolume()
                        if curvol == vol and not forcevol:
                            vol = None
                        need_duration = False
                        if vol is not None or quit is True or resume is True:
                            need_duration = True

                        url, duration, mp3filename = get_notif_data(
                            value, need_duration)
                        if durationparam > 0:
                            duration = durationparam
                        if url is not None:
                            thumb = globals.JEEDOM_WEB + '/plugins/googlecast/desktop/images/notif.png'
                            jcast.disable_notif = True
                            if resume:
                                jcast.prepareTTSplay()
                            player = jcast.loadPlayer(
                                'media', {'quitapp': False, 'wait': 0})
                            if vol is not None:
                                gcast.media_controller.pause()
                                time.sleep(0.1)
                                gcast.set_volume(vol/100)
                                time.sleep(0.1)
                            if type == 'audio':
                                player.play_media(
                                    url, 'audio/mp3', 'NOTIF', thumb=thumb, stream_type=streamtype)
                            else:
                                player.play_media(
                                    url, 'video/mp4', 'NOTIF', thumb=thumb, stream_type=streamtype)
                            player.block_until_active(timeout=2)
                            jcast.disable_notif = False
                            sleep_done = False
                            if vol is not None:
                                time.sleep(duration+1)
                                if sleep > 0:
                                    time.sleep(sleep)
                                    sleep = 0
                                gcast.set_volume(curvol/100)
                                vol = None
                                sleep_done = True
                            if durationparam > 0:
                                if sleep_done is False:
                                    time.sleep(duration)
                                    sleep_done = True
                                gcast.media_controller.stop()
                            if quit:
                                if vol is None:
                                    time.sleep(duration+1)
                                    sleep_done = True
                                if sleep > 0:
                                    time.sleep(sleep)
                                    sleep = 0
                                gcast.quit_app()
                            if resume:
                                if vol is None and sleep_done is False:
                                    time.sleep(duration+1)
                                if sleep > 0:
                                    time.sleep(sleep)
                                    sleep = 0
                                forceapplaunch = False
                                if 'forceapplaunch' in command:
                                    forceapplaunch = True
                                resumeOk = manage_resume(
                                    uuid, message['device']['source'], forceapplaunch, 'NOTIF')
                                if resumeOk is False:
                                    logging.debug(
                                        "NOTIF------Resume is not possible!")
                        else:
                            logging.debug(
                                "NOTIF------Error while getting local media !")
                            sendErrorDeviceStatus(uuid, 'ERROR')

                        fallbackMode = False

                    elif cmd == 'tts':
                        logging.debug("ACTION------TTS action")
                        lang = globals.tts_language
                        if 'lang' in command:
                            lang = command['lang']
                        engine = globals.tts_engine
                        if 'engine' in command:
                            engine = command['engine']
                        speed = globals.tts_speed
                        if 'speed' in command:
                            speed = float(command['speed'])
                        forcetts = False
                        if 'forcetts' in command:
                            forcetts = True
                        silence = 300
                        if 'silence' in command:
                            silence = int(command['silence'])
                        elif jcast.is_castgroup is True:
                            silence = 1000
                        generateonly = False
                        if 'generateonly' in command:
                            generateonly = True
                        quality = '32k'
                        if 'highquality' in command and command['highquality'] == '1':
                            quality = '64k'
                        streamtype = 'LIVE'
                        if 'buffered' in command and command['buffered'] == '1':
                            streamtype = 'BUFFERED'
                        forcevol = False
                        if 'forcevol' in command:
                            forcevol = True
                        resume = True
                        if 'noresume' in command:
                            resume = False
                        ttsparams = None
                        if 'voice' in command or 'usessml' in command:
                            ttsparams = {}
                            if 'voice' in command:
                                ttsparams['voice'] = command['voice']
                            if 'usessml' in command:
                                ttsparams['usessml'] = command['usessml']
                            if 'pitch' in command:
                                ttsparams['pitch'] = command['pitch']
                            if 'volgain' in command:
                                ttsparams['volgain'] = command['volgain']

                        curvol = jcast.getCurrentVolume()
                        if curvol == vol and not forcevol:
                            vol = None
                        need_duration = False
                        if vol is not None or quit is True or resume is True:
                            need_duration = True

                        if generateonly is False:
                            url, duration, mp3filename = get_tts_data(
                                value, lang, engine, speed, forcetts, need_duration, silence, quality, ttsparams)
                            if url is not None:
                                thumb = globals.JEEDOM_WEB + '/plugins/googlecast/desktop/images/tts.png'
                                jcast.disable_notif = True
                                if resume:
                                    jcast.prepareTTSplay()
                                player = jcast.loadPlayer(
                                    'media', {'quitapp': False, 'wait': 0})
                                if vol is not None:
                                    gcast.media_controller.pause()
                                    time.sleep(0.1)
                                    gcast.set_volume(vol/100)
                                    time.sleep(0.1)
                                player.play_media(
                                    url, 'audio/mp3', 'TTS', thumb=thumb, stream_type=streamtype)
                                player.block_until_active(timeout=2)
                                jcast.disable_notif = False
                                vol_done = False
                                if vol is not None:
                                    time.sleep(duration+(silence/1000)+1)
                                    if sleep > 0:
                                        time.sleep(sleep)
                                        sleep = 0
                                    gcast.set_volume(curvol/100)
                                    vol = None
                                    vol_done = True

                                if quit:
                                    if vol is None:
                                        time.sleep(duration+(silence/1000)+1)
                                    if sleep > 0:
                                        time.sleep(sleep)
                                        sleep = 0
                                    gcast.quit_app()
                                if resume:
                                    if vol is None and vol_done is False:
                                        time.sleep(duration+(silence/1000)+1)
                                    if sleep > 0:
                                        time.sleep(sleep)
                                        sleep = 0
                                    forceapplaunch = False
                                    if 'forceapplaunch' in command:
                                        forceapplaunch = True

                                    resumeOk = manage_resume(
                                        uuid, message['device']['source'], forceapplaunch, 'TTS')
                                    if resumeOk is False:
                                        logging.debug(
                                            "TTS------Resume is not possible!")
                            else:
                                logging.debug(
                                    "TTS------File generation failed !")
                                sendErrorDeviceStatus(uuid, 'ERROR')
                        else:
                            logging.error(
                                "TTS------Only generating TTS file without playing")
                            get_tts_data(value, lang, engine, speed,
                                         forcetts, False, silence)
                            needSendStatus = False

                        fallbackMode = False
                except Exception as e:
                    logging.error("ACTION------Error while playing action " +
                                  cmd + " on low level commands : %s" % str(e))
                    sendErrorDeviceStatus(uuid, 'ERROR')
                    logging.debug(traceback.format_exc())
                    jcast.manage_exceptions(str(e))
                    fallbackMode is False

            # media/application controler level Google Cast actions
            if fallbackMode is True:
                try:
                    player = gcast.media_controller
                    if cmd == 'play':
                        logging.debug("ACTION------Play action")
                        player.play()
                        fallbackMode = False
                    elif cmd == 'stop':
                        logging.debug("ACTION------Stop action")
                        player.stop()
                        fallbackMode = False
                    elif cmd == 'rewind':
                        logging.debug("ACTION------Rewind action")
                        player.rewind()
                        fallbackMode = False
                    elif cmd == 'skip':
                        logging.debug("ACTION------Skip action")
                        # player.skip()
                        player.queue_next()
                        fallbackMode = False
                    elif cmd == 'next':
                        logging.debug("ACTION------Next action")
                        player.queue_next()
                        fallbackMode = False
                    elif cmd == 'prev':
                        logging.debug("ACTION------Previous action")
                        player.queue_prev()
                        fallbackMode = False
                    elif cmd == 'seek':
                        logging.debug("ACTION------Seek action")
                        if value is not None and '+' in value:
                            player.seek(jcast.media_current_time +
                                        float(value.replace('+', '')))
                        elif value is not None and '-' in value:
                            player.seek(jcast.media_current_time -
                                        float(value.replace('-', '')))
                        else:
                            player.seek(0 if value is None else float(value))
                        fallbackMode = False
                    elif cmd == 'pause':
                        logging.debug("ACTION------Stop action")
                        player.pause()
                        fallbackMode = False
                    elif cmd == 'resume':
                        forceapplaunch = False
                        if 'forceapplaunch' in command:
                            forceapplaunch = True
                        offset = None
                        if 'offset' in command:
                            offset = command['offset']
                        status = None
                        if 'status' in command:
                            status = command['status']
                        jcast.prepareForceResume(status, offset)
                        resumeOk = manage_resume(
                            uuid, message['device']['source'], forceapplaunch, 'ACTION')
                        if resumeOk is False:
                            logging.debug(
                                "ACTION------Resume is not possible!")
                        else:
                            logging.debug("ACTION------Resume OK")
                        fallbackMode = False
                    elif cmd == "warmupnotif":
                        jcast.prepareWarumplay()
                        url = generate_warmupnotif()
                        if url is not None:
                            jcast.disable_notif = True
                            player = jcast.loadPlayer(
                                'media', {'quitapp': False, 'wait': 0})
                            player.play_media(
                                url, 'audio/mp3', 'WARMUP', stream_type="LIVE")
                            player.block_until_active(timeout=3)
                            time.sleep(0.3)
                            # gcast.quit_app()
                            jcast.disable_notif = False
                        fallbackMode = False
                    elif cmd == 'sleep':
                        logging.debug("ACTION------Sleep")
                        time.sleep(float(value))
                        fallbackMode = False
                except Exception as e:
                    logging.error("ACTION------Error while playing action " +
                                  cmd + " on default media controler : %s" % str(e))
                    logging.debug(traceback.format_exc())
                    jcast.manage_exceptions(str(e))

            if vol is not None and uuid in globals.GCAST_DEVICES:
                logging.debug("ACTION------SET VOLUME OPTION")
                time.sleep(0.1)
                try:
                    gcast.set_volume(vol/100)
                except Exception as e:
                    logging.error(
                        "ACTION------SET VOLUME OPTION ERROR : %s" % str(e))
                    jcast.manage_exceptions(str(e))

            if fallbackMode is True:
                logging.debug("ACTION------Action " + cmd +
                              " not implemented or exception occured !")
                sendErrorDeviceStatus(uuid, 'CMD UNKNOWN')

            if sleep > 0:
                time.sleep(sleep)

            if needSendStatus and uuid in globals.GCAST_DEVICES:
                time.sleep(0.1)
                jcast.sendDeviceStatus()

        if hascallback:
            callbackret = manage_callback(uuid, callback)
            callbackmsg = {'callback': 1, 'source': source,
                           'uuid': uuid, 'result': callbackret}
            globals.JEEDOM_COM.send_change_immediate(callbackmsg)

    else:
        logging.debug("ACTION------ Device not connected !")
        sendErrorDeviceStatus(uuid, 'NOT CONNECTED')
        return False

    return True


def manage_callback(uuid, callback_type):
    # todo things for callback before returning value
    return True


def generate_warmupnotif():
    logging.debug("WARMUPNOTIF------ Checking file generation...")
    cachepath = globals.tts_cachefolderweb
    symlinkpath = globals.tts_cachefoldertmp
    try:
        os.stat(symlinkpath)
    except Exception:
        os.mkdir(symlinkpath)
    try:
        os.stat(cachepath)
    except Exception:
        os.symlink(symlinkpath, cachepath)
    try:
        file = hashlib.md5('WARMUPNOTIF'.encode('utf-8')).hexdigest()
        filenamemp3 = os.path.join(cachepath, file+'.mp3')
        if not os.path.isfile(filenamemp3):
            warmup = AudioSegment.silent(duration=80)
            warmup.export(filenamemp3, format="mp3", bitrate='32k', tags={
                          'albumartist': 'Jeedom', 'title': 'WARMUPNOTIF', 'artist': 'Jeedom'}, parameters=["-ac", "1", "-ar", "24000"])
        else:
            try:   # touch file so cleaning can be done later based on date
                if os.stat(filenamemp3).st_mtime < (time.time() - 86400):
                    os.utime(filenamemp3, None)
            except Exception:
                logging.debug("WARMUPNOTIF------Touching file failed !")
                pass
        urltoplay = globals.JEEDOM_WEB+'/plugins/googlecast/tmp/'+file+'.mp3'
    except Exception as e:
        logging.error(
            "WARMUPNOTIF------Exception while generating warmupnotif file : %s" % str(e))
        urltoplay = None
    return urltoplay


def manage_resume(uuid, source='googlecast', forceapplaunch=False, origin='TTS'):
    jcast = globals.GCAST_DEVICES[uuid]
    prevcommand = jcast.getPreviousPlayerCmd(
        forceapplaunch, True if origin != 'ACTION' else False)
    if prevcommand is not None:
        newMessage = {
            'cmd': 'action',
            'delegated': True,
            'resume': True,
            'device': {'uuid': uuid, 'source': source},
            'command': prevcommand
        }
        logging.debug("RESUME------DELEGATED RESUME AFTER " +
                      origin+" for uuid : " + uuid)
        time.sleep(0.3)
        jcast.resetPreviousPlayerCmd()
        thread.start_new_thread(action_handler, (newMessage,))
        return True
    return False


def get_tts_data(text, language, engine, speed, forcetts, calcduration, silence=300, quality='32k', ttsparams=None):
    srclanguage = language
    if engine == 'gttsapidev':  # removed this engine but failover to gttsapi
        engine = 'gttsapi'
    if not globals.tts_gapi_haskey and engine == 'gttsapi':
        logging.error(
            "CMD-TTS------No key provided, fallback to picotts engine")
        engine = 'picotts'
        speed = 1

    if globals.tts_cacheenabled is False:
        try:
            if os.path.exists(globals.tts_cachefoldertmp):
                shutil.rmtree(globals.tts_cachefoldertmp)
        except Exception:
            pass
    cachepath = globals.tts_cachefolderweb
    # manage cache in ram memory
    symlinkpath = globals.tts_cachefoldertmp
    ttstext = text
    try:
        os.stat(symlinkpath)
    except Exception:
        os.mkdir(symlinkpath)
    try:
        os.stat(cachepath)
    except Exception:
        os.symlink(symlinkpath, cachepath)
    try:
        rawfilename = text+engine+language+str(silence)
        if engine == 'gttsapi':      # add exception when using gttsapi engine to use voice over language
            if ttsparams is not None and 'voice' in ttsparams:
                rawfilename = text+engine+ttsparams['voice']+str(silence)
            else:
                rawfilename = text+engine+globals.tts_gapi_voice+str(silence)
        file = hashlib.md5(rawfilename.encode('utf-8')).hexdigest()
        filenamemp3 = os.path.join(cachepath, file+'.mp3')
        logging.debug("CMD-TTS------TTS Filename hexdigest : " +
                      file + "  ("+rawfilename+")")
        if not os.path.isfile(filenamemp3) or forcetts is True:
            logging.debug("CMD-TTS------Generating file")
            samplerate = '24000'
            if quality != '32k':
                samplerate = '44100'

            if engine == 'gtts':
                speed = float(speed)
                language = language.split('-')[0]
                try:
                    tts = gTTS(text=ttstext, lang=language)
                    tts.save(filenamemp3)
                    if speed != 1:
                        try:
                            os.system('sox '+filenamemp3+' ' +
                                      filenamemp3 + 'tmp.mp3 tempo ' + str(speed))
                            os.remove(filenamemp3)
                            os.rename(filenamemp3+'tmp.mp3', filenamemp3)
                        except OSError:
                            pass
                    speech = AudioSegment.from_mp3(filenamemp3)
                    if silence > 0:
                        start_silence = AudioSegment.silent(duration=silence)
                        speech = start_silence + speech
                    speech.export(filenamemp3, format="mp3", bitrate=quality, tags={
                                  'albumartist': 'Jeedom', 'title': 'TTS', 'artist': 'Jeedom'}, parameters=["-ac", "1", "-ar", samplerate, "-vol", "200"])
                    duration_seconds = speech.duration_seconds
                except Exception as e:
                    if os.path.isfile(filenamemp3):
                        try:
                            os.remove(filenamemp3)
                        except OSError:
                            pass
                    logging.error(
                        "CMD-TTS------Google Translate API : Cannot connect to API - failover to picotts  (%s)" % str(e))
                    logging.debug(traceback.format_exc())
                    engine = 'picotts'
                    filenamemp3 = filenamemp3.replace(".mp3", "_failover.mp3")
                    file = file + '_failover'
                    language = srclanguage
                    speed = 1.2

            elif engine == 'gttsapi':
                ttsformat = 'text'
                voice = globals.tts_gapi_voice
                speed = float(speed) - 0.2
                pitch = 0.0
                volumegaindb = 0.0
                if ttsparams is not None:
                    if 'voice' in ttsparams:
                        voice = ttsparams['voice']
                    if 'pitch' in ttsparams:
                        pitch = float(ttsparams['pitch'])
                    if 'volgain' in ttsparams:
                        volumegaindb = float(ttsparams['volgain'])
                    if 'usessml' in ttsparams:
                        ttsformat = 'ssml'
                        ttstext = ttstext.replace('^', '=')
                        # ttstext = urllib.parse.quote_plus(ttstext)
                success = True
                try:
                    gctts = gcloudTTS(globals.tts_gapi_key)
                    rawttsdata = gctts.tts(
                        voice, voice[:5], ttstext, ttsformat, speed, pitch, volumegaindb, 'LINEAR16')
                except gcloudTTSError as e:
                    success = False
                    logging.error(
                        "CMD-TTS------Google Cloud TextToSpeech API Error :  %s" % str(e))
                except Exception:
                    success = False
                    logging.debug(
                        "CMD-TTS------Google Cloud TextToSpeech API : Unknown error")
                    logging.debug(traceback.format_exc())
                if success is True:
                    speech = AudioSegment(data=rawttsdata)
                    if silence > 0:
                        start_silence = AudioSegment.silent(duration=silence)
                        speech = start_silence + speech
                    # speech.export(filenamemp3, format="mp3", bitrate=quality, tags={'albumartist': 'Jeedom', 'title': 'TTS', 'artist':'Jeedom'}, parameters=["-ac", "1", "-ar", samplerate,"-vol", "200"])
                    speech.export(filenamemp3, format="mp3", tags={
                                  'albumartist': 'Jeedom', 'title': 'TTS', 'artist': 'Jeedom'}, parameters=["-ac", "1", "-vol", "200"])
                    duration_seconds = speech.duration_seconds
                else:
                    logging.error(
                        "CMD-TTS------Google Cloud TextToSpeech API : Error while using Google Cloud TextToSpeech API - failover to picotts")
                    engine = 'picotts'
                    filenamemp3 = filenamemp3.replace(".mp3", "_failover.mp3")
                    file = file + '_failover'
                    language = srclanguage
                    speed = 1.2

            elif engine == 'jeedomtts' or engine == 'ttswebserver':
                speed = float(speed)
                proxyttsfile = globals.JEEDOM_COM.proxytts(
                    engine, ttstext, {'language': language})
                if proxyttsfile is not None:
                    with open(filenamemp3, 'wb') as f:
                        f.write(proxyttsfile)
                    # if speed!=1:
                    #     try:
                    #         os.system('sox '+filenamemp3+' '+filenamemp3+ 'tmp.mp3 tempo ' +str(speed))
                    #         os.remove(filenamemp3)
                    #         os.rename(filenamemp3+'tmp.mp3', filenamemp3);
                    #     except OSError:
                    #         pass
                    speech = AudioSegment.from_mp3(filenamemp3)
                    if silence > 0:
                        start_silence = AudioSegment.silent(duration=silence)
                        speech = start_silence + speech
                    speech.export(filenamemp3, format="mp3", bitrate=quality, tags={
                                  'albumartist': 'Jeedom', 'title': 'TTS', 'artist': 'Jeedom'}, parameters=["-ac", "1", "-ar", samplerate, "-vol", "200"])
                    duration_seconds = speech.duration_seconds
                else:
                    logging.error(
                        "CMD-TTS------Jeedom TTS Proxy API : Cannot connect or incorrect output - failover to picotts")
                    engine = 'picotts'
                    filenamemp3 = filenamemp3.replace(".mp3", "_failover.mp3")
                    file = file + '_failover'
                    language = srclanguage
                    speed = 1.2

            if engine == 'picotts':
                speed = float(speed) - 0.2
                filename = os.path.join(cachepath, file+'.wav')
                # fix accent issue for picotts
                ttstext = ttstext.encode('utf-8').decode('ascii', 'ignore')
                os.system('pico2wave -l '+language+' -w ' +
                          filename + ' "' + ttstext + '"')
                speech = AudioSegment.from_wav(filename)
                if silence > 0:
                    start_silence = AudioSegment.silent(duration=silence)
                    speech = start_silence + speech
                speech.export(filenamemp3, format="mp3", bitrate=quality, tags={
                              'albumartist': 'Jeedom', 'title': 'TTS', 'artist': 'Jeedom'}, parameters=["-ac", "1", "-ar", samplerate, "-vol", "200"])
                duration_seconds = speech.duration_seconds
                if speed != 1:
                    try:
                        os.system('sox '+filenamemp3+' ' +
                                  filenamemp3 + 'tmp.mp3 tempo ' + str(speed))
                        os.remove(filenamemp3)
                        os.rename(filenamemp3+'tmp.mp3', filenamemp3)
                    except OSError:
                        pass
                try:
                    os.remove(filename)
                except OSError:
                    pass

            logging.debug("CMD-TTS------Sentence: '" + ttstext + "' (" +
                          engine+","+language+",speed:"+"{0:.2f}".format(speed)+")")

        else:
            logging.debug("CMD-TTS------Using from cache")
            if calcduration is True:
                try:
                    speech = AudioSegment.from_mp3(filenamemp3)
                    duration_seconds = speech.duration_seconds
                except Exception:
                    logging.error(
                        "CMD-TTS------Exception when trying to get duration. Will try to remove file to force generation next time...")
                    logging.debug(traceback.format_exc())
                    duration_seconds = 0
                    try:
                        os.remove(filenamemp3)
                    except Exception:
                        pass
            else:
                duration_seconds = 0
            logging.debug("CMD-TTS------Sentence: '" +
                          ttstext + "' ("+engine+","+language+")")

        try:   # touch file so cleaning can be done later based on date
            if os.stat(filenamemp3).st_mtime < (time.time() - 86400):
                os.utime(filenamemp3, None)
        except Exception:
            logging.debug("CMD-TTS------Touching file failed !")
            pass
        urltoplay = globals.JEEDOM_WEB+'/plugins/googlecast/tmp/'+file+'.mp3'
    except Exception as e:
        logging.error(
            "CMD-TTS------Exception while generating tts file : %s" % str(e))
        logging.debug(traceback.format_exc())
        urltoplay = None
        duration_seconds = 0
        filenamemp3 = None
    return urltoplay, duration_seconds, filenamemp3


def get_notif_data(mediafilename, calcduration):
    try:
        urltoplay = globals.JEEDOM_WEB+'/plugins/googlecast/' + \
            globals.localmedia_folder+'/'+mediafilename
        filename = os.path.join(globals.localmedia_fullpath, mediafilename)
        if os.path.isfile(filename):
            if calcduration:
                extension = os.path.splitext(filename)[1]
                if extension.lower() == '.mp3':
                    notifSound = AudioSegment.from_mp3(filename)
                else:
                    notifSound = AudioSegment.from_file(
                        filename,  extension.lower().replace('.', ''))
                duration_seconds = notifSound.duration_seconds
        else:
            logging.debug(
                "CMD-NOTIF------File doesn't exist (" + filename + ')')
            urltoplay = None
            duration_seconds = 0
            filename = None

    except Exception as e:
        logging.error("CMD-NOTIF------Error processing file  (%s)" % str(e))
        logging.debug(traceback.format_exc())
        urltoplay = None
        duration_seconds = 0
        filename = None
    logging.debug("CMD-NOTIF------NOTIF debug : " +
                  ('Unknown' if urltoplay is None else urltoplay) + ", duration: " + str(duration_seconds))
    return urltoplay, duration_seconds, filename


def logByTTS(text_id):
    lang = globals.tts_language
    engine = globals.tts_engine
    speed = globals.tts_speed
    if text_id == 'CMD_ERROR':
        text = "La commande n'a pas pu être lancée !"
    else:
        text = "Un erreur s'est produite !"
    url, duration, mp3filename = get_tts_data(
        text, lang, engine, speed, False, False, 300)
    thumb = globals.JEEDOM_WEB + '/plugins/googlecast/desktop/images/tts.png'
    jcast = None  # TODO: get googlecast device first
    player = jcast.loadPlayer('media', {'quitapp': False, 'wait': 0})
    player.play_media(url, 'audio/mp3', 'TTS', thumb=thumb, stream_type="LIVE")
    player.block_until_active(timeout=2)


def gcast_prepareAppParam(params):
    if params is None or params == '':
        return ''
    ret = ''
    s = [k for k in re.split("(,|\w*?:'.*?'|'.*?')", params)    # noqa: W605
         if k.strip() and k != ',']
    for p in s:
        p = p.strip()
        s2 = [k for k in re.split(
            "(:|'.*?'|http:.*|https:.*)", p) if k.strip() and k != ':']
        prefix = ''
        if len(s2) == 2:
            prefix = s2[0].strip() + '='
            p = s2[1].strip()
        if p.isnumeric():
            ret = ret + ',' + prefix + p
        elif p.lower() == 'true' or p.lower() == 'false' or p.lower() == 'none':
            ret = ret + ',' + prefix + p[0].upper()+p[1:]
        elif p.lower() == 't':
            ret = ret + ',' + prefix + 'True'
        elif p.lower() == 'f':
            ret = ret + ',' + prefix + 'False'
        else:
            # if starts already with simple quote
            if p.startswith("'") and p.endswith("'"):
                withoutQuote = p[1:-1].lower()
                if withoutQuote.isnumeric():
                    ret = ret + ',' + prefix + withoutQuote
                elif withoutQuote == 'true' or withoutQuote == 'false' or withoutQuote == 'none':
                    ret = ret + ',' + prefix + \
                        withoutQuote[0].upper()+withoutQuote[1:]
                else:
                    ret = ret + ',' + prefix + p
            else:
                ret = ret + ',' + prefix + '"' + p + '"'    # else add quotes
    retval = ret[1:].replace(')', '')
    logging.debug("PARAMPARSER---- Returned: " + str(retval))
    return retval


def start(cycle=2):
    jeedom_socket.open()
    logging.info(
        "GLOBAL------Socket started and waiting for messages from Jeedom...")
    # logging.info("GLOBAL------Waiting for messages...")
    thread.start_new_thread(read_socket, (globals.cycle_event,))
    globals.JEEDOM_COM.send_change_immediate(
        {'started': 1, 'source': globals.daemonname})
    try:
        generate_warmupnotif()
    except Exception:
        pass

    try:
        while not globals.IS_SHUTTINGDOWN:
            try:
                current_time = int(time.time())
                if globals.LEARN_MODE and (globals.LEARN_BEGIN+globals.LEARN_TIMEOUT) < current_time:
                    globals.LEARN_MODE = False
                    globals.ZEROCONF_RESTART = True
                    globals.SCAN_LAST = 0
                    logging.info(
                        'HEARTBEAT------Quitting learn mode (90s elapsed)')
                    globals.JEEDOM_COM.send_change_immediate(
                        {'learn_mode': 0, 'source': globals.daemonname})

                if (globals.LAST_BEAT + globals.HEARTBEAT_FREQUENCY/2) < current_time:
                    globals.JEEDOM_COM.send_change_immediate(
                        {'heartbeat': 1, 'source': globals.daemonname})
                    globals.LAST_BEAT = current_time

                if not globals.SCAN_PENDING:
                    if globals.LEARN_MODE:
                        thread.start_new_thread(scanner, ('learnmode',))
                    elif (current_time - globals.SCAN_LAST) > globals.SCAN_FREQUENCY:
                        thread.start_new_thread(scanner, ('schedule',))

                if (current_time - globals.NOWPLAYING_LAST) > globals.NOWPLAYING_FREQUENCY/2 and not globals.LEARN_MODE:
                    for uuid in globals.GCAST_DEVICES:
                        globals.GCAST_DEVICES[uuid].sendNowPlaying_heartbeat()
                    globals.NOWPLAYING_LAST = current_time

                time.sleep(cycle)

            except Exception:
                logging.error("GLOBAL------Exception on main loop")

    except KeyboardInterrupt:
        logging.error("GLOBAL------KeyboardInterrupt, shutdown")
        shutdown()


def read_socket(cycle):
    while not globals.IS_SHUTTINGDOWN:
        try:
            # global JEEDOM_SOCKET_MESSAGE
            if not JEEDOM_SOCKET_MESSAGE.empty():
                logging.debug(
                    "SOCKET-READ------Message received in socket JEEDOM_SOCKET_MESSAGE")
                message = json.loads(JEEDOM_SOCKET_MESSAGE.get())
                if message['apikey'] != globals.apikey:
                    logging.error(
                        "SOCKET-READ------Invalid apikey from socket : " + str(message))
                    return
                logging.debug(
                    'SOCKET-READ------Received command from jeedom : '+str(message['cmd']))
                if message['cmd'] == 'add':
                    logging.debug(
                        'SOCKET-READ------Add device : '+str(message['device']))
                    if 'uuid' in message['device']:
                        uuid = message['device']['uuid']
                        if uuid not in globals.KNOWN_DEVICES:
                            globals.KNOWN_DEVICES[uuid] = {
                                'uuid': uuid, 'status': {},
                                'typemsg': 'info',
                                'lastOnline': 0, 'online': False,
                                'lastSent': 0, 'lastOfflineSent': 0,
                                'options': message['device']['options']
                            }
                            globals.SCAN_LAST = 0
                            globals.ZEROCONF_RESTART = True
                elif message['cmd'] == 'remove':
                    logging.debug(
                        'SOCKET-READ------Remove device : '+str(message['device']))
                    if 'uuid' in message['device']:
                        uuid = message['device']['uuid']
                        if uuid in globals.NOWPLAYING_DEVICES:
                            del globals.NOWPLAYING_DEVICES[uuid]
                        if uuid in globals.GCAST_DEVICES:
                            globals.GCAST_DEVICES[uuid].disconnect()
                        if uuid in globals.KNOWN_DEVICES:
                            del globals.KNOWN_DEVICES[uuid]
                        globals.SCAN_LAST = 0
                elif message['cmd'] == 'nowplaying':
                    if 'uuid' in message:
                        uuid = message['uuid']
                        globals.NOWPLAYING_DEVICES[uuid] = int(time.time())
                        if uuid in globals.GCAST_DEVICES:
                            logging.debug(
                                'SOCKET-READ------Now playing activated for '+uuid)
                            globals.GCAST_DEVICES[uuid].startNowPlaying()
                        else:
                            logging.debug(
                                'SOCKET-READ------Now playing for ' + uuid + ' not activated because is offline')
                elif message['cmd'] == 'learnin':
                    logging.info('SOCKET-READ------Enter in learn mode')
                    globals.LEARN_MODE = True
                    globals.ZEROCONF_RESTART = True
                    globals.LEARN_BEGIN = int(time.time())
                    globals.JEEDOM_COM.send_change_immediate(
                        {'learn_mode': 1, 'source': globals.daemonname})
                elif message['cmd'] == 'learnout':
                    logging.info('SOCKET-READ------Leave learn mode')
                    globals.LEARN_MODE = False
                    globals.JEEDOM_COM.send_change_immediate(
                        {'learn_mode': 0, 'source': globals.daemonname})
                elif message['cmd'] == 'refresh':
                    logging.debug(
                        'SOCKET-READ------Attempt a refresh on a device')
                    uuid = message['device']['uuid']
                    if uuid in globals.GCAST_DEVICES:
                        globals.GCAST_DEVICES[uuid].sendDeviceStatus()
                elif message['cmd'] == 'cleanttscache':
                    logging.debug('SOCKET-READ------Clean TTS cache')
                    if 'days' in message:
                        cleanCache(int(message['days']))
                    else:
                        cleanCache()
                elif message['cmd'] == 'refreshall':
                    logging.debug(
                        'SOCKET-READ------Attempt a refresh on all devices')
                    for uuid in globals.GCAST_DEVICES:
                        globals.GCAST_DEVICES[uuid].sendDeviceStatus()
                elif message['cmd'] == 'action':
                    logging.debug(
                        'SOCKET-READ------Attempt an action on a device')
                    thread.start_new_thread(action_handler, (message,))
                    logging.debug('SOCKET-READ------Action Thread Launched')
                elif message['cmd'] == 'logdebug':
                    logging.info(
                        'SOCKET-READ------Passage du demon en mode debug force')
                    log = logging.getLogger()
                    for hdlr in log.handlers[:]:
                        log.removeHandler(hdlr)
                    jeedom_utils.set_log_level('debug')
                    logging.debug('SOCKET-READ------<----- La preuve ;)')
                elif message['cmd'] == 'lognormal':
                    logging.info(
                        'SOCKET-READ------Passage du demon en mode de log initial')
                    log = logging.getLogger()
                    for hdlr in log.handlers[:]:
                        log.removeHandler(hdlr)
                    jeedom_utils.set_log_level(globals.log_level)
                elif message['cmd'] == 'stop':
                    logging.info(
                        'SOCKET-READ------Arret du demon sur demande socket')
                    globals.JEEDOM_COM.send_change_immediate(
                        {'learn_mode': 0, 'source': globals.daemonname})
                    time.sleep(2)
                    shutdown()
        except Exception as e:
            logging.error("SOCKET-READ------Exception on socket : %s" % str(e))
            logging.debug(traceback.format_exc())
        time.sleep(cycle)


def zeroconfMonitoring_start():
    try:
        logging.debug("ZEROCONF------ Start zeroconf monitoring thread...")
        globals.NETDISCOVERY_PENDING = True

        def ccdiscovery_callback(chromecast):
            cast = JeedomChromeCast(chromecast, scan_mode=True)
            uuid = cast.uuid
            logging.debug(
                "ZEROCONF------ Signal detected from chromecast on zeroconf network : " + cast.friendly_name + "")
            if uuid not in globals.GCAST_DEVICES:
                logging.debug(
                    "ZEROCONF------ Signal from chromecast will be processed soon (" + cast.friendly_name + ")")
                globals.SCAN_LAST = 0
                globals.NETDISCOVERY_DEVICES[cast.uuid] = cast

        globals.NETDISCOVERY_STOPFN = pychromecast.get_chromecasts(
            tries=1, retry_wait=2, timeout=globals.SCAN_TIMEOUT, blocking=False, callback=ccdiscovery_callback)
    except Exception as e:
        logging.error(
            "ZEROCONF START------Exception on zeroconf monitoring : %s" % str(e))
        logging.debug(traceback.format_exc())


def zeroconfMonitoring_stop():
    logging.debug("ZEROCONF------ Stopping zeroconf monitoring thread...")
    try:
        globals.NETDISCOVERY_PENDING = False
        if globals.NETDISCOVERY_STOPFN is not None:
            globals.NETDISCOVERY_STOPFN()
        # globals.NETDISCOVERY_DEVICES = {}

    except Exception as e:
        # globals.NETDISCOVERY_DEVICES = {}
        logging.error(
            "ZEROCONF STOP------Exception on netdiscovery : %s" % str(e))
        logging.debug(traceback.format_exc())


def scanner(name='UNKNOWN SOURCE'):
    try:
        logging.debug("SCANNER------ Start scanning... (" + name + ")")
        globals.SCAN_PENDING = True
        show_memory_usage()

        scanForced = False
        discoveryMode = False
        if (int(time.time())-globals.DISCOVERY_LAST) > globals.DISCOVERY_FREQUENCY:
            scanForced = True
            discoveryMode = True

        if globals.ZEROCONF_RESTART is True:
            globals.ZEROCONF_RESTART = False
            scanForced = True

        if scanForced is True:
            zeroconfMonitoring_stop()
            zeroconfMonitoring_start()
            time.sleep(1)

        # go through discovered devices in case new appeared
        tobecleaned = []
        for uuid in globals.NETDISCOVERY_DEVICES:
            cast = globals.NETDISCOVERY_DEVICES[uuid]
            uuid = cast.uuid
            current_time = int(time.time())

            if uuid in globals.KNOWN_DEVICES:
                globals.KNOWN_DEVICES[uuid]['online'] = True
                globals.KNOWN_DEVICES[uuid]['lastScan'] = current_time
                globals.KNOWN_DEVICES[uuid]["lastOnline"] = current_time

                if uuid not in globals.GCAST_DEVICES:
                    logging.info(
                        "SCANNER------ Adding chromecast : " + cast.friendly_name)
                    globals.GCAST_DEVICES[uuid] = JeedomChromeCast(
                        cast.gcast, globals.KNOWN_DEVICES[uuid]["options"])

                if uuid in globals.NOWPLAYING_DEVICES:
                    if (current_time-globals.NOWPLAYING_DEVICES[uuid]) > globals.NOWPLAYING_TIMEOUT:
                        del globals.NOWPLAYING_DEVICES[uuid]
                        globals.GCAST_DEVICES[uuid].stopNowPlaying()
                    else:
                        globals.GCAST_DEVICES[uuid].startNowPlaying()

                globals.GCAST_DEVICES[uuid].sendDeviceStatusIfNew()

            else:
                if globals.LEARN_MODE:
                    data = {'friendly_name': cast.friendly_name,
                            'uuid': uuid, 'lastScan': current_time}
                    data['def'] = cast.getDefinition()
                    data['status'] = cast.getStatus()
                    data['learn'] = 1
                    logging.info("SCANNER------ LEARN MODE : New device : " +
                                 uuid + ' (' + data["friendly_name"] + ')')
                    globals.JEEDOM_COM.add_changes('devices::'+uuid, data)

                elif (current_time-globals.DISCOVERY_LAST) > globals.DISCOVERY_FREQUENCY:
                    logging.debug("SCANNER------ DISCOVERY MODE : New device : " +
                                  uuid + ' (' + cast.friendly_name + ')')
                    globals.JEEDOM_COM.send_change_immediate(
                        {'discovery': 1, 'uuid': uuid, 'friendly_name': cast.friendly_name})

                tobecleaned.append(uuid)

        # memory cleaning
        for uuid in list(globals.NETDISCOVERY_DEVICES.keys()):
            if uuid in tobecleaned:
                globals.NETDISCOVERY_DEVICES[uuid].disconnect()
            if uuid in globals.NETDISCOVERY_DEVICES:
                del globals.NETDISCOVERY_DEVICES[uuid]
        del tobecleaned

        # loop through all known devices to find those not connected
        for known in globals.KNOWN_DEVICES:
            current_time = int(time.time())
            is_not_available = True

            if known in globals.GCAST_DEVICES:
                if globals.GCAST_DEVICES[known].is_connected is True:
                    is_not_available = False
                else:
                    # something went wrong so disconnect completely
                    globals.GCAST_DEVICES[known].disconnect()

            if is_not_available is True:
                logging.debug("SCANNER------No connection to device " + known)
                if globals.KNOWN_DEVICES[known]['online'] is True:
                    logging.info(
                        "SCANNER------Connection lost to device " + known)

                globals.KNOWN_DEVICES[known]['lastScan'] = current_time
                if (globals.KNOWN_DEVICES[known]['online'] is True or (current_time-globals.KNOWN_DEVICES[known]['lastOfflineSent']) > globals.LOSTDEVICE_RESENDNOTIFDELAY):
                    globals.KNOWN_DEVICES[known]['online'] = False
                    globals.KNOWN_DEVICES[known]['lastOfflineSent'] = current_time
                    globals.KNOWN_DEVICES[known]['status'] = {
                        "uuid": known,
                        "is_stand_by": False, "is_active_input": False,
                        "display_name": globals.DEFAULT_NODISPLAY, "status_text": globals.DEFAULT_NOSTATUS,
                        "app_id": "", "icon_url": "", "is_busy": False,
                        "title": "", "artist": "", "series_title": "", "stream_type": "", "player_state": "",
                    }
                    # globals.JEEDOM_COM.add_changes('devices::'+known, globals.KNOWN_DEVICES[known])
                    globals.JEEDOM_COM.send_change_immediate_device(
                        known, globals.KNOWN_DEVICES[known])
                    globals.KNOWN_DEVICES[known]['lastSent'] = current_time
                    if known in globals.NOWPLAYING_DEVICES:
                        del globals.NOWPLAYING_DEVICES[known]
                        data = {
                            "uuid": known,
                            "online": False, "friendly_name": "",
                            "is_active_input": False, "is_stand_by": False,
                            "display_name": globals.DEFAULT_NODISPLAY, "status_text": globals.DEFAULT_NOSTATUS,
                            "app_id": "", "icon_url": "", "is_busy": False, "title": "",
                            "album_artist": "", "metadata_type": "",
                            "album_name": "", "current_time": 0,
                            "artist": "", "image": None,
                            "series_title": "", "season": "", "episode": "",
                            "stream_type": "", "track": "",
                            "player_state": "", "supported_media_commands": 0,
                            "supports_pause": "", "duration": 0,
                            "content_type": "", "idle_reason": ""
                        }
                        globals.JEEDOM_COM.send_change_immediate(
                            {'uuid':  known, 'nowplaying': data})

            else:
                globals.KNOWN_DEVICES[known]["lastScan"] = current_time

        if discoveryMode is True:
            globals.DISCOVERY_LAST = int(time.time())

    except Exception as e:
        logging.error("SCANNER------Exception on scanner : %s" % str(e))
        logging.debug(traceback.format_exc())

    globals.SCAN_LAST = int(time.time())
    globals.SCAN_PENDING = False


def sendErrorDeviceStatus(uuid, message, online=True):
    # send to plugin
    errorstatus = {
        "uuid": uuid, "display_name": message, "status_text": message
    }
    globals.JEEDOM_COM.add_changes(
        'devices::'+uuid, {'uuid': uuid, 'typemsg': 'error', 'status': errorstatus})
    # send to now playing widget
    data = {
        "uuid": uuid, "online": online,
        "is_active_input": False, "is_stand_by": False,
        "display_name": message, "status_text": message, "player_state": message,
        "title": "", "album_artist": "",
        "album_name": "", "current_time": 0,
        "artist": "", "image": None,
        'series_title': "", 'season': "", 'episode': "",
        "stream_type": "", "track": ""
    }
    globals.JEEDOM_COM.send_change_immediate(
        {'uuid':  uuid, 'nowplaying': data})


memory_last_use = 0
memory_last_time = int(time.time())
memory_first_time = int(time.time())


def show_memory_usage():
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        usage = resource.getrusage(resource.RUSAGE_SELF)
        try:
            global memory_last_use, memory_last_time, memory_first_time
            ru_utime = getattr(usage, 'ru_utime')
            ru_stime = getattr(usage, 'ru_stime')
            ru_maxrss = getattr(usage, 'ru_maxrss')
            total = ru_utime+ru_stime
            curtime = int(time.time())
            timedif = curtime-memory_last_time
            timediftotal = curtime-memory_first_time
            logging.debug(' MEMORY---- Total CPU time used : %.3fs (%.2f%%)  |  Last %i sec : %.3fs (%.2f%%)  | Memory : %s Mo' % (
                total, total/timediftotal*100, timedif, total-memory_last_use, (total-memory_last_use)/timedif*100, int(round(ru_maxrss/1000))))
            memory_last_use = total
            memory_last_time = curtime
        except Exception:
            pass


def cleanCache(nbDays=0):
    if nbDays == 0:    # clean entire directory including containing folder
        try:
            if os.path.exists(globals.tts_cachefoldertmp):
                shutil.rmtree(globals.tts_cachefoldertmp)
            generate_warmupnotif()
        except Exception:
            logging.warn(
                "CLEAN CACHE------Error while cleaning cache entirely")
            pass
    else:              # clean only files older than X days
        now = time.time()
        path = globals.tts_cachefoldertmp
        try:
            for f in os.listdir(path):
                logging.debug("CLEAN CACHE------Age for " + f + " is " + str(
                    int((now - (os.stat(os.path.join(path, f)).st_mtime)) / 86400)) + " days")
                if os.stat(os.path.join(path, f)).st_mtime < (now - (nbDays * 86400)):
                    os.remove(os.path.join(path, f))
                    logging.debug("CLEAN CACHE------Removed " + f +
                                  " due to expiration (" + str(nbDays) + " days)")
            generate_warmupnotif()
        except Exception:
            logging.warn(
                "CLEAN CACHE------Error while cleaning cache based on date number")
            pass


def handler(signum=None, frame=None):
    logging.debug("GLOBAL------Signal %i caught, exiting..." % int(signum))
    shutdown()


def shutdown():
    logging.debug("GLOBAL------Shutdown")
    globals.IS_SHUTTINGDOWN = True
    logging.debug("GLOBAL------Removing PID file " + str(globals.pidfile))
    try:
        os.remove(globals.pidfile)
    except Exception:
        pass
    try:
        globals.JEEDOM_COM.send_change_immediate(
            {'stopped': 1, 'source': globals.daemonname})
        zeroconfMonitoring_stop()
        for uuid in globals.GCAST_DEVICES:
            globals.GCAST_DEVICES[uuid].disconnect()
        time.sleep(0.5)
        jeedom_socket.close()
        logging.debug("GLOBAL------Shutdown completed !")
    except Exception:
        pass
    logging.debug("Exit 0")
    sys.stdout.flush()
    os._exit(0)


# -------------------------------------------
# ------ PROGRAM STARTS HERE ----------------
# -------------------------------------------
parser = argparse.ArgumentParser(
    description='GoogleCast Daemon for Jeedom plugin')
parser.add_argument("--loglevel", help="Log Level for the daemon", type=str)
parser.add_argument("--pidfile", help="PID filname", type=str)
parser.add_argument("--callback", help="Callback url", type=str)
parser.add_argument("--apikey", help="Jeedom API key", type=str)
parser.add_argument("--ttsweb", help="Jeedom Web server (for TTS)", type=str)
parser.add_argument("--ttslang", help="Default TTS language", type=str)
parser.add_argument("--ttsengine", help="Default TTS engine", type=str)
parser.add_argument("--ttscache", help="Use cache", type=str)
parser.add_argument("--ttsspeed", help="TTS speech speed", type=str)
parser.add_argument("--ttsgapikey", help="TTS Google Speech API Key", type=str)
parser.add_argument(
    "--gcttsvoice", help="TTS Google Speech API default voice", type=str)
parser.add_argument("--socketport", help="Socket Port", type=str)
parser.add_argument("--sockethost", help="Socket Host", type=str)
parser.add_argument("--daemonname", help="Daemon Name", type=str)
parser.add_argument("--scantimeout", help="GoogleCast scan timeout", type=str)
parser.add_argument("--scanfrequency", help="Frequency for scan", type=str)
parser.add_argument("--cycle", help="Cycle to send/receive event", type=str)
parser.add_argument("--cyclemain", help="Cycle for main loop", type=str)
parser.add_argument(
    "--cyclefactor", help="Factor for event cycles (default=1)", type=str)
parser.add_argument("--defaultstatus",
                    help="Returned display string", type=str)
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
    globals.tts_cacheenabled = False if int(args.ttscache) == 0 else True
if args.ttsgapikey:
    globals.tts_gapi_key = args.ttsgapikey
    if globals.tts_gapi_key != 'none':
        globals.tts_gapi_haskey = True
if args.gcttsvoice:
    globals.tts_gapi_voice = args.gcttsvoice
if args.cycle:
    globals.cycle_event = float(args.cycle)
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

if globals.cycle_factor == 0:
    globals.cycle_factor = 1
globals.NOWPLAYING_FREQUENCY = int(
    globals.NOWPLAYING_FREQUENCY*globals.cycle_factor)
globals.SCAN_FREQUENCY = int(globals.SCAN_FREQUENCY*globals.cycle_factor)

globals.socketport = int(globals.socketport)
globals.cycle_event = float(globals.cycle_event*globals.cycle_factor)
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
# logging.info('GLOBAL------Apikey : '+str(globals.apikey))
logging.info('GLOBAL------Apikey : *******************************')
logging.info('GLOBAL------TTS Jeedom server : '+str(globals.JEEDOM_WEB))
logging.info('GLOBAL------TTS default language : '+str(globals.tts_language))
logging.info('GLOBAL------TTS default engine : '+str(globals.tts_engine))
logging.info('GLOBAL------TTS default speech speed : '+str(globals.tts_speed))
if globals.tts_gapi_haskey:
    logging.info('GLOBAL------TTS Google Speech API Key (optional) : OK')
    logging.info('GLOBAL------TTS Google Speech API Voice (optional) : ' +
                 str(globals.tts_gapi_voice))
else:
    logging.info('GLOBAL------TTS Google API Key (optional) : NOK')
logging.info('GLOBAL------Cache status : '+str(globals.tts_cacheenabled))
logging.info('GLOBAL------Callback : '+str(globals.callback))
logging.info('GLOBAL------Event cycle : '+str(globals.cycle_event))
logging.info('GLOBAL------Main cycle : '+str(globals.cycle_main))
logging.info('GLOBAL------Default status message : ' +
             str(globals.DEFAULT_NOSTATUS))
logging.info('-----------------------------------------------------')

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)

try:
    jeedom_utils.write_pid(str(globals.pidfile))
    globals.JEEDOM_COM = jeedom_com(
        apikey=globals.apikey, url=globals.callback, cycle=globals.cycle_event)
    if not globals.JEEDOM_COM.test():
        logging.error(
            'GLOBAL------Network communication issues. Please fix your Jeedom network configuration.')
        shutdown()
    else:
        logging.info('GLOBAL------Network communication to jeedom OK.')
    jeedom_socket = jeedom_socket(
        port=globals.socketport, address=globals.sockethost)
    start(globals.cycle_main)

except Exception as e:
    logging.error('GLOBAL------Fatal error : '+str(e))
    logging.debug(traceback.format_exc())
    shutdown()
