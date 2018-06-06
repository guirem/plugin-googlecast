"""
Controller to interface with the Plex-app.
"""
from ..controllers import BaseController
from urllib.parse import urlparse

MESSAGE_TYPE = 'type'

TYPE_PLAY = "PLAY"
TYPE_PAUSE = "PAUSE"
TYPE_STOP = "STOP"

class PlexController(BaseController):
    """ Controller to interact with Plex namespace. """

    def __init__(self):
        super(PlexController, self).__init__(
            "urn:x-cast:plex", "9AC194DC")
        self.app_id="9AC194DC"
        self.namespace="urn:x-cast:plex"
        self.request_id = 0

    def stop(self):
        """ Send stop command. """
        self.namespace = "urn:x-cast:plex"
        self.request_id += 1
        self.send_message({MESSAGE_TYPE: TYPE_STOP})

    def pause(self):
        """ Send pause command. """
        self.namespace = "urn:x-cast:plex"
        self.request_id += 1
        self.send_message({MESSAGE_TYPE: TYPE_PAUSE})

    def play(self):
        """ Send play command. """
        self.namespace = "urn:x-cast:plex"
        self.request_id += 1
        self.send_message({MESSAGE_TYPE: TYPE_PLAY})


    def play_media(self,item,server,params,medtype="LOAD"):
        def app_launched_callback():
                self.set_load(item,server,params,medtype)

        receiver_ctrl = self._socket_client.receiver_controller
        receiver_ctrl.launch_app(self.app_id,
                                callback_function=app_launched_callback)

    def set_load(self,item,server,params,medtype="LOAD") :
        offset=0,
        if 'offset' in params :
            offset = params['offset']
        type='video'
        if 'type' in params :
            type = params['type']
        shuffle=0
        if 'shuffle' in params :
            shuffle = params['shuffle']
        repeat=0
        if 'repeat' in params :
            repeat = params['repeat']

        transient_token = server.query("/security/token?type=delegation&scope=all").attrib.get('token')
        playqueue = server.createPlayQueue(item, shuffle=shuffle, repeat=repeat).playQueueID
        self.request_id += 1
        #address = server.baseurl.split(":")[1][2:]
        server_uri = urlparse(server._baseurl)
        protocol = server_uri.scheme
        address = server_uri.hostname
        port = server_uri.port
        version = "1.3.3.3148"
        if server.version is not None :
            version = server.version
        self.namespace="urn:x-cast:com.google.cast.media"
        msg = {
                "type": medtype,
                "requestId": self.request_id,
                "sessionId": "jeedom_googlecast_plex",
                "autoplay": True,
                "duration": str(item.duration) if item.duration else None,
                "currentTime": offset,
                "media":{
                        "contentId": item.key,
                        "streamType": "BUFFERED",
                        "contentType": type,
                        "metadata" : {
                                "thumb" : str(item.thumb) if hasattr(item, 'thumb') else None
                            },
                        "customData": {
                                "offset": offset,
                                "server": {
                                        "machineIdentifier": server.machineIdentifier,
                                        "transcoderVideo": server.transcoderVideo,
                                        "transcoderVideoRemuxOnly": False,
                                        "transcoderAudio": server.transcoderAudio,
                                        "version": version,
                                        "myPlexSubscription": server.myPlexSubscription,
                                        "isVerifiedHostname": False,
                                        "protocol": protocol,
                                        "address": address,
                                        "port": str(port),
                                        "accessToken": transient_token,
                                },
                                "user": {"username": server.myPlexUsername},
                                "containerKey": "/playQueues/{}?own=1&window=200".format(playqueue),
                        },
                }
        }
        self.send_message(msg, inc_session_id=True)
