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

require_once dirname(__FILE__) . "/googlecast_utils.inc.php";

class googlecast extends eqLogic
{
    /*     * *************************Attributs****************************** */

    private $_collectDate = '';
    public static $_widgetPossibility = array('custom' => true);
    private $_lightsave = false;

    const GCAST_MODELS = array(
        'chromecast audio' =>
            array('logo' => 'model_chromecast_audio.png', 'ga' => false),
        'chromecast ultra'  =>
            array('logo' => 'model_chromecast_video_ultra.png', 'ga' => false),
        'chromecast' =>
            array('logo' => 'model_chromecast_video.png', 'ga' => false),
        'google home mini' =>
            array('logo' => 'model_googlehome_mini.png', 'ga' => true),
        'google nest mini' =>
            array('logo' => 'model_googlehome_mini.png', 'ga' => true),
        'google home hub' =>
            array('logo' => 'model_googlehome_hub.png', 'ga' => true),
        'google nest hub' =>
            array('logo' => 'model_googlehome_hub.png', 'ga' => true),
        'google home' =>
            array('logo' => 'model_googlehome.png', 'ga' => true),
        'google home max' =>
            array('logo' => 'model_googlehome.png', 'ga' => true),
        'google cast group' =>
            array('logo' => 'model_castgroup.png', 'ga' => false),
        'tv' =>
            array('logo' => 'model_tv.png', 'ga' => false),
        'shield' =>
            array('logo' => 'model_androidtv.png', 'ga' => false),
        'android' =>
            array('logo' => 'model_androidtv.png', 'ga' => false)
    );

    /*     * ***********************Methode static*************************** */

    public static function cron15()
    {
        foreach (googlecast::byType('googlecast') as $eqLogic) {
            $eqLogic->refreshChromecastConfig();
            usleep(500);
        }
    }

    public static function cronDaily()
    {
        try {
            $nbdays = config::byKey('tts_cleancache_days', 'googlecast', '10');
            if ($nbdays != '') {
                googlecast::cleanTTScache(intval($nbdays));
            }
        } catch (Exception $e) {
        }
    }

    /*     * *********************Methode d'instance************************* */

    public function preUpdate()
    {
        if ($this->getIsEnable() == false) {
            $this->disallowDevice();
        }
        try {
            if (class_exists('gcastplayer')) {
                gcastplayer::changeEnableState($this->getLogicalId(), null, $this->getIsEnable());
            }
        } catch (Exception $e) {
        }


        // manage logo
        $found = false;
        $imgRoot = "plugins/googlecast/desktop/models/";
        $imgLogo = $imgRoot . 'model_default.png';
        $modelName = strtolower($this->getConfiguration('model_name', 'UNKOWN'));

        $has_gassistant = false;
        if (array_key_exists($modelName, googlecast::GCAST_MODELS)) {
            $imgLogo = $imgRoot . googlecast::GCAST_MODELS[$modelName]['logo'];
            $found = true;
            $has_gassistant = googlecast::GCAST_MODELS[$modelName]['ga'];
        }
        if (!$found) {	// try to guess based on model name aproximation
            foreach (googlecast::GCAST_MODELS as $key => $data) {
                if (strpos($key, $modelName) !== false) {
                    $imgLogo = $imgRoot . $data['logo'];
                    $has_gassistant = $data['ga'];
                    $found = true;
                    break;
                }
            }
        }
        if (!$found) {	// try to guess based on manufacturer
            $castType = $this->getConfiguration('cast_type');
            $manufName = strtolower($this->getConfiguration('manufacturer', 'UNKOWN'));
            if (strpos($manufName, 'google') !== false) {
                if ($castType=='audio') {
                    $imgLogo = $imgRoot . 'model_googlehome.png';
                }
                if ($castType=='cast') {
                    $imgLogo = $imgRoot . 'model_chromecast_video.png';
                }
                if ($castType=='group') {
                    $imgLogo = $imgRoot . 'model_castgroup.png';
                }
            }
            if (strpos($manufName, 'xiaomi') !== false) {
                $imgLogo = $imgRoot . 'model_androidtv.png';
            }
            if (strpos($manufName, 'nvidia') !== false) {
                $imgLogo = $imgRoot . 'model_androidtv.png';
            }
        }
        $this->setConfiguration('logoDevice', $imgLogo);

        if ($this->getConfiguration('has_googleassistant', '')==='') {
            // if not set
            if ($has_gassistant===true) {
                $this->setConfiguration('has_googleassistant', '1');
            } else {
                $this->setConfiguration('has_googleassistant', '0');
            }
        }
    }

    public function preRemove()
    {
        $this->disallowDevice();

        try {
            if (class_exists('gcastplayer')) {
                gcastplayer::changeEnableState($this->getLogicalId(), null, false);
            }
        } catch (Exception $e) {
        }
    }

    public function lightSave()
    {
        $this->_lightsave = true;
        $this->save();
        $this->_lightsave = false;
    }

    /*
    public function postSave() {
        if ( $this->getIsEnable() ) {
            $this->allowDevice();
            try {
                $this->refreshChromecastConfig();
            } catch (Exception $e) {}
        }
    }
    */

    //public function postInsert() {
    public function postSave()
    {
        if ($this->_lightsave == true) {
            return true;
        }
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

        $cmd = $this->getCmd(null, 'refreshconfig');
        if (!is_object($cmd)) {
            $cmd = new googlecastCmd();
            $cmd->setLogicalId('refreshconfig');
            $cmd->setName(__('Rafraîchir Config', __FILE__));
            $cmd->setIsVisible(0);
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
            $cmd->setConfiguration('googlecast_cmd', true);
        }
        $cmd->setTemplate('dashboard', 'googlecast_status');
        $cmd->setType('info');
        $cmd->setSubType('binary');
        $cmd->setEqLogic_id($this->getId());
        $cmd->setDisplay('generic_type', 'ENERGY_STATE');
        $cmd->save();

        // $cmd = $this->getCmd(null, 'reboot');
        // if (!is_object($cmd)) {
        // 	$cmd = new googlecastCmd();
        // 	$cmd->setLogicalId('reboot');
        // 	$cmd->setName(__('Restart', __FILE__));
        // 	$cmd->setIsVisible(1);
        // 	$cmd->setDisplay('icon', '<i class="fa fa-power-off"></i>');
        // 	$cmd->setConfiguration('googlecast_cmd', true);
        // }
        // $cmd->setTemplate('dashboard', 'googlecast_reboot');
        // $cmd->setType('action');
        // $cmd->setSubType('other');
        // $cmd->setEqLogic_id($this->getId());
        // $cmd->save();

        // hide reboot button if exists as it's not available anymore in latest googlecast versions
        $cmd = $this->getCmd(null, 'reboot');
        if (is_object($cmd)) {
            // $cmd->remove();
            $cmd->setIsVisible(0);
            $cmd->save();
        }

        $cmd = $this->getCmd(null, 'is_busy');
        if (!is_object($cmd)) {
            $cmd = new googlecastCmd();
            $cmd->setLogicalId('is_busy');
            $cmd->setIsVisible(1);
            $cmd->setName(__('Occupé', __FILE__));
            $cmd->setConfiguration('googlecast_cmd', true);
        }
        $cmd->setTemplate('dashboard', 'googlecast_busy');
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
            $cmd->setTemplate('mobile', 'circle');
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
            $cmd->setTemplate('mobile', 'circle');
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
            //$cmd->setDisplay('icon', '<i class="icon techno-tv"></i>');
            $cmd->setOrder($order++);
        }
        $cmd->setType('info');
        $cmd->setSubType('string');
        $cmd->setEqLogic_id($this->getId());
        $cmd->setDisplay('generic_type', 'GENERIC');
        $cmd->save();

        $cmd = $this->getCmd(null, 'display_name');
        if (!is_object($cmd)) {
            $cmd = new googlecastCmd();
            $cmd->setLogicalId('display_name');
            $cmd->setIsVisible(0);
            $cmd->setName(__('Statut Name', __FILE__));
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
            $cmd->setOrder($order++);
        }
        $cmd->setType('info');
        $cmd->setSubType('string');
        $cmd->setEqLogic_id($this->getId());
        $cmd->setDisplay('generic_type', 'GENERIC');
        $cmd->save();

        $cmd = $this->getCmd(null, 'title');
        if (!is_object($cmd)) {
            $cmd = new googlecastCmd();
            $cmd->setLogicalId('title');
            $cmd->setIsVisible(0);
            $cmd->setName(__('Titre', __FILE__));
            $cmd->setConfiguration('googlecast_cmd', true);
            $cmd->setOrder($order++);
        }
        $cmd->setType('info');
        $cmd->setSubType('string');
        $cmd->setEqLogic_id($this->getId());
        $cmd->setDisplay('generic_type', 'GENERIC');
        $cmd->save();

        $cmd = $this->getCmd(null, 'artist');
        if (!is_object($cmd)) {
            $cmd = new googlecastCmd();
            $cmd->setLogicalId('artist');
            $cmd->setIsVisible(0);
            $cmd->setName(__('Artiste', __FILE__));
            $cmd->setConfiguration('googlecast_cmd', true);
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

        $cmd = $this->getCmd(null, 'prev');
        if (!is_object($cmd)) {
            $cmd = new googlecastCmd();
            $cmd->setLogicalId('prev');
            $cmd->setName(__('Previous', __FILE__));
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
            $cmd->setName(__('Next', __FILE__));
            $cmd->setIsVisible(1);
            $cmd->setDisplay('icon', '<i class="fa fa-step-forward"></i>');
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
            $cmd->setConfiguration('googlecast_cmd', true);
            $cmd->setOrder($order++);
        }
        $cmd->setDisplay('icon', '<i class="fa fa-backward"></i>');
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
            $cmd->setConfiguration('googlecast_cmd', true);
            $cmd->setOrder($order++);
        }
        $cmd->setTemplate('dashboard', 'googlecast_playing');
        $cmd->setTemplate('mobile', 'googlecast_playing');
        $cmd->setType('info');
        $cmd->setSubType('string');
        $cmd->setEqLogic_id($this->getId());
        $cmd->save();

        $cmd = $this->getCmd(null, 'castversion');
        if (!is_object($cmd)) {
            $cmd = new googlecastCmd();
            $cmd->setLogicalId('castversion');
            $cmd->setName(__('version', __FILE__));
            $cmd->setIsVisible(1);
            $cmd->setOrder($order++);
            $cmd->setConfiguration('googlecast_cmd', true);
        }
        $cmd->setType('info');
        $cmd->setSubType('string');
        $cmd->setEqLogic_id($this->getId());
        $cmd->save();

        $cmd = $this->getCmd(null, 'speak');
        if (!is_object($cmd)) {
            $cmd = new googlecastCmd();
            $cmd->setLogicalId('speak');
            $cmd->setName(__('Parle !', __FILE__));
            $cmd->setIsVisible(1);
            $cmd->setOrder($order++);
            $cmd->setConfiguration('googlecast_cmd', true);
        }
        $cmd->setTemplate('dashboard', 'googlecast_speak');
        $cmd->setTemplate('mobile', 'googlecast_speak');
        $cmd->setType('action');
        $cmd->setSubType('message');
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

        $cmd = $this->getCmd(null, 'cmdlist_radiolist');
        if (!is_object($cmd)) {
            $cmd = new googlecastCmd();
            $cmd->setLogicalId('cmdlist_radiolist');
            $cmdname = $this->getNonExistCmdName(__('Radio', __FILE__));
            $cmd->setName($cmdname);
            $cmd->setIsVisible(1);
            if ($order<=3) {
                $order=50;
            }
            $cmd->setOrder($order++);
            $cmd->setEqLogic_id($this->getId());
            $radiolist = googlecast_utils::buildRadioSelectlist();
            $cmd->setConfiguration('listValue', $radiolist);
        }
        $cmd->setType('action');
        $cmd->setSubType('select');
        $cmd->save();

        $castType = $this->getConfiguration('cast_type');
        if ($this->getConfiguration('firstTimeCreation', true)) {
            $order = 200;

            if ($castType=='cast') {
                $logid = "app=backdrop";
                $cmd = $this->getCmd(null, $logid);
                if (!is_object($cmd)) {
                    $cmd = new googlecastCmd();
                    $cmd->setLogicalId($logid);
                    $cmd->setName(__('Backdrop', __FILE__));
                    $cmd->setIsVisible(1);
                    $cmd->setOrder($order++);
                    $cmd->setType('action');
                    $cmd->setSubType('other');
                    $cmd->setEqLogic_id($this->getId());
                    $cmd->save();
                }

                $logid = "app=youtube|cmd=play_video|value=fra4QBLF3GU";
                $cmd = $this->getCmd(null, $logid);
                if (!is_object($cmd)) {
                    $cmd = new googlecastCmd();
                    $cmd->setLogicalId($logid);
                    $cmd->setName(__('YouTube', __FILE__));
                    $cmd->setIsVisible(1);
                    $cmd->setOrder($order++);
                    $cmd->setType('action');
                    $cmd->setSubType('other');
                    $cmd->setEqLogic_id($this->getId());
                    $cmd->save();
                }
            }

            $logid = "app=media|cmd=play_media|value='http://bit.ly/2JzYtfX','video/mp4','Mon film'";
            $cmd = $this->getCmd(null, $logid);
            if (!is_object($cmd)) {
                $cmd = new googlecastCmd();
                $cmd->setLogicalId($logid);
                $cmd->setName(__('Media', __FILE__));
                $cmd->setIsVisible(1);
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
                $cmd->setOrder($order++);
            }
            $cmd->setType('action');
            $cmd->setSubType('other');
            $cmd->setEqLogic_id($this->getId());
            $cmd->save();

            $logid = "cmd=notif|value=bigben1.mp3|vol=100";
            $cmd = $this->getCmd(null, $logid);
            if (!is_object($cmd)) {
                $cmd = new googlecastCmd();
                $cmd->setLogicalId($logid);
                $cmd->setName(__('Notif', __FILE__));
                $cmd->setIsVisible(1);
                $cmd->setOrder($order++);
            }
            $cmd->setType('action');
            $cmd->setSubType('other');
            $cmd->setEqLogic_id($this->getId());
            $cmd->save();

            // $cmd = $this->getCmd(null, 'cmd=getconfig|data=opencast_pin_code');
            // if (!is_object($cmd)) {
            // 	$cmd = new googlecastCmd();
            // 	$cmd->setLogicalId('cmd=getconfig|data=opencast_pin_code');
            // 	$cmd->setName(__('Pincode', __FILE__));
            // 	$cmd->setIsVisible(0);
            // 	$cmd->setOrder($order++);
            // }
            // $cmd->setType('info');
            // $cmd->setSubType('string');
            // $cmd->setEqLogic_id($this->getId());
            // $cmd->save();

            $this->setConfiguration('firstTimeCreation', false);
            $this->save();
        }

        if (intval($this->getConfiguration('has_googleassistant', '0')) == 1) {
            //$order = googlecast_utils::getCmdDefinition($this, 'googlehome', 210);
        }
        
        // fix to be able to remove old gh_* commands
        $cmd = $this->getCmd(null, 'gh_get_alarm_date_0');
        if (is_object($cmd)) {
            $cmd->setConfiguration('googlecast_cmd', false);
            $cmd->save();
        }
        $cmd = $this->getCmd(null, 'gh_get_alarm_status_0');
        if (is_object($cmd)) {
            $cmd->setConfiguration('googlecast_cmd', false);
            $cmd->save();
        }
        // -- end fix
        
        $this->checkAndUpdateCmd('nowplaying', $this->getLogicalId());

        if ($this->getIsEnable()) {
            $this->allowDevice();
            try {
                $this->refreshChromecastConfig();
            } catch (Exception $e) {
            }
        }
    }

    public static function createFromDef($_def)
    {
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
        $eqLogic->setConfiguration('uri', $_def['def']['uri']);
        $eqLogic->setConfiguration('ip', $eqLogic->getChromecastIPfromURI());
        $eqLogic->save();

        event::add('jeedom::alert', array(
            'level' => 'warning',
            'page' => 'googlecast',
            'message' => __('Module inclu avec succès ' .$_def['friendly_name'], __FILE__),
        ));
        return $eqLogic;
    }

    public function getNonExistCmdName($cmdname)
    {
        $new_cmdname = $cmdname;
        if (cmd::byEqLogicIdCmdName($this->getId(), $new_cmdname)) {
            $new_cmdname = 'Radio_' . strtotime("now");
        }
        return $new_cmdname;
    }

    public function getChromecastIPfromURI()
    {
        $uri = $this->getConfiguration('uri', '');

        if (strpos($uri, '[') === 0) {     // ipv6
            $exploded = explode("]:", $uri);
            $ip = substr($exploded[0], 1);
            if (strrpos($ip, ']') + strlen(']') === strlen($ip)) {
                $ip = substr($ip, -1);
            }
        } else {                          // ipv4
            $exploded = explode(":", $uri);
            $ip = $exploded[0];
        }
        return $ip;
    }

    public function getChromecastIP()
    {
        return $this->getConfiguration('ip', '');
    }

    public function getUUID()
    {
        return $this->getConfiguration('uuid', '');
    }

    public function getChromecastURI()
    {
        return $this->getConfiguration('uri', '');
    }

    public function refreshChromecastConfig()
    {
        $cmd = $this->getCmd(null, 'refreshconfig');
        if (is_object($cmd)) {
            return $cmd->execute();
        }
        return false;
    }

    /*     * **********************Getteur Setteur*************************** */

    public static function deamon_info()
    {
        $return = array();
        $return['log'] = 'googlecast';
        $return['state'] = 'nok';
        $pid_file = '/tmp/googlecast.pid';
        if (file_exists($pid_file)) {
            if (@posix_getsid(trim(file_get_contents($pid_file)))) {
                $return['state'] = 'ok';
            } else {
                shell_exec(system::getCmdSudo() . 'rm -rf ' . $pid_file . ' 2>&1 > /dev/null;rm -rf ' . $pid_file . ' 2>&1 > /dev/null;');
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

    public static function dependancy_info()
    {
        $return = array();
        $return['log'] = 'googlecast_update';
        $return['progress_file'] = '/tmp/dependancy_googlecast_in_progress';
        $cmd = system::getCmdSudo() . '/bin/bash ' . dirname(__FILE__) . '/../../resources/install_check.sh';
        if (exec($cmd) == "ok") {
            $return['state'] = 'ok';
        } else {
            $return['state'] = 'nok';
        }
        return $return;
    }

    public static function dependancy_install()
    {
        log::remove(__CLASS__ . '_update');
        return array('script' => dirname(__FILE__) . '/../../resources/install.sh', 'log' => log::getPathToLog(__CLASS__ . '_update'));
    }

    public static function getVersion()
    {
        $pluginVersion = 'Error';
        if (!file_exists(dirname(__FILE__) . '/../../plugin_info/info.json')) {
            log::add('googlecast', 'warning', 'Pas de fichier info.json');
        }
        $data = json_decode(file_get_contents(dirname(__FILE__) . '/../../plugin_info/info.json'), true);
        if (!is_array($data)) {
            log::add('googlecast', 'warning', 'Impossible de décoder le fichier info.json');
        }
        try {
            $pluginVersion = $data['version'];
        } catch (\Exception $e) {
            log::add('googlecast', 'warning', 'Impossible de récupérer la version.');
        }

        return $pluginVersion;
    }

    public static function dependancy_runlightinstall()
    {
        $shellret = shell_exec(system::getCmdSudo() . '/bin/bash ' . __DIR__ . '/../../resources/update.sh' . ' ' . __DIR__ . '/../../resources/requirements.txt 2>&1');
        log::add('googlecast', 'debug', "Light dependency update script logs :\n" . $shellret);
    }


    public static function deamon_start()
    {
        self::deamon_stop();
        $deamon_info = self::deamon_info();
        if ($deamon_info['launchable'] != 'ok') {
            throw new Exception(__('Veuillez vérifier la configuration', __FILE__));
        }
        $googlecast_path = realpath(dirname(__FILE__) . '/../../resources');
        $cmd = '/usr/bin/python3 ' . $googlecast_path . '/googlecast.py';
        #$cmd .= ' --scantimeout 10';
        $cmd .= ' --loglevel ' . log::convertLogLevel(log::getLogLevel('googlecast'));
        $cmd .= ' --socketport ' . config::byKey('socketport', 'googlecast');
        $cmd .= ' --sockethost 127.0.0.1';
        $jeedomurl = (config::byKey('fixdocker', 'googlecast')==0 ? network::getNetworkAccess('internal', 'proto:127.0.0.1:port:comp') : network::getNetworkAccess('internal'));
        $cmd .= ' --callback ' . $jeedomurl . '/plugins/googlecast/core/php/googlecast.api.php';
        $cmd .= ' --apikey ' . jeedom::getApiKey('googlecast');
        if (config::byKey('tts_externalweb', 'googlecast')==1) {
            $cmd .= ' --ttsweb ' . network::getNetworkAccess('external');
        } else {
            $cmd .= ' --ttsweb ' . network::getNetworkAccess('internal');
        }
        $cmd .= ' --ttslang ' . config::byKey('tts_language', 'googlecast', 'fr-FR');
        $cmd .= ' --ttsengine ' . config::byKey('tts_engine', 'googlecast', 'picotts');
        $cmd .= ' --ttsspeed ' . config::byKey('tts_speed', 'googlecast', '1.2');
        if (config::byKey('tts_disablecache', 'googlecast')==1) {
            $cmd .= ' --ttscache 0';
        } else {
            $cmd .= ' --ttscache 1';
        }
        $cmd .= ' --ttsgapikey ' . config::byKey('tts_gapikey', 'googlecast', 'none');
        $cmd .= ' --gcttsvoice ' . config::byKey('gctts_voice', 'googlecast', 'fr-FR-Standard-A');
        $cmd .= ' --daemonname local';
        $cmd .= ' --cyclefactor ' . config::byKey('cyclefactor', 'googlecast', '1');
        $cmd .= ' --defaultstatus ' . "'". config::byKey('defaultsatus', 'googlecast', "&nbsp;") ."'";
        log::add('googlecast', 'info', 'Lancement démon googlecast : ' . $cmd);
        $result = exec($cmd . ' >> ' . log::getPathToLog('googlecast_local') . ' 2>&1 &');
        $i = 0;
        while ($i < 20) {
            $deamon_info = self::deamon_info();
            if ($deamon_info['state'] == 'ok') {
                break;
            }
            sleep(1);
            $i++;
        }
        if ($i >= 30) {
            log::add('googlecast', 'error', __('Impossible de lancer le démon googlecast, vérifiez la log', __FILE__), 'unableStartDeamon');
            return false;
        }
        message::removeAll('googlecast', 'unableStartDeamon');
        config::save('include_mode', 0, 'googlecast');
        return true;
    }


    public static function socket_connection($_value)
    {
        try {
            $socket = socket_create(AF_INET, SOCK_STREAM, 0);
            @socket_connect($socket, '127.0.0.1', config::byKey('socketport', 'googlecast'));
            @socket_write($socket, $_value, strlen($_value));
            @socket_close($socket);
            return true;
        } catch (Exception $e) {
            return false;
        }
    }

    public static function cleanTTScache($days=0)
    {
        $value = json_encode(array('apikey' => jeedom::getApiKey('googlecast'), 'cmd' => 'cleanttscache', 'days' => $days));
        self::socket_connection($value);
    }

    public static function testAddress($useExternal=null)
    {
        if ($useExternal===null) {
            $useExternal = config::byKey('tts_externalweb', 'googlecast');
        }

        $testAddress = '';
        if ($useExternal===1 || $useExternal===true || $useExternal==='true') {
            $testAddress .= network::getNetworkAccess('external');
        } else {
            $testAddress .= network::getNetworkAccess('internal');
        }
        return $testAddress . "/plugins/googlecast/localmedia/bigben1.mp3";
    }

    public static function deamon_stop()
    {
        $pid_file = '/tmp/googlecast.pid';
        if (file_exists($pid_file)) {
            $pid = intval(trim(file_get_contents($pid_file)));
            system::kill($pid);
        }
        system::kill('googlecast.py');
        system::fuserk(config::byKey('socketport', 'googlecast'));
        sleep(1);
    }

    public static function changeIncludeState($_state, $_mode)
    {
        if ($_mode == 1) {
            if ($_state == 1) {
                $value = json_encode(array('apikey' => jeedom::getApiKey('googlecast'), 'cmd' => 'learnin'));
                self::socket_connection($value);
            } else {
                $value = json_encode(array('apikey' => jeedom::getApiKey('googlecast'), 'cmd' => 'learnout'));
                self::socket_connection($value);
            }
        }
    }

    public static function sendDisplayAction($_uuid, $_cmd, $_options = null)
    {
        if ($_cmd == "customcmd" and !isset($_options['message'])) {
            return false;	// message is mandatory for customcmd
        }
        $eqLogic = eqLogic::byId($_uuid);
        if ($eqLogic) {
            $cmd = $eqLogic->getCmd(null, $_cmd);
            if (is_object($_cmd)) {
                $cmd->execute($_options);
                return true;
            }
        }
        return false;
    }

    public static function sendIdToDeamon()
    {
        foreach (self::byType('googlecast') as $eqLogic) {
            $eqLogic->allowDevice();
            usleep(500);
        }
    }

    public static function manageCallback($data)
    {
        // TODO
        log::add('googlecast', 'debug', 'Received callcak command for ' . $data['uuid']);
    }

    public static function registerNowPlayging($uuid)
    {
        $value = array('apikey' => jeedom::getApiKey('googlecast'), 'cmd' => 'nowplaying', 'uuid' => $uuid);
        $value = json_encode($value);
        self::socket_connection($value);
    }


    public function allowDevice()
    {
        $value = array('apikey' => jeedom::getApiKey('googlecast'), 'cmd' => 'add');

        if ($this->getLogicalId() != '') {
            $value['device'] = array(
                'uuid' => $this->getLogicalId(),
                'options' => array(
                    'ignore_CEC' => $this->getConfiguration('ignore_CEC', '0')
                )
            );
            $value = json_encode($value);
            self::socket_connection($value);
        }
    }

    public function disallowDevice()
    {
        if ($this->getLogicalId() == '') {
            return;
        }
        $value = json_encode(array('apikey' => jeedom::getApiKey('googlecast'), 'cmd' => 'remove', 'device' => array('uuid' => $this->getLogicalId())));
        self::socket_connection($value);
    }


    public function refreshStatusAll()
    {
        $value = array('apikey' => jeedom::getApiKey('googlecast'),
                'cmd' => 'refreshall');
        $value = json_encode($value);
        self::socket_connection($value);
    }

    public function refreshStatusByUUID($uuid)
    {
        $value = array('apikey' => jeedom::getApiKey('googlecast'),
                'cmd' => 'refresh',
                'uuid' => $uuid);
        $value = json_encode($value);
        self::socket_connection($value);
    }

    public function helperSendSimpleCmd($command_name, $value=null, $_callback=null, $_source='googlecast', $_app='media', $_appid='CC1AD845')
    {
        $command_name = googlecast_utils::getFullCmdTranslation($command_name);
        $fulldata = array(
            'apikey' => jeedom::getApiKey('googlecast'),
            'cmd' => 'action',
            'device' => array(
                'uuid' => $this->getLogicalId(),
                'source' => $_source,
                'callback' => $_callback,
            ),
            'command' => array(
                'cmd' => $command_name,
                'value' => ($value!==null ? $value : ''),
                'app' => $_app,
                'appid' => $_appid,
            ),
        );

        return self::socket_connection(json_encode($fulldata));
    }

    public static function helperSendNotifandWait_static($uuid, $_commands, $maxwait=30, $retrydelay=500, $initialdelay=2)
    {
        $googlecast = googlecast::byLogicalId($uuid, 'googlecast');
        if (!is_object($googlecast)) {
            return false;
        } else {
            return $googlecast->helperSendNotifandWait($_commands, $maxwait, $retrydelay, $initialdelay);
        }
    }

    public function helperSendNotifandWait($_commands, $maxwait=30, $retrydelay=500, $initialdelay=2)
    {
        $retrydelay = $retrydelay*1000;

        if ($this->getIsEnable()==false or $this->isOnline()==false) {
            return false;
        } else {
            $this->helperSendCustomCmd($_commands);
            sleep($initialdelay); // make sure command has started
            $status = $this->getInfoValue('status_text');
            $starttime = time();
            while ($status=='Casting: TTS' or $status=='Casting: NOTIF') {
                usleep($retrydelay);    // or sleep(1);	// 1 sec
                $status = $this->getInfoValue('status_text');
                if ((time()-$starttime)>$maxwait) {
                    return false;
                }
            }
            return true;
        }
    }

    // send commands as php array of by sequence (seperated by $$)
    public function helperSendCustomCmd($_commands, $_callback=null, $_source='googlecast', $_app='media', $_appid='CC1AD845')
    {
        $datalist = array();
        $commandlist = $_commands;
        if (!is_array($_commands)) {
            $commandlist = explode('$$', $_commands);
        }
        foreach ($commandlist as $commandstring) {
            $commandstring = googlecast_utils::getFullCmdTranslation($commandstring);

            $data = array();
            $splitcmd = explode('|', $commandstring);
            $splitcount = count($splitcmd);
            foreach ($splitcmd as $value) {
                $value = explode('=', $value);
                // ex: cmd=set_volume|value=10
                if (count($value) == 2) {
                    $data[trim($value[0])] = trim($value[1]);
                }
                // ex: cmd=play  (no value=X and single param)
                elseif (count($value) == 1 && $splitcount==1) {
                    $data['cmd'] = trim($value[0]);
                    $data['value'] = 0;
                }
                // ex: cmd=set_volume|value=10|refresh (refresh is set to 1)
                elseif (count($value) == 1 && $splitcount>1) {
                    $data[trim($value[0])] = 1;
                }
            }
            if (!isset($data['app']) && !is_null($_app)) {
                $data['app'] = $_app;
            }
            if (!isset($data['appid']) && !is_null($_appid)) {
                $data['appid'] = $_appid;
            }
            array_push($datalist, $data);
        }
        log::add('googlecast', 'debug', 'helperSendCustomCmd : ' . print_r($datalist, true));

        $fulldata = array(
            'apikey' => jeedom::getApiKey('googlecast'),
            'cmd' => 'action',
            'device' => array(
                'uuid' => $this->getLogicalId(),
                'source' => $_source,
                'callback' => $_callback,
            ),
            'command' => $datalist,
        );

        return self::socket_connection(json_encode($fulldata));
    }

    public function helperSendConfigInfoCmd($_commands, $_destLogicalId, $setType=false, $_callback=null, $showError=false)
    {
        if ($setType==false) {
            $ret = $this->getInfoHttp($_commands, $showError, false, 'json', ',', null, $_destLogicalId);
        } else {
            $ret = $this->setInfoHttp($_commands, $showError, $_destLogicalId);
        }
        return $ret;
    }

    public function getInfoHttpSimple($cmdLogicalId, $destLogicalId=null)
    {
        $cmdLogicalIdTranslate = googlecast_utils::getFullCmdTranslation($cmdLogicalId);
        if (is_null($destLogicalId)) {
            $destLogicalId = ($cmdLogicalIdTranslate!=$cmdLogicalId ? $cmdLogicalId : null);
        }
        return $this->getInfoHttp($cmdLogicalIdTranslate, false, false, 'string', ',', null, $destLogicalId);
    }

    public function getInfoHttp($cmdLogicalId, $showError=false, $errorRet=false, $format='string', $sep=',', $fnc=null, $destLogicalId=null, $updatecmd=true)
    {
        log::add('googlecast', 'debug', "getInfoHttp : " . $cmdLogicalId);
        $uri = $this->getChromecastIP();
        $cmd = $this->getCmd(null, (!is_null($destLogicalId)?$destLogicalId:$cmdLogicalId));
        $has_cmd = false;
        if (is_object($cmd)) {
            $has_cmd = true;
        }
        $listCmd = $cmdLogicalId;

        $datalist=array();
        $cmdgroups = explode('$$', $listCmd);
        foreach ($cmdgroups as $listCmd) {
            $data = array();
            $values = explode('|', $listCmd);
            foreach ($values as $value) {
                $value = explode('=', $value);
                if (count($value) == 2) {
                    $data[trim($value[0])] = trim($value[1]);
                }
            }
            if (count($data) == 0) {
                return;
            }
            array_push($datalist, $data);
        }

        foreach ($datalist as $data) {
            if (isset($data['cmd']) && $data['cmd'] == 'getconfig') {
                if (isset($data['error']) && ($data['error']==1 or $data['error']=='true')) {
                    $showError = true;
                }
                if (isset($data['reterror'])) {
                    $errorRet = $data['reterror'];
                }
                if (isset($data['fnc'])) {
                    $fnc = $data['fnc'];
                }
                if (isset($data['noupdatecmd'])) {
                    $updatecmd = false;
                }
                if (isset($data['format'])) {
                    $format = $data['format'];
                }
                $isPost = false;
                $isSSL = false;
                if (isset($data['value']) && $data['value']!='eureka_info') {
                    $uripath = $data['value'];
                    if (strpos($uripath, 'post:') === 0) {
                        $isPost = true;
                        $uripath = str_replace('post:', '', $uripath);
                    }
                    $isSSL = true;
                    $url = 'https://' . $uri . ':8443/setup/' . $uripath. '?options=detail';
                } else {
                    $url = 'http://' . $uri . ':8008/setup/eureka_info?options=detail';
                }
                $request_http = new com_http($url);

                $has_error = false;
                $headers = array();
                if ($isSSL) {
                    $gatoken = $this->getConfiguration('ga_token', '');
                    if ($gatoken == '') {
                        log::add('googlecast', 'warning', __('Le jeton Google Home n\'est pas configuré!', __FILE__));
                        $gatoken = 'none';
                    }
                    $request_http->setNoSslCheck(true);
                    array_push($headers, 'cast-local-authorization-token: ' . $gatoken);
                }
                if ($isPost) {
                    $request_http->setPost('');
                    array_push($headers, 'Connection: close', 'content-type: application/json');
                }
                if (count($headers)>0) {
                    $request_http->setHeader($headers);
                }
                try {
                    $httpret = $request_http->exec($_timeout=1, $_maxRetry=1);
                    $arrayret = json_decode($httpret, true);
                } catch (Exception $e) {
                    $has_error = true;
                }

                // for test
                //$httpret = '{"alarm":[{"date_pattern":{"day":13,"month":6,"year":2018},"fire_time":1528909200000.0,"id":"alarm/5b205564-0000-27be-9e26-089e082ee87c","status":1,"time_pattern":{"hour":13,"minute":0,"second":0}}],"timer":[]}';
                //$arrayret = json_decode($httpret, true);

                if (isset($arrayret)) {
                    log::add('googlecast', 'debug', 'Request response content : ' . print_r($arrayret, true));
                }
                if ($has_error===true or ($arrayret and count($arrayret)==0)) {
                    if ($showError==true) {
                        log::add('googlecast', 'error', __('Configuration non accessible', __FILE__));
                    }
                    if ($has_error===true) {
                        log::add('googlecast', 'debug', "getInfoHttp : Error while accessing device (offline ?)");
                    } else {
                        log::add('googlecast', 'debug', "getInfoHttp : Result is empty (device compatible ?)");
                    }
                    if ($has_cmd===true and $errorRet===false) {
                        $ret = $cmd->execCmd();
                        log::add('googlecast', 'debug', "getInfoHttp : Result error (previous result) : " . $ret);
                    }
                    if ($errorRet!==false) {
                        $ret = $errorRet;
                    }
                    $retSave = $ret;
                    $ret = googlecast_utils::getFncResult($ret, $fnc);
                    log::add('googlecast', 'debug', "getInfoHttp : Result error (with default) : " . $retSave . " => " . $ret);

                    if ($format=='json') {
                        $ret = json_encode($ret);
                    }
                    if ($has_cmd===true and $updatecmd===true) {
                        $cmd->event($ret);
                    }

                    return $ret;
                }

                // for test
                //$httpret = '{"alarm":[{"date_pattern":{"day":15,"month":1,"year":2018},"time_pattern":{"hour":6,"minute":50,"second":0},"fire_time":1515995400000.0,"id":"alarm/xxx","status":1}]}';
                //$arrayret = json_decode($httpret, true);

                if (isset($data['data'])) {
                    $dataItemList = explode(',', $data['data']);
                    $retArray = array();
                    foreach ($dataItemList as $dataItem) {
                        if (strpos($dataItem, '$') === 0) {   // jsonpath type
                            array_push($retArray, googlecast_utils::getJsonPathResult($httpret, $dataItem));
                        } else {  // legacy using '/' as separator
                            $pathList = explode('/', $dataItem);
                            array_push($retArray, $this->recursePath($arrayret, $pathList, $errorRet));
                        }
                    }

                    if ($format=='json') {
                        $ret = json_encode($retArray);
                    } elseif ($format=='php') {
                        return $retArray;
                    } elseif ($format=='string') {
                        $flattenAr = $this->array_flatten($retArray);
                        //log::add('googlecast','debug',"getInfoHttp : Debug format string : " . print_r($flattenAr, true));
                        $ret = join($sep, $flattenAr);
                    } else {
                        $ret = '';
                        foreach ($retArray as $retElem) {
                            $ret .=  $sep . $this->formatString($retElem, $format, $errorRet);
                        }
                        $ret = substr($ret, 1);
                    }
                    $retsave = $ret;
                    $ret = googlecast_utils::getFncResult($ret, $fnc);
                    if ($ret=='' && $errorRet!==false) {
                        $ret = $errorRet;
                    }
                    log::add('googlecast', 'debug', "getInfoHttp : Result success : " . $retsave . " => " . $ret);

                    if ($has_cmd===true and $updatecmd===true) {
                        $cmd->event($ret);
                    }
                } else {
                    $ret = json_encode($arrayret);
                    if ($has_cmd===true) {
                        $cmd->event($ret);
                    }
                }
                return $ret;
            }
        }
    }

    private function formatString($array, $format, $errorRet)
    {
        if (!is_array($array) && ($array=='unknown' or $array==$errorRet)) {
            return $array;
        }
        $array = json_decode($array, true);
        $flattenArray = $this->array_flatten($array);
        $ret = vsprintf($format, $flattenArray);
        return $ret;
    }

    private function array_flatten($array)
    {
        $return = array();
        foreach ($array as $key => $value) {
            if (is_array($value)) {
                $return = array_merge($return, $this->array_flatten($value));
            } else {
                $return[$key] = $value;
            }
        }
        return $return;
    }

    // old version using '/' as path sepearator
    private function recursePath($array, $pathList, $errorRet)
    {
        $pathItem = array_shift($pathList);
        if (is_null($pathItem)) {
            if (is_array($array)) {
                return json_encode($array);
            } else {
                return $array;
            }
        }
        if (is_null($array)) {
            return $errorRet;
        }
        if (is_numeric($pathItem) && isset($array[intval($pathItem)])) {
            return $this->recursePath($array[intval($pathItem)], $pathList, $errorRet);
        } elseif (array_key_exists($pathItem, $array)) {
            return $this->recursePath($array[$pathItem], $pathList, $errorRet);
        } elseif (isset($array[0]) && count($array)==1) {
            return $this->recursePath($array[0], $pathList, $errorRet);
        }
        return ($errorRet!=false?$errorRet:'unknown');
    }

    public function setInfoHttpSimple($cmdLogicalId, $destLogicalId=null)
    {
        $cmdLogicalId = googlecast_utils::getFullCmdTranslation($cmdLogicalId);
        return $this->setInfoHttp($cmdLogicalId, false, $destLogicalId);
    }

    public function setInfoHttp($cmdLogicalId, $showError=false, $destLogicalId=null)
    {
        $uri = $this->getChromecastIP();
        $hasCmd = false;
        if (!is_null($destLogicalId)) {
            $cmd = $this->getCmd(null, $destLogicalId);
            $hasCmd = false;
            if (is_object($cmd)) {
                $hasCmd = true;
            }
        }
        $listCmd = $cmdLogicalId;

        $datalist=array();
        $cmdgroups = explode('$$', $listCmd);
        foreach ($cmdgroups as $listCmd) {
            $data = array();
            $values = explode('|', $listCmd);
            foreach ($values as $value) {
                $value = explode('=', $value);
                if (count($value) == 2) {
                    $data[trim($value[0])] = trim($value[1]);
                }
            }
            if (count($data) == 0) {
                return;
            }
            array_push($datalist, $data);
        }

        foreach ($datalist as $data) {
            if (isset($data['cmd']) && $data['cmd'] == 'setconfig') {
                if (isset($data['error']) && ($data['error']==1 or $data['error']=='true')) {
                    $showError = true;
                }
                $isSSL = false;
                if (isset($data['value']) && $data['value']!='set_eureka_info') {
                    $url = 'https://' . $uri . ':8443/setup/' . $data['value'];
                    $isSSL = true;
                } else {
                    $url = 'http://' . $uri . ':8008/setup/set_eureka_info';
                }
                $request_http = new com_http($url);
                
                $headers = array('content-type: application/json');
                if ($isSSL) {
                    $gatoken = $this->getConfiguration('ga_token', '');
                    if ($gatoken == '') {
                        log::add('googlecast', 'warning', __('Le jeton Google Home n\'est pas configuré!', __FILE__));
                        $gatoken = 'none';
                    }
                    $request_http->setNoSslCheck(true);
                    array_push($headers, 'cast-local-authorization-token: ' . $gatoken);
                }
                
                $request_http->setHeader($headers);
                $request_http->setPost((isset($data['data']) ? $data['data'] : ''));
                try {
                    $httpret = $request_http->exec();
                    log::add('googlecast', 'debug', 'setInfoHttp : Result : ' . $httpret);
                } catch (Exception $e) {
                    if ($showError==true) {
                        log::add('googlecast', 'error', __('Configuration non accessible', __FILE__));
                    }
                    return false;
                }
                if ($hasCmd==true) {
                    $ret = $cmd->execCmd();
                }
                return true;
            }
        }
    }

    public function getInfoValue($logicalID)
    {
        $cmd = $this->getCmd('info', $logicalID);
        if (!is_object($cmd)) {
            return null;
        }
        $ret = $cmd->execCmd();
        if (is_null($ret)) {
            return '';
        }
        return $ret;
    }

    public function isOnline()
    {
        $ret = $this->getInfoValue('online');
        if ($ret==1 or $ret===true) {
            return true;
        }
        return false;
    }
}

class googlecastcmd extends cmd
{
    /*     * *************************Attributs****************************** */

    /*     * ***********************Methode static*************************** */

    /*     * *********************Methode d'instance************************* */

    public function execute($_options = null)
    {
        $originalLogicalId = $this->getLogicalId();

        $translatedLogicalId = googlecast_utils::getFullCmdTranslation($originalLogicalId);

        if ($this->getType() == 'action') {
            // special case of custom command
            if ($originalLogicalId == "customcmd") {
                $translatedLogicalId = trim($_options['message']);
            }

            // special case of 'action' command with subtype 'list' starting with 'cmdlist_'
            elseif (strpos($originalLogicalId, 'cmdlist_')===0) {
                $translatedLogicalId = str_replace('^', '|', trim($_options['select']));    // replace ^ by |
                if ($translatedLogicalId=='') {     // case of default value ('none' selected)
                    $translatedLogicalId='quit_app';
                }
            }

            // if speak command is used in scenario
            if ($originalLogicalId=='speak' && isset($_options['title']) && is_numeric($_options['title'])) {
                $_options['volume'] = $_options['title'];
            }

            if ($translatedLogicalId=='') {
                return;
            }
        }
        $listCmd = $translatedLogicalId;

        $eqLogic = $this->getEqLogic();

        switch ($this->getSubType()) {      // manage placeholder replacement
            case 'slider':
                $listCmd = str_replace('#slider#', $_options['slider'], $listCmd);
                break;
            case 'color':
                $listCmd = str_replace('#', '', str_replace('#color#', $_options['color'], $listCmd));
                break;
            case 'select':
                $listCmd = str_replace('#listValue#', $_options['select'], $listCmd);
                break;
            case 'message':
                $listCmd = str_replace('#message#', $_options['message'], $listCmd);
                if (isset($_options['title'])) {
                    $listCmd = str_replace('#title#', $_options['title'], $listCmd);
                }
                if (isset($_options['volume'])) {
                    $listCmd = str_replace('#volume#', $_options['volume'], $listCmd);
                }
                break;
        }

        $datalist=array();
        $cmdgroups = explode('$$', $listCmd);   // split multiple commands (sequences)

        foreach ($cmdgroups as $listCmd) {
            $originalListCmd = $listCmd;
            $listCmd = googlecast_utils::getFullCmdTranslation($originalListCmd);
            $data = array();

            // if this is a command 'info' to retrieve google cast device configuration using http
            if ($this->getType() != 'action') {
                // command must contains string 'cmd=getconfig'
                if (stristr($listCmd, 'cmd=getconfig')!=false) {
                    $eqLogic->getInfoHttpSimple($listCmd, $originalListCmd);
                    log::add('googlecast', 'debug', "Envoi d'une commande GoogleCast API http depuis Jeedom");
                } else {
                    continue;
                }
            }

            // 'refresh' type command
            if ($listCmd == "refreshconfig" || $listCmd == "refresh") {
                // both refresh commands require refreshing conifguration command refresh
                foreach ($eqLogic->getCmd('info') as $cmd) {
                    $logicalId = googlecast_utils::getFullCmdTranslation($cmd->getLogicalId());
                    if (stristr($logicalId, 'cmd=getconfig')!=false) {
                        $eqLogic->getInfoHttpSimple($logicalId, $cmd->getLogicalId());
                    }
                }

                if ($listCmd == "refreshconfig") {
                    continue;     // do not need to go further in that case
                }
            }
            // if this is a command 'action' to modify google cast device configuration using http
            if (stristr($listCmd, 'cmd=setconfig')!=false) {
                log::add('googlecast', 'debug', "Envoi d'une commande GoogleCast API http depuis Jeedom (set)");
                $eqLogic->setInfoHttpSimple($listCmd, null);
                continue;
            }

            $values = explode('|', $listCmd);     // split commands
            foreach ($values as $value) {
                $value = explode('=', $value);
                if (count($value) == 2) {    // X=Y
                    $data[trim($value[0])] = trim($value[1]);
                } elseif (count($value) == 1) {    // // X only, then assume this is a command
                    $data['cmd'] = trim($value[0]);
                    switch ($this->getSubType()) {
                        case 'slider':
                            $data['value'] = $_options['slider'];
                            break;
                        /*
    					case 'select':
    						$data['value'] = trim($_options['select']);
    						break;
    					case 'message':
    						$data['value'] = trim($_options['message']);
    						break;
                        */
                    }
                }
            }
            if (count($data) == 0) {  // something is wrong because no value
                continue;
            }
            array_push($datalist, $data);   // push in the sequence array (even if only one command)
        }

        if (count($datalist)>0) {
            // generate the query to be sent
            $fulldata = array(
                'apikey' => jeedom::getApiKey('googlecast'),
                'cmd' => 'action',
                'device' => array(
                    'uuid' => $eqLogic->getLogicalId(),
                    'source' => 'googlecast',
                ),
                'command' => $datalist,
            );
            log::add('googlecast', 'debug', "Envoi de la commande [$originalLogicalId] depuis Jeedom");
            googlecast::socket_connection(json_encode($fulldata));
        }
    }


    /*     * **********************Getteur Setteur*************************** */
}
