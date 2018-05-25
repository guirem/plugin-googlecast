<?php
if (!isConnect('admin')) {
	throw new Exception('{{401 - Accès non autorisé}}');
}
$plugin = plugin::byId('googlecast');
sendVarToJS('eqType', $plugin->getId());
$eqLogics = eqLogic::byType($plugin->getId());

function sortByOption($a, $b) {
	return strcmp($a['name'], $b['name']);
}
if (config::byKey('include_mode', 'googlecast', 0) == 1) {
	echo '<div class="alert jqAlert alert-warning" id="div_inclusionAlert" style="margin : 0px 5px 15px 15px; padding : 7px 35px 7px 15px;">{{Vous êtes en mode scan. Recliquez sur le bouton scan pour sortir de ce mode (sinon le mode restera actif une minute)}}</div>';
} else {
	echo '<div id="div_inclusionAlert"></div>';
}

?>
<div class="row row-overflow">
  <div class="col-lg-2">
    <div class="bs-sidebar">
      <ul id="ul_eqLogic" class="nav nav-list bs-sidenav">
        <li class="filter" style="margin-bottom: 5px;"><input class="filter form-control input-sm" placeholder="{{Rechercher}}" style="width: 100%"/></li>
<?php
foreach ($eqLogics as $eqLogic) {
	echo '<li class="cursor li_eqLogic" data-eqLogic_id="' . $eqLogic->getId() . '"><a>' . $eqLogic->getHumanName(true) . '</a></li>';
}
?>
     </ul>
   </div>
</div>
 <div class="col-lg-10 col-md-9 col-sm-8 eqLogicThumbnailDisplay" style="border-left: solid 1px #EEE; padding-left: 25px;">
   <legend><i class="fa fa-cog"></i>  {{Gestion}}</legend>
   <div class="eqLogicThumbnailContainer">
<?php
if (config::byKey('include_mode', 'googlecast', 0) == 1) {
	echo '<div class="cursor changeIncludeState include card" data-mode="1" data-state="0" style="background-color : #ffffff; height : 140px;margin-bottom : 10px;padding : 5px;border-radius: 2px;width : 160px;margin-left : 10px;" >';
	echo '<center class="includeicon">';
	echo '<i class="fa fa-spinner fa-pulse" style="font-size : 6em;color:red"></i>';
	echo '</center>';
	echo '<span class="includeicon_text" style="font-size : 1.1em;position:relative; top : 15px;word-break: break-all;white-space: pre-wrap;word-wrap: break-word;color:red;font-weight: bold;"><center>{{Arrêter Scan}}</center></span>';
	echo '</div>';
} else {
	echo '<div class="cursor changeIncludeState include card" data-mode="1" data-state="1" style="background-color : #ffffff; height : 140px;margin-bottom : 10px;padding : 5px;border-radius: 2px;width : 160px;margin-left : 10px;" >';
	echo '<center class="includeicon">';
	echo '<i class="fa fa-bullseye" style="font-size : 6em;color:#94ca02;"></i>';
	echo '</center>';
	echo '<span class="includeicon_text" style="font-size : 1.1em;position:relative; top : 15px;word-break: break-all;white-space: pre-wrap;word-wrap: break-word;color:#94ca02";font-weight: normal;><center>{{Lancer Scan}}</center></span>';
	echo '</div>';
}
?>
   <div class="cursor eqLogicAction" data-action="gotoPluginConf" style="background-color : #ffffff; height : 120px;margin-bottom : 10px;padding : 5px;border-radius: 2px;width : 160px;margin-left : 10px;">
    <center>
      <i class="fa fa-wrench" style="font-size : 6em;color:#767676;"></i>
    </center>
    <span style="font-size : 1.1em;position:relative; top : 15px;word-break: break-all;white-space: pre-wrap;word-wrap: break-word;color:#767676"><center>{{Configuration}}</center></span>
  </div>
  <div class="cursor" id="bt_healthgooglecast" style="background-color : #ffffff; height : 120px;margin-bottom : 10px;padding : 5px;border-radius: 2px;width : 160px;margin-left : 10px;" >
    <center>
      <i class="fa fa-medkit" style="font-size : 6em;color:#767676;"></i>
    </center>
    <span style="font-size : 1.1em;position:relative; top : 15px;word-break: break-all;white-space: pre-wrap;word-wrap: break-word;color:#767676"><center>{{Santé}}</center></span>
  </div>
</div>
<legend><i class="icon techno-cable1"></i>  {{Mes équipements GoogleCast}}
</legend>
<div class="eqLogicThumbnailContainer">
<?php
foreach ($eqLogics as $eqLogic) {
	$opacity = '';
	if ($eqLogic->getIsEnable() != 1) {
		$opacity = 'opacity:0.3;';
	}
	echo '<div class="eqLogicDisplayCard cursor" data-eqLogic_id="' . $eqLogic->getId() . '" style="text-align: center; background-color : #ffffff; height : 200px;margin-bottom : 10px;padding : 5px;border-radius: 2px;width : 160px;margin-left : 10px;' . $opacity . '" >';
	echo '<img src="' . $eqLogic->getConfiguration('logoDevice', 'plugins/googlecast/desktop/images/model_default.png') . '" height="125" width="120" />';
	echo "<br>";
	echo '<span style="font-size : 1.1em;position:relative; top : 10px;word-break: break-all;white-space: pre-wrap;word-wrap: break-word;">' . $eqLogic->getHumanName(true, true) . '</span>';
	echo '</div>';
	$url = network::getNetworkAccess('external') . '/plugins/googlecast/core/php/googlecast.ajax.php?apikey=' . jeedom::getApiKey('googlecast') . '&id=' . $eqLogic->getId();
}
?>
</div>
</div>
<div class="col-lg-10 eqLogic" style="border-left: solid 1px #EEE; padding-left: 25px;display: none;">
  <a class="btn btn-success eqLogicAction pull-right" data-action="save"><i class="fa fa-check-circle"></i> {{Sauvegarder}}</a>
  <a class="btn btn-danger eqLogicAction pull-right" data-action="remove"><i class="fa fa-minus-circle"></i> {{Supprimer}}</a>
  <a class="btn btn-default eqLogicAction pull-right" data-action="configure"><i class="fa fa-cogs"></i> {{Configuration avancée}}</a>
  <a class="btn btn-default eqLogicAction pull-right" data-action="copy"><i class="fa fa-copy"></i> {{Dupliquer}}</a>
  <ul class="nav nav-tabs" role="tablist">
    <li role="presentation"><a href="#" class="eqLogicAction" aria-controls="home" role="tab" data-toggle="tab" data-action="returnToThumbnailDisplay"><i class="fa fa-arrow-circle-left"></i></a></li>
    <li role="presentation" class="active"><a href="#eqlogictab" aria-controls="home" role="tab" data-toggle="tab"><i class="fa fa-tachometer"></i> {{Equipement}}</a></li>
    <li role="presentation"><a href="#commandtab" aria-controls="profile" role="tab" data-toggle="tab"><i class="fa fa-list-alt"></i> {{Commandes}}</a></li>
  </ul>
  <div class="tab-content" style="height:calc(100% - 50px);overflow:auto;overflow-x: hidden;">
    <div role="tabpanel" class="tab-pane active" id="eqlogictab">
      <br/>
      <form class="form-horizontal">
        <fieldset>
          <div class="form-group">
            <label class="col-lg-3 control-label">{{Nom de l'équipement}}</label>
            <div class="col-lg-4">
              <input type="text" class="eqLogicAttr form-control" data-l1key="id" style="display : none;" />
              <input type="text" class="eqLogicAttr form-control" data-l1key="name" placeholder="{{Nom de l'équipement}}"/>
            </div>
          </div>
          <div class="form-group">
            <label class="col-lg-3 control-label" >{{Objet parent}}</label>
            <div class="col-lg-4">
              <select id="sel_object" class="eqLogicAttr form-control" data-l1key="object_id">
                <option value="">{{Aucun}}</option>
                <?php
foreach (object::all() as $object) {
	echo '<option value="' . $object->getId() . '">' . $object->getName() . '</option>';
}
?>
             </select>
           </div>
         </div>
         <div class="form-group">
          <label class="col-lg-3 control-label">{{Catégorie}}</label>
          <div class="col-lg-9">
            <?php
foreach (jeedom::getConfiguration('eqLogic:category') as $key => $value) {
	echo '<label class="checkbox-inline">';
	echo '<input type="checkbox" class="eqLogicAttr" data-l1key="category" data-l2key="' . $key . '" />' . $value['name'];
	echo '</label>';
}
?>
         </div>
       </div>
       <div class="form-group">
        <label class="col-sm-3 control-label"></label>
        <div class="col-sm-9">
          <label class="checkbox-inline"><input type="checkbox" class="eqLogicAttr" data-l1key="isEnable" checked/>{{Activer}}</label>
          <label class="checkbox-inline"><input type="checkbox" class="eqLogicAttr" data-l1key="isVisible" checked/>{{Visible}}</label>
        </div>
      </div>
      <div class="form-group">
        <label class="col-lg-3 control-label">{{UUDI}}</label>
        <div class="col-lg-4">
          <input type="text" class="eqLogicAttr form-control" data-l1key="logicalId" placeholder="Logical ID" readonly/>
        </div>
      </div>
	  <div class="form-group">
        <label class="col-lg-3 control-label">{{Nom diffusé}}</label>
        <div class="col-lg-4">
          <input type="text" class="eqLogicAttr form-control" data-l1key="configuration" data-l2key="friendly_name" readonly/>
        </div>
      </div>
	  <div class="form-group">
        <label class="col-lg-3 control-label">{{Modèle}}</label>
        <div class="col-lg-4">
          <input type="text" class="eqLogicAttr form-control" data-l1key="configuration" data-l2key="model_name" readonly/>
        </div>
      </div>
	  <div class="form-group">
        <label class="col-lg-3 control-label">{{Constructeur}}</label>
        <div class="col-lg-4">
          <input type="text" class="eqLogicAttr form-control" data-l1key="configuration" data-l2key="manufacturer" readonly/>
        </div>
      </div>
	  <div class="form-group">
        <label class="col-lg-3 control-label">{{Type}}</label>
        <div class="col-lg-4">
          <input type="text" class="eqLogicAttr form-control" data-l1key="configuration" data-l2key="cast_type" readonly/>
        </div>
      </div>
	  <div class="form-group">
        <label class="col-lg-3 control-label">{{IP}}</label>
        <div class="col-lg-4">
          <input type="text" class="eqLogicAttr form-control" data-l1key="configuration" data-l2key="ip" readonly/>
        </div>
      </div>
	  <div class="form-group">
        <label class="col-lg-3 control-label">{{Ignorer contrôle CEC}}</label>
        <div class="col-lg-4">
          <input type="checkbox" class="eqLogicAttr" data-l1key="configuration" data-l2key="ignore_CEC"/>
		  {{Si le statut 'Occupé' ne remonte pas bien}}
        </div>
      </div>
    </fieldset>
  </form>
</div>
<div role="tabpanel" class="tab-pane" id="commandtab">
  <a class="btn btn-success btn-sm cmdAction pull-right" data-action="add" style="margin-top:5px;"><i class="fa fa-plus-circle"></i> {{Ajouter une commande}}</a><br/><br/>
  <table id="table_cmd" class="table table-bordered table-condensed">
    <thead>
      <tr>
        <th style="width: 300px;">{{Nom}}</th>
        <th style="width: 130px;">Type</th>
        <th>{{Logical ID (info) ou Commande brute (action)}}</th>
        <th>{{Paramètres}}</th>
        <th style="width: 100px;">{{Options}}</th>
        <th></th>
      </tr>
    </thead>
    <tbody></tbody>
  </table>
</div>
</div>
</div>
</div>

<?php include_file('desktop', 'googlecast', 'js', 'googlecast');?>
<?php include_file('core', 'plugin.template', 'js');?>
