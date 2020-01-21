<?php

/* This file is part of Jeedom.
 *
 * Jeedom is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Jeedom is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Jeedom. If not, see <http://www.gnu.org/licenses/>.
 */
require_once dirname(__FILE__) . "/../../../../core/php/core.inc.php";

if (!jeedom::apiAccess(init('apikey'), 'googlecast')) {
	echo 'Clef API non valide, vous n\'etes pas autorisé à effectuer cette action';
	die();
}

if (init('test') != '') {
	echo 'OK';
	die();
}
$result = json_decode(file_get_contents("php://input"), true);
if (!is_array($result)) {
	die();
}
if (isset($result['source'])){
	log::add('googlecast','debug','This is a message from googlecast program ' . $result['source']);
}

if (isset($result['learn_mode'])) {
	if ($result['learn_mode'] == 1) {
		config::save('include_mode', 1, 'googlecast');
		event::add('googlecast::includeState', array(
			'mode' => 'learn',
			'state' => 1)
		);
	} else {
		config::save('include_mode', 0, 'googlecast');
		event::add('googlecast::includeState', array(
			'mode' => 'learn',
			'state' => 0)
		);
	}
}
if (isset($result['discovery'])) {
	$disableNotification = config::byKey('disableNotification', 'googlecast');
	if ( isset($result['uuid']) and isset($result['friendly_name']) && $disableNotification==false ) {
		$googlecast = googlecast::byLogicalId($result['uuid'], 'googlecast');
		if (!is_object($googlecast) or $googlecast->getIsEnable() != false) {
			$msg = 'Un nouveau GoogleCast ('. $result['friendly_name'] .") existe sur le réseau ! Vous pouvez lancer un scan via le plugin pour l'ajouter.";
			$action = 'Lancer un scan';
			message::add('Google Cast', $msg, $action, null);
		}
	}
}
if (isset($result['started'])) {
	if ($result['started'] == 1) {
		log::add('googlecast','info','Process started. Sending known devices now...');
		usleep(500);
		googlecast::sendIdToDeamon();
	}
}
if (isset($result['stopped'])) {
	if ($result['stopped'] == 1) {
		log::add('googlecast','info','Process stopped !');
	}
}
if (isset($result['heartbeat'])) {
	if ($result['heartbeat'] == 1) {
		log::add('googlecast','warn','Googlecast program heartbeat');
	}
}

if ( isset($result['nowplaying']) ) {
	if ( isset($result['uuid']) ) {
		event::add('googlecast::'.$result['uuid'].'::nowplaying', $result);
	}
}

if ( isset($result['callback']) ) {
	if ( isset($result['uuid']) ) {
        if ( isset($result['source']) && $result['source'].startsWith('plugin') && class_exists('gcastplayer') ) {
            gcastplayer::manageCallback($result);
        }
        else {
            googlecast::manageCallback($result);
        }
	}
}

if (isset($result['devices'])) {

	foreach ($result['devices'] as $key => $data) {
		if (!isset($data['uuid'])) {
			continue;
		}
		$googlecast = googlecast::byLogicalId($data['uuid'], 'googlecast');
		if (!is_object($googlecast)) {
			if ($data['learn'] != 1) {
				continue;
			}
			log::add('googlecast','info','New GoogleCast device detected ' . $data['uuid']);
			$googlecast = googlecast::createFromDef($data);
			event::add('jeedom::alert', array(
				'level' => 'warning',
				'page' => 'googlecast',
				'message' => '',
			));
			event::add('googlecast::includeDevice', $googlecast->getId());
		}
		else {
			$flattenResults = array_flatten($data);
			foreach ($googlecast->getCmd('info') as $cmd) {
				$logicalId = $cmd->getLogicalId();
				if ( isset($flattenResults[$logicalId]) ) {
					$cmd->event($flattenResults[$logicalId]);
				}
			}

            if ( isset($flattenResults['friendly_name']) && $flattenResults['friendly_name'] != $googlecast->getConfiguration('friendly_name') ) {
                $googlecast->setConfiguration('friendly_name', $flattenResults['friendly_name']);
                $googlecast->lightSave();
            }
            if ( isset($flattenResults['uri']) && $flattenResults['uri'] != $googlecast->getConfiguration('uri') ) {
                $googlecast->setConfiguration('uri', $flattenResults['uri']);
                $googlecast->setConfiguration('ip', $googlecast->getChromecastIPfromURI());
                $googlecast->lightSave();
            }

		}
	}
}

if (isset($result['ttsproxy'])) {

    if (isset($result['ttsmsg'])) {
        $ttsmsg = trim($result['ttsmsg']);
    }
    else {
        log::add('googlecast','debug','TTS PROXY : No TTS message in the request');
        http_response_code(400);
        return;
    }

    $ttsdata = false;

	if ($result['ttsproxy'] == 'jeedomtts') {
		log::add('googlecast','debug','[PROXY TTS] with jeedom engine');
        $additionnalOptions = '';
        if ($result['options'] && $result['options']['language']) {
            $additionnalOptions = '&voice=' . $result['options']['language'];
        }
        $ttsdata = file_get_contents(network::getNetworkAccess('internal') . '/core/api/tts.php?apikey=' . config::byKey('api', 'core') . $additionnalOptions . '&path=0&text=' . urlencode($ttsmsg));
	}

    if ($result['ttsproxy'] == 'ttswebserver') {
		log::add('googlecast','debug','[PROXY TTS] with webserver TTS engine (plugin)');

		if (config::byKey('active', 'ttsWebServer', 0) == 1) {
			$ttsws_config = config::byKey('ttsws_config', 'googlecast', '');
			if ($ttsws_config == '') {
				log::add('googlecast', 'warning', '[PROXY TTS] [TTSWebServer] options of TTSWebServer is empty, stop action for ttswebserver');
			}
            else {
				list($ttsws_opt_id, $_ttsws_opt_voice) = explode('|', $ttsws_config);

				if ($ttsws_opt_id > 0) {
					$ttsws_options = array('eqLogicId' => $ttsws_opt_id, 'message' => $ttsmsg, 'returnType' => 'path', 'returnFormat' => 'mp3');
					if ($_ttsws_opt_voice != '') {
						$ttsws_options['voice'] = $_ttsws_opt_voice;
					}
					log::add('googlecast', 'debug', '[PROXY TTS] [TTSWebServer] show _ttswsOptions=' . print_r($ttsws_options, true));

                    $ttsws_filepath = ttsWebServer::getAudioFile($ttsws_options);
                    log::add('googlecast', 'debug', '[PROXY TTS] [TTSWebServer] show _fileTTSWSPath="' . $ttsws_filepath . '"');

                    $ttsdata = file_get_contents($ttsws_filepath);

				} else {
					log::add('googlecast', 'warning', '[PROXY TTS] [TTSWebServer] id of TTSWebServer equipement is wrong (' . $ttsws_opt_id . '), stop action for ttswebserver');
				}
			}
		} else {
			log::add('googlecast', 'warning', '[PROXY TTS] [TTSWebServer] TTS WebServer plugin is not active');
		}
	}

    if ($ttsdata !== false) {
        //log::add('googlecast', 'debug', '[PROXY TTS] File successfuly sent !');

        header("Content-Disposition: attachment; filename=proxytts.mp3;");
        header("Content-Type: Content-Type: audio/mpeg");
		header("Content-Transfer-Encoding: binary");
		header("Pragma: no-cache");
        header('Content-Length: ' . strlen($ttsdata));
        http_response_code(200);
        echo $ttsdata;
    }
    else {
        log::add('googlecast', 'debug', '[PROXY TTS] Error while generating TTS file using PROXY TTS engine');

        http_response_code(400);
        echo 'Error while generating TTS file using PROXY TTS engine';
    }
}

function array_flatten($array) {
    $return = array();
    foreach ($array as $key => $value) {
        if (is_array($value))
            $return = array_merge($return, array_flatten($value));
        else
            $return[$key] = $value;
    }
    return $return;
}
