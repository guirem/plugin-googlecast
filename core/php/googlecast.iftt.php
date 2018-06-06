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

error_reporting(E_ALL);
ini_set('display_errors', 'On');
require_once dirname(__FILE__) . '/../../../../core/php/core.inc.php';

try {

    $querystr = parse_url(urldecode($_SERVER["REQUEST_URI"]));
    parse_str($querystr['query'], $queryparams);

    $apikey=null;
    if ( isset($queryparams['apikey']) ) {
        $apikey=$queryparams['apikey'];
    }

    if ($apikey!==null && !jeedom::apiAccess($apikey, 'googlecast')) {
    	echo __('Clef API non valide, vous n\'êtes pas autorisé à effectuer cette action (gcast)', __FILE__);
    	die();
    }

    $content = file_get_contents('php://input');
    $json = json_decode($content, true);

    $googlecast = googlecast::byLogicalId($uuid);
    if (!is_object($googlecast)) {
    	echo json_encode(array('text' => __('UUID inconnu : ', __FILE__) . $uuid));
    	die();
    }

    $query = "";
    if ( isset($queryparams['query']) ) {
        $query = $queryparams['query'];
    }
    else {
        echo __('Pas de query !', __FILE__);
    	die();
    }

    log::add('googlecast', 'debug', 'Query received ' . $query);

    $parameters['plugin'] = 'googlecast';
    $customcmd = $googlecast->getCmd(null, 'customcmd');
    if (is_object($cmd) && $customcmd->askResponse($query)) {
    	log::add('googlecast', 'debug', 'Répondu à un ask en cours');
    	die();
    }

    $reply = interactQuery::tryToReply(trim($query), $parameters);
    log::add('googlecast', 'debug', 'Interaction ' . print_r($reply, true));

    $queryTransform = str_replace(array('[',']') , ' ', $reply['reply']);
    $cmd = "cmd=tts|value=".$queryTransform;
    #$googlecast->helperSendCustomCmd($cmd, null, 'mqtt', null, null);
    $customcmd->execCmd(array('message' => $cmd));
    die();

    /*     * *********Catch exeption*************** */
} catch (Exception $e) {
    ajax::error(displayException($e), $e->getCode());
}
