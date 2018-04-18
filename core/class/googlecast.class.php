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

class googlecast extends eqLogic {
	/*     * *************************Attributs****************************** */

	private $_collectDate = '';
	public static $_widgetPossibility = array('custom' => true);

	/*     * ***********************Methode static*************************** */


	/*     * *********************Methode d'instance************************* */

	public function preUpdate() {
		/*
		if ($this->getConfiguration('socketport') == '') {
			throw new Exception(__('Le champs Port Socket ne peut etre vide', __FILE__));
		}
		*/
	}

	public function preRemove() {
		$this->disallowDevice();
	}


	public function postSave() {
		$order = 1;

		$cmd = $this->getCmd(null, 'refresh');
		if (!is_object($cmd)) {
			$cmd = new googlecastCmd();
			$cmd->setLogicalId('refresh');
			$cmd->setName(__('Rafraîchir', __FILE__));
			$cmd->setIsVisible(1);
			$cmd->setConfiguration('googlecast_cmd', true);
		}
		$cmd->setType('action');
		$cmd->setSubType('other');
		$cmd->setEqLogic_id($this->getId());
		$cmd->save();

		$cmd = $this->getCmd(null, 'online');
		if (!is_object($cmd)) {
			$cmd = new googlecastCmd();
			$cmd->setLogicalId('online');
			$cmd->setIsVisible(1);
			$cmd->setName(__('Online', __FILE__));
			$cmd->setTemplate('dashboard', 'googlecast_status');
			$cmd->setConfiguration('googlecast_cmd', true);
		}
		$cmd->setType('info');
		$cmd->setSubType('binary');
		$cmd->setEqLogic_id($this->getId());
		$cmd->setDisplay('generic_type', 'ENERGY_STATE');
		$cmd->save();

		$cmd = $this->getCmd(null, 'reboot');
		if (!is_object($cmd)) {
			$cmd = new googlecastCmd();
			$cmd->setLogicalId('reboot');
			$cmd->setName(__('Restart', __FILE__));
			$cmd->setIsVisible(1);
			$cmd->setTemplate('dashboard', 'googlecast_reboot');
			$cmd->setDisplay('icon', '<i class="fa fa-power-off"></i>');
			$cmd->setConfiguration('googlecast_cmd', true);
		}
		$cmd->setType('action');
		$cmd->setSubType('other');
		$cmd->setEqLogic_id($this->getId());
		$cmd->save();

		$cmd = $this->getCmd(null, 'is_busy');
		if (!is_object($cmd)) {
			$cmd = new googlecastCmd();
			$cmd->setLogicalId('is_busy');
			$cmd->setIsVisible(1);
			$cmd->setName(__('Occupé', __FILE__));
			$cmd->setTemplate('dashboard', 'googlecast_busy');
			$cmd->setConfiguration('googlecast_cmd', true);
		}
		$cmd->setType('info');
		$cmd->setSubType('binary');

		$cmd->setEqLogic_id($this->getId());
		$cmd->setDisplay('generic_type', 'ENERGY_STATE');
		$cmd->save();

		$cmd = $this->getCmd(null, 'volume_level');
		if (!is_object($cmd)) {
			$cmd = new googlecastCmd();
			$cmd->setLogicalId('volume_level');
			$cmd->setIsVisible(0);
			$cmd->setName(__('Volume', __FILE__));
			$cmd->setConfiguration('googlecast_cmd', true);
			$cmd->setOrder($order++);
		}
		$cmd->setType('info');
		$cmd->setSubType('numeric');
		$cmd->setEqLogic_id($this->getId());
		$cmd->setUnite('%');
		$cmd->setDisplay('generic_type', 'LIGHT_STATE');
		$cmd->save();
		$volume_id = $cmd->getId();

		$cmd = $this->getCmd(null, 'volume_set');
		if (!is_object($cmd)) {
			$cmd = new googlecastCmd();
			$cmd->setLogicalId('volume_set');
			$cmd->setName(__('Volume niveau', __FILE__));
			$cmd->setIsVisible(1);
			$cmd->setConfiguration('googlecast_cmd', true);
			$cmd->setOrder($order++);
		}
		$cmd->setType('action');
		$cmd->setSubType('slider');
		$cmd->setConfiguration('minValue', 0);
		$cmd->setConfiguration('maxValue', 100);
		$cmd->setValue($volume_id);
		$cmd->setEqLogic_id($this->getId());
		$cmd->save();

		$cmd = $this->getCmd(null, 'volume_muted');
		if (!is_object($cmd)) {
			$cmd = new googlecastCmd();
			$cmd->setLogicalId('volume_muted');
			$cmd->setIsVisible(0);
			$cmd->setName(__('Mute', __FILE__));
			$cmd->setConfiguration('googlecast_cmd', true);
			$cmd->setOrder($order++);
		}
		$cmd->setType('info');
		$cmd->setSubType('binary');
		$cmd->setEqLogic_id($this->getId());
		$cmd->setDisplay('generic_type', 'SIREN_STATE');
		$cmd->save();
		$mute_id = $cmd->getId();

		$cmd = $this->getCmd(null, 'volume_down');
		if (!is_object($cmd)) {
			$cmd = new googlecastCmd();
			$cmd->setLogicalId('volume_down');
			$cmd->setName(__('Volume -', __FILE__));
			$cmd->setIsVisible(1);
			$cmd->setDisplay('icon', '<i class="fa fa-volume-down"></i>');
			$cmd->setConfiguration('googlecast_cmd', true);
			$cmd->setOrder($order++);
		}
		$cmd->setType('action');
		$cmd->setSubType('other');
		$cmd->setEqLogic_id($this->getId());
		$cmd->save();

		$cmd = $this->getCmd(null, 'volume_up');
		if (!is_object($cmd)) {
			$cmd = new googlecastCmd();
			$cmd->setLogicalId('volume_up');
			$cmd->setName(__('Volume +', __FILE__));
			$cmd->setIsVisible(1);
			$cmd->setDisplay('icon', '<i class="fa fa-volume-up"></i>');
			$cmd->setConfiguration('googlecast_cmd', true);
			$cmd->setOrder($order++);
		}
		$cmd->setType('action');
		$cmd->setSubType('other');
		$cmd->setEqLogic_id($this->getId());
		$cmd->save();

		$cmd = $this->getCmd(null, 'mute_on');
		if (!is_object($cmd)) {
			$cmd = new googlecastCmd();
			$cmd->setLogicalId('mute_on');
			$cmd->setName(__('Muet ON', __FILE__));
			$cmd->setIsVisible(1);
			$cmd->setTemplate('dashboard', 'btnCircle');
			$cmd->setTemplate('mobile', 'binaryDefault');
			$cmd->setConfiguration('googlecast_cmd', true);
			$cmd->setOrder($order++);
		}
		$cmd->setType('action');
		$cmd->setSubType('other');
		$cmd->setEqLogic_id($this->getId());
		$cmd->setDisplay('generic_type', 'SIREN_ON');
		$cmd->setValue($mute_id);
		$cmd->save();

		$cmd = $this->getCmd(null, 'mute_off');
		if (!is_object($cmd)) {
			$cmd = new googlecastCmd();
			$cmd->setLogicalId('mute_off');
			$cmd->setName(__('Muet OFF', __FILE__));
			$cmd->setIsVisible(1);
			$cmd->setTemplate('dashboard', 'btnCircle');
			$cmd->setTemplate('mobile', 'binaryDefault');
			$cmd->setConfiguration('googlecast_cmd', true);
			$cmd->setOrder($order++);
		}
		$cmd->setType('action');
		$cmd->setSubType('other');
		$cmd->setEqLogic_id($this->getId());
		$cmd->setDisplay('generic_type', 'SIREN_OFF');
		$cmd->setValue($mute_id);
		$cmd->save();

		$cmd = $this->getCmd(null, 'status_text');
		if (!is_object($cmd)) {
			$cmd = new googlecastCmd();
			$cmd->setLogicalId('status_text');
			$cmd->setIsVisible(1);
			$cmd->setName(__('Statut', __FILE__));
			$cmd->setConfiguration('googlecast_cmd', true);
			$cmd->setDisplay('showNameOndashboard', false);
			$cmd->setOrder($order++);
		}
		$cmd->setType('info');
		$cmd->setSubType('string');
		$cmd->setEqLogic_id($this->getId());
		$cmd->setDisplay('generic_type', 'GENERIC');
		$cmd->save();

		$cmd = $this->getCmd(null, 'player_state');
		if (!is_object($cmd)) {
			$cmd = new googlecastCmd();
			$cmd->setLogicalId('player_state');
			$cmd->setIsVisible(0);
			$cmd->setName(__('Statut Player', __FILE__));
			$cmd->setConfiguration('googlecast_cmd', true);
			$cmd->setDisplay('showNameOndashboard', false);
			$cmd->setOrder($order++);
		}
		$cmd->setType('info');
		$cmd->setSubType('string');
		$cmd->setEqLogic_id($this->getId());
		$cmd->setDisplay('generic_type', 'GENERIC');
		$cmd->save();

		$cmd = $this->getCmd(null, 'quit_app');
		if (!is_object($cmd)) {
			$cmd = new googlecastCmd();
			$cmd->setLogicalId('quit_app');
			$cmd->setName(__('Quitter', __FILE__));
			$cmd->setIsVisible(1);
			$cmd->setDisplay('icon', '<i class="fa fa-eject"></i>');
			#$cmd->setDisplay('forceReturnLineBefore', 1);
			$cmd->setConfiguration('googlecast_cmd', true);
			$cmd->setOrder($order++);
		}
		$cmd->setType('action');
		$cmd->setSubType('other');
		$cmd->setEqLogic_id($this->getId());
		$cmd->save();

		$cmd = $this->getCmd(null, 'stop');
		if (!is_object($cmd)) {
			$cmd = new googlecastCmd();
			$cmd->setLogicalId('stop');
			$cmd->setName(__('Stop', __FILE__));
			$cmd->setIsVisible(1);
			$cmd->setDisplay('icon', '<i class="fa fa-stop"></i>');
			$cmd->setConfiguration('googlecast_cmd', true);
			$cmd->setOrder($order++);
		}
		$cmd->setType('action');
		$cmd->setSubType('other');
		$cmd->setEqLogic_id($this->getId());
		$cmd->save();

		$cmd = $this->getCmd(null, 'pause');
		if (!is_object($cmd)) {
			$cmd = new googlecastCmd();
			$cmd->setLogicalId('pause');
			$cmd->setName(__('Pause', __FILE__));
			$cmd->setIsVisible(1);
			$cmd->setDisplay('icon', '<i class="fa fa-pause"></i>');
			$cmd->setConfiguration('googlecast_cmd', true);
			$cmd->setOrder($order++);
		}
		$cmd->setType('action');
		$cmd->setSubType('other');
		$cmd->setEqLogic_id($this->getId());
		$cmd->save();

		$cmd = $this->getCmd(null, 'rewind');
		if (!is_object($cmd)) {
			$cmd = new googlecastCmd();
			$cmd->setLogicalId('rewind');
			$cmd->setName(__('Back', __FILE__));
			$cmd->setIsVisible(1);
			$cmd->setDisplay('icon', '<i class="fa fa-step-backward"></i>');
			$cmd->setConfiguration('googlecast_cmd', true);
			$cmd->setOrder($order++);
		}
		$cmd->setType('action');
		$cmd->setSubType('other');
		$cmd->setEqLogic_id($this->getId());
		$cmd->save();

		$cmd = $this->getCmd(null, 'skip');
		if (!is_object($cmd)) {
			$cmd = new googlecastCmd();
			$cmd->setLogicalId('skip');
			$cmd->setName(__('Skip', __FILE__));
			$cmd->setIsVisible(1);
			$cmd->setDisplay('icon', '<i class="fa fa-step-forward"></i>');
			$cmd->setConfiguration('googlecast_cmd', true);
			$cmd->setOrder($order++);
		}
		$cmd->setType('action');
		$cmd->setSubType('other');
		$cmd->setEqLogic_id($this->getId());
		$cmd->save();

		$cmd = $this->getCmd(null, 'play');
		if (!is_object($cmd)) {
			$cmd = new googlecastCmd();
			$cmd->setLogicalId('play');
			$cmd->setName(__('Play', __FILE__));
			$cmd->setIsVisible(1);
			$cmd->setDisplay('icon', '<i class="fa fa-play"></i>');
			$cmd->setConfiguration('googlecast_cmd', true);
			$cmd->setOrder($order++);
		}
		$cmd->setType('action');
		$cmd->setSubType('other');
		$cmd->setEqLogic_id($this->getId());
		$cmd->save();

		$cmd = $this->getCmd(null, 'nowplaying');
		if (!is_object($cmd)) {
			$cmd = new googlecastCmd();
			$cmd->setLogicalId('nowplaying');
			$cmd->setName(__('Playing Widget', __FILE__));
			$cmd->setIsVisible(1);
			$cmd->setTemplate('dashboard','googlecast_playing');
			$cmd->setConfiguration('googlecast_cmd', true);
			$cmd->setOrder($order++);
		}
		$cmd->setType('info');
		$cmd->setSubType('string');
		$cmd->setEqLogic_id($this->getId());
		$cmd->save();

		$cmd = $this->getCmd(null, 'customcmd');
		if (!is_object($cmd)) {
			$cmd = new googlecastCmd();
			$cmd->setLogicalId('customcmd');
			$cmd->setName(__('Custom Cmd', __FILE__));
			$cmd->setIsVisible(0);
			$cmd->setOrder($order++);
			$cmd->setConfiguration('googlecast_cmd', true);
		}
		$cmd->setType('action');
		$cmd->setSubType('message');
		$cmd->setEqLogic_id($this->getId());
		$cmd->save();

		if ($this->getConfiguration('firstTimeCreation', True)) {

			$logid = "app=backdrop";
			$cmd = $this->getCmd(null, $logid);
			if (!is_object($cmd)) {
				$cmd = new googlecastCmd();
				$cmd->setLogicalId($logid);
				$cmd->setName(__('Backdrop', __FILE__));
				$cmd->setIsVisible(1);
				$cmd->setOrder(200);
				$cmd->setOrder($order++);
			}
			$cmd->setType('action');
			$cmd->setSubType('other');
			$cmd->setEqLogic_id($this->getId());
			$cmd->save();

			$logid = "app=youtube|cmd=play_video|value=fra4QBLF3GU";
			$cmd = $this->getCmd(null, $logid);
			if (!is_object($cmd)) {
				$cmd = new googlecastCmd();
				$cmd->setLogicalId($logid);
				$cmd->setName(__('YouTube', __FILE__));
				$cmd->setIsVisible(1);
				$cmd->setOrder(200);
				$cmd->setOrder($order++);
			}
			$cmd->setType('action');
			$cmd->setSubType('other');
			$cmd->setEqLogic_id($this->getId());
			$cmd->save();

			$logid = "app=media|cmd=play_media|value='http://bit.ly/2JzYtfX,video/mp4','Mon film'";
			$cmd = $this->getCmd(null, $logid);
			if (!is_object($cmd)) {
				$cmd = new googlecastCmd();
				$cmd->setLogicalId($logid);
				$cmd->setName(__('Media', __FILE__));
				$cmd->setIsVisible(1);
				$cmd->setOrder(201);
				$cmd->setOrder($order++);
			}
			$cmd->setType('action');
			$cmd->setSubType('other');
			$cmd->setEqLogic_id($this->getId());
			$cmd->save();

			$logid = "app=web|cmd=load_url|value='http://pictoplasma.sound-creatures.com',True,10";
			$cmd = $this->getCmd(null, $logid);
			if (!is_object($cmd)) {
				$cmd = new googlecastCmd();
				$cmd->setLogicalId($logid);
				$cmd->setName(__('Web', __FILE__));
				$cmd->setIsVisible(1);
				$cmd->setOrder(202);
				$cmd->setOrder($order++);
			}
			$cmd->setType('action');
			$cmd->setSubType('other');
			$cmd->setEqLogic_id($this->getId());
			$cmd->save();

			$this->setConfiguration('firstTimeCreation', False);
			$this->save();
		}

		$this->checkAndUpdateCmd('nowplaying', $this->getLogicalId());

		$this->allowDevice();
	}

	public static function createFromDef($_def) {
		event::add('jeedom::alert', array(
			'level' => 'warning',
			'page' => 'googlecast',
			'message' => __('Nouveau GoogleCast detecté', __FILE__),
		));
		if (!isset($_def['uuid']) || !isset($_def['def'])) {
			log::add('googlecast', 'error', 'Information manquante pour ajouter l\'équipement : ' . print_r($_def, true));
			event::add('jeedom::alert', array(
				'level' => 'danger',
				'page' => 'googlecast',
				'message' => __('Information manquante pour ajouter l\'équipement. Inclusion impossible', __FILE__),
			));
			return false;
		}

		$googlecast = googlecast::byLogicalId($_def['uuid'], 'googlecast');
		if (!is_object($googlecast)) {
			$eqLogic = new googlecast();
			$eqLogic->setName($_def['friendly_name']);
		}
		$eqLogic->setLogicalId($_def['uuid']);
		$eqLogic->setEqType_name('googlecast');
		$eqLogic->setIsEnable(1);
		$eqLogic->setIsVisible(1);
		$eqLogic->setConfiguration('device', $_def['def']['cast_type']);
		$eqLogic->setConfiguration('friendly_name', $_def['friendly_name']);
		$eqLogic->setConfiguration('model_name', $_def['def']['model_name']);
		$eqLogic->setConfiguration('manufacturer', $_def['def']['manufacturer']);
		$eqLogic->setConfiguration('cast_type', $_def['def']['cast_type']);
		$eqLogic->setConfiguration('cancontrol',1);
		$eqLogic->setConfiguration('needsrefresh',0);
		$eqLogic->setConfiguration('specificwidgets',0);
		#$eqLogic->setConfiguration('iconModel', 'niu/niu_' . strtolower($_def['color']));

		$eqLogic->save();



		event::add('jeedom::alert', array(
			'level' => 'warning',
			'page' => 'googlecast',
			'message' => __('Module inclu avec succès ' .$_def['friendly_name'], __FILE__),
		));
		return $eqLogic;
	}

	/*     * **********************Getteur Setteur*************************** */

	public static function deamon_info() {
		$return = array();
		$return['log'] = 'googlecast';
		$return['state'] = 'nok';
		$pid_file = '/tmp/googlecast.pid';
		if (file_exists($pid_file)) {
			if (@posix_getsid(trim(file_get_contents($pid_file)))) {
				$return['state'] = 'ok';
			} else {
				shell_exec('sudo rm -rf ' . $pid_file . ' 2>&1 > /dev/null;rm -rf ' . $pid_file . ' 2>&1 > /dev/null;');
			}
		}
		$return['launchable'] = 'ok';
		$socketport = config::byKey('socketport', 'googlecast');
		if ($socketport == '') {
			$return['launchable'] = 'nok';
			$return['launchable_message'] = __('Le port n\'est pas configuré', __FILE__);
		}
		return $return;
	}

	public static function dependancy_info() {
		$return = array();
		$return['log'] = 'googlecast_update';
		$return['progress_file'] = '/tmp/dependancy_googlecast_in_progress';
		if (exec('sudo pip list | grep -E "bluepy" | wc -l') < 1) {
			$return['state'] = 'nok';
		} else {
			$return['state'] = 'ok';
		}
		return $return;
	}

	public static function dependancy_install() {
		log::remove('googlecast_update');
		$cmd = 'sudo /bin/bash ' . dirname(__FILE__) . '/../../resources/install.sh';
		$cmd .= ' >> ' . log::getPathToLog('googlecast_dependancy') . ' 2>&1 &';
		exec($cmd);
	}

	public static function deamon_start() {
		self::deamon_stop();
		$deamon_info = self::deamon_info();
		if ($deamon_info['launchable'] != 'ok') {
			throw new Exception(__('Veuillez vérifier la configuration', __FILE__));
		}
		$port = "hey";
		$googlecast_path = realpath(dirname(__FILE__) . '/../../resources');
		$cmd = 'sudo /usr/bin/python3 ' . $googlecast_path . '/googlecast.py';
		$cmd .= ' --loglevel ' . log::convertLogLevel(log::getLogLevel('googlecast'));
		$cmd .= ' --device ' . $port;
		$cmd .= ' --socketport ' . config::byKey('socketport', 'googlecast');
		$cmd .= ' --sockethost 127.0.0.1';
		$cmd .= ' --callback ' . network::getNetworkAccess('internal', 'proto:127.0.0.1:port:comp') . '/plugins/googlecast/core/php/googlecast.api.php';
		$cmd .= ' --apikey ' . jeedom::getApiKey('googlecast');
		$cmd .= ' --daemonname local';
		log::add('googlecast', 'info', 'Lancement démon googlecast : ' . $cmd);
		$result = exec($cmd . ' >> ' . log::getPathToLog('googlecast_local') . ' 2>&1 &');
		$i = 0;
		while ($i < 30) {
			$deamon_info = self::deamon_info();
			if ($deamon_info['state'] == 'ok') {
				break;
			}
			sleep(1);
			$i++;
		}
		if ($i >= 30) {
			log::add('googlecast', 'error', __('Impossible de lancer le démon googlecast, vérifiez la log',__FILE__), 'unableStartDeamon');
			return false;
		}
		message::removeAll('googlecast', 'unableStartDeamon');
		config::save('include_mode', 0, 'googlecast');
		return true;
	}


	public static function socket_connection($_value) {
		$socket = socket_create(AF_INET, SOCK_STREAM, 0);
		socket_connect($socket, '127.0.0.1', config::byKey('socketport', 'googlecast'));
		socket_write($socket, $_value, strlen($_value));
		socket_close($socket);
	}

	public static function changeLogLive($_level) {
		$value = array('apikey' => jeedom::getApiKey('googlecast'), 'cmd' => $_level);
		$value = json_encode($value);
		self::socket_connection($value,True);
	}

	public static function deamon_stop() {
		$pid_file = '/tmp/googlecast.pid';
		if (file_exists($pid_file)) {
			$pid = intval(trim(file_get_contents($pid_file)));
			system::kill($pid);
		}
		system::kill('googlecast.py');
		system::fuserk(config::byKey('socketport', 'googlecast'));
		sleep(1);
	}

	public static function changeIncludeState($_state, $_mode) {
		if ($_mode == 1) {
			if ($_state == 1) {
				$value = json_encode(array('apikey' => jeedom::getApiKey('googlecast'), 'cmd' => 'learnin'));
				self::socket_connection($value,True);
			} else {
				$value = json_encode(array('apikey' => jeedom::getApiKey('googlecast'), 'cmd' => 'learnout'));
				self::socket_connection($value,True);
			}
		}
	}

	public static function sendIdToDeamon() {
		foreach (self::byType('googlecast') as $eqLogic) {
			$eqLogic->allowDevice();
			usleep(500);
		}
	}


	public function allowDevice() {
		$value = array('apikey' => jeedom::getApiKey('googlecast'), 'cmd' => 'add');

		if ($this->getLogicalId() != '') {
			$value['device'] = array(
				'uuid' => $this->getLogicalId(),
				'name' => $this->getConfiguration('friendly_name','Unknown')
			);
			$value = json_encode($value);
			self::socket_connection($value,True);
		}
	}


	public static function registerNowPlayging($uuid) {
		#$googlecast = googlecast::byLogicalId($uuid, 'googlecast');
		#if (!is_object($googlecast)) {
			$value = array('apikey' => jeedom::getApiKey('googlecast'), 'cmd' => 'nowplaying', 'uuid' => $uuid);
			$value = json_encode($value);
			self::socket_connection($value,True);
		#}
	}
/*
	public function followRealtime() {
		$value = array('apikey' => jeedom::getApiKey('googlecast'), 'cmd' => 'realtime');

		if ($this->getLogicalId() != '') {
			$value['device'] = array(
				'uuid' => $this->getLogicalId(),
				'name' => $this->getConfiguration('friendly_name','Unknown')
			);
			$value = json_encode($value);
			self::socket_connection($value,True);
		}
	}
*/
	public function disallowDevice() {
		if ($this->getLogicalId() == '') {
			return;
		}
		$value = json_encode(array('apikey' => jeedom::getApiKey('googlecast'), 'cmd' => 'remove', 'device' => array('uuid' => $this->getLogicalId())));
		self::socket_connection($value,True);
	}

	public function getCurrentPlaying($id) {
		$eqLogic = eqLogic::byId($id);
		if ($eqLogic) {
			$cmd = $eqLogic->getCmd(null, 'nowplaying');
			if (!is_object($cmd)) {
				$cmd->getCache('nowplaying');
			}
			return $eqLogic->getDisplayData();
		}
		return 'Error fetching '.$id;
	}

}

class googlecastcmd extends cmd {
	/*     * *************************Attributs****************************** */

	/*     * ***********************Methode static*************************** */

	/*     * *********************Methode d'instance************************* */

	public function execute($_options = null) {
		if ($this->getType() != 'action') {
			return;
		}
		$eqLogic = $this->getEqLogic();
		$listCmd = $this->getLogicalId();
		# special case of custom command
		if ($this->getLogicalId() == "customcmd") {
			$listCmd = trim($_options['message']);
		}
		$values = explode('|', $listCmd);
		foreach ($values as $value) {
			$value = explode('=', $value);
			if (count($value) == 2) {
				switch ($this->getSubType()) {
					case 'slider':
						$data[trim($value[0])] = trim(str_replace('#slider#', $_options['slider'], $value[1]));
						break;
					case 'color':
						$data[trim($value[0])] = str_replace('#','',trim(str_replace('#color#', $_options['color'], $value[1])));
						break;
					case 'select':
						$data[trim($value[0])] = trim(str_replace('#listValue#', $_options['select'], $value[1]));
						break;
					case 'message':
						$data[trim($value[0])] = trim(str_replace('#message#', $_options['message'], $value[1]));
						$data[trim($value[0])] = trim(str_replace('#title#', $_options['title'], $data[trim($value[0])]));
						break;
					default:
						$data[trim($value[0])] = trim($value[1]);
				}
			}
			elseif (count($value) == 1) {
				$data['cmd'] = trim($value[0]);
				switch ($this->getSubType()) {
					case 'slider':
						$data['value'] = $_options['slider'];
						break;
					case 'select':
						$data['value'] = trim($_options['select']);
						break;
					case 'message':
						$data['value'] = trim($_options['message']);
						break;
				}
			}
		}
		$data['device'] = array(
				'uuid' => $eqLogic->getLogicalId(),
				'delay' => $eqLogic->getConfiguration('delay',0),
				'needsrefresh' => $eqLogic->getConfiguration('needsrefresh',0),
				'name' => $eqLogic->getConfiguration('name','0'),
		);
		if (count($data) == 0) {
			return;
		}
		if ($this->getLogicalId() == 'refresh'){
			$data['name'] = $eqLogic->getConfiguration('name','0');
			$value = json_encode(array('apikey' => jeedom::getApiKey('googlecast'), 'cmd' => $this->getLogicalId(), 'device' => array('uuid' => $eqLogic->getLogicalId()), 'command' => $data));
		} else {
			$value = json_encode(array('apikey' => jeedom::getApiKey('googlecast'), 'cmd' => 'action', 'device' => array('uuid' => $eqLogic->getLogicalId()), 'command' => $data));
		}
		log::add('googlecast','debug',"Envoi d'une commande depuis Jeedom");
		googlecast::socket_connection($value);

	}

	/*     * **********************Getteur Setteur*************************** */
}
