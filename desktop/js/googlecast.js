
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
			}
		}
	}
});

$('body').on('googlecast::includeDevice', function (_event,_options) {
    if (modifyWithoutSave) {
        $('#div_inclusionAlert').showAlert({message: '{{Un GoogleCast vient d\'être inclu/exclu. Veuillez réactualiser la page}}', level: 'warning'});
    } else {
        if (_options == '') {
            window.location.reload();
        } else {
            window.location.href = 'index.php?v=d&p=googlecast&m=googlecast&id=' + _options;
        }
    }
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
   var tr = '<tr class="cmd" data-cmd_id="' + init(_cmd.id) + '">';
   if ( (_cmd.logicalId != null) && _cmd.configuration.googlecast_cmd!==undefined ) {
       tr += '<td>';
       tr += '<div class="row">';
       tr += '<div class="col-sm-6">';
       tr += '<a class="cmdAction btn btn-default btn-sm" data-l1key="chooseIcon"><i class="fa fa-flag"></i> Icône</a>';
       tr += '<span class="cmdAttr" data-l1key="display" data-l2key="icon" style="margin-left : 10px;"></span>';
       tr += '</div>';
       tr += '<div class="col-sm-6">';
       tr += '<input class="cmdAttr form-control input-sm" data-l1key="name">';
       tr += '</div>';
       tr += '</div>';
       tr += '<select class="cmdAttr form-control input-sm" data-l1key="value" style="display : none;margin-top : 5px;" title="La valeur de la commande vaut par défaut la commande">';
       tr += '<option value="">Aucune</option>';
       tr += '</select>';
       tr += '</td>';
       tr += '<td>';
       tr += '<input class="cmdAttr form-control input-sm" data-l1key="id" style="display : none;" readonly>';
       tr += '<span>' + init(_cmd.type) + '</span>';
       tr += '</td>';
       tr += '<td><input class="cmdAttr form-control input-sm" data-l1key="logicalId" value="0" style="width : 70%; display : inline-block;" placeholder="{{Commande}}" readonly><br/>';
       tr += '</td>';
       tr += '<td>';
       tr += '<span><label class="checkbox-inline"><input type="checkbox" class="cmdAttr checkbox-inline" data-l1key="isVisible" checked/>{{Afficher}}</label></span> ';
       tr += '<span><label class="checkbox-inline"><input type="checkbox" class="cmdAttr checkbox-inline" data-l1key="isHistorized" checked/>{{Historiser}}</label></span> ';
       tr += '</td>';
       tr += '<td>';
       tr += '<span></span>';
       tr += '</td>';
       tr += '<td>';
       if (is_numeric(_cmd.id)) {
           tr += '<a class="btn btn-default btn-xs cmdAction" data-action="configure"><i class="fa fa-cogs"></i></a> ';
           tr += '<a class="btn btn-default btn-xs cmdAction" data-action="test"><i class="fa fa-rss"></i> Tester</a>';
       }
       //tr += '<i class="fa fa-minus-circle pull-right cmdAction cursor" data-action="remove"></i></td>';
} else {	// is new created command
        tr += '<td>';
        tr += '<div class="row">';
        tr += '<div class="col-sm-6">';
        tr += '<a class="cmdAction btn btn-default btn-sm" data-l1key="chooseIcon"><i class="fa fa-flag"></i> Icône</a>';
        tr += '<span class="cmdAttr" data-l1key="display" data-l2key="icon" style="margin-left : 10px;"></span>';
        tr += '</div>';
        tr += '<div class="col-sm-6">';
        tr += '<input class="cmdAttr form-control input-sm" data-l1key="name">';
        tr += '</div>';
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
        tr += '<td><input class="cmdAttr form-control input-sm" data-l1key="logicalId" value="0" style="width : 70%; display : inline-block;" placeholder="{{Commande}}"><br/>';
        tr += '</td>';
        tr += '<td>';
        tr += '<span><label class="checkbox-inline"><input type="checkbox" class="cmdAttr checkbox-inline" data-l1key="isVisible" checked/>{{Afficher}}</label></span> ';
        tr += '<span><label class="checkbox-inline"><input type="checkbox" class="cmdAttr checkbox-inline" data-l1key="isHistorized"/>{{Historiser}}</label></span> ';
        tr += '<span><label class="checkbox-inline"><input type="checkbox" class="cmdAttr" data-l1key="display" data-l2key="invertBinary"/>{{Inverser}}</label></span> ';
        tr += '<br/><input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="returnStateValue" placeholder="{{Valeur retour d\'état}}" style="width : 20%; display : inline-block;margin-top : 5px;margin-right : 5px;">';
        tr += '<input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="returnStateTime" placeholder="{{Durée avant retour d\'état (min)}}" style="width : 20%; display : inline-block;margin-top : 5px;margin-right : 5px;">';
        tr += '</td>';
        tr += '<td>';
        tr += '<select class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="updateCmdId" style="display : none;margin-top : 5px;" title="Commande d\'information à mettre à jour">';
        tr += '<option value="">Aucune</option>';
        tr += '</select>';
        tr += '<input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="updateCmdToValue" placeholder="Valeur de l\'information" style="display : none;margin-top : 5px;">';
        tr += '<input class="tooltips cmdAttr form-control input-sm expertModeVisible" data-l1key="configuration" data-l2key="listValue" placeholder="Liste de valeur|texte sÃ©parÃ© par ;" title="Liste" style="margin-top : 5px;">';
        tr += '<input class="cmdAttr form-control input-sm" data-l1key="unite"  style="width : 100px;" placeholder="Unité" title="Unité">';
        tr += '<input class="tooltips cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="minValue" placeholder="Min" title="Min" style="width : 40%;display : inline-block;"> ';
        tr += '<input class="tooltips cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="maxValue" placeholder="Max" title="Max" style="width : 40%;display : inline-block;">';
        tr += '</td>';
        tr += '<td>';
        if (is_numeric(_cmd.id)) {
            tr += '<a class="btn btn-default btn-xs cmdAction" data-action="configure"><i class="fa fa-cogs"></i></a> ';
            tr += '<a class="btn btn-default btn-xs cmdAction" data-action="test"><i class="fa fa-rss"></i> Tester</a>';
        }
        if (_cmd.configuration.googlecast_cmd_mod===undefined) {
            tr += '<i class="fa fa-minus-circle pull-right cmdAction cursor" data-action="remove"></i></td>';
        }
    }
   tr += '</tr>';
   $('#table_cmd tbody').append(tr);
   var tr = $('#table_cmd tbody tr:last');
   jeedom.eqLogic.builSelectCmd({
       id: $(".li_eqLogic.active").attr('data-eqLogic_id'),
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
