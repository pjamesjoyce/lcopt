$(document).ready(function(){
	////console.log('Hello from function_box.js')

	$.getJSON('/parameters.json', function(data){
		//////console.log(data);
		setUpSelectize(data)
	})

function setUpSelectize(external_data){
	////console.log('Hello from setUpSelectize')
	////console.log(external_data);

	// set up the operators in the options and optgroups
	var my_options = [],
		operators = [
			{value: '*', text: ' * ', optgroup: 'Operators', custom_type: 'operator'},
			{value: '-', text: ' - ', optgroup: 'Operators', custom_type: 'operator'},
			{value: '+', text: ' + ', optgroup: 'Operators', custom_type: 'operator'},
			{value: '/', text: ' / ', optgroup: 'Operators', custom_type: 'operator'},
			{value: ')', text: ' ) ', optgroup: 'Operators', custom_type: 'operator'},
			{value: '(', text: ' ( ', optgroup: 'Operators', custom_type: 'operator'},
		],
		my_optgroups = [],
		operator_optgroup = [{label: 'Operators', value: 'Operators'}, {label:'Numbers', value:'number'}],

		custom_type_map = {
			"Inputs from the 'technosphere'":'input',
	        "Inputs from other processes":'intermediate',
	        "Direct emissions to the environment":'biosphere'
		},

		icon_map = {
			'input':'business',
			'intermediate':'trending_flat',
			'biosphere': 'local_florist',
			'global':'language',
		},

		name_map = {}



	for(this_process in external_data){
		to_full = external_data[this_process]['name']
		to = to_full.replace(/\t?\([A-Za-z 0-9]*\)$/i,"");
		//console.log("|" + to_full + "|")
		my_optgroups.push({label: to, value: to})
		subsections = external_data[this_process]['my_items']
		for (subsection in subsections){
			subsection_name = subsections[subsection]['name']
			//console.log("\t" + subsection_name)
			items = subsections[subsection]['my_items']
			for (item in items){
				id = items[item]['id']
				name = items[item]['name']

				if(custom_type_map[subsection_name] == 'biosphere'){
					option_text = "Emission of "+ name + " from " + to;
					option_custom_type = custom_type_map[subsection_name];
				}else if (to_full == 'Global Parameters'){
					option_text = name;
					option_custom_type = 'global'
				}
				else{
					option_text = "Input of "+ name + " to " + to;
					option_custom_type = custom_type_map[subsection_name];
				}
				//console.log("\t\t"+id+"\t"+name)
				my_options.push({value: id , text: option_text, optgroup: to, custom_type: option_custom_type});
				name_map[id] = option_text;
			}

		}

	}

	full_options = my_options.concat(operators);
	full_optgroups = my_optgroups.concat(operator_optgroup);

	$('#select-to').selectize({
		//plugins: ['drag_drop'],
		delimiter: ' ',
		persist: false,
		hideSelected: false, // from original null
		duplicates: true, // from original false
		cache:false,
		selectOnTab:true,
		options:full_options,
		optgroups:full_optgroups,
		autocomplete: false, 
		addPrecedence:false,
		onChange: function(value){
			//////console.log('change')
			$('#input_value').val($('#select-to').val())
			////console.log(this.options)
		},
		onItemAdd: function(value, $item){
			//////console.log($item)
			//////console.log($item[0])
		},
		/*createFilter: function(input) {
	        var match, regex;

	        // email@address.com
	        regex = new RegExp('^[\d\.]?$', 'i');
	        match = input.match(regex);
	        if (match) return !this.options.hasOwnProperty(match[0]);

	        return false;
	    },*/
	    create: function(input) {
	        if ((new RegExp('^[0-9\.]*$', 'i')).test(input)) {
	        	//console.log('its a number')
	            return {value: input, text:input, custom_type:'number', optgroup:'number'};
	        }
	        //console.log('|' + input +'|')
	        //console.log('not a number')
	        return false;
	    },
		render:{
			option: custom_option,
			optgroup: custom_optgroup,
			item: custom_item,
		},// end of render
	
	})// end of selectize

	$('#parameter-select').selectize({
		//plugins: ['drag_drop'],
		delimiter: ' ',
		persist: false,
		hideSelected: false, // from original null
		duplicates: true, // from original false
		cache:false,
		selectOnTab:true,
		options:my_options,
		optgroups:my_optgroups,
		create: false, 
		render:{
			option: custom_option,
			optgroup: custom_optgroup,
			item: custom_item,
		},// end of render
		onChange:function(value){
			console.log(value)
			name = name_map[value]
			console.log(name)
			$('#parsed_function_label').text(value + " =")
			$('#function_label').text(name + " =")
		}
	
	})// end of selectize

		
	function custom_optgroup(data, escape){
		if(data.value == "Operators"|| data.value == 'number'){
			//return data.html.replace('class="', 'class="hide_me ')
			var search = 'class="',
				replacement = 'class="hide_me ';
			return data.html.replace(new RegExp(search, 'g'), replacement);
		}else{
			return data.html
		}
	}//end of custom_optgroup

	function custom_option(data, escape){
		////console.log(data)
		$option = $("<div></div>");
		$option.append(data.text)

		if (data.custom_type == 'operator' || data.custom_type == 'number'){
			$option.addClass('hide_me')
		}

		if(data.value == $('#parameter-select').val()){
			$option.addClass('hide_me')
		}

		icon_name = icon_map[data.custom_type]

		$option.append('<i class="material-icons grey pull-right">'+icon_name+'</i>')

		html = $option.prop('outerHTML');

		////console.log(html)

		return html
	}//end of custom_option

	function custom_item(data, escape){
		$item = $("<div></div>");
		$item.append(data.text)
		//console.log(data)

		$item.addClass("item_"+ data.custom_type)

		html = $item.prop('outerHTML');

		//console.log(html)

		return html
	}
}// end of setUpSelectize


$('#save_function').click(function(){
	console.log($('#select-to').val())
	postData = {
		action : 'create_function',
		for : $('#parameter-select').val(),
		my_function : $('#select-to').val(),
		description:  $('#description').val(),
	}

	$.post('/process_post', postData)

	window.location.replace("/parameters");

})

})// end of document.ready