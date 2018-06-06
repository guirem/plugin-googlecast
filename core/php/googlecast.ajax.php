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
try {
    require_once dirname(__FILE__) . '/../../../../core/php/core.inc.php';

    include_file('core', 'authentification', 'php');

	ajax::init();

    if (init('action') == 'changeIncludeState') {
        googlecast::changeIncludeState(init('state'), init('mode'));
        ajax::success();
    }

    if (init('action') == 'cleanTTScache') {
		ajax::success(googlecast::cleanTTScache());
	}

    if (init('action') == 'nowplaying') {
        ajax::success(googlecast::registerNowPlayging(init('uuid')));
    }

    if (init('action') == 'refreshall') {
        ajax::success(googlecast::refreshStatusAll());
    }


	if (init('action') == 'sendcmd') {
		$ret = googlecast::sendDisplayAction(init('uuid'),init('cmd'), init('options'));
		if ($ret) {
			ajax::success();
		}
		else {
			ajax::error();
		}
	}

    throw new Exception(__('Aucune methode correspondante à : ', __FILE__) . init('action'));
    /*     * *********Catch exeption*************** */
} catch (Exception $e) {
    ajax::error(displayException($e), $e->getCode());
}
