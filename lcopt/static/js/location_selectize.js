function setup_location_box(){

	$.getJSON('/locations.json', function(data){

		console.log(data);

		$location = $('#location');

		$location.selectize({
			valueField: 'code',
	    	labelField: 'name',
	    	searchField: ['name', 'code'],
	    	options: data,
			render: {
				option: custom_option,
				item :custom_item
			},
			maxItems: '1',
			openOnFocus: true,
		});

	});

}


function custom_option(data, escape){
	console.log(data)
	$option = $("<div></div>");
	$option.append(data.name);

	$option.append('<span class="grey pull-right">'+data.code+'</span>')

	html = $option.prop('outerHTML');

	////console.log(html)

	return html;
}//end of custom_option

function custom_item(data, escape){
	console.log(data)
	$option = $("<div></div>");
	$option.append(data.name);

	$option.append('<span class="grey"> {'+data.code+'}</span>')

	html = $option.prop('outerHTML');

	////console.log(html)

	return html;
}//end of custom_option
