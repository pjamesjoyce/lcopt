function update_status(){

	$has_model = $('#status_has_model');
	$model_has_impacts = $('#status_model_has_impacts');
	$model_has_parameters = $('#status_model_has_parameters');
	$model_has_functions = $('#status_model_has_functions');
	$model_is_runnable = $('#status_model_is_runnable');
	$model_is_fully_formed = $('#status_model_is_fully_formed');

	items = [
				[$has_model, 'has_model'],
				[$model_has_impacts,'model_has_impacts'],
				[$model_has_parameters,'model_has_parameters'], 
				[$model_has_functions,'model_has_functions'], 
				[$model_is_runnable,'model_is_runnable'], 
				[$model_is_fully_formed,'model_is_fully_formed']

			];

	$.getJSON( "/status.json", function(data) {

		for (var i = items.length - 1; i >= 0; i--) {
			set_display(items[i][0], data[items[i][1]]);
		}

	});


	$('[data-toggle="popover"]').popover({
    delay: {
       show: "0",
       hide: "50"
    },
  });

}


function set_display(item, bool){

	$icon = item.find('.status_item > i');

	if(bool){
		$icon.addClass('is_true');
		$icon.removeClass('is_false');
		$icon.html('check');
	}else{
		$icon.addClass('is_false');
		$icon.removeClass('is_true');
		$icon.html('close');
	}

}


update_status();
    $('[data-toggle="popover"]').popover({
    delay: {
       show: "0",
       hide: "50"
    },
});