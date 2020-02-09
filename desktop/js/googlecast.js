
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

 $('.changeIncludeState').on('click', function () {
	var mode = $(this).attr('data-mode');
	var state = $(this).attr('data-state');
	changeIncludeState(state, mode);
});

 $('#bt_healthgooglecast').on('click', function () {
    $('#md_modal').dialog({title: "{{Santé GoogleCast}}"});
    $('#md_modal').load('index.php?v=d&plugin=googlecast&modal=googlecast.health').dialog('open');
});

$('#bt_healthrefresh').on('click', function () {
    $.ajax({// fonction permettant de faire de l'ajax
        type: "POST", // methode de transmission des données au fichier php
        url: "plugins/googlecast/core/php/googlecast.ajax.php", // url du fichier php
        data: {
            action: "refreshall"
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
            $('#md_modal').dialog({title: "{{Santé GoogleCast}}"});
            $('#md_modal').load('index.php?v=d&plugin=googlecast&modal=googlecast.health').dialog('open');
        }
    });
});

$('.has_googleassistant_form').on('change', manage_ga_token_input);
function manage_ga_token_input() {
    var value = $('.ga_token_input').prop('checked')
    if (value) {
        $('.ga_token_form').show();
    }
    else {
        $('.ga_token_form').hide();
    }
}

$('body').on('googlecast::includeState', function (_event,_options) {
	if (_options['mode'] == 'learn') {
		if (_options['state'] == 1) {
			if($('.include').attr('data-state') != 0){
				$.hideAlert();
				$('.include:not(.card)').removeClass('btn-default').addClass('btn-success');
				$('.include').attr('data-state', 0);
				$('.include.card span center').text('{{Arrêter le scan}}');
				$('.includeicon').empty().append('<i class="fa fa-spinner fa-pulse" style="font-size : 6em;color:red;font-weight: bold;"></i>');
                $('.includeicon_text').css('color', 'red').css('font-weight', 'bold');
				$('#div_inclusionAlert').showAlert({message: '{{Mode scan en cours pendant 1 minute... (Cliquer sur arrêter pour stopper avant)}}', level: 'warning'});
			}
		} else {
			if($('.include').attr('data-state') != 1){
				$.hideAlert();
				$('.include:not(.card)').addClass('btn-default').removeClass('btn-success btn-danger');
				$('.include').attr('data-state', 1);
				$('.includeicon').empty().append('<i class="fa fa-bullseye" style="font-size : 6em;color:#94ca02;font-weight: normal;"></i>');
                $('.includeicon_text').css('color', '#94ca02').css('font-weight', 'normal');
				$('.include.card span center').text('{{Lancer Scan}}');
				$('.include.card').css('background-color','#ffffff');
                window.location.reload();
			}
		}
	}
});

$('body').on('googlecast::includeDevice', function (_event, _options) {
    friendly_name = 'NONAME';
    if ( _options && _options['friendly_name'] ) {
        friendly_name = _options['friendly_name'];
    }
    $('#div_inclusionAlert').showAlert({message: '{{Un GoogleCast vient d\'être inclu :}} "' + friendly_name + '".   {{Veuillez réactualiser la page}}', level: 'info'});
    //window.location.reload();
});

function changeIncludeState(_state,_mode,_type='') {
    $.ajax({// fonction permettant de faire de l'ajax
        type: "POST", // methode de transmission des données au fichier php
        url: "plugins/googlecast/core/php/googlecast.ajax.php", // url du fichier php
        data: {
            action: "changeIncludeState",
            state: _state,
            mode: _mode,
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
        }
    });
}


$("#table_cmd").sortable({axis: "y", cursor: "move", items: ".cmd", placeholder: "ui-state-highlight", tolerance: "intersect", forcePlaceholderSize: true});

function addCmdToTable(_cmd) {
   if (!isset(_cmd)) {
       var _cmd = {configuration: {}};
   }
   var tr = '';
   if ( (_cmd.logicalId != null) && _cmd.configuration.googlecast_cmd!==undefined ) {
       tr = '<tr class="cmd" data-cmd_id="' + init(_cmd.id) + '" style="background:#F2F2F2">';
       tr += '<td>';
       tr += '<div style="width:250px;">';
       tr += '<a class="cmdAction btn btn-default btn-sm" data-l1key="chooseIcon"><i class="fa fa-flag"></i> Icône</a>';
       tr += '<span class="cmdAttr" data-l1key="display" data-l2key="icon" style="margin-left : 8px;display: inline-block;"></span>';
       tr += '<input class="cmdAttr form-control input-sm" style="width:140px;float:right;" data-l1key="name">';
       tr += '</div>';
       //tr += '<select class="cmdAttr form-control input-sm" data-l1key="value" style="display : none;margin-top : 0px;" title="La valeur de la commande vaut par défaut la commande">';
       //tr += '<option value="">Aucune</option>';
       //tr += '</select>';
       tr += '</td>';
       tr += '<td>';
       tr += '<input class="cmdAttr form-control input-sm" data-l1key="id" style="display : none;" readonly>';
       //tr += '<span><center>' + init(_cmd.type) + '</center></span><span style="display:none;" class="type" type="' + init(_cmd.type) + '">' + jeedom.cmd.availableType() + '</span>';
       //tr += '<span><center>' + init(_cmd.subType) + '</center></span><span style="display:none;" class="subType" subType="' + init(_cmd.subType) + '"></span>';
       tr += '<span><center>{{' + init(_cmd.type) + '}}</center></span>';
       // tr += '<span><center style="font-size:x-small;">({{' + init(_cmd.subType) + '}})</center></span>';
       tr += '</td>';
       tr += '<td><input class="cmdAttr form-control input-sm" data-l1key="logicalId" value="0" style="width : 98%; display : inline-block;" title="{{Commande par défaut du plugin}}" readonly><br/>';
       tr += '</td>';
       tr += '<td>';
       tr += '<span><label class="checkbox-inline"><input type="checkbox" class="cmdAttr checkbox-inline" data-l1key="isVisible" checked/>{{Afficher}}</label></span> ';
       if (init(_cmd.type)=='info') {
           tr += '<span><label class="checkbox-inline"><input type="checkbox" class="cmdAttr checkbox-inline" data-l1key="isHistorized"/>{{Historiser}}</label></span> ';
       }
       else {
           tr += '<span style="display:none;><label class="checkbox-inline"><input type="checkbox" class="cmdAttr checkbox-inline" data-l1key="isHistorized"/>{{Historiser}}</label></span> ';
       }
       tr += '</td>';
       tr += '<td>';
       tr += '<span></span>';
       tr += '</td>';
       tr += '<td>';
       if (is_numeric(_cmd.id)) {
           tr += '<a class="btn btn-default btn-xs cmdAction" data-action="configure"><i class="fa fa-cogs"></i></a> ';
           tr += '<a class="btn btn-default btn-xs cmdAction" data-action="test"><i class="fa fa-rss"></i> Tester</a>';
       }
} else {	// is new created command
        if (!is_numeric(_cmd.id)) {
            tr = '<tr class="cmd" data-cmd_id="' + init(_cmd.id) + '" style="background:#F5F6CE">';
        }
        else {
            tr = '<tr class="cmd" data-cmd_id="' + init(_cmd.id) + '" style="background:#ECF8E0">';
        }
        tr += '<td>';
        tr += '<div style="width:250px;">';
        tr += '<a class="cmdAction btn btn-default btn-sm" data-l1key="chooseIcon"><i class="fa fa-flag"></i> Icône</a>';
        tr += '<span class="cmdAttr" data-l1key="display" data-l2key="icon" style="margin-left : 8px;display: inline-block;"></span>';
        tr += '<input class="cmdAttr form-control input-sm" style="width:140px;float:right;" data-l1key="name">';
        tr += '</div>';
        tr += '<select class="cmdAttr form-control input-sm" data-l1key="value" style="display : none;margin-top : 5px;" title="La valeur de la commande vaut par défaut la commande">';
        tr += '<option value="">Aucune</option>';
        tr += '</select>';
        tr += '</td>';
        tr += '<td>';
        tr += '<input class="cmdAttr form-control input-sm" data-l1key="id" style="display : none;">';
        tr += '<span class="type" type="' + init(_cmd.type) + '">' + jeedom.cmd.availableType() + '</span>';
        tr += '<span class="subType" subType="' + init(_cmd.subType) + '"></span>';
        tr += '</td>';
        tr += '<td><input class="cmdAttr form-control input-sm" data-l1key="logicalId" value="" style="width : 98%; display : inline-block;" placeholder="{{ex : cmd=tts|value=Mon texte TTS (voir documentation pour plus d\'info)}}" maxlength="128" title="{{Limité à 128 caractères}}"><br/>';
        tr += '<textarea class="tooltips cmdAttr form-control input-sm expertModeVisible" data-l1key="configuration" data-l2key="listValue" title="<id>|<texte> séparé par ;" rows="4" style="resize:vertical;margin-top : 5px;width : 98%" placeholder="{{Liste de valeurs au format \'<id>|<texte>;<id>|<texte>;...\'\n Si la commande a pour nom \'cmdlist_<XXX>\', <id> => <commandes> (avec ^ pour séparateur), sinon utiliser \'#listValue#\' pour récuperer <id> dans la liste de commandes.}}"></textarea>';
        tr += '</td>';
        tr += '<td>';
        tr += '<span><label class="checkbox-inline"><input type="checkbox" class="cmdAttr checkbox-inline" data-l1key="isVisible" checked/>{{Afficher}}</label></span> ';
        tr += '<span><label class="checkbox-inline"><input type="checkbox" class="cmdAttr checkbox-inline" data-l1key="isHistorized"/>{{Historiser}}</label></span> ';
        tr += '<span><label class="checkbox-inline"><input type="checkbox" class="cmdAttr" data-l1key="display" data-l2key="invertBinary"/>{{Inverser}}</label></span> ';
        tr += '<br/><input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="returnStateValue" title="{{Valeur retour d\'état}}" placeholder="{{Valeur retour d\'état}}" style="width : 67%; display : inline-block;margin-top : 5px;margin-right : 4px;">';
        tr += '<input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="returnStateTime" title="{{Durée avant retour d\'état (min)}}" placeholder="{{Durée avant retour d\'état (min)}}" style="width : 25%; display : inline-block;margin-top : 5px;margin-right : 2px;">';
        tr += '</td>';
        tr += '<td>';
        tr += '<select class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="updateCmdId" style="display : none;margin-top : 0px;" title="Commande d\'information à mettre à jour">';
        tr += '<option value="">Aucune</option>';
        tr += '</select>';
        tr += '<input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="updateCmdToValue" placeholder="Valeur de l\'information" title="Valeur de l\'information" style="display : none;margin-top : 5px;">';
        tr += '<input class="cmdAttr form-control input-sm" data-l1key="unite"  style="width : 120px;" placeholder="Unité" title="Unité">';
        tr += '<input class="tooltips cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="minValue" placeholder="Min" title="Min" style="margin-top=5px;width : 45%;display : inline-block;"> ';
        tr += '<input class="tooltips cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="maxValue" placeholder="Max" title="Max" style="margin-top=5px;width : 45%;display : inline-block;">';
        tr += '</td>';
        tr += '<td>';
        if (is_numeric(_cmd.id)) {
            tr += '<a class="btn btn-default btn-xs cmdAction" data-action="configure"><i class="fa fa-cogs"></i></a> ';
            tr += '<a class="btn btn-default btn-xs cmdAction" data-action="test"><i class="fa fa-rss"></i> Tester</a>';
        }
        if (_cmd.configuration.googlecast_cmd_mod===undefined) {
            tr += '<br><center><i class="fa fa-minus-circle cmdAction cursor" style="margin-top:10px;font-size:18px;color:red" data-action="remove"></i></center></td>';
        }
    }
   tr += '</tr>';
   $('#table_cmd tbody').append(tr);
   var tr = $('#table_cmd tbody tr:last');
   jeedom.eqLogic.builSelectCmd({
       id: $('.eqLogicAttr[data-l1key=id]').value(),
       filter: {type: 'info'},
       error: function (error) {
           $('#div_alert').showAlert({message: error.message, level: 'danger'});
       },
       success: function (result) {
           tr.find('.cmdAttr[data-l1key=value]').append(result);
           tr.find('.cmdAttr[data-l1key=configuration][data-l2key=updateCmdId]').append(result);
           tr.setValues(_cmd, '.cmdAttr');
           jeedom.cmd.changeType(tr, init(_cmd.subType));
       }
   });
}
