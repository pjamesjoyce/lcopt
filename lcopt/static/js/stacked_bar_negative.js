var bound_data

var stack_bar_margin = {top: 50, right: 250, bottom: 20, left: 75},
	stack_bar_dimensions ={height:470, width: 750};

	stack_bar_width = stack_bar_dimensions.width - stack_bar_margin.left - stack_bar_margin.right,
	stack_bar_height = stack_bar_dimensions.height - stack_bar_margin.top - stack_bar_margin.bottom;

var legend_dimensions = {width:150, height:stack_bar_height}

/*
$('#methodChoice').change(function(){
	do_stack($('#methodChoice').val()-1)
})


d3.json("results3.json", function(error, data) {
    if (error) throw error;
    bound_data = data;
    console.log(bound_data);
    do_stack(0);
});
*/

function do_stack(m){

	var data = [];
	var keys = [];
	var stack_color = d3.scaleOrdinal(d3.schemeCategory20)

	for (ps=0; ps < bound_data.results.length; ps++){

		this_ps = bound_data.results[ps]

		this_item = {'ps_name': this_ps.ps_name}

		for (result in this_ps.foreground_results){
			this_item[result] = this_ps.foreground_results[result][m]

			if(ps==bound_data.results.length-1){
				this_key = keys.push(result);
			}	
		}
		
		data.push(this_item);
	}

	var kill_list = [];

	for(k in keys){
		running_total = 0;
		for(p = 0; p < data.length; p++){
			running_total += Math.abs(data[p][keys[k]])
		}
		if (running_total == 0){
			kill_list.push(keys[k])
		}
		
	}

	filtered_data = [];

	for(p = 0; p < data.length; p++){
		new_item = {};
		for(i in data[p]){
			if($.inArray(i, kill_list) == -1){
				new_item[i] = data[p][i];	
			}
		}
		filtered_data.push(new_item);
	}

	filtered_keys = [];
	for(k in keys){
		this_key = keys[k];
		if($.inArray(this_key, kill_list) == -1){
			filtered_keys.push(this_key);
		}
	}


	stack_color.domain(filtered_keys);

	var series = d3.stack()
    .keys(filtered_keys)
    .offset(d3.stackOffsetDiverging)
    (filtered_data);

    var internal_margin = {top: 20, right: 30, bottom: 30, left: 60};

    d3.select("#stackedbar").select("svg").remove();
    var stack_svg = d3.select("#stackedbar").append("svg")
    		.attr("width", stack_bar_dimensions.width)
    		.attr("height", stack_bar_dimensions.height);
	    

	var stack_scale_x = d3.scaleBand()
	    .domain(data.map(function(d) { return d.ps_name; }))
	    .rangeRound([internal_margin.left, stack_bar_width - internal_margin.right])
	    .padding(0.1);

	var stack_scale_y = d3.scaleLinear()
	    .domain([d3.min(series, stackMin), d3.max(series, stackMax)]).nice()
	    .rangeRound([stack_bar_height - internal_margin.bottom, internal_margin.top]);

	var bars = stack_svg.append("g")
		.attr("class", "bars");
	var barSeries = bars.selectAll("g")
	  .data(series)

	barSeries
		.attr("y", function(d) { return stack_scale_y(d[1]); })
	    .attr("height", function(d) { return stack_scale_y(d[0]) - stack_scale_y(d[1]); });

	barSeries
	  .enter().append("g")
	  	.attr("class", "series")
	    .attr("fill", function(d) { return stack_color(d.key); })
	    //.attr("id", function(d){return d.key})
	    .attr("data-legend", function(d){ return d.key })
	  .selectAll("rect")
	  .data(function(d) { return d; })
	  .enter().append("rect")
	    .attr("width", stack_scale_x.bandwidth)
	    .attr("x", function(d) { return stack_scale_x(d.data.ps_name); })
	    .attr("y", function(d) { return stack_scale_y(d[1]); })
	    .attr("height", function(d) { return stack_scale_y(d[0]) - stack_scale_y(d[1]); })

	  .merge(barSeries)
	  	.attr("y", function(d) { return stack_scale_y(d[1]); })
	    .attr("height", function(d) { return stack_scale_y(d[0]) - stack_scale_y(d[1]); });

	barSeries
	  .exit().remove();

	stack_svg.append("g")
	    .attr("transform", "translate(0," + stack_scale_y(0) + ")")
	    .call(d3.axisBottom(stack_scale_x));

	stack_svg.append("g")
	    .attr("transform", "translate(" + internal_margin.left + ",0)")
	    .call(d3.axisLeft(stack_scale_y));

	stack_svg.append("text")
	    .attr("class", "y label")
	    .attr("id", "s_bar_yaxis_label")
	    .attr("text-anchor", "end")
	    .attr("y", 6)
	    .attr("dy", ".75em")
	    .attr("transform", "rotate(-90)")
	    .text(bound_data.settings.method_units[m]);

	stack_svg.append("g")
		.attr("class", "legendNew")
		.attr("transform", 
			"translate(" + (stack_bar_width) + "," + 0 + ")");

	function stackMin(series) {
	  return d3.min(series, function(d) { return d[0]; });
	}

	function stackMax(series) {
	  return d3.max(series, function(d) { return d[1]; });
	}

	var legend = d3.legendColor()
	  .labelFormat(d3.format(".2f"))
	  //.useClass(true)
	  .title("")
	  .titleWidth(100)
	  .scale(stack_color);
	  //.labels(function(d){console.log(d); return d.domain[d.i].split("'")[1]})
	  //.orient('horizontal');

	stack_svg.select(".legendNew")
	  .call(legend);
}
