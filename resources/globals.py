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

JEEDOM_COM = ''
KNOWN_DEVICES = {}
NOWPLAYING_DEVICES = {}
GCAST_DEVICES = {}

NOWPLAYING_TIMEOUT = 15*60  # 15 minutes
NOWPLAYING_FREQUENCY = 15     # 15 seconds
NOWPLAYING_LAST = 0

LEARN_BEGIN = int(time.time())
LEARN_MODE = False          # is learn mode ?
LEARN_TIMEOUT = 60

HEARTBEAT_FREQUENCY = 600   # 10 minutes
LAST_BEAT = int(time.time())

SCAN_FREQUENCY = 60         # in seconds
SCAN_PENDING = False        # is scanner running?
SCAN_LAST = 0               # when last started
SCAN_TIMEOUT = 10           # timout of gcast scan

DISCOVERY_FREQUENCY = 14400         # every 4 hours
DISCOVERY_LAST = int(time.time())   # when last started

LOSTDEVICE_RESENDNOTIFDELAY = 60*5        # not used yet

IFACE_DEVICE = 0

cycle_factor = 2
cycle = 0.5
cycle_main = 2

log_level = "info"
pidfile = '/tmp/googlecast.pid'
apikey = ''
callback = ''
daemonname=''
socketport=55012
sockethost='127.0.0.1'
