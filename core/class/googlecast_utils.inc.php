<?php
class googlecast_utils {

    public static function getCmdTranslation($logicalId) {
        $ret = $logicalId;

        if ( $logicalId == 'speak' ) {
            $ret = 'cmd=tts|value=#message#|vol=#volume#|resume=1';
        }
        elseif ( $logicalId == 'speak_noresume' ) {
            $ret = 'cmd=tts|value=#message#|vol=#volume#';
        }
        elseif ( $logicalId == 'speak_forceresume' ) {
            $ret = 'cmd=tts|value=#message#|vol=#volume#|resume=1|forceapplaunch=1';
        }
        elseif ( strpos($logicalId, 'gh_get_alarm_date_') === 0 ) {
            $param = str_replace("gh_get_alarm_date_", "", $logicalId);
            $ret = 'cmd=getconfig|value=assistant/alarms|data=alarm/'.$param.'/fire_time|fnc=ts2long|reterror=Undefined';
        }
        elseif ( strpos($logicalId, 'gh_get_alarm_status_') === 0 ) {
            $param = str_replace("gh_get_alarm_status_", "", $logicalId);
            $ret = 'cmd=getconfig|value=assistant/alarms|data=alarm/'.$param.'/status|reterror=0';
        }
        elseif ( strpos($logicalId, 'gh_get_alarm_datenice_') === 0 ) {
            $param = str_replace("gh_get_alarm_datenice_", "", $logicalId);
            $ret = 'cmd=getconfig|value=assistant/alarms|data=alarm/'.$param.'/fire_time|fnc=ts2longnice|reterror=Undefined';
        }
        elseif ( strpos($logicalId, 'gh_get_alarm_timestamp_') === 0 ) {
            $param = str_replace("gh_get_alarm_timestamp_", "", $logicalId);
            $ret = 'cmd=getconfig|value=assistant/alarms|data=alarm/'.$param.'/fire_time|reterror=Undefined';
        }
        elseif ( strpos($logicalId, 'gh_get_timer_timesec_') === 0 ) {
            $param = str_replace("gh_get_timer_time_", "", $logicalId);
            $ret = 'cmd=getconfig|value=assistant/alarms|data=timer/'.$param.'/fire_time|fnc=ts2sec|reterror=Undefined';
        }
        elseif ( strpos($logicalId, 'gh_get_timer_time_') === 0 ) {
            $param = str_replace("gh_get_timer_timenice_", "", $logicalId);
            $ret = 'cmd=getconfig|value=assistant/alarms|data=timer/'.$param.'/fire_time|fnc=ts2long|reterror=Undefined';
        }
        elseif ( strpos($logicalId, 'gh_get_timer_timestamp_') === 0 ) {
            $param = str_replace("gh_get_timer_timestamp_", "", $logicalId);
            $ret = 'cmd=getconfig|value=assistant/alarms|data=timer/'.$param.'/fire_time|reterror=Undefined';
        }
        elseif ( strpos($logicalId, 'gh_get_timer_duration_') === 0 ) {
            $param = str_replace("gh_get_timer_duration_", "", $logicalId);
            $ret = 'cmd=getconfig|value=assistant/alarms|data=timer/'.$param.'/original_duration|fnc=2sec|reterror=0';
        }
        elseif ( strpos($logicalId, 'gh_get_timer_status_') === 0 ) {
            $param = str_replace("gh_get_timer_status_", "", $logicalId);
            $ret = 'cmd=getconfig|value=assistant/alarms|data=timer/'.$param.'/status|reterror=0';
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
            $ret = 'cmd=getconfig|data=opencast_pin_code';
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
                $val = intval($data)/1000;
            } catch (Exception $e) {
                return $data;
            }
            $date = date_create_from_format('U', $val);
            $date->setTimezone(new DateTimeZone(date_default_timezone_get()));
            if (is_null($date)) {
                $date = date_create_from_format('U', 0);
            }
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
                $val = intval($data)/1000;
            } catch (Exception $e) {
                return $data;
            }
            $date = date_create_from_format('U', $val);
            $date->setTimezone(new DateTimeZone(date_default_timezone_get()));
            if (is_null($date)) {
                $date = date_create_from_format('U', 0);
            }
            $ret = date_format($date, "d-m-Y H:i");
            return $ret;
        }
        elseif ($fnc=='time') {
            $date = date_create_from_format('d-m-Y H:i', $data);
            $date->setTimezone(new DateTimeZone(date_default_timezone_get()));
            if (is_null($date)) {
                return $data;
            }
            return date_format($date, "H:i");
        }
        elseif ($fnc=='2sec') {
            try {
                $ret = intval($data)/1000;
            } catch (Exception $e) {
                $ret = 0;
            }
            return "";
        }
        elseif ($fnc=='ts2sec') {
            $ret = '';
            if (!is_numeric($data)) {
                return $data;
            }
            try {
                $val = intval($data);
            } catch (Exception $e) {
                return $data;
            }
            $date = date_create_from_format('U', $val);
            $date->setTimezone(new DateTimeZone(date_default_timezone_get()));
            if (is_null($date)) {
                return $data;
            }
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
