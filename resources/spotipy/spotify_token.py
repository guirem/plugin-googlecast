"""Utility module that helps get a webplayer access token"""
import os
import requests
import threading
import time
import logging

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"


class SpotifyWpToken():

    def __init__(self, username, password):
        self.__value__ = None
        self.status = threading.Event()
        self.username = username
        self.password = password
        threading.Thread(target=self.__fetch__).start() #run in parallel

    def __fetch__(self):
        start_time = time.time()

        try:
            GOTO = ["https://accounts.spotify.com/en/login", "https://accounts.spotify.com/api/login", "https://open.spotify.com/browse"]

            browser_session = requests.session()
            browser_session.cookies.set('__bon' , 'MHwwfDE0NTYxNzA5NzV8NjExNTkxODA5NTB8MXwxfDF8MQ==', domain='accounts.spotify.com')
            headers = { 'User-Agent': USER_AGENT }

            #1. get csrf
            response = browser_session.get(GOTO[0], headers=headers)
            response.raise_for_status()
            csrf_token = browser_session.cookies['csrf_token']

            #2. Login
            login_data = dict(username=self.username, password=self.password, csrf_token=csrf_token)
            headers['Referer'] = GOTO[0]
            response = browser_session.post(GOTO[1], data=login_data, headers=headers)
            response.raise_for_status()

            #3. get token
            response = browser_session.get(GOTO[2], headers=headers)
            response.raise_for_status()
            self.__value__ = browser_session.cookies['wp_access_token']

        except Exception as e:
            logging.error(e)

        self.status.set() #unlock
        logging.info ("wp_access_token fetch took [%s] seconds", ( time.time() - start_time ))

    @property
    def value(self):
        logging.debug ( "Waiting for wp_access_token..." )
        self.status.wait(10) #wait for lock
        logging.debug ( "Received wp_access_token [%s]", self.__value__)
        return self.__value__
