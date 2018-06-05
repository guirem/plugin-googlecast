# -*- coding: utf-8 -*-
import sys
import requests
import os.path

try:
    import spotify.spotify_token as stoken
    import spotipy
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

def getSpotifyToken():
	arg_username=sys.argv[2]
	arg_password=sys.argv[3]
    data = stoken.start_session(arg_username, arg_password)
    access_token = data[0]
    return access_token

def getSpotifyPlaylists():
    arg_token=sys.argv[2]
    arg_playlist=sys.argv[3]
    # TODO
    out = arg_playlist
    return out

actions = {
    "getPlexToken" : getPlexToken,
    "testPlex" : testPlex,
    "getSpotifyToken" : getSpotifyToken,
    "testSpotify" : testSpotify,
    "getSpotifyPlaylists" : getSpotifyPlaylists
}
arg_action=sys.argv[1]
actions[arg_action]()
