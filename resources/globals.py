import time

JEEDOM_COM = ''
KNOWN_DEVICES = {}
NOWPLAYING_DEVICES = {}
GCAST_DEVICES = {}

NOWPLAYING_TIMEOUT = 15*60  # 15 minutes
NOWPLAYING_FREQUENCY = 15     # 30 seconds
NOWPLAYING_LAST = int(time.time())

LEARN_BEGIN = int(time.time())
LEARN_MODE = False          # is learn mode ?
LEARN_TIMEOUT = 60

HEARTBEAT_FREQUENCY = 300   # 5 minutes
LAST_BEAT = int(time.time())

READ_FREQUENCY = 60         # in seconds

SCAN_FREQUENCY = 60         # in seconds
SCAN_PENDING = False        # is scanner running?
SCAN_LAST = 0               # when last started

EVENTLISTENER_FILTERDELAY = 1          # in seconds, filter out multiple events that trigger in the same time
EVENTLISTENER_LASTEVENT = 0
EVENTLISTENER_NBTRIES = 10

LOSTDEVICE_RESENDNOTIFDELAY = 60*5        # not used yet

IFACE_DEVICE = 0

log_level = "debug"
pidfile = '/tmp/googlecast.pid'
apikey = ''
callback = ''
cycle = 0.3
daemonname=''
socketport=55012
sockethost=''
device=''

# dev
callback = 'http://127.0.0.1:80/plugins/googlecast/core/php/googlecast.api.php'
apikey = '4UMYbYhLSDhxrZ8dPlgFkOQLMZ9ndlEe'
sockethost = '127.0.0.1'
#KNOWN_DEVICES['d2fd3db1-bd0f-fe4c-d8dd-ce8c44033b44'] = {}
#REALTIME_DEVICES['d2fd3db1-bd0f-fe4c-d8dd-ce8c44033b44'] = {}
