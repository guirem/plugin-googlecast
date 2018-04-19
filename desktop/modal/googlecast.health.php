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

if (!isConnect('admin')) {
	throw new Exception('401 Unauthorized');
}
$eqLogics = googlecast::byType('googlecast');
?>

<table class="table table-condensed tablesorter" id="table_health">
	<thead>
		<tr>
			<th></th>
			<th>{{Nom}}</th>
			<th>{{Nom diffusé}}</th>
			<th>{{UUID}}</th>
			<th>{{Modèle}}</th>
			<th>{{Type}}</th>
			<th>{{Online}}</th>
            <th>{{Occupé}}</th>
			<th>{{Dernière com}}</th>
			<th>{{Date création}}</th>
		</tr>
	</thead>
	<tbody>
	 <?php
foreach ($eqLogics as $eqLogic) {
	$opacity = ($eqLogic->getIsEnable()) ? '' : jeedom::getConfiguration('eqLogic:style:noactive');
	$img = '<img class="lazy" style="margin:0x;padding:0px;" src="'.$eqLogic->getConfiguration('logoDevice').'" height="45" width="45"/>';
	echo '<tr style="' . $opacity . '">';
	echo '<td style="margin:0x;padding:0px;">' . $img . '</td>';
	echo '<td><a href="' . $eqLogic->getLinkToConfiguration() . '"style="text-decoration: none;">' . $eqLogic->getHumanName(true) . '</a></td>';
	echo '<td><span class="label label-info" style="font-size:1em;cursor:default;">' . $eqLogic->getConfiguration('friendly_name') . '</span></td>';
	echo '<td><span class="label label-info" style="font-size:1em;cursor:default;">' . $eqLogic->getLogicalId() . '</span></td>';
	echo '<td><span class="label label-info" style="font-size:1em;cursor:default;">' . $eqLogic->getConfiguration('model_name') . '</span></td>';
	echo '<td><span class="label label-info" style="font-size:1em;cursor:default;">' . $eqLogic->getConfiguration('cast_type') . '</span></td>';
	$onlinecmd = $eqLogic->getCmd('info', 'online');
	$online = '<span class="label label-danger" style="font-size:1em;cursor:default;">{{Offline}}</span>';
	if ($onlinecmd->execCmd() == 1) {
		$online = '<span class="label label-success" style="font-size:1em;cursor:default;">{{Online}}</span>';
	}
	echo '<td>' . $online . '</td>';
	$busycmd = $eqLogic->getCmd('info', 'is_busy');
	$busy = '<span class="label label-danger" style="font-size:1em;cursor:default;">{{Non}}</span>';
	if ($busycmd->execCmd() == 1) {
		$busy = '<span class="label label-success" style="font-size:1em;cursor:default;">{{Oui}}</span>';
	}
	echo '<td>' . $busy . '</td>';
	echo '<td><span class="label label-info" style="font-size:1em;cursor:default;">' . $eqLogic->getStatus('lastCommunication') . '</span></td>';
	echo '<td><span class="label label-info" style="font-size:1em;cursor:default;">' . $eqLogic->getConfiguration('createtime') . '</span></td>';
	echo '</tr>';
}
?>
	</tbody>
</table>
