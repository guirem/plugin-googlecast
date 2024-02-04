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
	        <input  type="checkbox" class="configKey addressForm" data-l1key="tts_externalweb"/>
            <span class="addressTestURL"></span>
	    </div>
    </div>
    <div class="form-group languageform">
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
				<option value="gttsapi">{{Google Cloud Text-to-Speech (clé api & internet requis)}}</option>
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
	    <label class="col-lg-4 control-label">{{Key Google Cloud Text-to-Speech}}</label>
	    <div class="col-lg-4">
	        <input  type="text" class="configKey form-control" data-l1key="tts_gapikey" placeholder="Voir la documenttion pour obtenir une clé API"/>
	    </div>
    </div>
	<div class="form-group voicegcttsform">
	    <label class="col-lg-4 control-label">{{Voix Google Cloud Text-to-Speech}} (<a target="_blank" href="https://cloud.google.com/text-to-speech/">{{tester}}</a>)</label>
	    <div class="col-lg-4">
            <select class="configKey form-control" data-l1key="gctts_voice">
				<option value="fr-FR-Standard-A">French (France) - Standard A Female (fr-FR-Standard-A)</option>
				<option value="fr-FR-Standard-B">French (France) - Standard B Male (fr-FR-Standard-B)</option>
				<option value="fr-FR-Standard-C">French (France) - Standard C Female (fr-FR-Standard-C)</option>
				<option value="fr-FR-Standard-D">French (France) - Standard D Male (fr-FR-Standard-D)</option>
				<option value="fr-FR-Standard-E">French (France) - Standard E Female (fr-FR-Standard-E)</option>
				<option value="fr-FR-Wavenet-A">French (France) - WaveNet A Female (fr-FR-Wavenet-A)</option>
				<option value="fr-FR-Wavenet-B">French (France) - WaveNet B Male (fr-FR-Wavenet-B)</option>
				<option value="fr-FR-Wavenet-C">French (France) - WaveNet C Female (fr-FR-Wavenet-C)</option>
				<option value="fr-FR-Wavenet-D">French (France) - WaveNet D Male (fr-FR-Wavenet-D)</option>
				<option value="fr-FR-Wavenet-E">French (France) - WaveNet E Female (fr-FR-Wavenet-E)</option>
				<option value="fr-CA-Standard-A">French (Canada) - Standard A Female (fr-CA-Standard-A)</option>
				<option value="fr-CA-Standard-B">French (Canada) - Standard B Male (fr-CA-Standard-B)</option>
				<option value="fr-CA-Standard-C">French (Canada) - Standard C Female (fr-CA-Standard-C)</option>
				<option value="fr-CA-Standard-D">French (Canada) - Standard D Male (fr-CA-Standard-D)</option>
				<option value="fr-CA-Wavenet-A">French (Canada) - WaveNet A Female (fr-CA-Wavenet-A)</option>
				<option value="fr-CA-Wavenet-B">French (Canada) - WaveNet B Male (fr-CA-Wavenet-B)</option>
				<option value="fr-CA-Wavenet-C">French (Canada) - WaveNet C Female (fr-CA-Wavenet-C)</option>
				<option value="fr-CA-Wavenet-D">French (Canada) - WaveNet D Male (fr-CA-Wavenet-D)</option>
				<option value="es-ES-Standard-A">Spanish (Spain) - Standard A Female (es-ES-Standard-A)</option>
				<option value="en-AU-Standard-A">English (Australia) - Standard A Female (en-AU-Standard-A)</option>
				<option value="en-AU-Standard-B">English (Australia) - Standard B Male (en-AU-Standard-B)</option>
				<option value="en-AU-Standard-C">English (Australia) - Standard C Female (en-AU-Standard-C)</option>
				<option value="en-AU-Standard-D">English (Australia) - Standard D Male (en-AU-Standard-D)</option>
				<option value="en-AU-Wavenet-A">English (Australia) - WaveNet A Female (en-AU-Wavenet-A)</option>
				<option value="en-AU-Wavenet-B">English (Australia) - WaveNet B Male (en-AU-Wavenet-B)</option>
				<option value="en-AU-Wavenet-C">English (Australia) - WaveNet C Female (en-AU-Wavenet-C)</option>
				<option value="en-AU-Wavenet-D">English (Australia) - WaveNet D Male (en-AU-Wavenet-D)</option>
				<option value="en-IN-Standard-A">English (India) - Standard A Female (en-IN-Standard-A)</option>
				<option value="en-IN-Standard-B">English (India) - Standard B Male (en-IN-Standard-B)</option>
				<option value="en-IN-Standard-C">English (India) - Standard C Male (en-IN-Standard-C)</option>
				<option value="en-IN-Wavenet-A">English (India) - WaveNet A Female (en-IN-Wavenet-A)</option>
				<option value="en-IN-Wavenet-B">English (India) - WaveNet B Male (en-IN-Wavenet-B)</option>
				<option value="en-IN-Wavenet-C">English (India) - WaveNet C Male (en-IN-Wavenet-C)</option>
				<option value="en-GB-Standard-A">English (UK) - Standard A Female (en-GB-Standard-A)</option>
				<option value="en-GB-Standard-B">English (UK) - Standard B Male (en-GB-Standard-B)</option>
				<option value="en-GB-Standard-C">English (UK) - Standard C Female (en-GB-Standard-C)</option>
				<option value="en-GB-Standard-D">English (UK) - Standard D Male (en-GB-Standard-D)</option>
				<option value="en-GB-Wavenet-A">English (UK) - WaveNet A Female (en-GB-Wavenet-A)</option>
				<option value="en-GB-Wavenet-B">English (UK) - WaveNet B Male (en-GB-Wavenet-B)</option>
				<option value="en-GB-Wavenet-C">English (UK) - WaveNet C Female (en-GB-Wavenet-C)</option>
				<option value="en-GB-Wavenet-D">English (UK) - WaveNet D Male (en-GB-Wavenet-D)</option>
				<option value="en-US-Standard-B">English (US) - Standard B Male (en-US-Standard-B)</option>
				<option value="en-US-Standard-C">English (US) - Standard C Female (en-US-Standard-C)</option>
				<option value="en-US-Standard-D">English (US) - Standard D Male (en-US-Standard-D)</option>
				<option value="en-US-Standard-E">English (US) - Standard E Female (en-US-Standard-E)</option>
				<option value="en-US-Wavenet-A">English (US) - WaveNet A Male (en-US-Wavenet-A)</option>
				<option value="en-US-Wavenet-B">English (US) - WaveNet B Male (en-US-Wavenet-B)</option>
				<option value="en-US-Wavenet-C">English (US) - WaveNet C Female (en-US-Wavenet-C)</option>
				<option value="en-US-Wavenet-D">English (US) - WaveNet D Male (en-US-Wavenet-D)</option>
				<option value="en-US-Wavenet-E">English (US) - WaveNet E Female (en-US-Wavenet-E)</option>
				<option value="en-US-Wavenet-F">English (US) - WaveNet F Female (en-US-Wavenet-F)</option>
				<option value="ar-XA-Standard-A">Arabic - Standard A Female (ar-XA-Standard-A)</option>
				<option value="ar-XA-Standard-B">Arabic - Standard B Male (ar-XA-Standard-B)</option>
				<option value="ar-XA-Standard-C">Arabic - Standard C Male (ar-XA-Standard-C)</option>
				<option value="ar-XA-Wavenet-A">Arabic - WaveNet A Female (ar-XA-Wavenet-A)</option>
				<option value="ar-XA-Wavenet-B">Arabic - WaveNet B Male (ar-XA-Wavenet-B)</option>
				<option value="ar-XA-Wavenet-C">Arabic - WaveNet C Male (ar-XA-Wavenet-C)</option>
				<option value="cs-CZ-Standard-A">Czech (Czech Republic) - Standard A Female (cs-CZ-Standard-A)</option>
				<option value="cs-CZ-Wavenet-A">Czech (Czech Republic) - WaveNet A Female (cs-CZ-Wavenet-A)</option>
				<option value="da-DK-Standard-A">Danish (Denmark) - Standard A Female (da-DK-Standard-A)</option>
				<option value="da-DK-Wavenet-A">Danish (Denmark) - WaveNet A Female (da-DK-Wavenet-A)</option>
				<option value="nl-NL-Standard-A">Dutch (Netherlands) - Standard A Female (nl-NL-Standard-A)</option>
				<option value="nl-NL-Standard-B">Dutch (Netherlands) - Standard B Male (nl-NL-Standard-B)</option>
				<option value="nl-NL-Standard-C">Dutch (Netherlands) - Standard C Male (nl-NL-Standard-C)</option>
				<option value="nl-NL-Standard-D">Dutch (Netherlands) - Standard D Female (nl-NL-Standard-D)</option>
				<option value="nl-NL-Standard-E">Dutch (Netherlands) - Standard E Female (nl-NL-Standard-E)</option>
				<option value="nl-NL-Wavenet-A">Dutch (Netherlands) - WaveNet A Female (nl-NL-Wavenet-A)</option>
				<option value="nl-NL-Wavenet-B">Dutch (Netherlands) - WaveNet B Male (nl-NL-Wavenet-B)</option>
				<option value="nl-NL-Wavenet-C">Dutch (Netherlands) - WaveNet C Male (nl-NL-Wavenet-C)</option>
				<option value="nl-NL-Wavenet-D">Dutch (Netherlands) - WaveNet D Female (nl-NL-Wavenet-D)</option>
				<option value="nl-NL-Wavenet-E">Dutch (Netherlands) - WaveNet E Female (nl-NL-Wavenet-E)</option>
				<option value="fil-PH-Standard-A">Filipino (Philippines) - Standard A Female (fil-PH-Standard-A)</option>
				<option value="fil-PH-Wavenet-A">Filipino (Philippines) - WaveNet A Female (fil-PH-Wavenet-A)</option>
				<option value="fi-FI-Standard-A">Finnish (Finland) - Standard A Female (fi-FI-Standard-A)</option>
				<option value="fi-FI-Wavenet-A">Finnish (Finland) - WaveNet A Female (fi-FI-Wavenet-A)</option>
				<option value="de-DE-Standard-A">German (Germany) - Standard A Female (de-DE-Standard-A)</option>
				<option value="de-DE-Standard-B">German (Germany) - Standard B Male (de-DE-Standard-B)</option>
				<option value="de-DE-Wavenet-A">German (Germany) - WaveNet A Female (de-DE-Wavenet-A)</option>
				<option value="de-DE-Wavenet-B">German (Germany) - WaveNet B Male (de-DE-Wavenet-B)</option>
				<option value="de-DE-Wavenet-C">German (Germany) - WaveNet C Female (de-DE-Wavenet-C)</option>
				<option value="de-DE-Wavenet-D">German (Germany) - WaveNet D Male (de-DE-Wavenet-D)</option>
				<option value="el-GR-Standard-A">Greek (Greece) - Standard A Female (el-GR-Standard-A)</option>
				<option value="el-GR-Wavenet-A">Greek (Greece) - WaveNet A Female (el-GR-Wavenet-A)</option>
				<option value="hi-IN-Standard-A">Hindi (India) - Standard A Female (hi-IN-Standard-A)</option>
				<option value="hi-IN-Standard-B">Hindi (India) - Standard B Male (hi-IN-Standard-B)</option>
				<option value="hi-IN-Standard-C">Hindi (India) - Standard C Male (hi-IN-Standard-C)</option>
				<option value="hi-IN-Wavenet-A">Hindi (India) - WaveNet A Female (hi-IN-Wavenet-A)</option>
				<option value="hi-IN-Wavenet-B">Hindi (India) - WaveNet B Male (hi-IN-Wavenet-B)</option>
				<option value="hi-IN-Wavenet-C">Hindi (India) - WaveNet C Male (hi-IN-Wavenet-C)</option>
				<option value="hu-HU-Standard-A">Hungarian (Hungary) - Standard A Female (hu-HU-Standard-A)</option>
				<option value="hu-HU-Wavenet-A">Hungarian (Hungary) - WaveNet A Female (hu-HU-Wavenet-A)</option>
				<option value="id-ID-Standard-A">Indonesian (Indonesia) - Standard A Female (id-ID-Standard-A)</option>
				<option value="id-ID-Standard-B">Indonesian (Indonesia) - Standard B Male (id-ID-Standard-B)</option>
				<option value="id-ID-Standard-C">Indonesian (Indonesia) - Standard C Male (id-ID-Standard-C)</option>
				<option value="id-ID-Wavenet-A">Indonesian (Indonesia) - WaveNet A Female (id-ID-Wavenet-A)</option>
				<option value="id-ID-Wavenet-B">Indonesian (Indonesia) - WaveNet B Male (id-ID-Wavenet-B)</option>
				<option value="id-ID-Wavenet-C">Indonesian (Indonesia) - WaveNet C Male (id-ID-Wavenet-C)</option>
				<option value="it-IT-Standard-A">Italian (Italy) - Standard A Female (it-IT-Standard-A)</option>
				<option value="it-IT-Standard-B">Italian (Italy) - Standard B Female (it-IT-Standard-B)</option>
				<option value="it-IT-Standard-C">Italian (Italy) - Standard C Male (it-IT-Standard-C)</option>
				<option value="it-IT-Standard-D">Italian (Italy) - Standard D Male (it-IT-Standard-D)</option>
				<option value="it-IT-Wavenet-A">Italian (Italy) - WaveNet A Female (it-IT-Wavenet-A)</option>
				<option value="it-IT-Wavenet-B">Italian (Italy) - WaveNet B Female (it-IT-Wavenet-B)</option>
				<option value="it-IT-Wavenet-C">Italian (Italy) - WaveNet C Male (it-IT-Wavenet-C)</option>
				<option value="it-IT-Wavenet-D">Italian (Italy) - WaveNet D Male (it-IT-Wavenet-D)</option>
				<option value="ja-JP-Standard-A">Japanese (Japan) - Standard A Female (ja-JP-Standard-A)</option>
				<option value="ja-JP-Standard-B">Japanese (Japan) - Standard B Female (ja-JP-Standard-B)</option>
				<option value="ja-JP-Standard-C">Japanese (Japan) - Standard C Male (ja-JP-Standard-C)</option>
				<option value="ja-JP-Standard-D">Japanese (Japan) - Standard D Male (ja-JP-Standard-D)</option>
				<option value="ja-JP-Wavenet-A">Japanese (Japan) - WaveNet A Female (ja-JP-Wavenet-A)</option>
				<option value="ja-JP-Wavenet-B">Japanese (Japan) - WaveNet B Female (ja-JP-Wavenet-B)</option>
				<option value="ja-JP-Wavenet-C">Japanese (Japan) - WaveNet C Male (ja-JP-Wavenet-C)</option>
				<option value="ja-JP-Wavenet-D">Japanese (Japan) - WaveNet D Male (ja-JP-Wavenet-D)</option>
				<option value="ko-KR-Standard-A">Korean (South Korea) - Standard A Female (ko-KR-Standard-A)</option>
				<option value="ko-KR-Standard-B">Korean (South Korea) - Standard B Female (ko-KR-Standard-B)</option>
				<option value="ko-KR-Standard-C">Korean (South Korea) - Standard C Male (ko-KR-Standard-C)</option>
				<option value="ko-KR-Standard-D">Korean (South Korea) - Standard D Male (ko-KR-Standard-D)</option>
				<option value="ko-KR-Wavenet-A">Korean (South Korea) - WaveNet A Female (ko-KR-Wavenet-A)</option>
				<option value="ko-KR-Wavenet-B">Korean (South Korea) - WaveNet B Female (ko-KR-Wavenet-B)</option>
				<option value="ko-KR-Wavenet-C">Korean (South Korea) - WaveNet C Male (ko-KR-Wavenet-C)</option>
				<option value="ko-KR-Wavenet-D">Korean (South Korea) - WaveNet D Male (ko-KR-Wavenet-D)</option>
				<option value="cmn-CN-Standard-A">Mandarin Chinese - Standard A Female (cmn-CN-Standard-A)</option>
				<option value="cmn-CN-Standard-B">Mandarin Chinese - Standard B Male (cmn-CN-Standard-B)</option>
				<option value="cmn-CN-Standard-C">Mandarin Chinese - Standard C Male (cmn-CN-Standard-C)</option>
				<option value="cmn-CN-Wavenet-A">Mandarin Chinese - WaveNet A Female (cmn-CN-Wavenet-A)</option>
				<option value="cmn-CN-Wavenet-B">Mandarin Chinese - WaveNet B Male (cmn-CN-Wavenet-B)</option>
				<option value="cmn-CN-Wavenet-C">Mandarin Chinese - WaveNet C Male (cmn-CN-Wavenet-C)</option>
				<option value="nb-NO-Standard-A">Norwegian (Norway) - Standard A Female (nb-NO-Standard-A)</option>
				<option value="nb-NO-Standard-B">Norwegian (Norway) - Standard B Male (nb-NO-Standard-B)</option>
				<option value="nb-NO-Standard-C">Norwegian (Norway) - Standard C Female (nb-NO-Standard-C)</option>
				<option value="nb-NO-Standard-D">Norwegian (Norway) - Standard D Male (nb-NO-Standard-D)</option>
				<option value="nb-NO-Wavenet-A">Norwegian (Norway) - WaveNet A Female (nb-NO-Wavenet-A)</option>
				<option value="nb-NO-Wavenet-B">Norwegian (Norway) - WaveNet B Male (nb-NO-Wavenet-B)</option>
				<option value="nb-NO-Wavenet-C">Norwegian (Norway) - WaveNet C Female (nb-NO-Wavenet-C)</option>
				<option value="nb-NO-Wavenet-D">Norwegian (Norway) - WaveNet D Male (nb-NO-Wavenet-D)</option>
				<option value="nb-no-Standard-E">Norwegian (Norway) - Standard E Female (nb-no-Standard-E)</option>
				<option value="nb-no-Wavenet-E">Norwegian (Norway) - WaveNet E Female (nb-no-Wavenet-E)</option>
				<option value="pl-PL-Standard-A">Polish (Poland) - Standard A Female (pl-PL-Standard-A)</option>
				<option value="pl-PL-Standard-B">Polish (Poland) - Standard B Male (pl-PL-Standard-B)</option>
				<option value="pl-PL-Standard-C">Polish (Poland) - Standard C Male (pl-PL-Standard-C)</option>
				<option value="pl-PL-Standard-D">Polish (Poland) - Standard D Female (pl-PL-Standard-D)</option>
				<option value="pl-PL-Standard-E">Polish (Poland) - Standard E Female (pl-PL-Standard-E)</option>
				<option value="pl-PL-Wavenet-A">Polish (Poland) - WaveNet A Female (pl-PL-Wavenet-A)</option>
				<option value="pl-PL-Wavenet-B">Polish (Poland) - WaveNet B Male (pl-PL-Wavenet-B)</option>
				<option value="pl-PL-Wavenet-C">Polish (Poland) - WaveNet C Male (pl-PL-Wavenet-C)</option>
				<option value="pl-PL-Wavenet-D">Polish (Poland) - WaveNet D Female (pl-PL-Wavenet-D)</option>
				<option value="pl-PL-Wavenet-E">Polish (Poland) - WaveNet E Female (pl-PL-Wavenet-E)</option>
				<option value="pt-BR-Standard-A">Portuguese (Brazil) - Standard A Female (pt-BR-Standard-A)</option>
				<option value="pt-BR-Wavenet-A">Portuguese (Brazil) - WaveNet A Female (pt-BR-Wavenet-A)</option>
				<option value="pt-PT-Standard-A">Portuguese (Portugal) - Standard A Female (pt-PT-Standard-A)</option>
				<option value="pt-PT-Standard-B">Portuguese (Portugal) - Standard B Male (pt-PT-Standard-B)</option>
				<option value="pt-PT-Standard-C">Portuguese (Portugal) - Standard C Male (pt-PT-Standard-C)</option>
				<option value="pt-PT-Standard-D">Portuguese (Portugal) - Standard D Female (pt-PT-Standard-D)</option>
				<option value="pt-PT-Wavenet-A">Portuguese (Portugal) - WaveNet A Female (pt-PT-Wavenet-A)</option>
				<option value="pt-PT-Wavenet-B">Portuguese (Portugal) - WaveNet B Male (pt-PT-Wavenet-B)</option>
				<option value="pt-PT-Wavenet-C">Portuguese (Portugal) - WaveNet C Male (pt-PT-Wavenet-C)</option>
				<option value="pt-PT-Wavenet-D">Portuguese (Portugal) - WaveNet D Female (pt-PT-Wavenet-D)</option>
				<option value="ru-RU-Standard-A">Russian (Russia) - Standard A Female (ru-RU-Standard-A)</option>
				<option value="ru-RU-Standard-B">Russian (Russia) - Standard B Male (ru-RU-Standard-B)</option>
				<option value="ru-RU-Standard-C">Russian (Russia) - Standard C Female (ru-RU-Standard-C)</option>
				<option value="ru-RU-Standard-D">Russian (Russia) - Standard D Male (ru-RU-Standard-D)</option>
				<option value="ru-RU-Wavenet-A">Russian (Russia) - WaveNet A Female (ru-RU-Wavenet-A)</option>
				<option value="ru-RU-Wavenet-B">Russian (Russia) - WaveNet B Male (ru-RU-Wavenet-B)</option>
				<option value="ru-RU-Wavenet-C">Russian (Russia) - WaveNet C Female (ru-RU-Wavenet-C)</option>
				<option value="ru-RU-Wavenet-D">Russian (Russia) - WaveNet D Male (ru-RU-Wavenet-D)</option>
				<option value="sk-SK-Standard-A">Slovak (Slovakia) - Standard A Female (sk-SK-Standard-A)</option>
				<option value="sk-SK-Wavenet-A">Slovak (Slovakia) - WaveNet A Female (sk-SK-Wavenet-A)</option>
				<option value="sv-SE-Standard-A">Swedish (Sweden) - Standard A Female (sv-SE-Standard-A)</option>
				<option value="sv-SE-Wavenet-A">Swedish (Sweden) - WaveNet A Female (sv-SE-Wavenet-A)</option>
				<option value="tr-TR-Standard-A">Turkish (Turkey) - Standard A Female (tr-TR-Standard-A)</option>
				<option value="tr-TR-Standard-B">Turkish (Turkey) - Standard B Male (tr-TR-Standard-B)</option>
				<option value="tr-TR-Standard-C">Turkish (Turkey) - Standard C Female (tr-TR-Standard-C)</option>
				<option value="tr-TR-Standard-D">Turkish (Turkey) - Standard D Female (tr-TR-Standard-D)</option>
				<option value="tr-TR-Standard-E">Turkish (Turkey) - Standard E Male (tr-TR-Standard-E)</option>
				<option value="tr-TR-Wavenet-A">Turkish (Turkey) - WaveNet A Female (tr-TR-Wavenet-A)</option>
				<option value="tr-TR-Wavenet-B">Turkish (Turkey) - WaveNet B Male (tr-TR-Wavenet-B)</option>
				<option value="tr-TR-Wavenet-C">Turkish (Turkey) - WaveNet C Female (tr-TR-Wavenet-C)</option>
				<option value="tr-TR-Wavenet-D">Turkish (Turkey) - WaveNet D Female (tr-TR-Wavenet-D)</option>
				<option value="tr-TR-Wavenet-E">Turkish (Turkey) - WaveNet E Male (tr-TR-Wavenet-E)</option>
				<option value="uk-UA-Standard-A">Ukrainian (Ukraine) - Standard A Female (uk-UA-Standard-A)</option>
				<option value="uk-UA-Wavenet-A">Ukrainian (Ukraine) - WaveNet A Female (uk-UA-Wavenet-A)</option>
				<option value="vi-VN-Standard-A">Vietnamese (Vietnam) - Standard A Female (vi-VN-Standard-A)</option>
				<option value="vi-VN-Standard-B">Vietnamese (Vietnam) - Standard B Male (vi-VN-Standard-B)</option>
				<option value="vi-VN-Standard-C">Vietnamese (Vietnam) - Standard C Female (vi-VN-Standard-C)</option>
				<option value="vi-VN-Standard-D">Vietnamese (Vietnam) - Standard D Male (vi-VN-Standard-D)</option>
				<option value="vi-VN-Wavenet-A">Vietnamese (Vietnam) - WaveNet A Female (vi-VN-Wavenet-A)</option>
				<option value="vi-VN-Wavenet-B">Vietnamese (Vietnam) - WaveNet B Male (vi-VN-Wavenet-B)</option>
				<option value="vi-VN-Wavenet-C">Vietnamese (Vietnam) - WaveNet C Female (vi-VN-Wavenet-C)</option>
				<option value="vi-VN-Wavenet-D">Vietnamese (Vietnam) - WaveNet D Male (vi-VN-Wavenet-D)</option>
            </select>
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
		<label class="col-lg-4 control-label">{{Delai avant restauration du volume initial}}</label>
	    <div class="col-lg-2">
	        <input class="configKey form-control" type="number" data-l1key="tts_default_restoretime" min="-1000" max="10000" placeholder="{{Durée en milisecondes}}" />
	    </div>
		<div class="col-lg-2">ms (défaut: 1300)</div>
    </div>
	<div class="form-group">
		<label class="col-lg-4 control-label">{{Durée du silence ajouté avant la notification}}</label>
	    <div class="col-lg-2">
	        <input class="configKey form-control" type="number" data-l1key="tts_default_silence_duration" min="0" max="10000" placeholder="{{Durée en milisecondes}}" />
	    </div>
		<div class="col-lg-2">ms (défaut: 300)</div>
    </div>
    <div class="form-group">
	    <label class="col-lg-4 control-label">{{Ne pas utiliser le cache (déconseillé)}}</label>
	    <div class="col-lg-2">
	        <input  type="checkbox" class="configKey" data-l1key="tts_disablecache"/>
	    </div>
		<div class="col-lg-2">
            <a class="btn btn-warning cleanTTScache">{{Nettoyer tout le cache}}</a>
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
    $('.ttsspeedform').show();
    var val = $('.ttsengineform').val();

    if (val=='gttsapi' || val=='gttsapidev') {
        $('.ttsgapikeyform').show();
		$('.voicegcttsform').show();
    }
    else {
        $('.ttsgapikeyform').hide();
		$('.voicegcttsform').hide();
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

$('.addressForm').on('change', function () {

    $.ajax({
           type: "POST",
           url: "plugins/googlecast/core/php/googlecast.ajax.php",
           data: {
               action: "testAddress",
               value: $('.addressForm').prop('checked')
           },
           dataType: 'json',
           error: function (request, status, error) {
               $('.addressTestURL').text("");
               handleAjaxError(request, status, error);
           },
           success: function (data) { // si l'appel a bien fonctionné
               var spanContent = '&nbsp; &nbsp; &nbsp;<a href="'+data.result+'" target="_blank">(test)</a>';
               $('.addressTestURL').html(spanContent);
           }
       });
});
</script>
