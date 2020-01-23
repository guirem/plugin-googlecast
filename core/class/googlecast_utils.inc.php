<?php

require_once dirname(__FILE__) . "/../../3rdparty/JsonPath/JsonStore.php";

class googlecast_utils {

    public static function getFullCmdTranslation($logicalId) {
        $ret = $logicalId;

        if ( $logicalId == 'speak' ) {
            $ret = 'cmd=tts|value=#message#|vol=#volume#';
        }
        elseif ( $logicalId == 'speak_noresume' ) {
            $ret = 'cmd=tts|value=#message#|vol=#volume#|noresume=1';
        }
        elseif ( $logicalId == 'speak_forceresume' ) {
            $ret = 'cmd=tts|value=#message#|vol=#volume#|forceapplaunch=1';
        }
        elseif ( $logicalId == 'castversion' ) {
            $ret = 'cmd=getconfig|data=cast_build_revision';
        }
        elseif ( strpos($logicalId, 'radio_') === 0 ) {
            try {
                $streamtype='LIVE';
                if ( substr($logicalId, -1)=='*' ) {
                    $streamtype = 'BUFFERED';
                }
                $radioname = str_replace("*", "", $logicalId);
                $radioname = substr( $radioname , 6) ;  // remove start with "radio_"
                $radioname = strtolower( $radioname );  // to lower just in case of typo
                $radioArray = json_decode(file_get_contents(dirname(__FILE__) . "/../webradios/radiolist.json"), true);
                if ( isset($radioArray[$radioname]) ) {
                    $radio = $radioArray[$radioname];
                    $ret = "app=media|forceplay=2|live=1|value='".$radio['location']."','audio/mpeg',title:'".$radio['title']."',thumb:'".$radio['image']."',stream_type:'".$streamtype."'";
                }
                if ( file_exists(dirname(__FILE__) . "/../webradios/custom.json") ) {
                    $radioArray = json_decode(file_get_contents(dirname(__FILE__) . "/../webradios/custom.json"), true);
                    if ( isset($radioArray[$radioname]) ) {
                        $radio = $radioArray[$radioname];
                        $ret = "app=media|forceplay=2|live=1|value='".$radio['location']."','audio/mpeg',title:'".$radio['title']."',thumb:'".$radio['image']."',stream_type:'".$streamtype."'";
                    }
                }
            } catch (Exception $e) {}
        }
        elseif ( $logicalId == 'gh_get_alarms_date' ) {
            $ret = 'cmd=getconfig|value=assistant/alarms|data=$.alarm..fire_time|fnc=ts2long|reterror=Undefined';
        }
        elseif ( $logicalId == 'gh_get_alarms_id' ) {
            $ret = 'cmd=getconfig|value=assistant/alarms|data=$..id|fnc=ts2long|reterror=Undefined';
        }
        elseif ( strpos($logicalId, 'gh_get_alarm_date_') === 0 ) {
            $param = str_replace("gh_get_alarm_date_", "", $logicalId);
            if ( is_numeric($param) ) {
                $ret = 'cmd=getconfig|value=assistant/alarms|data=$.alarm.['.$param.'].fire_time|fnc=ts2long|reterror=Undefined';
            }
            else {
                $ret = 'cmd=getconfig|value=assistant/alarms|data=$..[?(@.id='.$param.')].fire_time|fnc=ts2long|reterror=Undefined';
            }
        }
        elseif ( strpos($logicalId, 'gh_get_alarm_status_') === 0 ) {
            $param = str_replace("gh_get_alarm_status_", "", $logicalId);
            if ( is_numeric($param) ) {
                $ret = 'cmd=getconfig|value=assistant/alarms|data=$.alarm.['.$param.'].status|reterror=0';
            }
            else {
                $ret = 'cmd=getconfig|value=assistant/alarms|data=$..[?(@.id='.$param.')].fire_time|fnc=ts2long|reterror=Undefined';
            }
        }
        elseif ( strpos($logicalId, 'gh_get_alarm_datenice_') === 0 ) {
            $param = str_replace("gh_get_alarm_datenice_", "", $logicalId);
            if ( is_numeric($param) ) {
                $ret = 'cmd=getconfig|value=assistant/alarms|data=$.alarm.['.$param.'].fire_time|fnc=ts2longnice|reterror=Undefined';
            }
            else {
                $ret = 'cmd=getconfig|value=assistant/alarms|data=$..[?(@.id='.$param.')].fire_time|fnc=ts2long|reterror=Undefined';
            }
        }
        elseif ( strpos($logicalId, 'gh_get_alarm_timestamp_') === 0 ) {
            $param = str_replace("gh_get_alarm_timestamp_", "", $logicalId);
            if ( is_numeric($param) ) {
                $ret = 'cmd=getconfig|value=assistant/alarms|data=$.alarm.['.$param.'].fire_time|reterror=Undefined';
            }
            else {
                $ret = 'cmd=getconfig|value=assistant/alarms|data=$..[?(@.id='.$param.')].fire_time|fnc=ts2long|reterror=Undefined';
            }
        }
        elseif ( strpos($logicalId, 'gh_get_timer_timesec_') === 0 ) {
            $param = str_replace("gh_get_timer_time_", "", $logicalId);
            $ret = 'cmd=getconfig|value=assistant/alarms|data=$.timer.['.$param.'].fire_time|fnc=ts2sec|reterror=Undefined';
        }
        elseif ( strpos($logicalId, 'gh_get_timer_time_') === 0 ) {
            $param = str_replace("gh_get_timer_timenice_", "", $logicalId);
            $ret = 'cmd=getconfig|value=assistant/alarms|data=$.timer.['.$param.'].fire_time|fnc=ts2long|reterror=Undefined';
        }
        elseif ( strpos($logicalId, 'gh_get_timer_timestamp_') === 0 ) {
            $param = str_replace("gh_get_timer_timestamp_", "", $logicalId);
            $ret = 'cmd=getconfig|value=assistant/alarms|data=$.timer.['.$param.'].fire_time|reterror=Undefined';
        }
        elseif ( strpos($logicalId, 'gh_get_timer_duration_') === 0 ) {
            $param = str_replace("gh_get_timer_duration_", "", $logicalId);
            $ret = 'cmd=getconfig|value=assistant/alarms|data=$.timer.['.$param.'].original_duration|fnc=2sec|reterror=0';
        }
        elseif ( strpos($logicalId, 'gh_get_timer_status_') === 0 ) {
            $param = str_replace("gh_get_timer_status_", "", $logicalId);
            $ret = 'cmd=getconfig|value=assistant/alarms|data=$.timer.['.$param.'].status|reterror=0';
        }
        elseif ($logicalId=='gh_get_donotdisturb') {
            $ret = 'cmd=getconfig|value=post:assistant/notifications';
        }
        elseif ($logicalId=='gh_set_donotdisturb_on') {
            $ret = 'cmd=setconfig|value=assistant/notifications|data={"notifications_enabled":true}';
        }
        elseif ($logicalId=='gh_set_donotdisturb_off') {
            $ret = 'cmd=setconfig|value=assistant/notifications|data={"notifications_enabled":false}';
        }
        elseif ( strpos($logicalId, 'gh_set_donotdisturb_') === 0 ) {
            $param = str_replace("gh_set_alarms_volume_", "", $logicalId);
            $ret = 'cmd=setconfig|value=assistant/notifications|data={"notifications_enabled":'.$param.'}';
        }
        elseif ( strpos($logicalId, 'gh_set_alarms_volume_') === 0 ) {
            $param = round ( floatval(str_replace("gh_set_alarms_volume_", "", $logicalId))/100 , 2);
            $ret = 'cmd=setconfig|value=assistant/alarms/volume|data={"volume": '.$param.'}';
        }
        elseif ( $logicalId=='gh_get_alarms_volume' ) {
            $ret = 'cmd=getconfig|value=post:assistant/alarms/volume';
        }
        elseif ( $logicalId=='conf_pincode' ) {
            $ret = 'cmd=getconfig|data=$.opencast_pin_code|reterror=Undefined';
        }
        elseif ( $logicalId=='conf_getbonded_bluetooth' ) {
            $ret = 'cmd=getconfig|value=bluetooth/get_bonded';
        }
        elseif ( $logicalId=='conf_getconnected_wifi' ) {
            $ret = 'cmd=getconfig|value=configured_networks|data=0/ssid';
        }
        elseif ( $logicalId=='bt_connectdefault' ) {
            $ret = 'cmd=setconfig|value=bluetooth/connect|data={"connect":true}';
        }
        elseif ( strpos($logicalId, 'bt_connect_X') === 0 ) {
            $param = str_replace("bt_connect_X", "", $logicalId);
            $ret = 'cmd=setconfig|value=bluetooth/connect|data={"mac_address": "'.$param.'","profile": 2,"connect":true}';
        }
        elseif ( $logicalId=='bt_disconnectdefault' ) {
            $ret = 'cmd=setconfig|value=bluetooth/connect|data={"connect":false}';
        }
        return $ret;
    }

    public static function buildRadioSelectlist() {
        $ret = '';
        try {
            $radioArray = array();
            $radioFile = json_decode(file_get_contents(dirname(__FILE__) . "/../webradios/radiolist.json"), true);
            foreach ($radioFile as $radio_id => $radio_data){
                $radioArray[$radio_id] = $radio_data['title'];
            }
            if ( file_exists(dirname(__FILE__) . "/../webradios/custom.json") ) {
                $radioFile = json_decode(file_get_contents(dirname(__FILE__) . "/../webradios/custom.json"), true);
                foreach ($radioFile as $radio_id => $radio_data){
                    $radioArray[$radio_id] = $radio_data['title'];
                }
            }
            ksort($radioArray);
            foreach ($radioArray as $radio_id => $radio_title){
                $ret .= 'radio_' . $radio_id . '|' . $radio_title . ';';
            }
            if ( strlen($ret)>0 ) { // remove last ';' that cause empty line in select
                $ret = substr($ret, 0, strlen($ret)-1);
            }
        } catch (Exception $e) {}

        return $ret;
    }

    public static function getCmdTranslation($cmd) {
        return $cmd;
    }

    public static function getJsonPathResult($json, $path) {
        $store = new JsonStore($json);
        return $store->get($path);
    }

    public static function getFncResult($data, $fnc) {
        if (is_null($fnc)) {
            return $data;
        }
        if ($fnc=='ts2longnice') {
            $ret = '';
            if (!is_numeric($data)) {
                return $data;
            }
            try {
                $val = intval(substr(trim($data),0,10));
            } catch (Exception $e) {
                return $data;
            }
            $date = date_create_from_format('U', $val);
            if (is_null($date) or $date===false) {
                $date = date_create_from_format('U', 0);
            }
            $date->setTimezone(new DateTimeZone(date_default_timezone_get()));
            $dateTmp = clone $date;
            $dateTmp->setTime( 0, 0, 0 );
            $today = new DateTime("now", new DateTimeZone(date_default_timezone_get()));
            $today->setTime( 0, 0, 0 );
            $diff = $today->diff( $dateTmp );
            $diffDays = (integer)$diff->format( "%R%a" );
            switch( $diffDays ) {
                case 0:
                    $ret = __("Aujourd'hui", __FILE__). ' ' . date_format($date, "H:i");
                    break;
                case +1:
                    $ret = __("Demain", __FILE__). ' ' . date_format($date, "H:i");
                    break;
                default:
                    $ret = date_format($date, "d-m-Y H:i");
            }
            return $ret;
        }
        elseif ($fnc=='ts2long') {
            $ret = '';
            if (!is_numeric($data)) {
                return $data;
            }
            try {
                $val = intval(substr(trim($data),0,10));
            } catch (Exception $e) {
                return $data;
            }
            $date = date_create_from_format('U', $val);
            if (is_null($date) or $date===false) {
                $date = date_create_from_format('U', 0);
            }
            $date->setTimezone(new DateTimeZone(date_default_timezone_get()));
            $ret = date_format($date, "d-m-Y H:i");
            return $ret;
        }
        elseif ($fnc=='time') {
            $date = date_create_from_format('d-m-Y H:i', $data);
            if (is_null($date) or $date===false) {
                return $data;
            }
            $date->setTimezone(new DateTimeZone(date_default_timezone_get()));
            return date_format($date, "H:i");
        }
        elseif ($fnc=='2sec') {
            try {
                $ret = intval(substr(trim($data),0,10));
            } catch (Exception $e) {
                $ret = 0;
            }
            return $ret;
        }
        elseif ($fnc=='ts2sec') {
            $ret = '';
            if (!is_numeric($data)) {
                return $data;
            }
            try {
                $val = intval(substr(trim($data),0,10));
            } catch (Exception $e) {
                return $data;
            }
            $date = date_create_from_format('U', $val);
            if (is_null($date) or $date===false) {
                return $data;
            }
            $date->setTimezone(new DateTimeZone(date_default_timezone_get()));
            $today = new DateTime();
            $diffsec = $date - $today;
            return $diffsec;
        }
        elseif ($fnc=='binary') {

        }
        return $data;
    }


    public static function getCmdDefinition($eqlogic, $type, $order) {
        if ($type=='googlehome') {

            $cmd = $eqlogic->getCmd(null, 'gh_get_alarm_date_0');
            if (!is_object($cmd)) {
                $cmd = new googlecastCmd();
                $cmd->setLogicalId('gh_get_alarm_date_0');
                $cmd->setName(__('Alarme 1', __FILE__));
                $cmd->setIsVisible(1);
                $cmd->setOrder($order++);
                $cmd->setConfiguration('googlecast_cmd', true);
            }
            $cmd->setType('info');
            $cmd->setSubType('string');
            $cmd->setEqLogic_id($eqlogic->getId());
            $cmd->save();

            $cmd = $eqlogic->getCmd(null, 'gh_get_alarm_status_0');
            if (!is_object($cmd)) {
                $cmd = new googlecastCmd();
                $cmd->setLogicalId('gh_get_alarm_status_0');
                $cmd->setName(__('Statut Alarme 1', __FILE__));
                $cmd->setIsVisible(1);
                $cmd->setOrder($order++);
                $cmd->setConfiguration('googlecast_cmd', true);
            }
            $cmd->setType('info');
            $cmd->setSubType('binary');
            $cmd->setEqLogic_id($eqlogic->getId());
            $cmd->save();

        }
        elseif ($type=='chromecast') {

        }
        return $order;
    }

}
