function setUpSelectize(external_data, current_methods){
	////console.log('Hello from setUpSelectize')
	console.log(external_data);
	console.log(current_methods);

	// set up the operators in the options and optgroups
	var my_optgroups = [],
		my_options = [],
		optgroup_list = [];
		
	for(m in external_data){
		this_method = external_data[m]
		//console.log(this_method)
		//console.log($.inArray(this_method[0], my_optgroups))
		if ($.inArray(this_method[0], optgroup_list) == -1){
			optgroup_list.push(this_method[0])
			my_optgroups.push({label: this_method[0], value: this_method[0]})
		}

		my_description = this_method.slice(1).join(", ")

		my_options.push({value: this_method , text: my_description, optgroup: this_method[0]});
	}


	console.log(current_methods)


	$select = $('#settings_methods').selectize({
		delimiter: ',',
		items: current_methods,
		options: my_options,
		optgroups: my_optgroups,
		optgroupField: 'optgroup',
		labelField: 'text',
		searchField: ['optgroup', 'text'],
		render: {
			optgroup_header: function(data, escape){
				return '<div class="optgroup-header">' + escape(data.label) + '</div>';
			},
			option: custom_option,
			item: custom_item,
			
		},

	})// end of selectize


	function custom_option(data, escape){
		////console.log(data)
		$option = $("<div></div>");
		$option.append(data.text)

		$option.append('<span class="grey pull-right">'+data.optgroup+'</span>')

		html = $option.prop('outerHTML');

		////console.log(html)

		return html
	}//end of custom_option

	function custom_item(data, escape){
		$item = $("<div></div>");
		$item.append('<span class="grey method_group">' + data.value[0] + '</span> <span>' + data.text + '</span>') 
		//console.log(data)

		$item.addClass("item_method")

		html = $item.prop('outerHTML');

		//console.log(html)

		return html
	}



}//end of setUpSelectize

