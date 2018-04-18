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

import subprocess
import os,re
import logging
import sys
import argparse
import time
from datetime import datetime
import signal
import json
import traceback
import select

import globals
from threading import Timer
import _thread as thread

try:
	import pychromecast.pychromecast as pychromecast
	import pychromecast.pychromecast.controllers.dashcast as dashcast
	import pychromecast.pychromecast.controllers.youtube as youtube
	import pychromecast.pychromecast.controllers.plex as plex
	import pychromecast.pychromecast.controllers.spotify as Spotify
except ImportError:
	print("Error: importing pychromecast module")
	sys.exit(1)

try:
	from jeedom.jeedom import *
except ImportError:
	print("Error: importing module from jeedom folder")
	sys.exit(1)


class JeedomChromeCast :
	def __init__(self, gcast):
		self.gcast = gcast
		self.gcast.media_controller.register_status_listener(self)
		self.gcast.register_status_listener(self)
		self.previous_status = {"uuid" : self.uuid, "online" : False}
		self.gcast.register_connection_listener(self)
		self.now_playing = False
		self.online = True
		if self.gcast.device.cast_type != 'cast' and self.friendly_name not in pychromecast.IGNORE_CEC:
			pychromecast.IGNORE_CEC.append(self.gcast.device.friendly_name)

	@property
	def device(self):
		return self.gcast.device

	@property
	def uuid(self):
		return str(self.gcast.device.uuid)

	def friendly_name(self):
		return self.gcast.device.friendly_name

	def startNowPlaying(self):
		if self.now_playing == False and self.online == True:
			logging.debug("JEEDOMCHROMECAST------ Starting monitoring of " + self.uuid)
			self.now_playing = True
			thread.start_new_thread(self.thread_nowlaying, ("nowPlayingTHread",))

	def stopNowPlaying(self):
		logging.debug("JEEDOMCHROMECAST------ Stopping monitoring of " + self.uuid)
		self.now_playing = False

	def new_cast_status(self, new_status):
		#logging.debug("JEEDOMCHROMECAST------ Status " + str(new_status))
		self._internal_refresh_status(False)

	def new_connection_status(self, new_status):
		logging.debug("JEEDOMCHROMECAST------ Connection " + str(new_status.status))
		if new_status.status == "DISCONNECTED" :
			self.disconnect()
		else :
			self.online = True

	def sendDeviceStatus(self, _force=True):
		try :
			self.gcast.media_controller.update_status()
			time.sleep(0.2)
		except Exception :
			pass
		self._internal_refresh_status(_force)

	def disconnect(self):
		#if self.online == True :
		self.online = False
		if self.now_playing :
			self._internal_send_now_playing()
			time.sleep(1)
		self.now_playing = False
		if self.uuid in globals.GCAST_DEVICES :
			del globals.GCAST_DEVICES[self.uuid]
		self.gcast.disconnect()

	def sendDeviceStatusIfNew(self):
		self.sendDeviceStatus(False)

	def loadControler(self, controler, _quit_app_before=True, _force_register=False):
		if self.gcast.socket_client :
			if controler.namespace in self.gcast.socket_client._handlers and not _force_register :
				logging.debug("JEEDOMCHROMECAST------ Loading controller from memory " + str(controler.namespace))
				return self.gcast.socket_client._handlers[controler.namespace]
			else :
				logging.debug("JEEDOMCHROMECAST------ Initiating controler " + str(controler.namespace))
				self.gcast.register_handler(controler)
				time.sleep(1)
				if not self.gcast.is_idle and _quit_app_before:
					self.gcast.quit_app()
					time.sleep(3)
				return controler

	def _internal_refresh_status(self,_force = False):
		uuid = str(self.device.uuid)
		status = self._internal_get_status()
		if _force or self._internal_status_different(status)  :
			logging.debug("Detected changes in status of " +self.device.friendly_name)
			globals.KNOWN_DEVICES[uuid]['status'] = status
			self.previous_status = status
			globals.KNOWN_DEVICES[uuid]['online'] = self.online
			globals.JEEDOM_COM.add_changes('devices::'+uuid,globals.KNOWN_DEVICES[uuid])
			globals.KNOWN_DEVICES[uuid]['lastSent'] = int(time.time())

	def _internal_get_status(self):
		if self.gcast.status!=None :
			self.online = True
			uuid = self.uuid
			status = {
				"uuid" : uuid,
				"friendly_name" : self.gcast.device.friendly_name,
				"is_active_input" : True if self.gcast.status.is_active_input else False,
				"is_stand_by" :  True if self.gcast.status.is_stand_by else False,
				"volume_level" : int(self.gcast.status.volume_level*100),
				"volume_muted" : self.gcast.status.volume_muted,
				"app_id" : self.gcast.status.app_id,
				"display_name" : self.gcast.status.display_name,
				"status_text" : self.gcast.status.status_text,
				"is_busy" : not self.gcast.is_idle,
			}
			return status
		else :
			self.online = False
			return {
				"uuid" : self.uuid,
				"friendly_name" : "", "is_stand_by" :  False, "is_active_input" : False,
				"app_id" : "",	"display_name" : "", "status_text" : "",
				"status_text" : "", "is_busy" : False,
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
		uuid = str(self.gcast.device.uuid)
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


	def thread_nowlaying(self, name):
		logging.debug(" JEEDOMCHROMECAST------Starting NowPlaying thread for " + self.uuid)
		delay = 0
		firstTime = True
		while self.now_playing :
			if delay >= globals.NOWPLAYING_FREQUENCY or firstTime :
				try :
					self.gcast.media_controller.update_status(callback_function_param=self._internal_send_now_playing)
				except Exception :
					self._internal_send_now_playing()
					pass
				firstTime = False
				delay = 0
			delay = delay + 1
			time.sleep(1)

		logging.debug(" JEEDOMCHROMECAST------Closing NowPlaying thread for " + self.uuid)

	def _internal_send_now_playing(self, message=None):
		#logging.debug(" JEEDOMCHROMECAST------crap message " + str(crap))
		uuid = self.uuid
		if self.gcast.status:
			playStatus = self.gcast.media_controller.status
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
				"display_name" : self.gcast.status.display_name,
				"status_text" : self.gcast.status.status_text,
				"is_busy" : not self.gcast.is_idle,
				"title" : playStatus.title,
				"album_artist" : playStatus.album_artist,
				"metadata_type" : playStatus.metadata_type,
				"album_name" : playStatus.album_name,
				"current_time" : '{0:.0f}'.format(playStatus.current_time),
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
				'duration': playStatus.duration, #'{0:.0f}'.format(playStatus.duration),
				'content_type': playStatus.content_type,
				'idle_reason': playStatus.idle_reason
			}
			globals.JEEDOM_COM.send_change_immediate({'uuid' :  uuid, 'nowplaying':data});

		else :
			data = {
				"uuid" : uuid,
				"online" : False, "friendly_name" : "",
				"is_active_input" : False, "is_stand_by" :  False,
				"app_id" : "",	"display_name" : "", "status_text" : "",
				"is_busy" : False,	"title" : "",
				"album_artist" : "","metadata_type" : "",
				"album_name" : "",	"current_time" : 0,
				"artist" : "",	"image" : None,
				'series_title': "",  'season': "", 'episode': "",
				"stream_type" : "",	"track" : "",
				"player_state" : "","supported_media_commands" : 0,
				"supports_pause" : "",	'duration': 0,
				'content_type': "",	'idle_reason': ""
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

		gcast = globals.GCAST_DEVICES[uuid].gcast
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
		elif cmd == 'play':
			logging.debug("ACTION------Play action")
			gcast.media_controller.play()
		elif cmd == 'stop':
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
			gcast.media_controller.seek(0 if value==None else value)
		elif cmd == 'start_app':
			logging.debug("ACTION------Stop action")
			gcast.start_app('' if value==None else value)
		elif cmd == 'quit_app':
			logging.debug("ACTION------Stop action")
			gcast.quit_app()
		elif cmd == 'pause':
			logging.debug("ACTION------Stop action")
			gcast.media_controller.pause()
		elif cmd == 'mute_on':
			logging.debug("ACTION------Mute on action")
			gcast.set_volume_muted(True)
		elif cmd == 'mute_off':
			logging.debug("ACTION------Mute off action")
			gcast.set_volume_muted(False)
		elif app != None:
			logging.debug("ACTION------Plyaing action " + cmd + ' for application ' + app)
			try:
				quit_app_before=True
				if 'quit_app_before' in message['command'] :
					quit_app_before = True if message['command']['quit_app_before'] else False
				force_register=False
				if 'force_register' in message['command'] :
					force_register = True if message['command']['force_register'] else False

				if app == 'web':	# app=web|cmd=load_url|value=https://news.google.com,True,5
					force_register=True
					possibleCmd = ['load_url']
					if cmd in possibleCmd :
						player = dashcast.DashCastController()
						player = globals.GCAST_DEVICES[uuid].loadControler(player, quit_app_before, force_register)
						eval( 'player.' + cmd + '('+ gcast_prepareAppParam(value) +')' )
				elif app == 'youtube':  # app=youtube|cmd=play_video|value=fra4QBLF3GU
					if gcast.device.cast_type == 'cast' :
						possibleCmd = ['play_video', 'add_to_queue', 'update_screen_id', 'clear_playlist']
						if cmd in possibleCmd :
							player = youtube.YouTubeController()
							player = globals.GCAST_DEVICES[uuid].loadControler(player, quit_app_before, force_register)
							eval( 'player.' + cmd + '('+ gcast_prepareAppParam(value) +')' )
					else :
						logging.error("ACTION------ YouTube not availble on Chromecast Audio")
				elif app == 'spotify':  # app=spotify|cmd=launch_app|token=XXXXXX
					possibleCmd = ['launch_app']
					if cmd in possibleCmd :
						if 'token' not in message['command'] :
							logging.error("ACTION------ Token missing for Spotify")
						else :
							player = spotify.SpotifyController(message['command']['token'])
							player = globals.GCAST_DEVICES[uuid].loadControler(player, quit_app_before, force_register)
							player.launch_app()
				elif app == 'backdrop':  # also called backdrop
					if gcast.device.cast_type == 'cast' :
						gcast.start_app('E8C28D3C')
					else :
						logging.error("ACTION------ Backdrop not availble on Chromecast Audio")
				elif app == 'plex':			# app=plex|cmd=pause
					quit_app_before=False
					possibleCmd = ['play', 'stop', 'pause']
					if cmd in possibleCmd :
						player = plex.PlexController()
						player = globals.GCAST_DEVICES[uuid].loadControler(player, quit_app_before, force_register)
						time.sleep(1)
						eval( 'player.' + cmd + '('+ gcast_prepareAppParam(value) +')' )
				else : # media		# app=media|cmd=play_media|value=http://bit.ly/2JzYtfX,video/mp4,Mon film
					possibleCmd = ['play', 'stop', 'pause', 'play_media']
					eval( 'gcast.media_controller.' + cmd + '('+ gcast_prepareAppParam(value) +')' )
			except Exception as e:
				logging.error("ACTION------Error while playing "+app+" : %s" % str(e))

		else:
			logging.debug("ACTION------NOT IMPLEMENTED : " + cmd)

		if needSendStatus :
			globals.GCAST_DEVICES[uuid].sendDeviceStatus()
	return


def gcast_prepareAppParam(params):
	if params is None or params == '':
		return ''
	ret = ''
	s = params.split(",")
	for p in s :
		p = p.strip()
		s2 = p.split("=")
		prefix = ''
		if len(s2)==2 :
			prefix = s2[0].strip() + '='
			p = s2[1].strip()

		if p.isnumeric() :
			ret = ret + ',' + prefix + p
		elif p == 'True' or p == 'False' or p == 'None' :
			ret = ret + ',' + prefix + p
		else :
			if p.startswith( "'" ) :	# if starts already with simple quote
				ret = ret + ',' + prefix + p
			else :
				ret = ret + ',' + prefix + '"'+ p +'"'	# else add quotes
	return ret[1:]


def read_device(name):
	while 1:
		now = datetime.datetime.utcnow()
		try:
			for uuid in list(globals.KNOWN_DEVICES):
				if (int(time.time())-globals.KNOWN_DEVICES[uuid]['lastSent']) > globals.READ_FREQUENCY:
					globals.JEEDOM_COM.add_changes('devices::'+uuid, globals.KNOWN_DEVICES[uuid])
					globals.KNOWN_DEVICES[uuid]['lastSent'] = int(time.time())
		except Exception as e:
			logging.error("READER------Exception on read device : %s" % str(e))
		time.sleep(10)


def listen():
	jeedom_socket.open()
	logging.info("GLOBAL------Start listening...")
	logging.info("GLOBAL------Socket started...")
	thread.start_new_thread( read_socket, ('socket',))
	logging.debug('GLOBAL------Heartbeat Thread Launched')
	thread.start_new_thread( heartbeat_handler, (19,))
	globals.JEEDOM_COM.send_change_immediate({'started' : 1,'source' : globals.daemonname});

	try:
		while 1:
			try:

				if not globals.SCAN_PENDING and globals.LEARN_MODE :
					thread.start_new_thread( scanner, ('scan learn',))

				if not globals.SCAN_PENDING and (int(time.time()) - globals.SCAN_LAST) > globals.SCAN_FREQUENCY :
					thread.start_new_thread( scanner, ('scanner',))

				while globals.SCAN_PENDING:
					time.sleep(1)

				if globals.LEARN_MODE :
					time.sleep(0.2)
				else :
					time.sleep(3)

			except Exception as e:
				logging.warning("GLOBAL------Exception on scanner")

	except KeyboardInterrupt:
		logging.error("GLOBAL------KeyboardInterrupt, shutdown")
		shutdown()


def read_socket(name):
	while 1:
		try:
			global JEEDOM_SOCKET_MESSAGE
			if not JEEDOM_SOCKET_MESSAGE.empty():
				logging.debug("SOCKET-READ------Message received in socket JEEDOM_SOCKET_MESSAGE")
				#message = json.loads(jeedom_utils.stripped(JEEDOM_SOCKET_MESSAGE.get()))
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
								'lastSent': 0, 'lastOfflineSent': 0
							}
							globals.SCAN_LAST = 0
				elif message['cmd'] == 'remove':
					logging.debug('SOCKET-READ------Remove device : '+str(message['device']))
					if 'uuid' in message['device']:
						uuid = message['device']['uuid']
						if uuid in globals.KNOWN_DEVICES :
							del globals.KNOWN_DEVICES[uuid]
						if uuid in globals.GCAST_DEVICES :
							globals.GCAST_DEVICES[uuid].disconnect()
							del globals.GCAST_DEVICES[uuid]
						if uuid in globals.NOWPLAYING_DEVICES :
							del globals.NOWPLAYING_DEVICES[uuid]
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
					thread.start_new_thread( read_device, ('action',))
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
		time.sleep(0.3)


def scanner(name):
	try:
		logging.debug("SCANNER------ Start scanning...")
		globals.SCAN_PENDING = True
		DISCOVER_DEVICES = {}

		scanForced = False
		for known in globals.KNOWN_DEVICES :
			if known not in globals.GCAST_DEVICES :
				scanForced = scanForced or True

		if scanForced==True or globals.LEARN_MODE==True:
			logging.debug("SCANNER------ Looking for chromecasts on network...")
			casts = pychromecast.get_chromecasts(tries=1, retry_wait=2, timeout=10)
		else :
			logging.debug("SCANNER------ No need to scan, everything is there")
			casts = list(globals.GCAST_DEVICES.values())

		for cast in casts :
			uuid = str(cast.device.uuid)
			DISCOVER_DEVICES[uuid] = {'friendly_name':cast.device.friendly_name, 'uuid': uuid, 'lastScan': int(time.time()) }

			# starting event thread
			if uuid in globals.KNOWN_DEVICES :
				globals.KNOWN_DEVICES[uuid]['uuid'] = uuid
				globals.KNOWN_DEVICES[uuid]['online'] = True
				globals.KNOWN_DEVICES[uuid]['lastScan'] = int(time.time())
				globals.KNOWN_DEVICES[uuid]["lastOnline"] = int(time.time())

				if uuid not in globals.GCAST_DEVICES :
					logging.info("SCANNER------ Detected chromecast : " + cast.device.friendly_name)
					globals.GCAST_DEVICES[uuid] = JeedomChromeCast(cast)

				if uuid in globals.NOWPLAYING_DEVICES :
					if (int(time.time())-globals.NOWPLAYING_DEVICES[uuid]) > globals.NOWPLAYING_TIMEOUT :
						del globals.NOWPLAYING_DEVICES[uuid]
						globals.GCAST_DEVICES[uuid].stopNowPlaying()
					else :
						globals.GCAST_DEVICES[uuid].startNowPlaying()

				globals.GCAST_DEVICES[uuid].sendDeviceStatusIfNew()

			else :
				if globals.LEARN_MODE :
					data = {}
					jcast = JeedomChromeCast(cast)
					data = {'friendly_name':cast.device.friendly_name, 'uuid': uuid, 'lastScan': int(time.time()) }
					data['def'] = jcast.getDefinition()
					data['status'] = jcast.getStatus()
					data['learn'] = 1;
					logging.info("SCANNER------ LEARN MODE : New device : " + uuid + ' (' + data["friendly_name"] + ')')
					globals.JEEDOM_COM.add_changes('devices::'+uuid,data)

		for known in globals.KNOWN_DEVICES :
			if known not in DISCOVER_DEVICES :
				logging.info("SCANNER------No connection to device " + known)
				if known in globals.GCAST_DEVICES :
					globals.GCAST_DEVICES[known].disconnect()
					del globals.GCAST_DEVICES[known]
				globals.KNOWN_DEVICES[known]['lastScan'] = int(time.time())
				#if ( (int(time.time())-globals.KNOWN_DEVICES[known]['lastOfflineSent']) > globals.LOSTDEVICE_RESENDNOTIFDELAY) :
				if ( globals.KNOWN_DEVICES[known]['online']==True or (int(time.time())-globals.KNOWN_DEVICES[known]['lastOfflineSent'])>globals.LOSTDEVICE_RESENDNOTIFDELAY ) :
					globals.KNOWN_DEVICES[known]['online'] = False
					globals.KNOWN_DEVICES[known]['lastOfflineSent'] = int(time.time())
					globals.KNOWN_DEVICES[known]['status'] = status = {
						"uuid" : known,
						"friendly_name" : "",
						"is_stand_by" :  False,
						"app_id" : "",
						"display_name" : "",
						"status_text" : "",
						"idle" : False,
					}
					#globals.JEEDOM_COM.add_changes('devices::'+known, globals.KNOWN_DEVICES[known])
					#globals.JEEDOM_COM.send_change_immediate({'devices': [ globals.KNOWN_DEVICES[known] ] });
					globals.JEEDOM_COM.send_change_immediate_device(known, globals.KNOWN_DEVICES[known]);
					if known in globals.NOWPLAYING_DEVICES:
						data = {
							"uuid" : known,
							"online" : False, "friendly_name" : "",
							"is_active_input" : False, "is_stand_by" :  False,
							"app_id" : "",	"display_name" : "", "status_text" : "",
							"idle" : False,	"title" : "",
							"album_artist" : "","metadata_type" : "",
							"album_name" : "",	"current_time" : 0,
							"artist" : "",	"image" : None,
							'series_title': "",  'season': "", 'episode': "",
							"stream_type" : "",	"track" : "",
							"player_state" : "","supported_media_commands" : 0,
							"supports_pause" : "",	'duration': 0,
							'content_type': "",	'idle_reason': ""
						}
						globals.JEEDOM_COM.send_change_immediate({'uuid' :  known, 'nowplaying':data});

			else :
				globals.KNOWN_DEVICES[known]["lastScan"] = int(time.time())

	except Exception as e:
		logging.error("SCANNER------Exception on scanner : %s" % str(e))
		logging.debug(traceback.format_exc())

	globals.SCAN_LAST = int(time.time())
	globals.SCAN_PENDING = False


def heartbeat_handler(delay):
	while True:
		if globals.LEARN_MODE and (globals.LEARN_BEGIN + globals.LEARN_TIMEOUT/2)  < int(time.time()):
			globals.LEARN_MODE = False
			logging.debug('HEARTBEAT------Quitting learn mode (60s elapsed)')
			globals.JEEDOM_COM.send_change_immediate({'learn_mode' : 0,'source' : globals.daemonname});

		if (globals.LAST_BEAT + globals.HEARTBEAT_FREQUENCY/2 -5)  < int(time.time()):
			globals.JEEDOM_COM.send_change_immediate({'heartbeat' : 1,'source' : globals.daemonname});
			globals.LAST_BEAT = int(time.time())

		time.sleep(10)		# every 10 secondes


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
parser = argparse.ArgumentParser(description='Blead Daemon for Jeedom plugin')
parser.add_argument("--device", help="Device", type=str)
parser.add_argument("--loglevel", help="Log Level for the daemon", type=str)
parser.add_argument("--pidfile", help="Value to write", type=str)
parser.add_argument("--callback", help="Value to write", type=str)
parser.add_argument("--apikey", help="Value to write", type=str)
parser.add_argument("--socketport", help="Socket Port", type=str)
parser.add_argument("--sockethost", help="Socket Host", type=str)
parser.add_argument("--daemonname", help="Daemon Name", type=str)
parser.add_argument("--cycle", help="Cycle to send event", type=str)
args = parser.parse_args()

if args.device:
	globals.device = args.device
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
if args.socketport:
	globals.socketport = args.socketport
if args.sockethost:
	globals.sockethost = args.sockethost
if args.daemonname:
	globals.daemonname = args.daemonname

globals.socketport = int(globals.socketport)
globals.cycle = float(globals.cycle)

jeedom_utils.set_log_level(globals.log_level)
logging.info('GLOBAL------Start googlecast')
logging.info('GLOBAL------Log level : '+str(globals.log_level))
logging.info('GLOBAL------Socket port : '+str(globals.socketport))
logging.info('GLOBAL------Socket host : '+str(globals.sockethost))
logging.info('GLOBAL------PID file : '+str(globals.pidfile))
logging.info('GLOBAL------Apikey : '+str(globals.apikey))
logging.info('GLOBAL------Callback : '+str(globals.callback))
logging.info('GLOBAL------Cycle : '+str(globals.cycle))

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)
#globals.IFACE_DEVICE = int(globals.device[-1:])
try:
	jeedom_utils.write_pid(str(globals.pidfile))
	globals.JEEDOM_COM = jeedom_com(apikey = globals.apikey,url = globals.callback,cycle=globals.cycle)
	if not globals.JEEDOM_COM.test():
		logging.error('GLOBAL------Network communication issues. Please fix your Jeedom network configuration.')
		shutdown()
	else :
		logging.info('GLOBAL------Network communication to jeedom OK.')
	jeedom_socket = jeedom_socket(port=globals.socketport,address=globals.sockethost)
	listen()
except Exception as e:
	logging.error('GLOBAL------Fatal error : '+str(e))
	logging.debug(traceback.format_exc())
	shutdown()
