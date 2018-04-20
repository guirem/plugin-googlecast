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
    <legend><i class="icon loisir-darth"></i> {{Démon}}</legend>
    <div class="form-group">
	    <label class="col-lg-4 control-label">{{Port socket interne (modification dangereuse)}}</label>
	    <div class="col-lg-2">
	        <input class="configKey form-control" data-l1key="socketport" placeholder="{{55012}}" />
	    </div>
    </div>
	<legend><i class="fa fa-envelope-o"></i> {{Notifications}}</legend>
	<div class="form-group">
	    <label class="col-lg-4 control-label">{{Désactiver notif pour nouveaux GoogleCast}}</label>
	    <div class="col-lg-2">
	        <input  type="checkbox" class="configKey" data-l1key="disableNotification"/>
	    </div>
    </div>
</fieldset>
</form>
<script>
 $('.changeLogLive').on('click', function () {
	 $.ajax({// fonction permettant de faire de l'ajax
            type: "POST", // methode de transmission des données au fichier php
            url: "plugins/googlecast/core/php/googlecast.ajax.php", // url du fichier php
            data: {
                action: "changeLogLive",
				level : $(this).attr('data-log')
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
