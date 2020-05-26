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
 <div class="col-xs-12 eqLogicThumbnailDisplay">
   <legend><i class="fa fa-cog"></i> &nbsp; {{Gestion}}</legend>
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
<legend><i class="icon techno-cable1"></i> &nbsp; {{Mes équipements Google Cast}}</legend>
<input class="form-control" placeholder="{{Rechercher}}" id="in_searchEqlogic" />
<div class="eqLogicThumbnailContainer">
<?php
foreach ($eqLogics as $eqLogic) {
    $opacity = ($eqLogic->getIsEnable()) ? '' : 'disableCard';
    echo '<div class="eqLogicDisplayCard cursor '.$opacity.'" data-eqLogic_id="' . $eqLogic->getId() . '" >';
	echo '<img src="' . $eqLogic->getConfiguration('logoDevice', 'plugins/googlecast/desktop/images/model_default.png') . '" />';
	echo '<br>';
	echo '<span class="name">' . $eqLogic->getHumanName(true, true) . '</span>';
	echo '</div>';
}
?>
</div>
</div>
<div class="col-xs-12 eqLogic" style="display: none;">
  <!-- <a class="btn btn-default pull-right bt_sidebarToogle"><i class="fa fa-dedent"></i></a> -->
  <a class="btn btn-success eqLogicAction pull-right" data-action="save"><i class="fa fa-check-circle"></i> {{Sauvegarder}}</a>
  <a class="btn btn-danger eqLogicAction pull-right" data-action="remove"><i class="fa fa-minus-circle"></i> {{Supprimer}}</a>
  <a class="btn btn-default eqLogicAction pull-right" data-action="configure"><i class="fa fa-cogs"></i> {{Configuration avancée}}</a>
  <a class="btn btn-primary pull-right" target="_blank" href="{{https://github.com/guirem/plugin-googlecast/blob/master/docs/fr_FR/index.md#commandes-personnalisées}}"><i class="fa fa-book"></i> Documentation</a>
  <ul class="nav nav-tabs" role="tablist">
    <li role="presentation"><a href="#" class="eqLogicAction" aria-controls="home" role="tab" data-toggle="tab" data-action="returnToThumbnailDisplay"><i class="fa fa-arrow-circle-left"></i></a></li>
    <li role="presentation" class="active"><a href="#eqlogictab" aria-controls="home" role="tab" data-toggle="tab"><i class="fa fa-tachometer"></i> {{Google Cast}}</a></li>
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
                foreach (jeeObject::all() as $object) {
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
        <label class="col-lg-3 control-label">{{UUID}}</label>
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
	  <div class="form-group has_googleassistant_form">
        <label class="col-lg-3 control-label">{{Compatible Google Assistant ?}}</label>
        <div class="col-lg-4">
          <input type="checkbox" class="eqLogicAttr ga_token_input" data-l1key="configuration" data-l2key="has_googleassistant"/>
        </div>
      </div>
	  <div class="form-group ga_token_form">
        <label class="col-lg-3 control-label">{{Jeton Google Assistant/Home}}</label>
        <div class="col-lg-4">
          <textarea type="textarea" rows="2" class="eqLogicAttr form-control" data-l1key="configuration" data-l2key="ga_token" placeholder="{{Optionnel - Permet d'avoir accès à certaines configurations Google Home (alarmes, timers...)}}"></textarea>
        </div>
      </div>
    </fieldset>
  </form>
</div>
<div role="tabpanel" class="tab-pane" id="commandtab">
  <a class="btn btn-success btn-sm cmdAction pull-right" data-action="add" style="margin-top:5px;margin-right:10px;"><i class="fa fa-plus-circle"></i> {{Ajouter une commande}}</a><br/><br/>
  <table id="table_cmd" class="table table-bordered table-condensed">
    <thead>
      <tr>
        <th style="width: 250px;">{{Nom}}</th>
        <th style="width: 75px;">Type</th>
        <th>{{Liste de commandes}}</th>
        <th style="width: 185px;">{{Paramètres}}</th>
        <th style="width: 125px;">{{Options}}</th>
        <th style="width: 92px;">{{Actions}}</th>
      </tr>
    </thead>
    <tbody></tbody>
  </table>
   <a class="btn btn-primary btn-sm pull-left" style="margin-top:5px;margin-left:10px;" target="_blank" href="{{https://github.com/guirem/plugin-googlecast/blob/master/docs/fr_FR/index.md#commandes-personnalisées}}"><i class="fa fa-book"></i> Documentation</a>
   <a class="btn btn-success btn-sm cmdAction pull-right" data-action="add" style="margin-top:5px;margin-right:10px;"><i class="fa fa-plus-circle"></i> {{Ajouter une commande}}</a><br/><br/>
</div>
</div>
</div>
</div>

<?php include_file('desktop', 'googlecast', 'js', 'googlecast');?>
<?php include_file('core', 'plugin.template', 'js');?>
