//set up global absolute variables
// first the size and margins

var stack_bar_margin = {top: 50, right: 250, bottom: 20, left: 75},
	stack_bar_dimensions = {height:400, width: 750}
	    stack_bar_width = stack_bar_dimensions.width - stack_bar_margin.left - stack_bar_margin.right,
	    stack_bar_height = stack_bar_dimensions.height - stack_bar_margin.top - stack_bar_margin.bottom;

var legend_dimensions = {width:150, height:stack_bar_height}

// set the ranges
var stack_xScale = d3.scaleBand()
          .range([0, stack_bar_width])
          .padding(0.1);
var stack_yScale = d3.scaleLinear()
          .range([stack_bar_height, 0]);


//set the colour scale
var stack_color = d3.scaleOrdinal(d3.schemeCategory20)

var stack_svg;

function setup_stack_bar(){

	// append the stack_svg object to the #bar div
	// append a 'group' element to 'stack_svg'
	// moves the 'group' element to the top left margin
	stack_svg = d3.select("#stackedbar").append("svg")
		.attr("id", "stackedbar_svg")
	    .attr("width", stack_bar_dimensions.width)
	    .attr("height", stack_bar_dimensions.height)
	  .append("g")
	    .attr("transform", 
	          "translate(" + stack_bar_margin.left + "," + stack_bar_margin.top + ")");

	// add the x Axis
	stack_svg.append("g")
		.attr("class", "stack_xAxis")
	    .attr("transform", "translate(0," + stack_bar_height + ")")
	    .call(d3.axisBottom(stack_xScale));
	// add the y Axis
	stack_svg.append("g")
		.attr("class", "stack_yAxis")
	    .call(d3.axisLeft(stack_yScale));  

	stack_svg.append("text")
	    .attr("class", "y label")
	    .attr("id", "s_bar_yaxis_label")
	    .attr("text-anchor", "end")
	    .attr("y", 6)
	    .attr("dy", ".75em")
	    .attr("transform", "rotate(-90)")
	    .text("");

	/*stack_svg.append("g")
		.attr("class", "legend")
		.attr("transform", 
	          "translate(" + (stack_bar_width - legend_dimensions.width) + "," + (stack_bar_height + 25) + ")");
*/
	stack_svg.append("g")
	  .attr("class", "legendNew")
	  .attr("transform", 
	  	"translate(" + (stack_bar_width) + "," + 0 + ")");

	update_stack_bar()
	update_stack_bar()

}

//here's the update function
function update_stack_bar(){
	//read the data
	//console.log('update_stack_bar')


	// process the bound data into the required form
	
	var stack_bar_data = []
	var item_names = []

	var m = $('#methodChoice').val() - 1

	for (i=0; i < bound_data.results.length; i++){
		//console.log(bound_data.results[i][m].foreground_results)
		this_stack_bar_data = []

		running_total = 0
		for (result in bound_data.results[i][m].foreground_results){
			value = bound_data.results[i][m].foreground_results[result]
			if (value != -1){
				this_stack_bar_data.push({label:result, value:value, previous:running_total})
				/*if (item_names.indexOf(result) == -1){
					item_names.push(result)
				}*/
				running_total += value
			}
		}
		//console.log(this_stack_bar_data)
		this_bar = {
			data: this_stack_bar_data,
			name: bound_data.results[i][m].ps_name,
		}
		stack_bar_data.push(this_bar)
	}
	
	to_include = []
	//for each item
	for (impact_item in bound_data.results[0][m].foreground_results){
		//set total to 0
		running_total=0
		//for each parameter set
		for (i=0; i < bound_data.results.length; i++){
			//for each method
			for(j=0; j<bound_data.settings.methods.length; j++){
				running_total += bound_data.results[i][j].foreground_results[impact_item]
			}
		}
		//console.log(impact_item, running_total)
		if (running_total != 0){
			to_include.push(impact_item)
		}
	}


	item_names = to_include

	
	//console.log(to_include)

	for (parameter_set in stack_bar_data){
		//console.log(stack_bar_data[parameter_set].data)
		new_dataset = []
		for (result_set in stack_bar_data[parameter_set].data){
			label = stack_bar_data[parameter_set].data[result_set].label
			
			if (to_include.indexOf(label) != -1){
					//console.log('adding ' + label)
					new_dataset.push(stack_bar_data[parameter_set].data[result_set])
				}
		}
		//console.log(new_dataset)
		stack_bar_data[parameter_set].data = new_dataset
	}
	
	//not currently used - might need it for the legend
	//item_names = ['item1', 'item2', 'item3']

	//var stack_bar_data = stackData
	
	var stackTotals = []
		for (x in stack_bar_data){
			////console.log(stackData[x])
			var t = 0
			for (i in stack_bar_data[x].data){
				////console.log(stackData[x].data[i])
				t+= stack_bar_data[x].data[i].value
			}
			stackTotals.push(t)
		} 

	stackMax = stackTotals.reduce(function(a, b) {
	    return Math.max(a, b);
	});

	// Scale the range of the data in the domains
	stack_xScale.domain(stack_bar_data.map(function(d) { return d.name; }));
	//console.log(stackMax)
	stack_yScale.domain([0, stackMax]);//d3.max(stack_bar_data, function(d) { return d.value; })]);
	
	stack_color.domain(item_names)

	for (n in item_names){
		//console.log(item_names[n], stack_color(item_names[n]))
	}

	// append the rectangles for the bar chart

	//console.log(stack_bar_data)


  // DATA JOIN
  // Join new data with old elements, if any
	var bars = stack_svg.selectAll(".stack_bar")
		.data(stack_bar_data);
		// UPDATE
  		// Update old elements as needed.
  	bars
  		.attr("y", function(d) { return stack_yScale(stackMax) })
  		.attr("height", function(d) { ; return stack_bar_height - stack_yScale(stackMax); })
		.attr("transform", function(d,i) { return "translate(" + stack_xScale(d.name) +"," +stack_yScale(stackMax)+ ")"; });

	// ENTER
  // Create new elements as needed.
  //
  // ENTER + UPDATE
  // After merging the entered elements with the update selection,
  // apply operations to both.

	bars.enter().append('g')
		.attr('class', 'stack_bar')
		.attr('x', function(d){ return stack_xScale(d.name)})
		.attr("y", function(d) { return stack_yScale(stackMax) })
		.attr("width", stack_xScale.bandwidth())
		.attr("height", function(d) { ; return stack_bar_height - stack_yScale(stackMax); })
		.attr("transform", function(d,i) { return "translate(" + stack_xScale(d.name) +"," +stack_yScale(stackMax)+ ")"; })

	.merge(bars)
		.attr("y", function(d) { return stack_yScale(stackMax) })
  		.attr("height", function(d) { ; return stack_bar_height - stack_yScale(stackMax); })
		.attr("transform", function(d,i) { return "translate(" + stack_xScale(d.name) +"," +stack_yScale(stackMax)+ ")"; });

// EXIT
  // Remove old elements as needed.

  	bars.exit().remove();	


// DATA JOIN
  // Join new data with old elements, if any
	var sections = bars.selectAll('.section')
		.data(function(d){ return d.data; });
		// UPDATE
  		// Update old elements as needed.
  	sections
  		.transition()
  		.attr("y", function(d) { return stack_yScale(d.value + d.previous); })
	    .attr("height", function(d) { return stack_bar_height - stack_yScale(d.value); });
	// ENTER
  // Create new elements as needed.
  //
  // ENTER + UPDATE
  // After merging the entered elements with the update selection,
  // apply operations to both.
	sections.enter().append("rect")
	    .attr("class", "section")
	    .attr("title", function(d){ return d.label})
	    .attr("data-legend", function(d){ return d.label })
	    .attr("fill", function(d){return stack_color(d.label)})
	    //.attr("x", function(d,i) { //console.log(); return stack_xScale(d.label); })
	    .attr("width", stack_xScale.bandwidth())
	    .attr("y", function(d) { return stack_yScale(d.value + d.previous); })
	    .attr("height", function(d) { return stack_bar_height - stack_yScale(d.value); })

	   .merge(sections).transition()

		  //.attr("x", function(d) { return stack_xScale(d.label); })
	      //.attr("width", stack_xScale.bandwidth())
	      .attr("y", function(d) { return stack_yScale(d.value + d.previous); })
	      .attr("height", function(d) { return stack_bar_height - stack_yScale(d.value); });

	sections.exit().remove()
		

	stack_svg.select('.stack_xAxis')
		.call(d3.axisBottom(stack_xScale));

	stack_svg.select('.stack_yAxis')
		.call(d3.axisLeft(stack_yScale));

	//console.log(bound_data.results[0][m].unit)

	stack_svg.select('#s_bar_yaxis_label').text(bound_data.results[0][m].unit)

	

/*	var legend = stack_svg.select('.legend').selectAll('.legend_item')
			.data(item_names);
		legend.selectAll("text")
			.text(function(d){return d})

			// UPDATE
  		// Update old elements as needed.
  	
  		// ENTER
  // Create new elements as needed.
  //
  // ENTER + UPDATE
  // After merging the entered elements with the update selection,
  // apply operations to both.

	legend_item = legend.enter().append('g')
		.attr('class', 'legend_item')
		.attr("transform", function(d,i) { return "translate(" + 0 +"," + (i * 10) + ")"; });

	legend_item.append("text")
		.text(function(d){return d})
		.attr("transform", function(d,i) { return "translate(" + 15 +"," + 0 + ")"; })
		.attr('dy', '8px');
	legend_item.append("rect")
		.attr("height", 10)
		.attr("width", 10)
		.attr("fill", function(d){ return stack_color(d)})
		.attr("transform", function(d,i) { return "translate(" + 0 +"," + 0 + ")"; });

	

// EXIT
  // Remove old elements as needd.

  	legend.exit().remove();	
*/

// new approach
  	

	var legend = d3.legendColor()
	  .labelFormat(d3.format(".2f"))
	  //.useClass(true)
	  .title("")
	  .titleWidth(100)
	  .scale(stack_color)
	  //.labels(function(d){console.log(d); return d.domain[d.i].split("'")[1]})
	  //.orient('horizontal');

	stack_svg.select(".legendNew")
	  .call(legend);

         

}

$(document).ready(function(){
	 $('#stacked_bar_export_button').click(function(){
    export_StyledSVG('stackedbar_svg', 'stacked_bar.png', stack_bar_dimensions.height , stack_bar_dimensions.width);
  });
})