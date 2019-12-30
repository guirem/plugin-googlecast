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
include_file('core', 'authentification', 'php');
if (!isConnect('admin')) {
	throw new Exception('{{401 - Accès non autorisé}}');
}
?>
<form class="form-horizontal">
    <fieldset>
    <legend><i class="icon loisir-darth"></i>&nbsp; {{Démon}}</legend>
    <div class="form-group">
	    <label class="col-lg-4 control-label">{{Port socket interne (modification dangereuse)}}</label>
	    <div class="col-lg-2">
	        <input class="configKey form-control" data-l1key="socketport" placeholder="{{55012}}" />
	    </div>
    </div>
	<div class="form-group">
	    <label class="col-lg-4 control-label">{{Configuration spéciale (eg: Docker, VM)}}</label>
	    <div class="col-lg-2">
	        <input  type="checkbox" class="configKey" data-l1key="fixdocker"/>
	    </div>
    </div>
	<div class="form-group">
	    <label class="col-lg-4 control-label">{{Fréquence de rafraichissement}}</label>
	    <div class="col-lg-2">
			<select class="configKey form-control" data-l1key="cyclefactor">
				<option value="0.5">{{Rapide}}</option>
			    <option value="1">{{Normal (recommandé)}}</option>
			    <option value="2">{{Basse}}</option>
			    <option value="3">{{Très basse}}</option>
			</select>
	    </div>
    </div>
    <legend><i class="fa fa-volume-up"></i>&nbsp; {{TTS - Text To Speech}}</legend>
	<div class="form-group">
	    <label class="col-lg-4 control-label">{{Utiliser l'adresse Jeedom externe}}</label>
	    <div class="col-lg-2">
	        <input  type="checkbox" class="configKey" data-l1key="tts_externalweb"/>
	    </div>
    </div>
    <div class="form-group">
	    <label class="col-lg-4 control-label">{{Langue par défaut}}</label>
	    <div class="col-lg-2">
            <select class="configKey form-control" data-l1key="tts_language">
                <option value="fr-FR">{{Français}}</option>
                <option value="fr-CA">{{Français - Canada}}</option>
                <option value="en-US">{{Anglais - US}}</option>
                <option value="en-GB">{{Anglais - GB}}</option>
                <option value="es-ES">{{Espagnol}}</option>
                <option value="de-DE">{{Allemand}}</option>
                <option value="it-IT">{{Italien}}</option>
            </select>
	    </div>
    </div>
	<div class="form-group">
	    <label class="col-lg-4 control-label">{{Moteur par défaut}}</label>
	    <div class="col-lg-4">
            <select class="configKey form-control ttsengineform" data-l1key="tts_engine">
				<option value="jeedomtts">{{Jeedom TTS (local)}}</option>
                <option value="picotts">{{PicoTTS (local)}}</option>
                <option value="gtts">{{Google Translate API (internet requis)}}</option>
				<option value="gttsapi">{{Google Speech API (clé api & internet requis)}}</option>
				<option value="gttsapidev">{{Google Speech API - dev (clé api & internet requis)}}</option>
                <?php
				if (config::byKey('active', 'ttsWebServer', 0) == 1) {
				echo '<option value="ttswebserver">{{TTS WebServer (plugin)}}</option>';
				}
				?>
            </select>
	    </div>
    </div>
    <div class='form-group ttswebserver'>
        <label class="col-lg-4 control-label">{{Voix TTS WebServer}}</label>
        <div class="col-lg-4">
        	<?php
        	if (config::byKey('active', 'ttsWebServer', 0) == 1) {
        		$_aTWSVoiceList = ttsWebServer::getVoicesList();
        		print_r($_aTWSVoiceList, 1);
        		echo "<select class=\"configKey form-control ttswsoptform\" data-l1key=\"ttsws_config\">";
        		for ($i = 0; $i < count($_aTWSVoiceList); $i++) {
        			echo "<option value=\"" . $_aTWSVoiceList[$i]['eqLogicId'] . "|" . $_aTWSVoiceList[$i]['voice'] . "\">[" . $_aTWSVoiceList[$i]['eqLogicName'] . "] " . $_aTWSVoiceList[$i]['voice'] . "</option>";
        		}
        		echo "</select>";
        	} else {
        		echo "Le plugin TTS WebServer n'est pas actif";
        	}
        	?>
        </div>
    </div>
	<div class="form-group ttsgapikeyform">
	    <label class="col-lg-4 control-label">{{Key Google Speech API}}</label>
	    <div class="col-lg-4">
	        <input  type="text" class="configKey form-control" data-l1key="tts_gapikey" placeholder="Voir la documenttion pour obtenir une clé API"/>
	    </div>
    </div>
	<div class="form-group ttsspeedform">
	    <label class="col-lg-4 control-label">{{Vitesse de parole}}</label>
	    <div class="col-lg-2">
            <select class="configKey form-control" data-l1key="tts_speed">
                <option value="0.8">{{Très lent}}</option>
				<option value="1">{{Lent}}</option>
				<option value="1.2">{{Normal}}</option>
                <option value="1.25">{{Normal +}}</option>
                <option value="1.3">{{Normal ++}}</option>
                <option value="1.4">{{Rapide}}</option>
				<option value="1.6">{{Très rapide}}</option>
				<option value="1.8">{{Encore plus rapide}}</option>
            </select>
	    </div>
    </div>
    <div class="form-group">
	    <label class="col-lg-4 control-label">{{Ne pas utiliser le cache (déconseillé)}}</label>
	    <div class="col-lg-2">
	        <input  type="checkbox" class="configKey" data-l1key="tts_disablecache"/>
	    </div>
    </div>
    <div class="form-group">
	    <label class="col-lg-4 control-label"></label>
	    <div class="col-lg-2">
            <a class="btn btn-success cleanTTScache">{{Nettoyer tout le cache}}</a>
	    </div>
    </div>
	<div class="form-group">
	    <label class="col-lg-4 control-label">{{Suppression automatique du cache de plus de X jours}}</label>
	    <div class="col-lg-2">
	        <input class="configKey form-control" type="number" data-l1key="tts_cleancache_days" min="0" max="90" placeholder="{{Nombre en jour}}" />
	    </div>
    </div>
    <legend><i class="fa fa-envelope-o"></i>&nbsp; {{Notifications}}</legend>
	<div class="form-group">
	    <label class="col-lg-4 control-label">{{Désactiver notifs pour nouveaux GoogleCast}}</label>
	    <div class="col-lg-2">
	        <input  type="checkbox" class="configKey" data-l1key="disableNotification"/>
	    </div>
    </div>

</fieldset>
</form>
<script>

function manage_ttsengineselection() {
    //console.log('in');
    $('.ttsspeedform').show();
    var val = $('.ttsengineform').val();

    if (val=='gttsapi' || val=='gttsapidev') {
        $('.ttsgapikeyform').show();
    }
    else {
        $('.ttsgapikeyform').hide();
    }

    if (val=='ttswebserver') {
        $('.ttswebserver').show();
		$('.ttsspeedform').hide();
    }
    else {
        $('.ttswebserver').hide();
    }

    if (val=='jeedomtts') {
		$('.ttsspeedform').hide();
    }

}

$( document ).ready(function() {
    manage_ttsengineselection();
});
$('.ttsengineform').on('change', manage_ttsengineselection);

$('.cleanTTScache').on('click', function () {
    $.ajax({// fonction permettant de faire de l'ajax
           type: "POST", // methode de transmission des données au fichier php
           url: "plugins/googlecast/core/php/googlecast.ajax.php", // url du fichier php
           data: {
               action: "cleanTTScache"
           },
           dataType: 'json',
           error: function (request, status, error) {
               handleAjaxError(request, status, error);
           },
           success: function (data) { // si l'appel a bien fonctionné
               if (data.state != 'ok') {
                   $('#div_alert').showAlert({message: data.result, level: 'danger'});
                   return;
               }
               $('#div_alert').showAlert({message: '{{Réussie}}', level: 'success'});
           }
       });
});
</script>
