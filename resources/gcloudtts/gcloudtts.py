import requests
import base64
import json
import click
import os
import logging

__all__ = ['gcloudTTS', 'gcloudTTSError']

# Logger
log = logging.getLogger(__name__)
#log.addHandler(logging.NullHandler())

class gcloudTTS:
    def __init__(self, apiKey):
        self.apiKey = apiKey

    def _makePostRequest(self, endpoint, payload):
        url = "https://texttospeech.googleapis.com/v1/" + endpoint
        querystring = {"key": self.apiKey}
        headers = {"content-type": "application/json"}
        r = requests.request(
            "POST", url, data=payload, headers=headers, params=querystring
        )

        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            raise gcloudTTSError(payload=payload, response=r)

    def _decodeB64Data(self, data):
        return base64.b64decode(data)

    def tts2file(self, voice, language, string, textType, speakingRate, pitch, volumeGainDb, format, path):
        dataBytes = self.tts(voice, language, string, textType, speakingRate, format)
        with open(path, "wb") as file:
            file.write(dataBytes)

    def tts2mp3(self, voice, language, string, textType, speakingRate, pitch, volumeGainDb, path):
        dataBytes = self.tts2file(voice, language, string, textType, speakingRate, "mp3", path)

    def tts(self, voice, language, string, textType, speakingRate, pitch, volumeGainDb, format):
        payload = json.dumps(
            {
                "voice": {
                    "name": voice,
                    "languageCode": language
                },
                "input": {
                    textType: string
                },
                "audioConfig": {
                    "audioEncoding": format,
                    "speakingRate": speakingRate,
                    "pitch": pitch,
                    "volumeGainDb": volumeGainDb,
                    "effectsProfileId": ["medium-bluetooth-speaker-class-device"]
                },
            }
        )
        #log.debug(str(payload))
        reqObj = self._makePostRequest("text:synthesize", payload)
        return self._decodeB64Data(reqObj["audioContent"])


@click.group()
def cli():
    pass


@click.command()
@click.option("--apikey", envvar="GCTTS_APIKEY", help="Google Cloud API key that has acceess to Cloud TTS.",)
@click.option("--voice", default="en-US-Wavenet-F", help="The Google TTS voice.")
@click.option("--language", default="en-US", help="The langage the voice should be created in.")
@click.option("--rate", default=1.00, help="The speed in which the voice speaks.")
@click.option("--pitch", default=0.00, help="Speaking pitch, in the range [-20.0, 20.0]. 20 means increase 20 semitones from the original pitch. -20 means decrease 20 semitones from the original pitch.")
@click.option("--volumegaindb", default=0.00, help="Volume gain (in dB) of the normal native volume supported by the specific voice, in the range [-96.0, 16.0].")
@click.option("--text", prompt="Text", help="Text that should be spoken.")
@click.option("--type", default="text", help="Either 'text' or 'ssml'.")
@click.option("--format", default="mp3", help="The langage the voice should be created in.")
@click.argument("filename")
def tts(apikey, voice, language, rate, text, type, format, filename):
    dirpath = os.getcwd()

    ttsInst = gcloudTTS(apikey)
    try:
        mp3Obj = ttsInst.tts(voice, language, text, type, str(rate), pitch, volumegaindb, format)
        with open(os.path.join(os.getcwd(), filename), "wb") as file:
            file.write(mp3Obj)
    except ValueError as error:
        click.echo("ERROR: " + str(error))


cli.add_command(tts)

if __name__ == "__main__":
    cli()

class gcloudTTSError(Exception):
    """Exception that uses context to present a meaningful error message"""

    def __init__(self, msg=None, **kwargs):
        self.payload = kwargs.pop('payload', None)
        self.rsp = kwargs.pop('response', None)
        if msg:
            self.msg = msg
        elif self.payload is not None and self.rsp is not None:
            self.msg = self.infer_msg(self.payload, self.rsp)
        else:
            self.msg = None
        super(gcloudTTSError, self).__init__(self.msg)

    def infer_msg(self, payload, rsp):
        """Attempt to guess what went wrong by using known
        information (e.g. http response) and observed behaviour

        """
        status = rsp.status_code
        reason = rsp.reason

        cause = "Unknown"
        if status == 404:
            cause = "Google Speech API endpoint error (404)"
        elif status >= 500:
            cause = "Uptream API error. Try again later."
        else:
            respdata = None
            if (rsp.json() and rsp.json()["error"] is not "null"
                and rsp.json()["error"]["message"]):
                respdata = rsp.json()["error"]["message"]

            if respdata is not None:
                if respdata.find("API key not valid") != -1:
                    cause = "API key not valid"
                elif respdata.find("Cloud Text-to-Speech API has not been used in project") != -1:
                    cause = "Cloud Text-to-Speech API is not enabled for this key. Check and enable this API for the project in Google Console."
                else:
                    cause = respdata

            log.debug("gcloudTTS DEBUG - Detailed reply ----")
            log.debug(rsp.text)
            log.debug("gcloudTTS DEBUG ---------------------")

        return "%i (%s) from Google Cloud TTS API. Probable cause: %s" % (
            status, reason, cause)
