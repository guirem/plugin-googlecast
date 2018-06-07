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

require_once dirname(__FILE__) . '/../../../core/php/core.inc.php';

function get_plugin_version() {
	$data = json_decode(file_get_contents(dirname(__FILE__) . '/info.json'), true);
    if (!is_array($data)) {
        $core_version = 0;
    }
    try {
        $core_version = $data['version'];
    } catch (\Exception $e) {
        $core_version = 0;
    }
	return $core_version;
}

function googlecast_update() {
	linkTemplate('dashboard/cmd.info.string.googlecast_playing.html');
    linkTemplate('dashboard/cmd.action.message.googlecast_speak.html');

	$core_version = get_plugin_version();
	config::save('plugin_version', $core_version, 'googlecast');

    createHtaccess();

	foreach (googlecast::byType('googlecast') as $googlecast) {
		try {
			$googlecast->save();
		} catch (Exception $e) {}
	}
	message::add('googlecast', 'Mise à jour du plugin Google Cast terminé (version ' . $core_version . ').', null, null);
}

function googlecast_install() {
	$core_version = get_plugin_version();
	config::save('plugin_version', $core_version, 'googlecast');
	if ( config::byKey('socketport', 'googlecast') == '' ) {
		config::save('socketport','55012', 'googlecast');
	}
	if ( config::byKey('fixdocker', 'googlecast') == '' ) {
		config::save('fixdocker','0', 'googlecast');
	}
	if ( config::byKey('cyclefactor', 'googlecast') == '' ) {
		config::save('cyclefactor','1', 'googlecast');
	}
	if ( config::byKey('tts_externalweb', 'googlecast') == '' ) {
		config::save('tts_externalweb','0', 'googlecast');
	}
    if ( config::byKey('tts_language', 'googlecast') == '' ) {
		config::save('tts_language','fr-FR', 'googlecast');
	}
    if ( config::byKey('tts_engine', 'googlecast') == '' ) {
		config::save('tts_engine','gtts', 'googlecast');
	}
	if ( config::byKey('tts_speed', 'googlecast') == '' ) {
		config::save('tts_speed','1.2', 'googlecast');
	}
	if ( config::byKey('tts_cleancache_days', 'googlecast') == '' ) {
		config::save('tts_cleancache_days','7', 'googlecast');
	}
    if ( config::byKey('tts_disablecache', 'googlecast') == '' ) {
		config::save('tts_disablecache','0', 'googlecast');
	}

	linkTemplate('dashboard/cmd.info.string.googlecast_playing.html');
    linkTemplate('dashboard/cmd.action.message.googlecast_speak.html');
    createHtaccess();

	message::removeAll('googlecast');
    message::add('googlecast', 'Installation du plugin Google Cast terminé (version ' . $core_version . ').', null, null);
}

function googlecast_remove() {
	unlinkTemplate('dashboard/cmd.info.string.googlecast_playing.html');
    unlinkTemplate('dashboard/cmd.action.message.googlecast_speak.html');
}

function linkTemplate($templateFilename) {
	#log::add('googlecast','info',"Création du lien sur template " . $templateFilename);
	$pathSrc = dirname(__FILE__) . '/../core/template/'.$templateFilename;
	$pathDest = dirname(__FILE__) . '/../../../core/template/'.$templateFilename;

	if (!file_exists($pathDest)) {
		shell_exec('ln -s '.$pathSrc. ' '. $pathDest);
	}
}

function createHtaccess() {
	$htaccess = dirname(__FILE__) . '/../.htaccess';

	if (!file_exists($htaccess)) {
        $content = "Options +FollowSymLinks\n";
        file_put_contents($htaccess, $content);
	}
}

function unlinkTemplate($templateFilename) {
	#log::add('googlecast','info',"Suppression du lien du template " . $templateFilename);
	$path = dirname(__FILE__) . '/../../../core/template/'.$templateFilename;

	if (file_exists($path)) {
		unlink($path);
	}
}
?>
