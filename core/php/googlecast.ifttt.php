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

    if (!jeedom::apiAccess(init('apikey'), 'googlecast')) {
        log::add('googlecast', 'error', 'IFTTT API : Incorrect API key !');
    	echo json_encode(array('text' => 'Incorrect API key !'));
    	die();
    }

    if ( init('uuid') != '' ) {
        $uuid=init('uuid');
    }
    else {
        log::add('googlecast', 'error', 'IFTTT API : No UUID provided !');
    	echo json_encode(array('text' => 'No UUID provided'));
    	die();
    }

    $action = 'interact';
    if ( init('action') != '' ) {
        $action = init('action');
    }

    if ( !($uuid=='any' and $action=='askreply') ) {
        $googlecast = googlecast::byLogicalId($uuid,'googlecast');
        if (!is_object($googlecast)) {
            log::add('googlecast', 'error', 'IFTTT API : Unkown UUID : ' . $uuid);
            echo json_encode(array('text' => 'Unkown UUID : ' . $uuid));
            die();
        }
        if ( $googlecast->getIsEnable() == 0) {
            log::add('googlecast', 'error', 'IFTTT API : Google Cast is disabled !');
            echo json_encode(array('text' => 'Google Cast is disabled !'));
            die();
        }
    }

    $query = null;
    if ( init('query') != '' ) {
        $query = urldecode( init('query') );
    }

    if ( is_null($query) ) {
        log::add('googlecast', 'error', 'IFTTT API : No query provided !');
        echo json_encode(array('text' => 'No query provided !'));
    	die();
    }


    if ( $action == 'interact' ) {
        log::add('googlecast', 'debug', 'IFTTT API : Query received ' . $query);

        $customcmd = $googlecast->getCmd(null, 'customcmd');

        $parameters['plugin'] = 'googlecast';
        $reply = interactQuery::tryToReply(trim($query), $parameters);
        log::add('googlecast', 'debug', 'IFTTT API : Interaction ' . print_r($reply, true));

        $queryTransform = str_replace(array('[',']') , ' ', $reply['reply']);
        $cmd = "cmd=tts|value=".$queryTransform;
        if ( init('vol') != '' ) {
            $cmd .= '|vol=' . $vol;
        }
        if ( init('noresume') != '' ) {
            $cmd .= '|noresume=1';
        }
        if ( init('quit') != '' ) {
            $cmd .= '|quit=1';
        }
        if ( init('silence') != '' ) {
            $cmd .= '|silence=' . $silence;
        }
        log::add('googlecast', 'debug', 'IFTTT API : Interaction reply cmd : ' . $cmd);
        $customcmd->execCmd(array('message' => $cmd));
        //echo json_encode(array('text' => 'OK !'));
        die();
    }
    if ( $action == 'askreply' ) {
        log::add('googlecast', 'debug', 'IFTTT API : Ask response received ' . $query);

        // uuid is set to any to try all devices
        if ($uuid=='any') {
            $askdone = false;
            foreach (googlecast::byType('googlecast') as $eqLogic) {
                if ($eqLogic->getCmd(null, 'customcmd')->askResponse($query)) {
                    $askdone = true;
                    break;
                }
                if ($eqLogic->getCmd(null, 'speak')->askResponse($query)) {
                    $askdone = true;
                    break;
                }
            }
            if ($askdone===true) {
                log::add('googlecast', 'debug', 'IFTTT API : Replied to pending ask query found on one device');
            }
            else {
                log::add('googlecast', 'debug', 'IFTTT API : No pending ask query found in any google cast devices !');
            }
            die();
        }
        // uuid is specified
        else {
            if ($googlecast->getCmd(null, 'customcmd')->askResponse($query)) {
            	log::add('googlecast', 'debug', 'IFTTT API : Replied to pending ask query (using customcmd)');
            }
            elseif ($googlecast->getCmd(null, 'speak')->askResponse($query)) {
            	log::add('googlecast', 'debug', 'IFTTT API : Replied to pending ask query (using speak)');
            }
            else {
                log::add('googlecast', 'debug', 'IFTTT API : No pending ask query found !');
            }
            die();
        }
    }
    elseif ( $action == 'customcmd' ) {
        log::add('googlecast', 'debug', 'IFTTT API : Custom action : ' . $query);
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
    log::add('googlecast', 'error', 'IFTTT API : Exception on ifttt api call : ' . $e->getMessage());
    echo json_encode(array('text' => 'Exception on ifttt api call !'));
    die();
}
