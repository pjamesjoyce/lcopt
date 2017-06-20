function update_table(){

	var ps = $('#parameterSetChoice').val() - 1;
  	var m = $('#methodChoice').val() - 1;

	ps_length = bound_data.results.length;

	var table_data = [];
	var cell_width = 100;

/*
	{% set running_total = [0] %}

    {% for i in range(colspan) %}
        {% for j in range(no_methods) %}
            {% if running_total.append(running_total.pop() + args.result_sets.results[i][j].foreground_results[f]) %}{% endif %}
        {% endfor %}
    {% endfor %}
    <!-- done -->
*/
	
	for(var i = 0; i<ps_length; i++){
		var foreground_results = bound_data.results[i][m].foreground_results;
		
		var row_data = []
		
		for(var data_row in foreground_results){

			var running_total=0;

			for(var p=0; p<ps_length; p++){
				//console.log(bound_data.results[p][m].foreground_results[data_row]);
				running_total += Math.abs(bound_data.results[p][m].foreground_results[data_row]);
			}
			//console.log(running_total);
			if(running_total != 0){
				row_data.push({name: data_row, value:foreground_results[data_row], rt:running_total});	
			}
		}
		row_data.sort(function(a, b) {
		    return parseFloat(b.rt) - parseFloat(a.rt);
		});

		table_data.push(row_data);
	}
	
	var $table_div = $('<div id="table" class="top-padding"><table id="myTable" class="table table-bordered table-condensed table-hover table-nonfluid"><thead></thead><tbody>');
	
	$table_div.find('thead').append('<tr class ="table_header" id="method_row">');

	$table_div.find('#method_row').append('<th rowspan="2">Process</th>');

	var method_name = bound_data.settings.method_names[m];
	var display_method_name = method_name.charAt(0).toUpperCase() + method_name.slice(1);

	$table_div.find('#method_row').append('<th colspan="'+ ps_length +'">'+ display_method_name + '</br><span class = "unit">' + bound_data.settings.method_units[m] + '</span></th>');

	$table_div.find('thead').append('<tr class ="table_header" id="ps_row">');

	for(var j = 0; j<ps_length; j++){
		$table_div.find('#ps_row').append('<th>'+ bound_data.settings.ps_names[j] +'</th>');
	}

	
	$table_div.find('tbody').append('<tr class="total_row">');
	
	$table_div.find('.total_row').append('<td>TOTAL</td>');

	for(var j = 0; j<ps_length; j++){
		//console.log(bound_data.settings.ps_names[j]);
		$table_div.find('.total_row').append('<th class="text-right data_cell">'+ bound_data.results[j][m].score.toPrecision(3) +'</th>');
	}
	
	//console.log(table_data);

	no_rows = table_data[0].length;

	for(var k = 0; k<no_rows; k++){
		html = '<tr class="item_row">';
		html += '<td class="row_title">'+table_data[0][k].name+'</td>';
		for(var d=0;d<ps_length;d++){
			if(table_data[d][k].value == 0){
				html += '<td class="text-muted text-right data_cell">-</td>';	
			}else{
				html += '<td class="text-right data_cell">' + table_data[d][k].value.toPrecision(3) + '</td>';	
			}
		}
		html += '</tr>';
		var $item_row = $table_div.find('tbody').append(html);
	}
	

	$("#dynamic_table").html($table_div);


}



function update_summary_table(){

	ps_length = bound_data.results.length;
	m_length = bound_data.settings.methods.length;

	var table_data = [];
	var cell_width = 100;

	
	var $table_div = $('<div id="table" class="top-padding"><table id="myTable" class="table table-bordered table-condensed table-hover table-nonfluid"><thead></thead><tbody>');
	
	$table_div.find('thead').append('<tr class ="table_header" id="parameter_row">');

	$table_div.find('#parameter_row').append('<th>Impact</th>');

	for(var p = 0; p<ps_length; p++){
		$table_div.find('#parameter_row').append('<th>' + bound_data.settings.ps_names[p] + '</th>');
	}

	for(var r = 0; r<m_length; r++){
		html = '<tr class="item_row">';
		for(var c = -1; c<ps_length; c++){
			if(c == -1){
				method_name = bound_data.settings.method_names[r];
				display_method_name = method_name.charAt(0).toUpperCase() + method_name.slice(1);
				html += '<td class="row_title">'+ display_method_name + ' <span class = "unit">(' + bound_data.settings.method_units[r] + ')</span></td>';
			}else{
				html += '<td class="text-right data_cell">' + bound_data.results[c][r].score.toPrecision(3) + '</td>';
			}
		}
		html += '</tr>';
		var $item_row = $table_div.find('tbody').append(html);
	}

	$("#dynamic_summary_table").html($table_div);

}


$(document).ready(function() {
	$("#table_export_button").click(function(e) {

	  var ps = $('#parameterSetChoice').val() - 1;
  	  var m = $('#methodChoice').val() - 1;

	  window.location.replace("/excel_export?type=method&ps=" + ps + "&m=" + m);

	});


	$("#summary_excel_button").click(function(e){

	  var ps = $('#parameterSetChoice').val() - 1;
  	  var m = $('#methodChoice').val() - 1;

	  window.location.replace("/excel_export?type=summary&ps=" + ps + "&m=" + m);

	});

});