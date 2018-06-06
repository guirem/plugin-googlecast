# -*- coding: utf-8 -*-
import sys
import requests
import os.path

import http.server
import socketserver

try:
    import spotipy
    from spotipy import oauth2
except ImportError:
    logging.error("ERROR: Spotify API not loaded !")
    logging.debug(traceback.format_exc())
    pass

try:
    from plexapi.myplex import MyPlexAccount
    from plexapi.server import PlexServer
except ImportError:
    logging.error("ERROR: Plex API not loaded !")
    logging.debug(traceback.format_exc())
    pass

PORT = 8907

# spotify data
SPOTIPY_CLIENT_ID = 'a892ad6e71a54b2d8bce6b6e2d9c8dd6'
SPOTIPY_CLIENT_SECRET = '73500b1b128040598a3a47f81defd023'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:' + str(PORT)
#SCOPE = 'user-library-read playlist-read-private playlist-read-public streaming user-modify-playback-state user-read-currently-playing user-read-playback-state'
SCOPE = 'user-library-read,playlist-read-private'
CACHE = '.spotipyoauthcache'




def getPlexToken():
    arg_serverurl=sys.argv[2]
    arg_username=sys.argv[3]
    arg_password=sys.argv[4]

    if arg_username is not None and arg_password is not None :
        try:
            account = MyPlexAccount(arg_username, arg_password)
            for res in account.resources() :
                logging.debug("PLEX------ Server name available : " +str(res.name))
            plexServer = account.resource(arg_serverurl).connect()
            logging.debug("PLEX------ Token for reuse : " +str(account._token))
            return str(account._token)
        except Exception as e :
            pass
    return ""

def getSpotifyToken(code=None, responseuri=None):
    retData = ""
    sp_oauth = oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI,scope=SCOPE,cache_path=CACHE )

    access_token = ""
    token_info = sp_oauth.get_cached_token()

    if token_info:
        print ("Found cached token!")
        access_token = token_info['access_token']
    else:
        if responseuri is not None:
            code = sp_oauth.parse_response_code(responseuri)
        if code is not None:
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']
        else:
            retData = "coderequired"

    if access_token:
        print ("Access token available! Trying to get user information...")
        sp = spotipy.Spotify(access_token)
        results = sp.current_user()
        retData = results

    else:

        auth_url = sp_oauth.get_authorize_url()
        #htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
        htmlLoginButton = auth_url
        retData = htmlLoginButton
        #print (retData)
        #basicWebServer()

    print (retData)


class SpotifyHTTPServer(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        fullURL = self.path
        getSpotifyToken(responseuri=fullURL)
        self.send_response(200, 'OK')
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write("<html><body><h1>Jeedom Spotify</h1>OK!</body></html>")
        return

def basicWebServer():
	Handler = SpotifyHTTPServer
	httpd = socketserver.TCPServer(("", PORT), Handler)
	print ("Opening server")
	httpd.serve_forever()


def getSpotifyPlaylists():
    arg_token=sys.argv[2]
    arg_playlist=sys.argv[3]
    # TODO
    out = arg_playlist
    return out

# start code
actions = {
    "getPlexToken" : getPlexToken,
    #"getPlexQueryResults" : getPlexQueryResults,
    #"testPlex" : testPlex,
    "getSpotifyToken" : getSpotifyToken,
    #"testSpotify" : testSpotify,
    #"getSpotifyPlaylists" : getSpotifyPlaylists
}
arg_action=sys.argv[1]
actions[arg_action]()
