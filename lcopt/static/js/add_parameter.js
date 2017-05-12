$(document).ready(function(){
	console.log('hello from add_parameter.js')

	var formTitle = 'Add global parameter'

	var formHtml = `
                    <form class="form-horizontal">
                      <div class="form-group">
                        <label for="paramName" class="control-label col-xs-3">Parameter ID</label> 
                        <div class="col-xs-9">
                          <input class="form-control" name = "paramName", id="paramName">
                        </div>
                      </div>
                      <div class="form-group">
                        <label for="paramDescription" class="control-label col-xs-3">Description</label> 
                        <div class="col-xs-9">
                          <input class="form-control" name = "paramDescription", id="paramDescription">
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
                  `


	$('#btn_add_parameter').click(function(){
		var inputModal = BootstrapDialog.show({
	    	title:formTitle,
	    	message: messageFunction,
	    	nl2br: false,

	    	buttons:[{
		        label:'Add',
		        cssClass: 'btn-primary',
		        action:function(dialogRef){
			            console.log('add parameter')

			            $message = dialogRef.$modalBody
						var param_id = $message.find('#paramName');
						var param_description = $message.find('#paramDescription');
						var param_default = $message.find('#paramDefault');

						var postData = {
							action: 'add_parameter',
							param_id:param_id.val(),
							param_description:param_description.val(),
							param_default:param_default.val(),
						};
						console.log(postData)

						$.post('/process_post', postData)

						
			          //close the dialog
			          dialogRef.close()
			          window.location.replace("/parameters");
			      },
			    }]

		  })
	})



    	
	


	function messageFunction(dialogRef){
				var $message = $('<div></div>').append(formHtml);
	    		return $message
	    	}

	

})