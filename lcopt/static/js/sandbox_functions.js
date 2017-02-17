var sayHello = function(){
  console.log("Hello from the functions file")
}

// unit choices 
var UNIT_CHOICES = {
    'Mass': [
        ['kg', 'kg'],
        ['t', 'tonne'],
    ]
    ,
    'Energy': [
        ['kWh', 'kWh'],
    ]
    ,
    'Volume': [
        ['m3', 'm3'],
    ]
    ,
    'Radioactivity': [
        ['Bq', 'Bq'],
    ]
    ,
    'Time': [
        ['h', 'hours'],
        ['d', 'days'],
    ]
    ,
    'Amount': [
        ['p', 'Item'],
    ]
    ,
}

// This function creates a new node from external data
var newNodeExternal = function(name, type, id, x, y, instance){
  
  var id = id//name.split(' ').join('_')//jsPlumbUtil.uuid();
  var d = $('<div>').attr('id', id).addClass('w ' + type);
  var title =  $('<div>').addClass('title').text(name);
  var buttons = $('<div>').addClass('buttons');
  var connect =  $('<div>').addClass('ep').html('<i class="ep2 material-icons w3-medium" data-toggle="popover" data-placement= "left" data-trigger="hover" title="Connect" data-content="Drag to connect to another process">trending_flat</i>');
  var input =  $('<div>').addClass('ip').html('<i class="material-icons w3-medium" data-toggle="popover" data-placement= "bottom" data-trigger="hover" title="Input" data-content="Add an input to this process">file_download</i>');
  var output =  $('<div>').addClass('op').html('<i class="material-icons w3-medium" data-toggle="popover" data-placement= "bottom" data-trigger="hover" title="Output" data-content="Add an output to this process">file_upload</i>');
  var del =  $('<div>').addClass('x').html('<i class="material-icons w3-medium" data-toggle="popover" data-placement= "right" data-trigger="hover" title="Remove" data-content="Remove this item">cancel</i>');
  var edit = $('<div>').addClass('ed').html('<i class="material-icons w3-medium" data-toggle="popover" data-placement= "bottom" data-trigger="hover" title="Edit" data-content="Edit quantity">edit</i>');


  if(type == 'transformation'){
    buttons.append(connect).append(input).append(output);
  }else{
    buttons.append(edit);
  };
  buttons.append(del);
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
  //console.log(instance);
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

            // initialise draggable elements.
            instance.draggable(el, {
              grid: [5,5],
              containment:true,
              stop: function(event) {

              var getID = el.id;
              if(typeof getID == 'undefined'){getID = el[0].id;};

              console.log('getID');
              console.log(getID);

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
              //console.log('#' + $(this).parent().parent().attr('id'));
              var target = $( e.target )
              var thisNodeID = target.parent().parent().parent().attr('id');
              var thisNode = $('#' + thisNodeID);

              var thisConnectionsTo = instance.getConnections({ target: thisNodeID });
              var thisConnectionsFrom = instance.getConnections({ source: thisNodeID });

              var choppingBlock = [];

              for(var i in thisConnectionsTo){
                var conn = thisConnectionsTo[i];
                var data = conn.getData();
                var thisType = data.connection_type;
                var intNode = thisNode.hasClass('transformation');
                var intermediate = thisType == "intermediate";
                if(intermediate == false && intNode == true){
                  choppingBlock.push($("#" + conn.sourceId + " .title").text());
                }
              };

              for(var i in thisConnectionsFrom){
                var conn = thisConnectionsFrom[i];
                var data = conn.getData();
                var thisType = data.connection_type;
                var intNode = thisNode.hasClass('transformation');
                var intermediate = thisType == "intermediate";
                if(intermediate == false && intNode == true){
                  choppingBlock.push($("#" + conn.targetId + " .title").text());
                }
              };

              //console.log(choppingBlock);

              var this_item = $('#' + thisNodeID + " .title").text()

              var del_title = "Delete " + this_item + "?";

              if(choppingBlock.length == 0){
                var del_body = "<p>Are you sure you want to delete " + this_item + "?</p>"
              }else{
                var del_body = `<p>Are you sure you want to delete ` + this_item + `?</p>
                <p>The following inputs/outputs will also be deleted:</p>
                <ul>`
                for(i in choppingBlock){
                del_body += "<li>" + choppingBlock[i] + "</li>";
              }
              del_body += "</ul>"
              };

              var testmodal = createModal(del_title, del_body);
              console.log(testmodal);
              $(document.body).append(testmodal);
              $('#myModal').modal('show');


              $('#confirm_button').unbind().click(function(e){
                console.log('confirm_button');
                $('#myModal').modal('hide');

                for(var i in thisConnectionsTo){
                  var conn = thisConnectionsTo[i];
                  var data = conn.getData();
                  var thisType = data.connection_type;
                  var intNode = thisNode.hasClass('transformation');
                  var intermediate = thisType == "intermediate";
                  if(intermediate == false && intNode == true){
                    console.log(conn.sourceId);
                    $("#" + conn.sourceId).remove();

                    deleteDatabaseItem(conn.sourceId,csrftoken,thisType,system_id)

                  }else{
                    $("#" + conn.sourceId).removeClass('inspect');
                  }
                  instance.detach(conn);
                };

                for(var i in thisConnectionsFrom){
                  var conn = thisConnectionsFrom[i];
                  var data = conn.getData();
                  var thisType = data.connection_type;
                  var intNode = thisNode.hasClass('transformation');
                  var intermediate = thisType == "intermediate";
                  if(intermediate == false  && intNode == true){
                    $("#" + conn.targetId).remove();

                    deleteDatabaseItem(conn.targetId,csrftoken,thisType,system_id)

                  }else{
                    $("#" + conn.targetId).removeClass('inspect');
                  }
                  instance.detach(conn);
                };



                if(thisNode.hasClass('input')){
                  thisNodeType = 'input';
                }else if (thisNode.hasClass('output')) {
                  thisNodeType = 'output';
                }else if (thisNode.hasClass('transformation')) {
                  thisNodeType = 'transformation';
                }

                deleteDatabaseItem(thisNodeID,csrftoken,thisNodeType,system_id);

                thisNode.remove();

                $('.popover').remove();



              });
              $('#myModal').on('hidden.bs.modal', function () {
                $('#myModal').remove()
              })

              e.stopPropagation();
            });
            
            //This is the add input function
            //TODO: Fix this for Flask implentation
            $('.ip').unbind().click(function(e){

              var target = $( e.target )

              var thisNodeID = target.parent().parent().parent().attr('id');
              console.log(thisNodeID);
              var thisConnections = instance.getConnections({ target: thisNodeID });

              thisConnectionList = [];

              for(i=0; i<thisConnections.length; i++){
                var sId = thisConnections[i].sourceId;
                thisConnectionList.push($('#'+ sId + " .title").text());
              }

              console.log(thisConnectionList);

              var x = target.offset().left - canvas.offset().left - 150;
              var y = target.offset().top - canvas.offset().top - 150;

              var chooseInput = $('<div>').addClass('enter')
              var inputTitle = $('<div>').addClass('popTitle').text('Select an input');
              var inputName = $('<select>').attr('name','inputsubstance').attr('id','inputsubstance').attr('data-live-search','true').attr('data-done-button','true').attr('data-live-search-placeholder','Search (or type to create new)').attr('data-width','100%').addClass('selectpicker');
              var inputAmountTitle = $('<div>').addClass('popTitle').text('How much is needed');
              var inputAmount = $('<input>').attr('name','inputamount').attr('id','inputamount');

              //input validation
              inputAmount.keyup(function() {
               var $th = $(this);
               $th.val( $th.val().replace(/[^0-9\.]/g, function(str) {  return ''; } ) );
              });
              //end

              var inputUnit = $('<div>').addClass('popUnit').text('');
              var okButton = $('<button>').text('OK');

              inputName.append($('<option>').attr('value','default').attr('disabled','disabled').attr('selected','selected').text('-------'));

              for(var key in allInputs){
                if($.inArray(allInputs[key][0],thisConnectionList) == -1){
                  inputName.append($('<option>').attr('value',key).text(allInputs[key][0]));
                }
              }


              chooseInput.css('left', x + "px");
              chooseInput.css('top', y + "px");

              var closeThis = $('<button>').text('Cancel');

              chooseInput.append(inputTitle).append(inputName).append(inputAmountTitle).append(inputAmount).append(inputUnit).append(okButton).append(closeThis);

              canvas.append(chooseInput);

              inputName.selectpicker();

              inputName.on('shown.bs.select',function(){
                var searchBox = $('.bs-searchbox input')
                  searchBox.keyup(function(){
                  //console.log('key pressed');
                  //input validation
                  var $th = $(this);
                  $th.val( $th.val().replace(/[^A-Za-z0-9\(\)\\\[\]/ ]/g, function(str) {  return ''; } ) );
                  //end
                  var noResults = $('.no-results');
                    noResults.html("'" + searchBox.val() + "' not found<button class='create_button btn btn-xs btn-primary pull-right'> Create </button>")
                    $('.create_button').click(function(){
                      createItem('input', searchBox.val(), csrftoken);
                  });
                });

              });

              closeThis.click(function(){
                chooseInput.remove();
              });

              inputName.change(function(){
                var inputId = $(this).val();
                var unit = allInputs[inputId][1];
                inputUnit.text(unit);
              });

              okButton.click(function(){
                var id = jsPlumbUtil.uuid();
                var inputId = inputName.val();
                var name = inputName.children("option").filter(":selected").text();
                var amount = inputAmount.val();
                var type = 'input';
                var unit = inputUnit.text()//allInputs[inputId][1];

                var thisNewNode = newNodeExternal(name, type, id, x+300, y, instance);
                initNode(thisNewNode);

                //console.log(id);
                //console.log(thisNodeID);

                var thisConnection = instance.connect({
                  source: id,
                  target: thisNodeID,
                  type:"basic input",
                  data:{'connection_type':'input', 'connection_amount':amount}
                })
                //thisConnection.addType("new");

                var postData = {
                    'uuid': id,
                    'y': y,
                    'x': x+300,
                    'csrfmiddlewaretoken': csrftoken,
                    'transform_id' : thisNodeID,
                    'input_id' : inputId,
                    'amount': amount,
                    'system_id': system_id,
                    'note': 'Note Placeholder',
                 }

                 console.log(postData);

                $.post('/sandbox/newInput/', postData);

                 //console.log('tried to post new input');

                thisConnection.getOverlay("label").setLabel(amount + " " + unit);

                chooseInput.remove();
              });
            });

            //This is the add output function
            //TODO: Fix this for Flask implentation
            $('.op').unbind().click(function(e){



              var target = $( e.target )

              var thisNodeID = target.parent().parent().parent().attr('id');
              //console.log(thisNodeID);
              var thisConnections = instance.getConnections({ source: thisNodeID });

              thisConnectionList = [];

              for(i=0; i<thisConnections.length; i++){
                var sId = thisConnections[i].sourceId;
                thisConnectionList.push($('#'+ sId + " .title").text());
              }

              var x = target.offset().left - canvas.offset().left - 150;
              var y = target.offset().top - canvas.offset().top - 150;

              var chooseOutput = $('<div>').addClass('enter')
              var outputTitle = $('<div>').addClass('popTitle').text('Select an emission/output');
              var outputName = $('<select>').attr('name','outputsubstance').attr('id','outputsubstance').attr('data-live-search','true').attr('data-done-button','true').attr('data-live-search-placeholder','Search (or type to create new)').attr('data-width','100%').addClass('selectpicker');
              var outputAmountTitle = $('<div>').addClass('popTitle').text('How much is needed');
              var outputAmount = $('<input>').attr('name','outputamount').attr('id','outputamount');

              //input validation
              outputAmount.keyup(function() {
               var $th = $(this);
               $th.val( $th.val().replace(/[^0-9\.]/g, function(str) {  return ''; } ) );
              });
              //end

              var outputUnit = $('<div>').addClass('popUnit').text('');
              var okButton = $('<button>').text('OK');

              outputName.append($('<option>').attr('value','default').attr('disabled','disabled').attr('selected','selected').text('-------'));

              for(var key in allOutputs){
                if($.inArray(allOutputs[key][0],thisConnectionList) == -1){
                  outputName.append($('<option>').attr('value',key).text(allOutputs[key][0]));
                }
              }


              chooseOutput.css('left', x + "px");
              chooseOutput.css('top', y + "px");

              var closeThis = $('<button>').text('Cancel');

              chooseOutput.append(outputTitle).append(outputName).append(outputAmountTitle).append(outputAmount).append(outputUnit).append(okButton).append(closeThis);
              console.log('triggered appending');
              canvas.append(chooseOutput);
              console.log('triggered appended');
              outputName.selectpicker();

              outputName.on('shown.bs.select',function(){
                var searchBox = $('.bs-searchbox input')
                  searchBox.keyup(function(){
                  //console.log('key pressed');
                  //input validation
                  var $th = $(this);
                  $th.val( $th.val().replace(/[^A-Za-z0-9\(\)\\\[\]/ ]/g, function(str) {  return ''; } ) );
                  //end
                  var noResults = $('.no-results');
                    noResults.html("'" + searchBox.val() + "' not found<button class='create_button btn btn-xs btn-primary pull-right'> Create </button>")
                    $('.create_button').click(function(){
                      createItem('output', searchBox.val(), csrftoken);
                  });
                });

              });

              closeThis.click(function(){
                chooseOutput.remove();
              });

              outputName.change(function(){
                var outputId = $(this).val();
                var unit = allOutputs[outputId][1];
                outputUnit.text(unit);
              });

              okButton.click(function(){
                var id = jsPlumbUtil.uuid();
                var outputId = outputName.val();
                var name = outputName.children("option").filter(":selected").text();
                var amount = outputAmount.val();
                var type = 'output';
                var unit = outputUnit.text();//allOutputs[outputId][1];

                var thisNewNode = newNodeExternal(name, type, id, x+300, y, instance);
                initNode(thisNewNode);

                //console.log(id);
                //console.log(thisNodeID);

                var thisConnection = instance.connect({
                  source: thisNodeID,
                  target: id,
                  type:"basic output",
                  data:{'connection_type':'output', 'connection_amount':amount}
                })
                //thisConnection.addType("new");

                var postData = {
                    'uuid': id,
                    'y': y,
                    'x': x+300,
                    'csrfmiddlewaretoken': csrftoken,
                    'transform_id' : thisNodeID,
                    'output_id' : outputId,
                    'amount': amount,
                    'system_id': system_id,
                    'note': 'Note Placeholder',
                 }

                 console.log(postData);

                $.post('/sandbox/newOutput/', postData);

                 //console.log('tried to post new output');

                thisConnection.getOverlay("label").setLabel(amount + " " + unit);

                chooseOutput.remove();
              });
            });

            //This is the edit function for inputs and outputs
            //TODO: Fix this for Flask implentation
            $('.ed').unbind().click(function(e){

              var target = $( e.target )

              var thisNodeID = target.parent().parent().parent().attr('id');
              var type = 'input';
              var thisConnections = instance.getConnections({ source: thisNodeID });

              if(thisConnections.length === 0){
                thisConnections = instance.getConnections({ target: thisNodeID });
                type = 'output';
              }

              var connectionData = thisConnections[0].getData();


              var itemName = $('#' + thisNodeID + ' .title').text();
              var initialValue=connectionData.connection_amount;

              console.log(thisNodeID);

              var formHtml = '<label for="newQuantity">Name:</label> <input name = "newQuantity", id="newQuantity" value = "'+initialValue+'">'

              var createdModal = createModal('Edit quantity of  ' + itemName, formHtml);

              $(document.body).append(createdModal);

              $('#myModal').modal('show');

              var itemIDNo = null
               $('#confirm_button').unbind().click(function(e){
                console.log('OK, editing quantity of ' + itemName +'(id = '+thisNodeID+')')

                var postData = {

                  'csrfmiddlewaretoken':csrftoken,
                  'id': thisNodeID,
                  'type': type,
                  'newAmount' : $('#newQuantity').val()
                }
                console.log(postData);
                $.post("/sandbox/editFlow/", postData);
                $('#myModal').modal('hide');

                //redo the connection



                console.log(thisConnections[0].sourceId);
                console.log(thisConnections[0].targetId);
                currentLabel = thisConnections[0].getOverlay("label").getLabel();
                unit = currentLabel.split(" ")[1];

                jsPlumb.detach(thisConnections[0]);


                var connection = instance.connect({
                   source: thisConnections[0].sourceId,
                   target: thisConnections[0].targetId,
                   type:"basic intermediate",
                   data:{'connection_type':type, 'connection_amount':$('#newQuantity').val()}
                 });
                 console.log(connection.getData());

                 console.log(currentLabel);
                 console.log(unit);
                 connection.getOverlay("label").setLabel($('#newQuantity').val() + " " + unit);

                 //connection.addType("new");


              });


              $('#myModal').on('hidden.bs.modal', function () {
               $('#myModal').remove();
              });
              $('#myModal').on('shown.bs.modal', function () {
               $('#newQuantity').focus()
             });
            });

            //This is the function that edits the title of the node
            //TODO: Fix this for Flask implentation
            $('.transformation>.title').unbind().click(function(e){
              var titleDiv = $(this);
              thisNodeID = titleDiv.parent().attr('id');
              console.log(titleDiv);
              var originalTitle = $(this).text();
              $(this).text('');
              console.log($(this).parent().parent().width());
              var titleInput = $('<input>').attr('id','tempTitleInput').attr('type', 'text').addClass('titleInput').val(originalTitle);
              $(this).append(titleInput);
              titleInput.focus().select();;

              titleInput.blur(function(e){
                $(this).parent().text(originalTitle);
              });

              titleInput.keyup(function(e) {
                if (e.keyCode === 13) {
                  if (this.value == ""){
                    $(this).parent().text(originalTitle);
                  }else{
                    $(this).parent().text(this.value);
                    console.log(thisNodeID)
                    var postData = {
                      'id':thisNodeID,
                      'newName':this.value,
                      'csrfmiddlewaretoken': csrftoken,
                    };
                    console.log(postData);
                    $.post("/sandbox/renameProcess/", postData)
                }
                }
                if (e.keyCode === 27) {
                  $(this).parent().text(originalTitle);
                }
              });
            })
};
      

// Saves the position of a node after dragging
// TODO : Implement for Flask      
var saveState = function(state) {
  console.log(state.selector)
  postData ={
      'action' : 'savePosition',
      'uuid': $(state).attr('id'),
      'y': $(state).position().top,
      'x': $(state).position().left,
      //'csrfmiddlewaretoken': csrftoken,
   };
   console.log(postData);

  $.post('/process_post', postData);
}

var saveModel = function(){
  console.log('saving model')
  postData = {
    'action' : 'saveModel'
  }
  $.post('/process_post', postData);
}

// This function sends the information required to the python side to create a new process in the loaded model instance
var newProcess = function(uuid, process_name, output_name, unit){
  console.log('saving model')
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
  //console.log('Dealing with a connection event (' + sID +')')

      source = $('#' + info.sourceId)
      target = $('#' + info.targetId)
          

      postData = {
          'action': 'newConnection',
          'sourceId' : info.sourceId,
          'targetId' : info.targetId,
          'label': info.connection.getOverlay('label').getLabel(),
        }

        console.log(postData);
        $.post('/process_post', postData);
}



//test receiving data back from the server

/*var echo = function(){

  postData = {
    'action': 'echo'
  }

  $.ajaxSetup({async:false});  //execute synchronously

    var returnedData = null
    $.post('/process_post', postData, function(data){
       returnedData = data
    }, "json");

    console.log(returnedData)

  $.ajaxSetup({async:true});  //return to default setting
}
*/

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
  console.log("dealing with result from echo");
  console.log('The server says\n' + returnedData['message']); 
}

var search_ecoinvent_dialog = function(instance){


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
                        <div class="col-xs-3">
                          <button type="button" id="search_button" type="submit" class="pull-right btn btn-primary">Search</button>
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

    // create the modal
    var createdModal = createModal(formTitle, formHtml);

    //append the modal to the page
    $(document.body).append(createdModal);

    // bind the enter key to the search button
    $('.ecoinventSearchTrigger').keypress(function(e){
      if(e.keyCode==13){
                 $('#search_button').trigger('click');
             }
    })
   
    // show the modal
    $('#myModal').modal('show');

    // this is the action of the search button
    $('#search_button').unbind().click(function(e){
      
      var search_term = $('#searchTerm').val();
      var location = $('#location').val();
      var markets_only = $('#marketsOnly').is(':checked');
      
      if(search_term != ''){
        search_ecoinvent(search_term, location, markets_only);  
      }

    });

    // this is the action that gets bound to the confirm button on the modal
    $('#confirm_button').unbind().click(function(e){

      var selected_process = $('#ecoinventSelect :selected').val()
      console.log(selected_process)
      // which finishes with closing it
      $('#myModal').modal('hide');

    })

   // sets the focus to the form item when the modal opens
   $('#myModal').on('shown.bs.modal', function () {
    $('#searchTerm').focus()
  });
 };

var search_ecoinvent = function(search_term, location, markets_only){
  //generate the data to send
  postData = {
    'action':'searchEcoinvent',
    'search_term': search_term,
    'location': location, 
    'markets_only': markets_only,
  }
  //console.log(postData)

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
  //console.log(data);

  results = data['result'];

  var result_count = 0
  var html = ""
  for(var key in results){
    if (results.hasOwnProperty(key)) {
      var item = results[key]
      html += '<option value = "'+ key +'">'+item['name']+' {' + item['location'] + '}</option>\n'
      //console.log(results[key]['name'] + '\t' + results[key]['location']);
      result_count++
    }
  }
  //console.log(result_count)
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
  //console.log("TODO: write an updated nodeOver function if necessary")
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
  //console.log("TODO: write an updated nodeOut function if necessary")
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
  //console.log("TODO: write an updated labelShow function if necessary")
}

var labelHide = function(conn){
  //console.log("TODO: write an updated labelHide function if necessary")
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
      console.log("clicked ok on the modal")

      //TODO: check for blank items

      // uuid is the md5 hash of name + type (process) + unit + location (GLO)
      // its created with the hex_md5() function from the md5 script

      process_name = $('#processName').val()
      output_name = $('#outputName').val()
      unit = $('#outputUnit').val()
      to_hash = process_name + 'process' + unit + 'GLO'
      console.log(to_hash)
      uuid = hex_md5(to_hash)
      console.log(uuid)

      // send the info to the python side server to create the item in the model
      newProcess(uuid, process_name, output_name, unit)

      // create a new node in the js side version for display on screen, and initiate it
      var thisNode = newNodeExternal(process_name,'transformation',uuid,250,250,instance);
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
      var myModal = $('<div>').attr('id','myModal').addClass("modal fade").attr("tabindex","-1").attr("role","dialog").attr("aria-labelledby","myModal").attr("aria-hidden","true").html(`
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
