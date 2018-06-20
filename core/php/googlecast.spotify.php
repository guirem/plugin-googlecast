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

/* * ***************************Includes********************************* */
//error_reporting(E_ALL);
//ini_set('display_errors', 'On');

require_once dirname(__FILE__) . "/../../../../core/php/core.inc.php";
require_once dirname(__FILE__) . "/../../3rdparty/spotify/SpotifyWebAPI.php";

$redirectURL = network::getNetworkAccess('external') . '/plugins/googlecast/core/php/googlecast.spotify.php';
$session = new SpotifyWebAPI\Session(
    'XXXXXXXXXXXXXXXXXXXXXXX',
    'XXXXXXXXXXXXXXXXXXXXXXX',
    $redirectURL
);

echo "<br>REdirect URL to add to spotify application : $redirectURL<br>";

$api = new SpotifyWebAPI\SpotifyWebAPI();

if (isset($_GET['code'])) {
    $session->requestAccessToken($_GET['code']);
    $api->setAccessToken($session->getAccessToken());

    echo '<br>Token :<br>';
    echo $session->getAccessToken();
    echo '<br>';
    echo '<br><br><a href="/plugins/googlecast/core/php/googlecast.spotify.php">New token</a>';
    //print_r($api->me());
} else {
    $options = [
        'scope' => [
            'user-read-email',
            'user-library-read',
            'playlist-read-private',
            'user-read-recently-played',
            //'playlist-read-public',
            'streaming',
            'user-read-currently-playing',
            'user-read-playback-state'
        ],
    ];

    header('Location: ' . $session->getAuthorizeUrl($options));
    die();
}
