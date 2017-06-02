$(document).ready(function(){
	/*
	$.getJSON( "/status.json", function(data) {
		console.log(data)
		$statusbox = $('#status_box_outer');

		$statusbox.append($('<div class = "status_box_item row" id = "status_has_model"></div>'))

		$has_model = $statusbox.find('#status_has_model')

		$has_model.append('<div class="status_title col-xs-10">Model exists</div>')
			if(data.has_model){$has_model.append('<div class = "status_item col-xs-6 col-xs-2"><i class="material-icons is_true">check</i></div>')}
				else{
					$has_model.append('<div class = "status_item col-xs-6 col-xs-2"><i class="material-icons is_false">close</i></div>')
				}

		$statusbox.append($('<div class = "status_box_item row" id = "status_model_has_impacts"></div>'))
		$model_has_impacts = $statusbox.find('#status_model_has_impacts')

		$model_has_impacts.append('<div class="status_title col-xs-10">Model is linked</div>')
			if(data.model_has_impacts){$model_has_impacts.append('<div class = "status_item col-xs-6 col-xs-2"><i class="material-icons is_true">check</i></div>')}
				else{
					$model_has_impacts.append('<div class = "status_item col-xs-6 col-xs-2"><i class="material-icons is_false">close</i></div>')
				}

		$statusbox.append($('<div class = "status_box_item row" id = "status_model_has_parameters"></div>'))
		$model_has_parameters = $statusbox.find('#status_model_has_parameters')

		$model_has_parameters.append('<div class="status_title col-xs-10">Model is parameterised</div>')
			if(data.model_has_parameters){$model_has_parameters.append('<div class = "status_item col-xs-6 col-xs-2"><i class="material-icons is_true">check</i></div>')}
				else{
					$model_has_parameters.append('<div class = "status_item col-xs-6 col-xs-2"><i class="material-icons is_false">close</i></div>')
				}

		$statusbox.append($('<div class = "status_box_item row" id = "status_model_has_functions"></div>'))
		$model_has_functions =  $statusbox.find('#status_model_has_functions')

		$model_has_functions.append('<div class="status_title col-xs-10">Model hase functions</div>')
			if(data.model_has_functions){$model_has_functions.append('<div class = "status_item col-xs-6 col-xs-2"><i class="material-icons is_true">check</i></div>')}
				else{
					$model_has_functions.append('<div class = "status_item col-xs-6 col-xs-2"><i class="material-icons is_false">close</i></div>')
				}

		$statusbox.append($('<div class = "status_box_item row" id = "status_model_is_runnable"></div>'))
		$model_is_runnable = $statusbox.find('#status_model_is_runnable')

		$model_is_runnable.append('<div class="status_title col-xs-10">Model is runnable</div>')
			if(data.model_is_runnable){$model_is_runnable.append('<div class = "status_item col-xs-6 col-xs-2"><i class="material-icons is_true">check</i></div>')}
				else{
					$model_is_runnable.append('<div class = "status_item col-xs-6 col-xs-2"><i class="material-icons is_false">close</i></div>')
				}

		$statusbox.append($('<div class = "status_box_item row" id = "status_model_is_fully_formed"></div>'))
		$model_is_fully_formed = $statusbox.find('#status_model_is_fully_formed')

		$model_is_fully_formed.append('<div class="status_title col-xs-10">Model is fully formed</div>')
			if(data.model_is_fully_formed){$model_is_fully_formed.append('<div class = "status_item col-xs-6 col-xs-2"><i class="material-icons is_true">check</i></div>')}
				else{
					$model_is_fully_formed.append('<div class = "status_item col-xs-6 col-xs-2"><i class="material-icons is_false">close</i></div>')
				}


	})
	*/
	// Second version - small

	$.getJSON( "/status.json", function(data) {
		console.log(data);
		$statusbox = $('#status_box_outer_small');

		$statusbox.append($('<div class = "status_box_item row" id = "status_has_model" data-toggle="popover" data-container = "body" data-placement= "left" data-trigger="hover" title="The model exists" data-content="The model contains at least one process."></div>'));
		$has_model = $statusbox.find('#status_has_model');

		$has_model.append('<div class="status_title col-xs-6"><i class="material-icons">wb_iridescent</i></div>');
			if(data.has_model){$has_model.append('<div class = "status_item col-xs-6"><i class="material-icons is_true">check</i></div>');}
				else{
					$has_model.append('<div class = "status_item col-xs-6"><i class="material-icons is_false">close</i></div>');
				}

		$statusbox.append($('<div class = "status_box_item row" id = "status_model_has_impacts" data-toggle="popover" data-container = "body" data-placement= "left" data-trigger="hover" title="The model has impacts" data-content="At least one process has an external link to an inventory or biosphere database. If the total impact is 0 the analysis will fail."></div>'));
		$model_has_impacts = $statusbox.find('#status_model_has_impacts');

		$model_has_impacts.append('<div class="status_title col-xs-6"><i class="material-icons">link</i></div>');
			if(data.model_has_impacts){$model_has_impacts.append('<div class = "status_item col-xs-6"><i class="material-icons is_true">check</i></div>');}
				else{
					$model_has_impacts.append('<div class = "status_item col-xs-6"><i class="material-icons is_false">close</i></div>');
				}

		$statusbox.append($('<div class = "status_box_item row" id = "status_model_has_parameters" data-toggle="popover" data-container = "body" data-placement= "left" data-trigger="hover" title="The model has parameters" data-content="The model has at least one parameter set that can be analysed."></div>'));
		$model_has_parameters = $statusbox.find('#status_model_has_parameters');

		$model_has_parameters.append('<div class="status_title col-xs-6"><i class="material-icons">format_list_numbered</i></div>');
			if(data.model_has_parameters){$model_has_parameters.append('<div class = "status_item col-xs-6"><i class="material-icons is_true">check</i></div>');}
				else{
					$model_has_parameters.append('<div class = "status_item col-xs-6"><i class="material-icons is_false">close</i></div>');
				}

		$statusbox.append($('<div class = "status_box_item row" id = "status_model_has_functions" data-toggle="popover" data-container = "body" data-placement= "left" data-trigger="hover" title="The model has functions" data-content="The model contains at least one function - this is not required to run the model."></div>'));
		$model_has_functions = $statusbox.find('#status_model_has_functions');

		$model_has_functions.append('<div class="status_title col-xs-6"><i class="material-icons">functions</i></div>');
			if(data.model_has_functions){$model_has_functions.append('<div class = "status_item col-xs-6"><i class="material-icons is_true">check</i></div>');}
				else{
					$model_has_functions.append('<div class = "status_item col-xs-6"><i class="material-icons is_false">close</i></div>');
				}

		$statusbox.append($('<div class = "status_box_item row" id = "status_model_is_runnable" data-toggle="popover" data-container = "body" data-placement= "left" data-trigger="hover" title="The model can be analysed" data-content="The model contains enough information for an analysis to be run - click on the analysis (pie chart) icon on a process to analyse it."></div>'));
		$model_is_runnable = $statusbox.find('#status_model_is_runnable');

		$model_is_runnable.append('<div class="status_title col-xs-6"><i class="material-icons">equalizer</i></div>');
			if(data.model_is_runnable){$model_is_runnable.append('<div class = "status_item col-xs-6"><i class="material-icons is_true">check</i></div>');}
				else{
					$model_is_runnable.append('<div class = "status_item col-xs-6"><i class="material-icons is_false">close</i></div>');
				}

		$statusbox.append($('<div class = "status_box_item row" id = "status_model_is_fully_formed" data-toggle="popover" data-container = "body" data-placement= "left" data-trigger="hover" title="The model is \'fully formed\'" data-content="The model contains all of the information required to run, plus functions"></div>'));
		$model_is_fully_formed = $statusbox.find('#status_model_is_fully_formed');

		$model_is_fully_formed.append('<div class="status_title col-xs-6"><i class="material-icons">language</i></div>');
			if(data.model_is_fully_formed){$model_is_fully_formed.append('<div class = "status_item col-xs-6"><i class="material-icons is_true">check</i></div>');}
				else{
					$model_is_fully_formed.append('<div class = "status_item col-xs-6"><i class="material-icons is_false">close</i></div>');
				}

		$('[data-toggle="popover"]').popover(); 
	});

});

