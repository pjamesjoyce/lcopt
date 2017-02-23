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
  var connect =  $('<div>').addClass('ep').html('<i class="ep2 material-icons w3-medium" data-toggle="popover" data-placement= "left" data-trigger="hover" title="Connect" data-content="Drag to connect to another process">trending_flat</i>');
  var input =  $('<div>').addClass('ip').html('<i class="material-icons w3-medium" data-toggle="popover" data-placement= "bottom" data-trigger="hover" title="Input" data-content="Add an input to this process">file_download</i>');
  //var output =  $('<div>').addClass('op').html('<i class="material-icons w3-medium" data-toggle="popover" data-placement= "bottom" data-trigger="hover" title="Output" data-content="Add an output to this process">file_upload</i>');
  //var del =  $('<div>').addClass('x').html('<i class="material-icons w3-medium" data-toggle="popover" data-placement= "right" data-trigger="hover" title="Remove" data-content="Remove this item">cancel</i>');
  //var edit = $('<div>').addClass('ed').html('<i class="material-icons w3-medium" data-toggle="popover" data-placement= "bottom" data-trigger="hover" title="Edit" data-content="Edit quantity">edit</i>');


  if(type == 'transformation'){
    buttons.append(connect).append(input)//.append(output);
  }else{
    //buttons.append(edit);
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
            $('.x').unbind().click(function(e){
              ////console.log('#' + $(this).parent().parent().attr('id'));

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
              
            }); 
            

            //This is the edit function for inputs and outputs
            //TODO: Fix this for Flask implentation
            $('.ed').unbind().click(function(e){

                //console.log('TODO: Fix this for Flask implentation')
              
            }); 
            
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
                        <label for="inputName" class="control-label col-xs-3">Name of input</label> 
                        <div class="col-xs-9">
                          <input class="form-control typeahead" name = "inputName", id="inputName">
                        </div>
                      </div>
                      <div class="form-group">
                        <label for="extLink" class="control-label col-xs-3">Link to external database</label> 
                        <div class="col-xs-9">
                          <input class="form-control disabled" name = "extLinkName", id="extLinkName" disabled>
                          <input class="form-control disabled" name = "extLink", id="extLink" disabled>
                        </div>
                      </div>
                      <div class="form-group">
                        <label for="unit" class = "control-label col-xs-3">Unit</label>
                        <div class="col-xs-6" id="unitDiv"></div>
                      </div>
                      <div class="form-group">
                        <label for="unlinked" class="control-label col-xs-3">Is burden free</label> 
                        <div class="col-xs-6">
                          <input type="checkbox" class="checkbox-inline" name = "unlinked", id="unlinked">
                        </div>
                        <div id="ext_data_button" class="col-xs-3">
                          
                        </div>
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


        var $button = $('<button type="button" id="ext_search_button" type="submit" class="pull-right btn btn-primary">Search external databases</button>')

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
          search_ecoinvent_dialog(logResult)

        })
        $message.find('#ext_data_button').append($button)
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
            var code = hex_md5(name+type+unit+location)
            var suffix = $('[id^=' + code + ']').size()
            var node_id = code + '__' + suffix
            //console.log('creating node with id ' + node_id)

            var postData = {
              'action': 'addInput',
              'targetId': thisNodeID,
              'name': name,
              'type': type,
              'unit': unit,
              'location': location,
              'code':code,
              'ext_link_name' : inputModal.getData('ext_link_name'),
              'ext_link': inputModal.getData('code'),

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
        }
      },]
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

var search_ecoinvent_dialog = function(callback){

  
    // this is the title of the modal
    var formTitle = 'Search the ecoinvent database'
    // this is the html that will go in the body of the modal
    var formHtml = `
                    <form class="form-horizontal">
                      <div class="form-group">
                        <label for="searchTerm" class="control-label col-xs-3">Search for:</label> 
                        <div class="col-xs-9">
                          <input class="form-control ecoinventSearchTrigger" name = "searchTerm", id="searchTerm">
                        </div>
                      </div>
                      <div class="form-group">
                        <label for="location" class="control-label col-xs-3">Location</label> 
                        <div class="col-xs-9">
                          <input class="form-control ecoinventSearchTrigger" name = "location", id="location">
                        </div>
                      </div>
                      <div class="form-group">
                        <label for="marketsOnly" class="control-label col-xs-3">Markets only:</label> 
                        <div class="col-xs-6">
                          <input type="checkbox" class="checkbox-inline ecoinventSearchTrigger" name = "marketsOnly", id="marketsOnly" checked="checked">
                        </div>
                        <div id = "button_goes_here" class="col-xs-3">
                          
                        </div>
                      </div>
                    </form>
                    
                    
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
        var $buttonDiv = $message.find('#button_goes_here');
        var $button = $('<button type="button" id="search_button" type="submit" class="pull-right btn btn-primary">Search</button>')
        $button.on('click', function(){
          var search_term = $('#searchTerm').val()
          var location = $('#location').val()
          var markets_only = $('#marketsOnly').is(':checked');
          search_ecoinvent(search_term, location, markets_only);
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

var search_ecoinvent = function(search_term, location, markets_only){
  //generate the data to send
  postData = {
    'action':'searchEcoinvent',
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
          process_ecoinvent_search_results(data);
        }
      },
      'json'
    );
}

var process_ecoinvent_search_results = function(data){
  ////console.log(data);

  results = data['result'];

  var result_count = 0
  var html = ""
  for(var key in results){
    if (results.hasOwnProperty(key)) {
      var item = results[key]
      html += '<option value = "'+ key +'">'+item['name']+' {' + item['location'] + '} [' + item['unit'] +']</option>\n'
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
                        <label for="processName" class="control-label col-xs-4">Process Name:</label> 
                        <div class="col-xs-8">
                          <input class="form-control" name = "processName", id="processName">
                        </div>
                      </div>
                      <div class="form-group">
                        <label for="outputName" class="control-label col-xs-4">Name of the output:</label> 
                        <div class="col-xs-8">
                          <input class="form-control" name = "outputName", id="outputName">
                        </div>
                      </div>
                      <div class="form-group">
                        <label for="outputUnit" class="control-label col-xs-4">Unit:</label> 
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

    // create the modal
    var createdModal = createModal(formTitle, formHtml);

    //append the modal to the page
    $(document.body).append(createdModal);
    // activate the unit selectpicker
    $('#outputUnit').selectpicker();

    //input validation
    $('#processName').keyup(function() {
     var $th = $(this);
     $th.val( $th.val().replace(/[^A-Za-z0-9\(\)\\\[\]/ ]/g, function(str) {  return ''; } ) );
    });
    //end

    // show the modal
    $('#myModal').modal('show');

    // this is the action that gets bound to the confirm button on the modal
    $('#confirm_button').unbind().click(function(e){
      //console.log("clicked ok on the modal")

      //TODO: check for blank items

      // uuid is the md5 hash of name + type (process) + unit + location (GLO)
      // its created with the hex_md5() function from the md5 script

      process_name = $('#processName').val()
      output_name = $('#outputName').val()
      unit = $('#outputUnit').val()
      to_hash = process_name + 'process' + unit + 'GLO'
      //console.log(to_hash)
      uuid = hex_md5(to_hash)
      //console.log(uuid)

      // send the info to the python side server to create the item in the model
      newProcess(uuid, process_name, output_name, unit)

      // create a new node in the js side version for display on screen, and initiate it
      var thisNode = newNodeExternal(process_name,'transformation',uuid,250,250,instance, outputlabel=output_name);
      initNode(thisNode,instance);
      
      // end with hiding the modal
      $('#myModal').modal('hide');
    });

   // sets the focus to the form item when the modal opens
   $('#myModal').on('shown.bs.modal', function () {
    $('#processName').focus()
  });
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
     $('#modal_id').remove();
   });

    return myModal;
};
