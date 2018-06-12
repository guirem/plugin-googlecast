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

//error_reporting(E_ALL);
//ini_set('display_errors', 'On');

require_once dirname(__FILE__) . '/../../../../core/php/core.inc.php';

try {

    $querystr = parse_url(urldecode($_SERVER["REQUEST_URI"]));
    parse_str($querystr['query'], $queryparams);

    $apikey=null;
    if ( isset($queryparams['apikey']) ) {
        $apikey=$queryparams['apikey'];
    }

    if ($apikey!==null && !jeedom::apiAccess($apikey, 'googlecast')) {
    	echo json_encode(array('text' => 'No API Key provided !'));
    	die();
    }

    $content = file_get_contents('php://input');
    $json = json_decode($content, true);

    if ( isset($queryparams['uuid']) ) {
        $uuid=$queryparams['uuid'];
    }
    else {
    	echo json_encode(array('text' => 'No UUID provided'));
    	die();
    }

    $googlecast = googlecast::byLogicalId($uuid,'googlecast');
    if (!is_object($googlecast)) {
    	echo json_encode(array('text' => 'Unkown UUID : '));
    	die();
    }
    if ( $googlecast->getIsEnable() == 0) {
    	echo json_encode(array('text' => 'Google Cast is disabled !'));
    	die();
    }

    $action = 'interact';
    if ( isset($queryparams['action']) ) {
        $action = $queryparams['action'];
    }

    if ( isset($queryparams['query']) ) {
        $query = $queryparams['query'];
    }
    else {
        echo json_encode(array('text' => 'No query provided !'));
    	die();
    }

    if ( $action == 'interact' ) {
        log::add('googlecast', 'debug', 'IFTTT Query received ' . $query);

        $parameters['plugin'] = 'googlecast';
        $customcmd = $googlecast->getCmd(null, 'customcmd');
        if (is_object($cmd) && $customcmd->askResponse($query)) {
        	log::add('googlecast', 'debug', 'Répondu à un ask en cours');
        	die();
        }

        $reply = interactQuery::tryToReply(trim($query), $parameters);
        log::add('googlecast', 'debug', 'IFTTT Interaction ' . print_r($reply, true));

        if ( isset($queryparams['vol']) ) {
            $vol=$queryparams['vol'];
        }
        if ( isset($queryparams['noresume']) ) {
            $has_noresume=true;
        }
        if ( isset($queryparams['quit']) ) {
            $has_quit=true;
        }
        if ( isset($queryparams['silence']) ) {
            $silence=$queryparams['silence'];
        }

        $queryTransform = str_replace(array('[',']') , ' ', $reply['reply']);
        $cmd = "cmd=tts|value=".$queryTransform;
        if ( isset($vol) ) {
            $cmd .= '|vol=' . $vol;
        }
        if ( isset($has_noresume) ) {
            $cmd .= '|noresume=1';
        }
        if ( isset($has_quit) ) {
            $cmd .= '|quit=1';
        }
        if ( isset($silence) ) {
            $cmd .= '|silence=' . $silence;
        }
        log::add('googlecast', 'debug', 'IFTTT Interaction reply cmd : ' . $cmd);
        $customcmd->execCmd(array('message' => $cmd));
        //echo json_encode(array('text' => 'OK !'));
        die();
    }
    elseif ( $action == 'customcmd' ) {
        log::add('googlecast', 'debug', 'IFTTT Custom action : ' . $query);
        $googlecast->helperSendCustomCmd($query, null, 'ifttt', null, null);
        //echo json_encode(array('text' => 'OK !'));
        die();
    }
    else {
        echo json_encode(array('text' => 'Action not implemented !'));
    	die();
    }
    /*     * *********Catch exeption*************** */
} catch (Exception $e) {
    ajax::error(displayException($e), $e->getCode());
}
