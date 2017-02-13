var jsPlumbsetup = function (nodes, links,linklabels, csrftoken,allInputs,allOutputs, allIntermediates,system_id,editable) {

    //console.log(allIntermediates);

    $.fn.bootstrapBtn = $.fn.button.noConflict();

    // setup some defaults for jsPlumb.
    var instance = jsPlumb.getInstance({
        Endpoint: ["Dot", {radius: 1}],
        Connector:[ "Flowchart", { stub: [0, 0], midpoint: 0.25 } ],//"Straight",
        Container: "body"
    });

    for(i=0;i<nodes.length;i++){
        newNodeExternal(nodes[i][0],nodes[i][1],nodes[i][2],nodes[i][3],nodes[i][4], instance);
    };

    instance.registerConnectionType("basic", {
      anchor:"Continuous",
      paintStyle: { strokeStyle: "#777", lineWidth: 1, outlineColor: "transparent", outlineWidth: 14 },
      detachable : false,
      hoverPaintStyle: {strokeStyle: "#1e8151", lineWidth: 1 },
      overlays: [
          [ "Arrow", {
              location: 1,
              id: "arrow",
              length: 7.5,
              width:7.5,
              foldback: 0.8
          } ],
          [ "Label", { label: "Establish connection", id: "label", cssClass: "aLabel" }],
          //["Custom", { label: "Hello", id:"type" }]
      ],
      //Connector:"Straight ",

    });

    instance.registerConnectionType("input", {
      paintStyle: { strokeStyle: "#2e6f9a", lineWidth: 1, outlineColor: "transparent", outlineWidth: 14 },
      //hoverPaintStyle: {strokeStyle: "blue", lineWidth: 1 },
    });
    instance.registerConnectionType("output", {
      paintStyle: { strokeStyle: "#484c51", lineWidth: 1, outlineColor: "transparent", outlineWidth: 14 },
      //hoverPaintStyle: {strokeStyle: "blue", lineWidth: 1 },
    });
    instance.registerConnectionType("intermediate", {
      paintStyle: { strokeStyle: "#aaa", lineWidth: 1, outlineColor: "transparent", outlineWidth: 14 },
      //hoverPaintStyle: {strokeStyle: "blue", lineWidth: 1 },
    });



    window.jsp = instance;

    var canvas = $("#main_canvas");
    var windows = jsPlumb.getSelector(".demo_container .w");

    //console.log(windows);

    // bind a click listener to each connection; the connection is deleted. you could of course
    // just do this: jsPlumb.bind("click", jsPlumb.detach), but I wanted to make it clear what was
    // happening.
    instance.bind("click", function (c) {

        connectionData = c.getData()
        console.log(connectionData);
        if (connectionData.connection_type == 'intermediate'){

          var dialogConfirm = $('<div>').attr('id','dialog-confirm').attr('title','Remove this link?').html('<p> Do you want to remove this link?</p>')

          //$.fn.bootstrapBtn = $.fn.button.noConflict();


            dialogConfirm.dialog({
              resizable: false,
              height:140,
              modal: true,
              buttons: {
                "Remove link": function() {
                  $( this ).dialog( "close" );
                  console.log ('remove connection for ' + c);

                  var postData={
                    'csrfmiddlewaretoken':csrftoken,
                    'source': c.sourceId,
                    'target': c.targetId,
                    'system_id':system_id
                  };

                  $.post('/sandbox/removeLink/', postData);

                  console.log(postData);

                  jsPlumb.detach(c);
                  dialogConfirm.remove();
                },
                Cancel: function() {
                  $( this ).dialog( "close" );
                  console.log('not happening')
                  dialogConfirm.remove();
                }
              }
            });

        };

    });

    // bind a connection listener. note that the parameter passed to this function contains more than
    // just the new connection - see the documentation for a full list of what is included in 'info'.
    // this listener sets the connection's internal
    // id as the label overlay's text.
    instance.bind("connection", function (info) {
        var sID = info.sourceId + "_" + info.targetId;
        //console.log(sID);

        source = $('#' + info.sourceId)
        target = $('#' + info.targetId)



        var labelText = linklabels[sID];

        //console.log(linklabels);
        console.log(labelText);
        if(typeof labelText == 'undefined'){
          console.log('doesnt have a label already');
          if(source.hasClass('transformation') && target.hasClass('transformation')){
            console.log('is a transformation to transformation link');
          var target = $('#' + info.targetId);
          var x = target.offset().left - canvas.offset().left - 150;
          var y = target.offset().top - canvas.offset().top - 150;

          var defineConnect = $('<div>').addClass('enter')
          var connectTitle = $('<div>').addClass('popTitle').text('Choose/create an intermediate');
          var connectName = $('<select>').attr('name','connectName').attr('id','connectName').attr('data-live-search','true').attr('data-done-button','true').attr('data-live-search-placeholder','Search (or type to create new)').attr('data-width','100%').addClass('selectpicker');
          var connectAmountTitle = $('<div>').addClass('popTitle').text('How much is needed');
          var connectAmount = $('<input>').attr('name','connectAmount').attr('id','connectAmount');

          //input validation
          connectAmount.keyup(function() {
           var $th = $(this);
           $th.val( $th.val().replace(/[^0-9\.]/g, function(str) {  return ''; } ) );
          });
          //end

          var connectUnit =  $('<div>').addClass('popUnit').text('');
          var okButton = $('<button>').text('OK');

          connectName.append($('<option>').attr('value','default').attr('disabled','disabled').attr('selected','selected').text('-------'));

              for(var key in allIntermediates){
                connectName.append($('<option>').attr('value',key).text(allIntermediates[key][0]));
              }


          defineConnect.css('left', x + "px");
          defineConnect.css('top', y + "px");

          var closeThis = $('<button>').text('Cancel');

          defineConnect.append(connectTitle).append(connectName).append(connectAmountTitle).append(connectAmount).append(connectUnit).append(okButton).append(closeThis);


          canvas.append(defineConnect);
          console.log('tried to show dialog')

          connectName.selectpicker();

          connectName.on('shown.bs.select',function(){
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
                      createItem('transformation', searchBox.val(), csrftoken);
                  });
                });

              });

          closeThis.click(function(){
            instance.detach(info.connection);
            defineConnect.remove();
          });

          connectName.change(function(){
            var connectID = $(this).val();
            var unit = allIntermediates[connectID][1];
            connectUnit.text(unit);
          });

          okButton.click(function(){

              var name = connectName.children("option").filter(":selected").text();
              var intermediateId = connectName.children("option").filter(":selected").val()
              var amount = connectAmount.val();
              var type = 'connection';
              var unit = connectUnit.text()

              postData = {
                'sourceId' : info.sourceId,
                'targetId' : info.targetId,
                'intermediateId': intermediateId,
                'amount_required': amount,
                'system_id': system_id,
                'input_uuid':jsPlumbUtil.uuid(),
                'output_uuid':jsPlumbUtil.uuid(),
                'csrfmiddlewaretoken': csrftoken,
              }

              console.log(postData);

                $.post('/sandbox/newConnection/', postData);



              labelText = name + " ("+ amount +" "+ unit +")";
              info.connection.getOverlay("label").setLabel(labelText);
              info.connection.setData({'connection_type':'intermediate', 'connection_amount':amount})
              console.log( info.connection.getData())

              defineConnect.remove();

          });


        }}
        //else
        //{
          info.connection.getOverlay("label").setLabel(labelText);

        //};
      //}

        info.connection.getOverlay("label").hide();
        info.connection.bind("mouseover", function(conn){
          labelShow(conn);
        });

        info.connection.bind("mouseout", function(conn){
          labelHide(conn);
        });
    });

    // bind a double click listener to "canvas"; add new node when this occurs.
    /*jsPlumb.on(canvas, "dblclick", function(e) {
        newNode(e.offsetX, e.offsetY);
    });*/

    //
        // initialise element as connection targets and source.
        //
        var initNode = function(el) {

            // initialise draggable elements.
            instance.draggable(el, {
              //grid: [10,10],
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


            //console.log('intitiating' + el)

            instance.makeSource(el, {
                filter: ".ep,.ep2",
                connectionType:"basic intermediate",
            });

            instance.makeTarget(el, {
                dropOptions: { hoverClass: "dragHover" },
                //anchor: "Continuous",
                allowLoopback: false
            });

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

        var newNode = function(x, y) {

            var id = jsPlumbUtil.uuid();
            var d = $('<div>').attr('id', id).addClass('w');
            var title =  $('<div>').addClass('title').text('');
            var itemName = $('<input>').attr('type','text');
            title.append(itemName);
            var buttons = $('<div>').addClass('buttons');
            var connect =  $('<div>').addClass('ep');
            var input =  $('<div>').addClass('ip');
            var output =  $('<div>').addClass('op');
            var del =  $('<div>').addClass('x');

            buttons.append(connect).append(input).append(output).append(del);
            d.append(title);
            d.append(buttons);

            canvas.append(d);



            //var d = document.createElement("div");

            //d.className = "w";
            //d.id = id;
            //d.innerHTML = id.substring(0, 7) + "<div class=\"ep\"></div>";
            d.css('left', x + "px");
            d.css('top', y + "px");
            //instance.getContainer().appendChild(d);
            initNode(d);

            itemName.keyup(function(e) {
              if (e.keyCode === 13) {
                $(this).parent().text(this.value);
              }
            });

            itemName.focus(); // give the focus to the item name


            return d;
        };


        var saveState = function(state) {
          postData ={
              'uuid': $(state).attr('id'),
              'y': $(state).position().top,
              'x': $(state).position().left,
              'csrfmiddlewaretoken': csrftoken,
           };
           console.log(postData);

          $.post('/sandbox/posUpdate/', postData);
        }



        // suspend drawing and initialise.
        instance.batch(function () {
            for (var i = 0; i < windows.length; i++) {
                initNode(windows[i], true);
            }
            // and finally, make a few connections
            for (i=0;i<links.length;i++){
              //console.log ('trying to link' + links[i][0] + ' to ' + links[i][1])
              //console.log(links);
              //console.log('source : ' + links[i][0].split(' ').join('_'))
              //console.log('target : ' + links[i][1].split(' ').join('_'))

              var connection = instance.connect({
                 source: links[i][0].split(' ').join('_'),
                 target: links[i][1].split(' ').join('_'),
                 type:"basic " +links[i][2],
                 data:{'connection_type':links[i][2], 'connection_amount':links[i][3]},

               });

               //console.log(connection);

              connection.unbind("mouseover", function(conn){

                labelShow(conn);
              });
              connection.unbind("mouseout", function(conn){
                labelHide(conn);
              });


            };




            //instance.connect({ source: "opened", target: "phone1", type:"basic" });
            //instance.connect({ source: "phone1", target: "phone1", type:"basic" });
            //instance.connect({ source: "phone1", target: "inperson", type:"basic" });
            //instance.connect({source:"phone2", target:"rejected", type:"basic"});
        });

    $('#addProcess').click(function(e){
      console.log("Add a new process")


      var formHtml = '<label for="createItem">Name:</label> <input name = "createItem", id="createItem">'

      var createdModal = createModal('New Process', formHtml);
      $(document.body).append(createdModal);

      //input validation
      $('#createItem').keyup(function() {
       var $th = $(this);
       $th.val( $th.val().replace(/[^A-Za-z0-9\(\)\\\[\]/ ]/g, function(str) {  return ''; } ) );
      });
      //end

      $('#myModal').modal('show');


      $('#confirm_button').unbind().click(function(e){
        uuid = jsPlumbUtil.uuid();
        createNewItem('process', $('#createItem').val(), "" ,csrftoken, system_id, uuid, 250, 250)
        var thisNode = newNodeExternal($('#createItem').val(),'transformation',uuid,250,250,instance);
        initNode(thisNode);
        $('#myModal').modal('hide');
      });

      $('#myModal').on('hidden.bs.modal', function () {
       $('#myModal').remove();
     });
     $('#myModal').on('shown.bs.modal', function () {
      $('#createItem').focus()
    });
   });

   var buttonTypes = {
     'show_intermediate' : 'intermediate',
     'hide_intermediate' : 'intermediate',
     'show_input':'input',
     'hide_input':'input',
     'show_output':'output',
     'hide_output':'output'
   }

   $('.showLabels').click(function(e){
     var type = buttonTypes[$(this).attr('id')];

     instance.select().each(function(connection){
       connectionData = connection.getData()

       if (connectionData.connection_type == type){
         connection.getOverlay('label').show()
       }
     });
   })
   $('.hideLabels').click(function(e){
     var type = buttonTypes[$(this).attr('id')];

     instance.select().each(function(connection){
       connectionData = connection.getData()

       if (connectionData.connection_type == type){
         connection.getOverlay('label').hide()
       }
     });
   });

  };



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
  var canvas = $("#main_canvas");
  canvas.append(d);

  d.css('left', x + "px");
  d.css('top', y + "px");


  d.bind("mouseover", function(el){
    nodeOver(el, instance);
  });
  d.bind("mouseout", function(el){
    nodeOut(el, instance);
  });

  //console.log(instance);
  $('[data-toggle="popover"]').popover({
    container: 'body',
    delay: {
       show: "1000",
       hide: "100"
    },
});
  return d;
};


var labelShow = function(conn){
  //console.log(conn.targetId)
  try {
    conn.getOverlay("label").show();
  }
  catch(err){}
};

var labelHide=function(conn){
  //console.log(conn.targetId)
  try {
  conn.getOverlay("label").hide();
  }
  catch(err){}
};

var nodeOver = function (el, instance){

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


};

var nodeOut = function (el, instance){
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
};

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

    return myModal;
};


var deleteDatabaseItem = function(uuid,csrftoken,type,system_id){
  var postData = {
      'uuid': uuid,
      'csrfmiddlewaretoken': csrftoken,
      'type': type,
      'system_id':system_id,
   }

   console.log(postData);

  $.post('/sandbox/deleteDatabaseItem/', postData);
};


var createItem = function(type, initialValue, csrftoken){

  var typeTrans = {
    'input' : 'input',
    'output': 'output',
    'transformation' : 'intermediate product'
  }

  friendlyType = typeTrans[type]

  console.log('time to create a new ' + friendlyType)




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

  var formHtml = `
      <label for="createItem">Name:</label> <input name = "createItem", id="createItem" value = "`+initialValue+`">
      <label for="createUnit">Unit:</label>
      <select name='createUnit' id='createUnit' data-width ='30%' class='selectpicker'>
  `
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

  formHtml += "</select>"

  var createdModal = createModal('New ' + friendlyType, formHtml);
  $(document.body).append(createdModal);
  $('#createUnit').selectpicker();

  //input validation
  $('#createItem').keyup(function() {
   var $th = $(this);
   $th.val( $th.val().replace(/[^A-Za-z0-9\(\)\\\[\]/ ]/g, function(str) {  return ''; } ) );
  });
  //end

  $('#myModal').modal('show');

  var itemIDNo = null
   $('#confirm_button').unbind().click(function(e){
    data = createNewItem(type, $('#createItem').val(), $('#createUnit').val(),csrftoken,0,0,0,0)
    $('#myModal').modal('hide');
        console.log(data)
        console.log(data.id)
        itemIDNo = data.id

        $(".popUnit").text($('#createUnit').val());
        $(".selectpicker").append('<option value='+ itemIDNo +'>'+$('#createItem').val()+'</option>')
       .selectpicker('refresh').selectpicker('val',itemIDNo);

  });

  $('#myModal').on('hidden.bs.modal', function () {
   $('#myModal').remove();
  });
  $('#myModal').on('shown.bs.modal', function () {
   $('#createItem').focus()
 });
};

createNewItem = function(type, name, unit ,csrftoken, system_id,uuid,x,y){

  var postData = {
      'csrfmiddlewaretoken': csrftoken,
      'type':type,
      'name':name,
      'unit':unit,
      'system_id':system_id,
      'uuid':uuid,
      'x':x,
      'y':y
   };
   console.log(postData);

    $.ajaxSetup({async:false});  //execute synchronously

    var returnedData = null
    $.post('/sandbox/newDatabaseItem/', postData, function(data){
       returnedData = data
    }, "json");

    $.ajaxSetup({async:true});  //return to default setting

    return returnedData;

}
