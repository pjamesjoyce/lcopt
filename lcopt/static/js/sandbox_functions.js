var sayHello = function(){
  //console.log("Hello from the functions file")
}


// unit choices 
var UNIT_CHOICES = {
    'Mass': [
        ['kg',  'kilogram'],
        ['g',  'gram'],
    ]
    ,
    'Energy': [
        ['kWh',  'kilowatt hour'],
        ['Wh',  'watt hour'],
        ['GJ',  'gigajoule'],
        ['kJ',  'kilojoule'],
        ['MJ',  'megajoule'],
    ]
    ,
    'Volume': [
        ['l',  'litre'],
        ['m3',  'cubic meter'],
    ]
    ,
    'Radioactivity': [
        ['Bq',  'Becquerel'],
        ['kBq',  'kilo Becquerel'],
    ]
    ,
    'Time': [
        ['a',  'year'],
        ['h',  'hour'],
    ]
    ,
    'Amount': [
        ['p',  'unit'],
    ]
    ,
    'Area':[
        ['ha',  'hectare'],
        ['m2',  'square meter'],
    ],
    'Transport':[
        ['kgkm',  'kilogram kilometer'],
        ['tkm',  'ton kilometer'],
        ['personkm',  'person kilometer'],
        ['vkm',  'vehicle kilometer'],
    ],
    'Distance':[
        ['km',  'kilometer'],
        ['m',  'meter'],
    ],
    'Other':[
        ['lu',  'livestock unit'],
        ['m*year',  'meter-year'],
        ['m2*year',  'square meter-year'],
        ['m3*year',  'cubic meter-year'],
        ['kg sw',  'kilogram separative work unit'],
        ['km*year',  'kilometer-year'],
        ['EUR2003', 'EUR2003']
    ]
} 

// This function creates a new node from external data
var newNodeExternal = function(name, type, id, x, y, instance, outputlabel = ''){
  
  if(outputlabel != ''){instance.data.outputlabels[id] = outputlabel};
  //console.log(outputlabel)
  //console.log(instance.data.outputlabels[id])
  var id = id//name.split(' ').join('_')//jsPlumbUtil.uuid();
  var d = $('<div>').attr('id', id).addClass('w ' + type);
  var title =  $('<div>').addClass('title').text(name);
  var buttons = $('<div>').addClass('buttons');
  var connect =  $('<div>').addClass('ep').html('<i class="ep2 material-icons md-18" data-toggle="popover" data-placement= "left" data-trigger="hover" title="Connect" data-content="Drag to connect to another process">trending_flat</i>');
  var input =  $('<div>').addClass('ip').html('<i class="material-icons md-18" data-toggle="popover" data-placement= "bottom" data-trigger="hover" title="Technosphere exchange" data-content="Add an input from the \'Technosphere\' (materials and energy) to this process">business</i>');
  var output =  $('<div>').addClass('op').html('<i class="material-icons md-18" data-toggle="popover" data-placement= "bottom" data-trigger="hover" title="Biosphere exchange" data-content="Add an emission (or resource flow) to/from the environment (biosphere) to this process">local_florist</i>');
  var analyse =  $('<div>').addClass('analyse').html('<i class="material-icons md-18" data-toggle="popover" data-placement= "right" data-trigger="hover" title="Analyse" data-content="Run LCA for this process">pie_chart</i>');
  //var edit = $('<div>').addClass('ed').html('<i class="material-icons w3-medium" data-toggle="popover" data-placement= "bottom" data-trigger="hover" title="Edit" data-content="Edit quantity">edit</i>');
  var unlink = $('<div>').addClass('unlink').html('<i class="material-icons md-18" data-toggle="popover" data-placement= "bottom" data-trigger="hover" title="Remove" data-content="Remove this input/emision">cancel</i>');

  if(type == 'transformation'){
    buttons.append(connect).append(input).append(output).append(analyse);
  }else{
    buttons.append(unlink);
  };
  //buttons.append(del);
  d.append(title);
  d.append(buttons);

  var canvas = $("#sandbox_container");
  canvas.append(d);

  d.css('left', x + "px");
  d.css('top', y + "px");


  d.bind("mouseover", function(el){
    nodeOver(el, instance);
  });
  d.bind("mouseout", function(el){
    nodeOut(el, instance);
  });

  // This is the tooltip that explains the icons
  ////console.log(instance);
  $('[data-toggle="popover"]').popover({
    container: '#sandbox_container',
    delay: {
       show: "1000",
       hide: "100"
    },
  });
  return d;
};



var initNode = function(el, instance) {

            var i = instance
            //console.log(i.data)
            //console.log(el)

            // initialise draggable elements.
            instance.draggable(el, {
              grid: [0.5,0.5],
              containment:true,
              stop: function(event) {

              var getID = el.id;
              if(typeof getID == 'undefined'){getID = el[0].id;};

              //console.log('getID');
              //console.log(getID);

              var $target = $('#' + getID)
              if ($target.find('select').length == 0) {
                saveState($target);
              }

            },

            });

            // make the link icon a source
            instance.makeSource(el, {
                filter: ".ep,.ep2",
                connectionType:"basic intermediate",
            });
            //make the whole thing a target
            instance.makeTarget(el, {
                dropOptions: { hoverClass: "dragHover" },
                //anchor: "Continuous",
                allowLoopback: false
            });

            //This is the delete function
            //TODO: Fix this for Flask implentation
            $('.unlink').unbind().click(function(e, instance = i){
              ////console.log(instance)
              ////console.log(i)

              removeInput(e, instance)

            });           



            $('.analyse').unbind().click(function(e){
              ////console.log('#' + $(this).parent().parent().attr('id'));
              this_id = $(this).parent().parent().attr('id')
              this_name = $(this).parent().parent().find('.title').text()
              start_analysis(this_id, this_name)

              //console.log('TODO: Fix this for Flask implentation')
              
            }); 
            
            //This is the add input function
            //TODO: Fix this for Flask implentation
            $('.ip').unbind().click(function(e, instance = i){
              ////console.log(instance)
              ////console.log(i)

              addInput(e, instance)

            });

            //This is the add output function
            //TODO: Fix this for Flask implentation
            $('.op').unbind().click(function(e){

                //console.log('TODO: Fix this for Flask implentation')
                addBiosphere(e, instance)
              
            }); 
            

            //This is the edit function for inputs and outputs
            //TODO: Fix this for Flask implentation
            $('.ed').unbind().click(function(e){

                //console.log('TODO: Fix this for Flask implentation')
              
            }); 

            update_status();
            
};
      

// Saves the position of a node after dragging
// TODO : Implement for Flask      
var saveState = function(state) {
  //console.log(state.selector)
  postData ={
      'action' : 'savePosition',
      'uuid': $(state).attr('id'),
      'y': $(state).position().top,
      'x': $(state).position().left,
      //'csrfmiddlewaretoken': csrftoken,
   };
   //console.log(postData);

  $.post('/process_post', postData);
}

var saveModel = function(){
  //console.log('saving model')
  postData = {
    'action' : 'saveModel'
  }
  $.post('/process_post', postData);
  
}

// This function sends the information required to the python side to create a new process in the loaded model instance
var newProcess = function(uuid, process_name, output_name, unit){

  //console.log('sending new process info to python model')
  postData = {
    'action' : 'newProcess',
    'uuid' : uuid,
    'process_name' : process_name,
    'output_name' : output_name,
    'unit': unit
  }
  $.post('/process_post', postData);
}

var newConnection = function(info, instance){
  ////console.log('Dealing with a connection event (' + sID +')')



      source = $('#' + info.sourceId)
      target = $('#' + info.targetId)

      //info.connection.setData({'connection_type':'intermediate'})

      postData = {
          'action': 'newConnection',
          'sourceId' : info.sourceId,
          'targetId' : info.targetId,
          'label': info.connection.getOverlay('label').getLabel(),
        }

        //console.log(postData);
        $.post('/process_post', postData);
}

var unlinkIntermediate = function(connection) {
    //console.log(connection.targetId)
    targetId = connection.targetId
    sourceId = connection.sourceId

    postData = {
          'action': 'unlinkIntermediate',
          'targetId' : targetId,
          'sourceId': sourceId,
        };

        //console.log(postData);
    $.post('/process_post', postData);

    jsPlumb.detach(connection)

}

var addInput = function(e, instance){

    var target = $( e.target )
    ////console.log(target)

    var thisNodeID = target.parent().parent().parent().attr('id');
    ////console.log("thisNodeID is...")
    ////console.log(thisNodeID);
    ////console.log(instance)
    var thisConnections = instance.getConnections({ target: thisNodeID });

    thisConnectionList = [];



    for(i=0; i<thisConnections.length; i++){
      var sId = thisConnections[i].sourceId;
      thisConnectionList.push($('#'+ sId + " .title").text());
    }

    ////console.log(thisConnectionList);

    var formTitle = 'Add input'
    // this is the html that will go in the body of the modal
    var formHtml = `
                    <form class="form-horizontal">
                      <div class="form-group">
                        <label for="inputName" class="control-label col-xs-3" data-toggle="popover" data-placement= "left" data-trigger="hover" title="Name of the input" 
                            data-content="Give the input an appropriate name, if you want to reuse it somewhere else you can search for it using its name.
                             Note, if you're going to use multiple versions of this input, make sure you name it with something identifying, e.g. Electricity [UK], Electricity [Belgium] "
                             >Name of input</label> 
                        <div class="col-xs-9">
                          <input class="form-control typeahead" name = "inputName" id="inputName" autocomplete="off" style="background-color: white;">
                        </div>
                      </div>
                      <div class="form-group">
                        <label for="unlinked" class="control-label col-xs-5"
                            data-toggle="popover" data-placement= "left" data-trigger="hover" title="Burden free?" 
                            data-content="If this is a waste being used as a resource, there's no need to specify it any further, we can assume it has an impact of zero"
                             >This input is burden free</label> 
                        <div class="col-xs-1">
                          <input type="checkbox" class="checkbox-inline" name = "unlinked", id="unlinked">
                        </div>
                        <div id="spacer" class="col-xs-3">
                        - or -
                        </div>
                        <div id="ext_data_button" class="col-xs-3">
                                                  
                        </div>
                      </div>
                      <div class="form-group">
                        <label for="extLink" class="control-label col-xs-3"
                            data-toggle="popover" data-placement= "left" data-trigger="hover" title="Link to LCI data" 
                            data-content="This is automatically populated if you're reusing an input or creating a new one with linked LCI data - its here so you can see the details of the LCI dataset (in case you're interested)"
                            >Link to LCI data</label> 
                        <div class="col-xs-9">
                          <input class="form-control disabled" name = "extLinkName", id="extLinkName" disabled>
                          <input class="form-control disabled" name = "extLink", id="extLink" disabled>
                        </div>
                      </div>
                      <div class="form-group">
                        <label for="unit" class = "control-label col-xs-3"
                            data-toggle="popover" data-placement= "left" data-trigger="hover" title="Unit" 
                            data-content="If your input is burden free, you need to specify a unit, otherwise it'll get automatically chosen based on the LCI dataset you're using">Unit</label>
                        <div class="col-xs-6" id="unitDiv"></div>
                      </div>
                      
                    </form>
                  `
    

    var inputModal = BootstrapDialog.show({
      title:formTitle,
      message:function(dialogRef){
        var $message = $('<div></div>').append(formHtml);
        // This populates the unit list from the UNIT_CHOICES variable
        var unitMap = {};
        var unitHtml = "<select name='unit' id='unit' class='selectpicker form-control col-xs-6'>"

        for(i in UNIT_CHOICES){
          unitHtml += "<optgroup label = '"+ i +"'>";
          
          for(j in UNIT_CHOICES[i]){
            unitHtml += "<option value = '"+UNIT_CHOICES[i][j][0]+"'>"+UNIT_CHOICES[i][j][1]+"</option>"
            unitMap[UNIT_CHOICES[i][j][1]] = [UNIT_CHOICES[i][j][0]]
          };
          unitHtml+="</optgroup>";
        };
        unitHtml+="</select>"
        var $units = $(unitHtml)
        

        $message.find('#unitDiv').append($units)
        $units.selectpicker()
        


        /*This bit sets up the typeahead*/

        function customTokenizer(datum) {
          var nameTokens = Bloodhound.tokenizers.whitespace(datum.name);
          //var ownerTokens = Bloodhound.tokenizers.whitespace(datum.owner);
          //var languageTokens = Bloodhound.tokenizers.whitespace(datum.language);

          return nameTokens//.concat(ownerTokens).concat(languageTokens);
        }

        function typeaheadCallback(postResponse){
          if (postResponse.isLinked == true) {
            //console.log(postResponse)
            var unit = unitMap[postResponse.ext_link_unit]
            $message.find('#extLinkName').val(postResponse.ext_link_string);
            $message.find('#extLink').val(postResponse.ext_link)
            $message.find('#unit').selectpicker('val', unit);
            $message.find('#unit').addClass('disabled').prop( "disabled", true )
            $message.find('#ext_search_button').addClass('disabled').prop( "disabled", true )
            $message.find('#unlinked').addClass('disabled').prop( "disabled", true ).prop("checked", false)
          }
          else
          {
            //console.log(postResponse)
            $message.find('#unit').selectpicker('val', postResponse.unlinked_unit);
            $message.find('#unit').addClass('disabled').prop( "disabled", true )
            $message.find('#unlinked').addClass('disabled').prop( "disabled", true ).prop("checked", true)
          }
        }

         function createNewTemplate(){
          current_input = $('#inputName').val()
          $create_new = $('<div class="tt-footer"><p>Create new input called <strong>'+current_input+'<strong></p></div>')
          $create_new.click(function(){
            $message.find('#ext_search_button').removeClass('disabled').prop( "disabled", false )
            $message.find('#unit').removeClass('disabled').prop( "disabled", false )
            $message.find('#unlinked').removeClass('disabled').prop( "disabled", false ).prop('checked', false)
            $('.typeahead').typeahead('close');
          })
          return $create_new
          }



        var inputs = new Bloodhound({
            //local: [{name: "James item", code:1},{name: "Claire item", code:2}],
            //local: [{"code": "acdf091633109d3b6b7744a602720412", "name": "Input of Unlinked input"}, {"code": "bc1d1b9e06255d25691d4bc25cbed054", "name": "Input of Quartz - linked"}, {"code": "440891b98348acaa325bb80b1e0080fb", "name": "Input of Energy, electricity"}],
            //identify: function(obj) { return obj.code; },
              datumTokenizer: customTokenizer,// Bloodhound.tokenizers.whitespace('name'),
              queryTokenizer: Bloodhound.tokenizers.whitespace,
              // The url points to a json file that contains an array of input names
              //prefetch: './inputs.json',
              prefetch: {
                url: 'inputs.json',
                transform: function(list) {
                    return $.map(list, function(item) {
                        return {
                            name: item.name,
                            code: item.code,
                            //etc:item.etc
                        };
                        
                    });
                },
                cache:false,
            },
          });
         //console.log(inputs)

          // Initializing the typeahead with remote dataset
          $message.find('.typeahead').typeahead({
            minLength: 1,
            highlight: true
            },
            {
                name: 'inputs',
                display:'name',
                source: inputs,
                templates:{
                  header: '<div class="tt-header"><p>Reuse existing input...</p></div>',
                  footer: createNewTemplate,
                  notFound: createNewTemplate,
            },
            }
          );

          function eventHandler(obj, suggestion){
            //console.log(suggestion)
            var postData ={
              'action': 'inputLookup',
              'code': suggestion.code,
              'format' : 'ecoinvent',
            }
            //console.log(postData)
            $.post('/process_post',
              postData, 
              function(data, status, xhr){
                  if(status == 'success'){
                    typeaheadCallback(data)
                  }
                }, 
                "json");
          }
          
        $message.find('#inputName').bind('typeahead:selected', function(obj, suggestion) {  
            //console.log('selected');
            eventHandler(obj, suggestion);
        });
        $message.find('#inputName').bind('typeahead:autocomplete', function(obj, suggestion) {  
            //console.log('autocomplete');
            eventHandler(obj, suggestion);
            $message.find('.tt-footer').addClass('hide')
        });

        $message.find('#inputName').keypress(function(e){
          if(e.keyCode==13){
            //console.log('enter')
          }
        });

        $message.find('#inputName').keydown(function(e){
          if(e.keyCode==8 || e.keyCode==46){
            //console.log('delete/backspace')
            $('#extLinkName').val('');
          $('#extLink').val('')
          $message.find('#ext_search_button').removeClass('disabled').prop( "disabled", false )
          $message.find('#unit').removeClass('disabled').prop( "disabled", false )
          $message.find('#unlinked').removeClass('disabled').prop( "disabled", false ).prop('checked', false)
          }
        });


        var $button = $('<button type="button" id="ext_search_button" type="submit" class="pull-right btn btn-primary" data-toggle="popover" data-placement= "right" data-trigger="hover" title="Search for LCI data" data-content="Search for Life Cycle Inventory data for this process">Search for LCI data</button>')

        // This is the callback function that gets run by the search box once it has a result
        function logResult(name, code){

          var unit_re = /\[([\w ]*)\]$/
          var unit_name = unit_re.exec(name)[1]
          var unit = unitMap[unit_name]
          //console.log(unit[0])



          $message.find('#extLink').val(code);
          $message.find('#extLinkName').val(name);
          $message.find('#unit').selectpicker('val', unit);
          $message.find('#unlinked').addClass("disabled");
          $message.find('#unit').addClass("disabled");
          $message.find('#unit').prop('disabled', true);
          inputModal.setData('code', code);
          inputModal.setData('ext_link_name', name);
          inputModal.setData('unit',unit);
        }

        $button.on('click', function(){
          // search_ecoinvent_dialog now takes a callback function which gets run when the user clicks ok
          search_external_dialog('Search for LCI data', logResult, 'searchEcoinvent')

        })
        $message.find('#ext_data_button').append($button)
        $message.find('[data-toggle="popover"]').popover({
          container: '#sandbox_container',
          delay: {
             show: "0",
             hide: "100"
          },
        });

        return $message
      },
      nl2br: false,
      buttons:[{
        label:'OK',
        cssClass: 'btn-primary',
        action:function(dialogRef){

            var name = $('#inputName').val();
            var type = 'product'
            var unit = $('#unit').selectpicker('val');//inputModal.getData('unit')[0],
            //console.log("unit at OK click " + unit)
            var location = 'GLO';
            var code = hex_md5(name+type+unit+location);
            var suffix = $('[id^=' + code + ']').size();
            var node_id = code + '__' + suffix;
            var ext_link_name = inputModal.getData('ext_link_name');
            var ext_link = inputModal.getData('code');
            var ext_link_check = $('#extLink').val();
            var unlinked = $('#unlinked').is(':checked') 
            //console.log('creating node with id ' + node_id)

            if(name && (ext_link_check || unlinked)){
              var postData = {
                  'action': 'addInput',
                  'targetId': thisNodeID,
                  'name': name,
                  'type': type,
                  'unit': unit,
                  'location': location,
                  'code':code,
                  'ext_link_name' : ext_link_name,
                  'ext_link': ext_link,
                  'lcopt_type': 'input'
    
               }
    
              console.log(postData);
    
              $.post('/process_post', postData);
              //close the dialog
              dialogRef.close()
    
              var position = $('#'+thisNodeID).position()
              //console.log(position)
    
              // create a new node in the js side version for display on screen, and initiate it
              var thisNode = newNodeExternal(name,'input',node_id,position.left + 25,position.top - 50,instance);
              initNode(thisNode,instance);
              saveState(thisNode);
    
              //connect the new node
              var thisConnection = instance.connect({
                source: node_id,
                target: thisNodeID,
                type:"basic input",
                data:{'connection_type':'input'}
              })
            }else{
              $('.inputMessage').remove();
              if(!name){
                $('#inputName').after('<div class="red inputMessage">Please give the exchange a name</div>');
              }
              if(!ext_link_check){
                $('#extLink').after('<div class="red inputMessage">Please specify an exchange (or mark this input as burden free)</div>');
              }
            }

        }
      },
      {
        label:'Cancel',
        action: function(dialogRef){
          dialogRef.close();
        }
      }]
    });
  };


var removeInput = function(e, instance){
  var target = $( e.target )
    ////console.log(target)

    var thisNodeID = target.parent().parent().parent().attr('id');
    ////console.log("thisNodeID is...")
    ////console.log(thisNodeID);
    ////console.log(instance)
    var thisConnections = instance.getConnections({ source: thisNodeID });

    console.log(thisConnections[0].sourceId, thisConnections[0].targetId)

    var postData ={
              'action': 'removeInput',
              'sourceId': thisConnections[0].sourceId,
              'targetId' : thisConnections[0].targetId,
            }
            //console.log(postData)
            $.post('/process_post', postData)

    // TODO : Update the GUI

    //jsPlumb.remove(thisNodeID)
    jsPlumb.detach(thisConnections[0])
    jsPlumb.remove(thisNodeID)
    $('.popover').remove()      
}

// This is the add biosphere function - a big copy of the addInput one - these could maybe be rationalised later...

var addBiosphere = function(e, instance){

    var target = $( e.target )
    ////console.log(target)

    var thisNodeID = target.parent().parent().parent().attr('id');
    ////console.log("thisNodeID is...")
    ////console.log(thisNodeID);
    ////console.log(instance)
    var thisConnections = instance.getConnections({ target: thisNodeID });

    thisConnectionList = [];



    for(i=0; i<thisConnections.length; i++){
      var sId = thisConnections[i].sourceId;
      thisConnectionList.push($('#'+ sId + " .title").text());
    }

    ////console.log(thisConnectionList);

    var formTitle = 'Add biosphere exchange'
    // this is the html that will go in the body of the modal
    var formHtml = `
                    <form class="form-horizontal">
                      <div class="form-group">
                        <label for="exchangeName" class="control-label col-xs-3"
                        data-toggle="popover" data-placement= "left" data-trigger="hover" title="Name of exchange" 
                            data-content="Give the emission (or resource) an appropriate name, if you want to reuse it somewhere else you can search for it using its name."
                             >Name of biosphere exchange</label> 
                        <div class="col-xs-9">
                          <input class="form-control typeahead" name = "exchangeName", id="exchangeName" autocomplete="off">
                        </div>
                      </div>
                      <div class="form-group">
                        <div id="ext_data_button" class="col-xs-9 col-xs-offset-3"></div>
                      </div>
                      <div class="form-group">
                        <label for="extLink" class="control-label col-xs-3"
                        data-toggle="popover" data-placement= "left" data-trigger="hover" title="Link to biosphere data" 
                            data-content="This is automatically populated with the linked biosphere data - its here so you can see the details of the biosphere dataset (in case you're interested)">Link to biosphere database</label> 
                        <div class="col-xs-9">
                          <input class="form-control disabled" name = "extLinkName", id="extLinkName" disabled>
                          <input class="form-control disabled" name = "extLink", id="extLink" disabled>
                        </div>
                      </div>
                      <div class="form-group">
                        <label for="unit" class = "control-label col-xs-3"
                            data-toggle="popover" data-placement= "left" data-trigger="hover" title="Unit" 
                            data-content="This will be automatically chosen based on the biosphere dataset you're using"
                            >Unit</label>
                        <div class="col-xs-9" id="unitDiv"></div>
                      </div>
                      
                    </form>
                  `
    

    var inputModal = BootstrapDialog.show({
      title:formTitle,
      message:function(dialogRef){
        var $message = $('<div></div>').append(formHtml);
        // This populates the unit list from the UNIT_CHOICES variable
        var unitMap = {};
        var unitHtml = "<select name='unit' id='unit' class='selectpicker form-control col-xs-6'>"

        for(i in UNIT_CHOICES){
          unitHtml += "<optgroup label = '"+ i +"'>";
          
          for(j in UNIT_CHOICES[i]){
            unitHtml += "<option value = '"+UNIT_CHOICES[i][j][0]+"'>"+UNIT_CHOICES[i][j][1]+"</option>"
            unitMap[UNIT_CHOICES[i][j][1]] = [UNIT_CHOICES[i][j][0]]
          };
          unitHtml+="</optgroup>";
        };
        unitHtml+="</select>"
        var $units = $(unitHtml)
        

        $message.find('#unitDiv').append($units)
        $units.selectpicker()

        /*This bit sets up the typeahead*/

        function customTokenizer(datum) {
          var nameTokens = Bloodhound.tokenizers.whitespace(datum.name);
          //var ownerTokens = Bloodhound.tokenizers.whitespace(datum.owner);
          //var languageTokens = Bloodhound.tokenizers.whitespace(datum.language);

          return nameTokens//.concat(ownerTokens).concat(languageTokens);
        }

        function typeaheadCallback(postResponse){
          if (postResponse.isLinked == true) {
            //console.log(postResponse)
            var unit = unitMap[postResponse.ext_link_unit]
            $message.find('#extLinkName').val(postResponse.ext_link_string);
            $message.find('#extLink').val(postResponse.ext_link)
            $message.find('#unit').selectpicker('val', unit);
            $message.find('#unit').addClass('disabled').prop( "disabled", true )
            $message.find('#ext_search_button').addClass('disabled').prop( "disabled", true )
            
          }
          else
          {
            //console.log(postResponse)
            $message.find('#unit').selectpicker('val', postResponse.unlinked_unit);
            $message.find('#unit').addClass('disabled').prop( "disabled", true )
            
          }
        }

         function createNewTemplate(){
          current_input = $('#exchangeName').val()
          $create_new = $('<div class="tt-footer"><p>Create new named exchange called <strong>'+current_input+'<strong></p></div>')
          $create_new.click(function(){
            $message.find('#ext_search_button').removeClass('disabled').prop( "disabled", false )
            $message.find('#unit').removeClass('disabled').prop( "disabled", false )
            
            $('.typeahead').typeahead('close');
          })
          return $create_new
          }



        var inputs = new Bloodhound({
            //local: [{name: "James item", code:1},{name: "Claire item", code:2}],
            //local: [{"code": "acdf091633109d3b6b7744a602720412", "name": "Input of Unlinked input"}, {"code": "bc1d1b9e06255d25691d4bc25cbed054", "name": "Input of Quartz - linked"}, {"code": "440891b98348acaa325bb80b1e0080fb", "name": "Input of Energy, electricity"}],
            //identify: function(obj) { return obj.code; },
              datumTokenizer: customTokenizer,// Bloodhound.tokenizers.whitespace('name'),
              queryTokenizer: Bloodhound.tokenizers.whitespace,
              // The url points to a json file that contains an array of input names
              //prefetch: './inputs.json',
              prefetch: {
                url: 'biosphere.json',
                transform: function(list) {
                    return $.map(list, function(item) {
                        return {
                            name: item.name,
                            code: item.code,
                            //etc:item.etc
                        };
                        
                    });
                },
                cache:false,
            },
          });
         //console.log(inputs)

          // Initializing the typeahead with remote dataset
          $message.find('.typeahead').typeahead({
            minLength: 1,
            highlight: true
            },
            {
                name: 'inputs',
                display:'name',
                source: inputs,
                templates:{
                  header: '<div class="tt-header"><p>Reuse existing exchange...</p></div>',
                  footer: createNewTemplate,
                  notFound: createNewTemplate,
            },
            }
          );

          function eventHandler(obj, suggestion){
            //console.log(suggestion)
            var postData ={
              'action': 'inputLookup',
              'code': suggestion.code,
              'format' : 'biosphere',
            }
            //console.log(postData)
            $.post('/process_post',
              postData, 
              function(data, status, xhr){
                  if(status == 'success'){
                    typeaheadCallback(data)
                  }
                }, 
                "json");
          }
          
        $message.find('#exchangeName').bind('typeahead:selected', function(obj, suggestion) {  
            //console.log('selected');
            eventHandler(obj, suggestion);
        });
        $message.find('#exchangeName').bind('typeahead:autocomplete', function(obj, suggestion) {  
            //console.log('autocomplete');
            eventHandler(obj, suggestion);
            $message.find('.tt-footer').addClass('hide')
        });

        $message.find('#exchangeName').keypress(function(e){
          if(e.keyCode==13){
            //console.log('enter')
          }
        });

        $message.find('#exchangeName').keydown(function(e){
          if(e.keyCode==8 || e.keyCode==46){
            //console.log('delete/backspace')
            $('#extLinkName').val('');
          $('#extLink').val('')
          $message.find('#ext_search_button').removeClass('disabled').prop( "disabled", false )
          $message.find('#unit').removeClass('disabled').prop( "disabled", false )
          }
        });


        var $button = $('<button type="button" id="ext_search_button" type="submit" class="btn btn-primary" data-toggle="popover" data-placement= "right" data-trigger="hover" title="Search for biosphere data" data-content="Search for the exchange with the environment you want to model">Search for biosphere data</button>')

        // This is the callback function that gets run by the search box once it has a result
        function logResult(name, code){

          var unit_re = /\[([\w ]*)\]$/
          var unit_name = unit_re.exec(name)[1]
          var unit = unitMap[unit_name]
          console.log(name)
          console.log(code)



          $message.find('#extLink').val(code);
          $message.find('#extLinkName').val(name);
          $message.find('#unit').selectpicker('val', unit);
          $message.find('#unit').addClass("disabled");
          $message.find('#unit').prop('disabled', true);
          inputModal.setData('code', code);
          inputModal.setData('ext_link_name', name);
          inputModal.setData('unit',unit);
        }

        $button.on('click', function(){
          // search_ecoinvent_dialog now takes a callback function which gets run when the user clicks ok
          //search_ecoinvent_dialog(logResult)
          search_external_dialog('Search for biosphere flow', logResult, 'searchBiosphere')

        })
        $message.find('#ext_data_button').append($button)
        $message.find('[data-toggle="popover"]').popover({
          container: '#sandbox_container',
          delay: {
             show: "0",
             hide: "100"
          },
        });
        return $message
      },
      nl2br: false,
      buttons:[{
        label:'OK',
        cssClass: 'btn-primary',
        action:function(dialogRef){

            var name = $('#exchangeName').val();
            var type = 'product'
            var unit = $('#unit').selectpicker('val');//inputModal.getData('unit')[0],
            //console.log("unit at OK click " + unit)
            var location = 'GLO';
            var code = hex_md5(name+type+unit+location);
            var suffix = $('[id^=' + code + ']').size();
            var node_id = code + '__' + suffix;
            var ext_link_name = inputModal.getData('ext_link_name');
            var ext_link = inputModal.getData('code');
            var ext_link_check = $('#extLink').val();

            //console.log('creating node with id ' + node_id)

            if(name && ext_link_check){
                var postData = {
                  'action': 'addInput',
                  'targetId': thisNodeID,
                  'name': name,
                  'type': type,
                  'unit': unit,
                  'location': location,
                  'code':code,
                  'ext_link_name' : ext_link_name,
                  'ext_link': ext_link,
                  'lcopt_type': 'biosphere',
               }
  
              console.log(postData);
  
              $.post('/process_post', postData);
              //close the dialog
              dialogRef.close()
  
              var position = $('#'+thisNodeID).position()
              //console.log(position)
  
              // create a new node in the js side version for display on screen, and initiate it
              var thisNode = newNodeExternal(name,'biosphere',node_id,position.left + 25,position.top - 50,instance);
              initNode(thisNode,instance);
              saveState(thisNode);
  
              //connect the new node
              var thisConnection = instance.connect({
                source: node_id,
                target: thisNodeID,
                type:"basic biosphere",
                data:{'connection_type':'biosphere'}
              })
  
              thisConnection.addClass('connection_biosphere')
            }else{
              $('.inputMessage').remove();
              if(!name){
                $('#exchangeName').after('<div class="red inputMessage">Please give the exchange a name</div>');
              }
              if(!ext_link_check){
                $('#extLink').after('<div class="red inputMessage">Please specify an exchange</div>');
              }
            }
        }
      },
      {
        label:'Cancel',
        action: function(dialogRef){
          dialogRef.close();
        }
      }]
    });
  };


var echo = function(){

  postData = {
    'action': 'echo'
  }
  // this sends a post request with the data and then sends the result to the 'carry_on' function which is defined separately
    $.post('/process_post',
        postData,
        function(data, status, xhr){
          if(status == 'success'){
            carry_on(data)
          }
        }, 
        "json");
}

// this is the carry_on function that recieves the data from the ajax request after it's been successful
var carry_on = function(returnedData){
  //console.log("dealing with result from echo");
  //console.log('The server says\n' + returnedData['message']); 
}

var search_external_dialog = function(title, callback, action){

  
    // this is the title of the modal
    var formTitle = title
    // this is the html that will go in the body of the modal
    var formHtml = `
                    <form class="form-horizontal">
                      <div class="form-group">
                        <label for="searchTerm" class="control-label col-xs-3"
                        data-toggle="popover" data-placement= "left" data-trigger="hover" title="Search term" 
                            data-content="What are you looking for?">Search for:</label> 
                        <div class="col-xs-9">
                          <input class="form-control ecoinventSearchTrigger" name = "searchTerm", id="searchTerm" autocomplete="off">
                          <input name="hidden_control_to_stop_submission" style="{display:none}" class = "hidden">
                        </div>
                      </div>
                      `
    if(action == 'searchEcoinvent'){
      formHtml +=`<div class="form-group">
                        <label for="location" class="control-label col-xs-3"
                          data-toggle="popover" data-placement= "left" data-trigger="hover" title="Location" 
                            data-content="You can filter your search by location - This is particularly useful for electricity. Leave this blank to search everywhere">Location</label> 
                        <div class="col-xs-9">
                          <select multiple class="ecoinventSearchTrigger" name = "location", id="location" autocomplete="off"></select>
                        </div>
                      </div>
                      <div class="form-group">
                        <label for="marketsOnly" class="control-label col-xs-3"
                            data-toggle="popover" data-placement= "left" data-trigger="hover" title="Market processes" 
                            data-content="<strong>Recommended if using ecoinvent 3</strong><br>In ecoinvent, market processes represent the mix of technologies/sources for the production of products used in the chosen location. If you don't know where or how an input is made, use markets processes. If you do, you can leave this unticked and search for production processes. If you're not using ecoinvent 3 (e.g. using FORWAST) leave this unticked">Only show market processes (ecoinvent):</label> 
                        <div class="col-xs-6">
                          <input type="checkbox" class="checkbox-inline ecoinventSearchTrigger" name = "marketsOnly", id="marketsOnly">
                        </div>
                        <div id = "button_goes_here" class="col-xs-3">
                          
                        </div>
                      </div>
                    </form>
                    `
    }else{
      formHtml += `<div class="form-group">
                        
                        <div id = "button_goes_here" class="col-xs-12">
                          
                        </div>
                      </div>
                    </form>
                    `
    }
                      
    formHtml +=     `
                    <div>
                      <div>
                        <h3 id='ecoinventResultsTitle'></h3>
                      </div>
                      <div id = "ecoinventResults" class="ecoinventResultsdiv">
                        
                      </div>
                    </div>
                  `


    var ecoinventModal = new BootstrapDialog({
      title:formTitle,
      message:function(){
        var $message = $('<div></div>').append(formHtml);

        $message.find('[data-toggle="popover"]').popover({
          //container: '#sandbox_container',
          html: true,
          delay: {
             show: "0",
             hide: "50"
          },
        })

        var $buttonDiv = $message.find('#button_goes_here');
        var $button = $('<button type="button" id="search_button" class="pull-right btn btn-primary">Search</button>')
        $button.on('click', function(){
          var search_term = $('#searchTerm').val()
          var location;
           if ($('#location').val()){
            location = $('#location').val()[0]
           }else{
            location = null;
           }
          console.log(location)
          var markets_only = $('#marketsOnly').is(':checked');
          //var action = 'searchEcoinvent'

          console.log(location)
          console.log(markets_only)


          search_external(search_term, location, markets_only, action);
        })
        $buttonDiv.append($button)
        //lets try this
        $message.find('.ecoinventSearchTrigger').keypress(function(e){
          if(e.keyCode==13){
                     $('#search_button').trigger('click');
                 }
        })


        return $message
      },
      onshown: function(dialogRef){
        console.log('showing the search box now');
        setup_location_box();
      },
      nl2br: false,
      //autodestroy:false,
      buttons:[{
        label:'OK',
        action: function(dialogRef){
          var selected_process = $('#ecoinventSelect :selected').val();
          var selected_process_name = $('#ecoinventSelect :selected').text();
          
          // run the callback function from the calling modal
          callback(selected_process_name, selected_process);
          // close the search modal
          dialogRef.close();
        }
      }],
    });

    //ecoinventModal.realize()

    
    return ecoinventModal.open()
 };

var search_external = function(search_term, location, markets_only, action){
  //generate the data to send
  postData = {
    'action': action,//'searchEcoinvent',
    'search_term': search_term,
    'location': location, 
    'markets_only': markets_only,
  }
  ////console.log(postData)

  //send the data using post
  $.post(
      '/process_post',
      postData,
      function(data, status, xhr){
        if(status == 'success'){
          process_search_results(data);
        }
      },
      'json'
    );
}

var process_search_results = function(data){
  ////console.log(data);

  results = data['result'];

  var result_count = 0
  var html = ""
  for(var key in results){
    if (results.hasOwnProperty(key)) {
      var item = results[key]
      if (data['format'] == 'ecoinvent'){
        html += '<option value = "'+ key +'">'+item['name']+' {' + item['location'] + '} [' + item['unit'] +']</option>\n'
      }
      else if(data['format'] == 'biosphere'){
        if(item['type'] == 'emission'){
          html += '<option value = "'+ key +'">'+item['name']+' (emission to ' + item['categories'] + ') [' + item['unit'] +']</option>\n'
        }else{
          html += '<option value = "'+ key +'">'+item['name']+' (' + item['categories'] + ') [' + item['unit'] +']</option>\n'
        }
      }
      ////console.log(results[key]['name'] + '\t' + results[key]['location']);
      result_count++
    }
  }
  ////console.log(result_count)
  $('#ecoinventResults').html(
   `
    <div class="form-group">
      <select class="form-control" id="ecoinventSelect" size = `+ Math.min(result_count,15) +`>
        
      </select>
    </div>
   `
   )
  $('#ecoinventSelect').append(html)
  // when focused on the select box, change enter key to trigger OK button
  $('#ecoinventSelect').keypress(function(e){
    if(e.keyCode==13){
           $('#confirm_button').trigger('click');
       }
  })
  
  $('#ecoinventResultsTitle').text(result_count + " results")
}

var nodeOver = function(el, instance){
  ////console.log("TODO: write an updated nodeOver function if necessary")
  /*
  var thisNodeID = el.currentTarget.id;

  var thisInputs = instance.getConnections({ target: thisNodeID });
  var thisOutputs = instance.getConnections({ source: thisNodeID });

  for(i=0; i<thisInputs.length; i++){
    var conn = thisInputs[i];
    conn.getOverlay("label").show();
    conn.addClass("inspectConnect");


    var sId = conn.sourceId;
    $('#'+ sId).addClass("inspect");

  }

  for(i=0; i<thisOutputs.length; i++){
    var conn = thisOutputs[i];
    conn.getOverlay("label").show();
    conn.addClass("inspectConnect");

    var sId = conn.targetId;
    $('#'+ sId).addClass("inspect");
  }
  */
}


var nodeOut = function(el, instance){
  ////console.log("TODO: write an updated nodeOut function if necessary")
  /*
  var thisNodeID = el.currentTarget.id;

  var thisInputs = instance.getConnections({ target: thisNodeID });
  var thisOutputs = instance.getConnections({ source: thisNodeID });

  for(i=0; i<thisInputs.length; i++){
    var conn = thisInputs[i];
    conn.getOverlay("label").hide();
    conn.removeClass("inspectConnect");

    var sId = conn.sourceId;
    $('#'+ sId).removeClass("inspect");
  }

  for(i=0; i<thisOutputs.length; i++){
    var conn = thisOutputs[i];
    conn.getOverlay("label").hide();
    conn.removeClass("inspectConnect");

    var sId = conn.targetId;
    $('#'+ sId).removeClass("inspect");
  }
  */
}


var labelShow = function(conn){
  ////console.log("TODO: write an updated labelShow function if necessary")
}

var labelHide = function(conn){
  ////console.log("TODO: write an updated labelHide function if necessary")
}


// This is the function that adds a new proces to the screen and sends a request to add it to the model
var addProcess = function(instance){


    // this is the title of the modal
    var formTitle = 'New Process'
    // this is the html that will go in the body of the modal
    var formHtml = `
                    <form class="form-horizontal">
                      <div class="form-group">
                        <label for="processName" class="control-label col-xs-4"  data-toggle="popover" data-placement= "left" data-trigger="hover" title="Name of the process" data-content="What is the process called. e.g. Mixing, Milling, Cheese production">Name of the process:</label> 
                        <div class="col-xs-8">
                          <input class="form-control" name = "processName" id="processName" autocomplete=off>
                        </div>
                      </div>
                      <div class="form-group">
                        <label for="outputName" class="control-label col-xs-4"  data-toggle="popover" data-placement= "left" data-trigger="hover" title="Name of the output" data-content="What is the output called. e.g. Mixed precursor, Flour, Cheese">Name of the output:</label> 
                        <div class="col-xs-8">
                          <input class="form-control" name = "outputName" id="outputName" autocomplete=off>
                        </div>
                      </div>
                      <div class="form-group">
                        <label for="outputUnit" class="control-label col-xs-4" data-toggle="popover" data-placement= "left" data-trigger="hover" title="Unit" data-content="What is the output measured in. e.g. kilograms, cubic metres, kilowatt hours">Unit:</label> 
                        <div class="col-xs-8">
                          <select name='outputUnit' id='outputUnit' class='selectpicker form-control'>                   
                    `
                    // Note = the select, the final divs and the form get closed below after the select has been populated programatically


    // This populates the unit list from the UNIT_CHOICES variable
    var unitList = [];

    for(i in UNIT_CHOICES){
      formHtml += "<optgroup label = '"+ i +"'>";
      unitList.push(i);
      for(j in UNIT_CHOICES[i]){
        formHtml += "<option value = '"+UNIT_CHOICES[i][j][0]+"'>"+UNIT_CHOICES[i][j][1]+"</option>"
        unitList.push(UNIT_CHOICES[i][j][1])
      };
      formHtml+="</optgroup>";
    };

    // this closes the select and the other open tags
    formHtml += `</select>
                  </div>
                </div>
              </form>`

  //create the modal the new way with BootstrapDialog
  var processModal = new BootstrapDialog({
      title:formTitle,
      message:function(){
        var $message = $('<div></div>').append(formHtml);
        $message.find('#outputUnit').selectpicker();
        $message.find('[data-toggle="popover"]').popover({
          container: '#sandbox_container',
          delay: {
             show: "0",
             hide: "50"
          },
        });

        return $message
      },
      nl2br: false,
      //autodestroy:false,
      buttons:[{
        label:'OK',
        cssClass: 'btn-primary',
        action: function(dialogRef){
            // uuid is the md5 hash of name + type (process) + unit + location (GLO)
            // its created with the hex_md5() function from the md5 script

            process_name = $('#processName').val()
            output_name = $('#outputName').val()
            unit = $('#outputUnit').val()
            to_hash = process_name + 'process' + unit + 'GLO'
            //console.log(to_hash)
            uuid = hex_md5(to_hash)
            //console.log(uuid)
            if(process_name && output_name){
              // send the info to the python side server to create the item in the model
              newProcess(uuid, process_name, output_name, unit)

              // create a new node in the js side version for display on screen, and initiate it
              var thisNode = newNodeExternal(process_name,'transformation',uuid,250,250,instance, outputlabel=output_name);
              initNode(thisNode,instance);
              
              // close the  modal
              dialogRef.close();  
            }else{

              $('.inputMessage').remove();
              if(!process_name){
                $('#processName').after('<div class="red inputMessage">Please give the process a name</div>');
              }
              if(!output_name){
                $('#outputName').after('<div class="red inputMessage">Please give the process an output</div>');
              }
            }
            
        }
      },
      {
        label:'Cancel',
        action: function(dialogRef){
          dialogRef.close();
        }
      }],
    });

    //ecoinventModal.realize()

    
    return processModal.open()



 };

// This is the helper function that creates a bootstrap pop up modal
// title is the title, body is whatever goes in the box - this can (and should) be html
var createModal = function(title, body){

    var modal_id = jsPlumbUtil.uuid()

      var myModal = $('<div>').attr('id','myModal').addClass("modal fade").attr("tabindex","-1").attr("role","dialog").attr("aria-labelledby", "myModal").attr("aria-hidden","true").html(`
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                <h4 class="modal-title" id="myModalLabel">` + title + `</h4>
                </div>
                <div class="modal-body">
                    ` + body + `
                </div>
                <div class="modal-footer">
                    <button type="button" id="cancel_button" class="btn btn-default" data-dismiss="modal">Cancel</button>
                    <button type="button" id="confirm_button" class="btn btn-primary">OK</button>
            </div>
        </div>
      </div>
    `);
    // when the modal gets hidden it gets removed from the DOM
    myModal.on('hidden.bs.modal', function () {
     $('#myModal').remove();
   });

    return myModal;
};


function start_analysis(id, name){

  $.getJSON( "/status.json", function(data) {
      can_analyse = data.model_is_runnable;
      console.log(can_analyse)
      if(can_analyse){
        console.log('starting analysis for ' + name)
        console.log(id)
        window.location.replace("/analyse?item=" + name + "&item_code=" + id);
      }else{

        items = {
          'model_has_impacts': '<div class="row"><div class="col-xs-12 bg-info"><h4>The model needs at least one link to a technosphere or biosphere exchange, otherwise the total impact of the system will be zero</h4> <p>Go to a process and click on the  <i class="material-icons md-18">business</i> icon to add a technoshere exchange or the <i class="material-icons md-18">local_florist</i>icon to add a biosphere exchange</p></div></div><div class="row"><div class="col-xs-12"><br></div></div>',
          'model_has_parameters': "<div class='row'><div class=' col-xs-12 bg-success'><h4>At least one of the links in the model needs to be specified with a number (that isn't zero!)</h4><p> Go to the <a href='/parameters'>Parameter Sets</a> tab and add some numbers/functions.</p></div></div>"
        }
        
        formTitle = "Can't run analysis yet..."
        popupHtml = "<div>"

        for (item in items) {
          if(!data[item]){
            popupHtml += items[item];
          }
        }

        popupHtml += '</div>'

        var inputModal = BootstrapDialog.show({
          title:formTitle,
          message: popupHtml,
          type: 'type-danger',
          buttons: [{
                label: 'OK',
                action: function(dialogItself){
                    dialogItself.close();
                }
            }]
        });


      
      }
  });
}