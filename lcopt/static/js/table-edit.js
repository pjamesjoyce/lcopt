$(document).ready(function(){


    var $TABLE = $('#table');
    var $BTN = $('#export-btn');
    var $EXPORT = $('#export');

    // A few jQuery helpers for exporting only
    jQuery.fn.pop = [].pop;
    jQuery.fn.shift = [].shift;

    // Post to the provided URL with the specified parameters.
    function post(path, parameters) {
        var form = $('<form></form>');

        form.attr("method", "post");
        form.attr("action", path);

        $.each(parameters, function(key, value) {
            var field = $('<input></input>');

            field.attr("type", "hidden");
            field.attr("name", key);
            field.attr("value", value);

            form.append(field);
        });

        // The form needs to be a part of the document in
        // order for us to be able to submit it.
        $(document.body).append(form);
        form.submit();
    }

    //$BTN.click(function () {

    function save_parameters(){
      var $rows = $TABLE.find('tr');
      var headers = [];
      var data = [];
      
      // Get the headers (add special header logic here)
      $($rows.shift()).find('th').each(function () {
        headers.push($(this).text());
      });
      
      console.log($rows)

      // Turn all existing rows into a loopable array
      $rows.each(function () {
        var $td, h;
        if ($(this).hasClass('data_row')){
            $td = $(this).find('.export');
            h = {};
            
            // Use the headers from earlier to name our hash keys
            headers.forEach(function (header, i) {
              h[header] = $td.eq(i).text();   
            });
            
            data.push(h);

        }else if($(this).hasClass('function_row')){
            $td = $(this).find('.export');
            h = {};
            
            // Use the headers from earlier to name our hash keys
            headers.forEach(function (header, i) {
              if(i<=2){
                h[header] = $td.eq(i).text();  
              }else{
                h[header] = "[FUNCTION]"; //$td.eq(i).text();   
              }
            });
            
            data.push(h);
        }
      });
      
    console.log(JSON.stringify(data));

    postData ={
        'action':'parse_parameters',
        'data' : JSON.stringify(data)
    };
    
    $.post('/process_post', postData);

    update_status();
    
    
    }

    $BTN.click(function() {
        save_parameters();
        window.location.replace("/parameters");

    });

    


    var myTable = $('#myTable'),
    iter = 0;

    $('#btnAddCol').click(function () {

        var count = myTable.find('.ps_name').length;

        myTable.find('.table_header').append('<th contenteditable="true" class="ps_name">ParameterSet_'+(count+1)+'</th>');

         myTable.find('.data_row,.function_row').each(function(){
                var trow = $(this);
           
                last_item = trow.find('td:last');
                
                trow.append('<td contenteditable="true" class="new_item right_align export">'+ last_item.text() +'</td>');
             
         });


         myTable.find('.table_section,.table_subsection').each(function(){
            $(this).attr('colspan', count+4);
         });
         
    });

    var formTitle = 'Add global parameter';

    var formHtml = `
                    <form class="form-horizontal">
                      <div class="form-group">
                        <label for="paramName" class="control-label col-xs-3">ID</label> 
                        <div class="col-xs-9">
                          <input class="form-control" name = "paramName", id="paramName">
                        </div>
                      </div>
                      <div class="form-group">
                        <label for="paramDescription" class="control-label col-xs-3">Name</label> 
                        <div class="col-xs-9">
                          <input class="form-control" name = "paramDescription", id="paramDescription">
                        </div>
                      </div>
                      <div class="form-group">
                        <label for="paramUnit" class="control-label col-xs-3">Unit (optional)</label> 
                        <div class="col-xs-9">
                          <input class="form-control" name = "paramUnit", id="paramUnit">
                        </div>
                      </div>
                      <div class="form-group">
                        <label for="paramDefault" class="control-label col-xs-3">Default value</label> 
                        <div class="col-xs-9">
                          <input class="form-control" name = "paramDefault", id="paramDefault">
                        </div>
                      </div>
                      </form>
                      <div class = "row">
                          <div class="col-xs-12">
                            <div id="paramButton" class="col-xs-3 pull-right">
                             <!--Button goes here--> 
                            </div>
                          </div>
                      </div>
                  `;


    $('#btn_add_parameter').click(function(){
        save_parameters();
        var inputModal = BootstrapDialog.show({
            title:formTitle,
            message: messageFunction,
            nl2br: false,

            buttons:[{
                label:'Add',
                cssClass: 'btn-primary',
                action:function(dialogRef){
                        console.log('add parameter');

                        $message = dialogRef.$modalBody;
                        var param_id = slugify($message.find('#paramName').val());
                        var param_description = $message.find('#paramDescription').val();
                        var param_default = $message.find('#paramDefault').val();
                        var param_unit = $message.find('#paramUnit').val();
                        var param_default_is_number = $.isNumeric(param_default);
                        console.log(param_default_is_number);

                        if(param_id && param_description && param_default && param_default_is_number){
                            var postData = {
                                action: 'add_parameter',
                                param_id: param_id,
                                param_description: param_description,
                                param_default: param_default,
                                param_unit: param_unit,
                            };
                            console.log(postData);

                            $.post('/process_post', postData);

                            
                          //close the dialog
                          dialogRef.close();
                          window.location.replace("/parameters");
                      }else{
                        $('.inputMessage').remove();
                          if(!param_id){
                            $('#paramName').after('<div class="red inputMessage">Please give the parameter a computer readable identifier</div>');
                          }
                          if(!param_description){
                            $('#paramDescription').after('<div class="red inputMessage">Please give the parameter a human readable name</div>');
                          }
                          if(!param_default){
                            $('#paramDefault').after("<div class='red inputMessage'>Please enter a default value (use 0 if you don't know what to choose)</div>");
                          }
                          if(param_default && !param_default_is_number){
                            $('#paramDefault').after("<div class='red inputMessage'>The default value needs to be a number</div>");
                          }
                      }
                  },
                }]

          });
    });

    function slugify(text){

          return text.toString().toLowerCase()
            .replace(/\s+/g, '_')           // Replace spaces with _
            .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
            .replace(/\_\_+/g, '_')         // Replace multiple _ with single _
            .replace(/^_+/, '')             // Trim _ from start of text
            .replace(/_+$/, '');            // Trim _ from end of text
        }

    function messageFunction(dialogRef){
                var $message = $('<div></div>').append(formHtml);
                return $message;
            }

});//end of document.ready