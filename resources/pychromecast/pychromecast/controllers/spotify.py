"""
Controller to interface with the DashCast app namespace.
"""
import logging
import time
import threading

from . import BaseController
from ..config import APP_SPOTIFY

APP_NAMESPACE = "urn:x-cast:com.spotify.chromecast.secure.v1"
TYPE_STATUS = "setCredentials"
TYPE_RESPONSE_STATUS = 'setCredentialsResponse'


# pylint: disable=too-many-instance-attributes
class SpotifyController(BaseController):
    """ Controller to interact with Spotify namespace. """

    # pylint: disable=useless-super-delegation
    # The pylint rule useless-super-delegation doesn't realize
    # we are setting default values here.
    def __init__(self):
        super(SpotifyController, self).__init__(APP_NAMESPACE, APP_SPOTIFY)

        self.logger = logging.getLogger(__name__)
        self.session_started = False
        self.is_launched = False
        self.device = None
        self.waiting = threading.Event()
    # pylint: enable=useless-super-delegation

    # pylint: disable=unused-argument,no-self-use
    def receive_message(self, message, data):
        """ Currently not doing anything with received messages. """
        if data['type'] == 'setCredentialsResponse':
            self.send_message({'type': 'getInfo', 'payload': {}})
        if data['type'] == 'setCredentialsError':
            self.device = None
            self.waiting.set()
        if data['type'] == 'getInfoResponse':
            self.device = data['payload']['deviceID']
            self.waiting.set()
        #self.logger.critical('Spotify controller data : '+str(data))
        return True

    def launch_app(self, access_token):
        """ Launch main application """
        self.access_token = access_token
        def callback():
            """Callback function"""
            self.waiting.clear()
            while not self.is_active:
                time.sleep(0.1)
            self.send_message({'type': 'setCredentials', 'credentials': self.access_token })

        self.launch(callback_function=callback)

    def wait(self):
        self.waiting.wait(15)
        return self.device
