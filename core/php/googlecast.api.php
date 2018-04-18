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

if (isset($result['started'])) {
	if ($result['started'] == 1) {
		log::add('googlecast','info','Process started. Sending known devices now...');
		usleep(500);
		googlecast::sendIdToDeamon();
	}
}
if (isset($result['heartbeat'])) {
	if ($result['heartbeat'] == 1) {
		log::add('googlecast','info','Googlecast program heartbeat');
	}
}

if ( isset($result['nowplaying']) ) {
	if ( isset($result['uuid']) ) {
		event::add('googlecast::'.$result['uuid'].'::nowplaying', $result);
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

		foreach ($googlecast->getCmd('info') as $cmd) {
			$logicalId = $cmd->getLogicalId();
			$result = array_flatten($data);
			if ( isset($result[$logicalId]) ) {
				$cmd->event($result[$logicalId]);
			}
		}
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
