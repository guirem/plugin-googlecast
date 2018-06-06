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

import time
import logging
import threading
import _thread as thread
import requests
from datetime import datetime
import collections
import os
import socket
import queue
import socketserver as SocketServer
from socketserver  import (TCPServer, StreamRequestHandler)

# ------------------------------------------------------------------------------

class jeedom_com():
    def __init__(self,apikey = '',url = '',cycle = 0.5,retry = 3):
        self.apikey = apikey
        self.url = url
        self.cycle = cycle
        self.retry = retry
        self.changes = {}
        if cycle > 0 :
            self.send_changes_async()
        logging.debug('Init request module v%s' % (str(requests.__version__),))

    def send_changes_async(self):
        try:
            if len(self.changes) == 0:
                resend_changes = threading.Timer(self.cycle, self.send_changes_async)
                resend_changes.start()
                return
            start_time = datetime.now()
            changes = self.changes
            self.changes = {}
            logging.debug('SENDER------Send to jeedom : '+str(changes))
            i=0
            while i < self.retry:
                try:
                    r = requests.post(self.url + '?apikey=' + self.apikey, json=changes, timeout=(0.5, 120), verify=False)
                    if r.status_code == requests.codes.ok:
                        break
                except Exception as error:
                    logging.error('SENDER------Error on send request to jeedom ' + str(error)+' retry : '+str(i)+'/'+str(self.retry))
                i = i + 1
            if r.status_code != requests.codes.ok:
                logging.error('SENDER------Error on send request to jeedom, return code %s' % (str(r.status_code),))
            dt = datetime.now() - start_time
            ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
            timer_duration = self.cycle - ms
            if timer_duration < 0.1:
                timer_duration = 0.1
            resend_changes = threading.Timer(timer_duration, self.send_changes_async)
            resend_changes.start()
        except Exception as error:
            logging.error('SENDER------Critical error on  send_changes_async %s' % (str(error),))
            resend_changes = threading.Timer(self.cycle, self.send_changes_async)
            resend_changes.start()

    def add_changes(self,key,value):
        if key.find('::') != -1:
            tmp_changes = {}
            changes = value
            for k in reversed(key.split('::')):
                if k not in tmp_changes:
                    tmp_changes[k] = {}
                tmp_changes[k] = changes
                changes = tmp_changes
                tmp_changes = {}
            if self.cycle <= 0:
                self.send_change_immediate(changes)
            else:
                self.merge_dict(self.changes,changes)
        else:
            if self.cycle <= 0:
                self.send_change_immediate({key:value})
            else:
                self.changes[key] = value

    def send_change_immediate(self,change):
        thread.start_new_thread( self.thread_change, (change,))

    def send_change_immediate_device(self,uuid, change):
        thread.start_new_thread( self.thread_change, ({'devices': {uuid: change}},))

    def thread_change(self,change):
        logging.debug('SENDER------Send to jeedom :  %s' % (str(change),))
        i=0
        while i < self.retry:
            try:
                r = requests.post(self.url + '?apikey=' + self.apikey, json=change, timeout=(0.5, 120), verify=False)
                if r.status_code == requests.codes.ok:
                    break
            except Exception as error:
                logging.error('SENDER------Error on send request to jeedom ' + str(error)+' retry : '+str(i)+'/'+str(self.retry))
            i = i + 1

    def set_change(self,changes):
        self.changes = changes

    def get_change(self):
        return self.changes

    def merge_dict(self,d1, d2):
        for k,v2 in d2.items():
            v1 = d1.get(k) # returns None if v1 has no value for this key
            if ( isinstance(v1, collections.Mapping) and
                 isinstance(v2, collections.Mapping) ):
                self.merge_dict(v1, v2)
            else:
                d1[k] = v2

    def test(self):
        try:
            response = requests.get(self.url + '?apikey=' + self.apikey, verify=False)
            if response.status_code != requests.codes.ok:
                logging.error('SENDER------Callback error: %s %s. Please check your network configuration page'% (response.status.code, response.status.message,))
                return False
        except Exception as e:
            logging.error('SENDER------Callback result as a unknown error: %s. Please check your network configuration page. '% str(e))
            return False
        return True

# ------------------------------------------------------------------------------

class jeedom_utils():

    @staticmethod
    def convert_log_level(level = 'error'):
        LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'notice': logging.WARNING,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL,
          'none': logging.NOTSET}
        return LEVELS.get(level, logging.NOTSET)

    @staticmethod
    def set_log_level(level = 'error'):
        FORMAT = '[%(asctime)-15s][%(levelname)s] : %(message)s'
        if level=='default' :
            level='info'
        if level=='1000' :
            level='critical'

        if level=='debug' :
            logging.getLogger("pychromecast").setLevel(logging.ERROR)
            logging.getLogger("plexapi").setLevel(logging.DEBUG)
            logging.getLogger("urllib3").setLevel(logging.ERROR)
            logging.getLogger("pydub").setLevel(logging.ERROR)
            logging.getLogger("gtts").setLevel(logging.ERROR)
        else :
            logging.getLogger("pychromecast").setLevel(logging.CRITICAL)
            logging.getLogger("plexapi").setLevel(logging.ERROR)
            logging.getLogger("urllib3").setLevel(logging.CRITICAL)
            logging.getLogger("pydub").setLevel(logging.CRITICAL)
            logging.getLogger("gtts").setLevel(logging.CRITICAL)

        logging.basicConfig(level=jeedom_utils.convert_log_level(level),format=FORMAT, datefmt="%Y-%m-%d %H:%M:%S")

    @staticmethod
    def write_pid(path):
        pid = str(os.getpid())
        logging.debug("Writing PID " + pid + " to " + str(path))
        open(path, 'w').write("%s\n" % pid)

# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------

JEEDOM_SOCKET_MESSAGE = queue.Queue()

class jeedom_socket_handler(StreamRequestHandler):
    def handle(self):
        global JEEDOM_SOCKET_MESSAGE
        logging.debug("SOCKETHANDLER------Client connected to [%s:%d]" % self.client_address)
        lg = self.rfile.readline().strip().decode("ascii")
        JEEDOM_SOCKET_MESSAGE.put(lg)
        logging.debug("SOCKETHANDLER------Message read from socket: " + lg)
        self.netAdapterClientConnected = False
        logging.debug("SOCKETHANDLER------Client disconnected from [%s:%d]" % self.client_address)

class jeedom_socket():

    def __init__(self,address='localhost', port=55000):
        self.address = address
        self.port = port
        SocketServer.TCPServer.allow_reuse_address = True

    def open(self):
        self.netAdapter = TCPServer((self.address, self.port), jeedom_socket_handler)
        if self.netAdapter:
            logging.debug("SOCKETHANDLER------Socket interface started")
            threading.Thread(target=self.loopNetServer, args=()).start()
        else:
            logging.debug("SOCKETHANDLER------Cannot start socket interface")

    def loopNetServer(self):
        logging.debug("SOCKETHANDLER------LoopNetServer Thread started")
        logging.debug("SOCKETHANDLER------Listening on: [%s:%d]" % (self.address, self.port))
        self.netAdapter.serve_forever()
        logging.debug("SOCKETHANDLER------LoopNetServer Thread stopped")

    def close(self):
        self.netAdapter.shutdown()

    def getMessage(self):
        return self.message

# ------------------------------------------------------------------------------
# END
# ------------------------------------------------------------------------------
