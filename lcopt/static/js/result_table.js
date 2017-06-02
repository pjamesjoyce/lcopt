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
				console.log(bound_data.results[p][m].foreground_results[data_row]);
				running_total += Math.abs(bound_data.results[p][m].foreground_results[data_row]);
			}
			console.log(running_total);
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
		console.log(bound_data.settings.ps_names[j]);
		$table_div.find('.total_row').append('<th class="text-right data_cell">'+ bound_data.results[j][m].score.toPrecision(2) +'</th>');
	}
	
	console.log(table_data);

	no_rows = table_data[0].length;

	for(var k = 0; k<no_rows; k++){
		html = '<tr class="item_row">';
		html += '<td class="row_title">'+table_data[0][k].name+'</td>';
		for(var d=0;d<ps_length;d++){
			if(table_data[d][k].value == 0){
				html += '<td class="text-muted text-right data_cell">-</td>';	
			}else{
				html += '<td class="text-right data_cell">' + table_data[d][k].value.toPrecision(2) + '</td>';	
			}
		}
		html += '</tr>';
		var $item_row = $table_div.find('tbody').append(html);
	}
	

	$("#dynamic_table").html($table_div);


}


/*
<div id="table" class="top-padding">
                        <table id="myTable" class="table table-bordered table-condensed table-hover">
                          <thead>
                              <tr class ="table_header">
                                <th rowspan="2">Process</th>
                                {% for i in range(no_methods) %}
                                <th colspan="{{colspan}}">{{args.result_sets.settings.method_names[i] | capitalize}} </br><span class = "unit">{{args.result_sets.settings.method_units[i]}}</span></th>
                                {% endfor %}
                              </tr>
                              <tr class ="table_header">
                                
                                {% for i in range(no_methods) %}
                                    {% for j in args.result_sets.settings.ps_names %}
                                        <th>{{j}}</th>
                                    {% endfor %}
                                {% endfor %}
                              </tr>
                            </thead>

                            <tbody>

                                <tr class = "total_row">
                                    <td>TOTAL</td>
                                    {% for j in range(no_methods) %}
                                        {% for i in range(colspan) %}
                                            
                                                <td class="right_align">{{"%0.2g" | format(args.result_sets.results[i][j].score)}}</td>
                                            {% endfor %}
                                        {% endfor %}
                                </tr>

                                
                                {% for f in args.result_sets.results[0][0].foreground_results %}
                                    <!-- calculate the row total, to see if its zero -->
                                    {% set running_total = [0] %}

                                    {% for i in range(colspan) %}
                                        {% for j in range(no_methods) %}
                                            {% if running_total.append(running_total.pop() + args.result_sets.results[i][j].foreground_results[f]) %}{% endif %}
                                        {% endfor %}
                                    {% endfor %}
                                    <!-- done -->

                                    
                                    {% if running_total[0] != 0 %}  

                                     <tr>
                                        <td class="row_title">{{f}}</td>
                                        {% for j in range(no_methods) %}
                                        {% for i in range(colspan) %}
                                            
                                                <td class="right_align">{{"%0.2g" | format(args.result_sets.results[i][j].foreground_results[f])}}</td>
                                            {% endfor %}
                                        {% endfor %}
                                    </tr>
                                    

                                    {% endif %}

                                {% endfor %}

                                
                            </tbody>
                            
                        </table>
                        </div>
                      </div>

*/