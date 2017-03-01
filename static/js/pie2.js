$(document).ready(function(){

//console.log ('hello world')

// set up some global variables
var pieDimensions = {
	height : 300,
	width: 600,
	innerRadius : 0,
	outerRadius: 100,
	labelInset: 30,
	pointerInset: 5,
	labelRadius:125,
};

var color = d3.scaleOrdinal(d3.schemeCategory20c)

var arc = d3.arc()
	.outerRadius(pieDimensions.outerRadius)
	.innerRadius(pieDimensions.innerRadius);
	
var labelArc = d3.arc()
	.outerRadius(pieDimensions.outerRadius - pieDimensions.labelInset)
	.innerRadius(pieDimensions.outerRadius - pieDimensions.labelInset);

var pointerArc = d3.arc()
	.outerRadius(pieDimensions.outerRadius - pieDimensions.pointerInset)
	.innerRadius(pieDimensions.outerRadius - pieDimensions.pointerInset);

var svg = d3.select("#pie")
	.append("svg")
	.attr("width", pieDimensions.width)
	.attr("height", pieDimensions.height)
		.append("g")
		.attr("class", "svg_container")
		.attr("transform", "translate(" + pieDimensions.width/2 + "," + pieDimensions.height/2 +")"); // Moving the center point. 1/2 the width and 1/2 the height

//set up the pie chart for the first time
d3.json("results.json", function(error, data) {
    if (error) throw error;
    //console.log('hello from json')
    //console.log(data[0]['pie_data'])

    var ps = $('#parameterSetChoice').val() - 1

    var pie_data = data[ps]['pie_data']

    var pie = d3.pie()
		.value(function(d) { return d.value; }).sort(null)(pie_data);

	//create the containing group with class arc, creating them and adding the class
	var g = svg.selectAll(".arc")
		.data(pie)
		.enter().append("g")
		.attr("class", "arc");
	//append the path - the actual arc, with its colour attribute
	g.append("path")
		.attr("d", arc)
		.style("fill", function(d) { return color(d.data.label);})
		.each(function(d) { this._current = d; });// store the initial angles;

	//append the text label
	g.append("text")
		/*
		// This is the original (working) version
		.attr("transform", function(d) { return "translate(" + labelArc.centroid(d) + ")"; })
		.text(function(d) { return d.data.label;})	
		.style("fill", "#000")
		.each(function(d) { this._current = d; }); // store the initial angles;
		*/
		// this is the experimental version
		.attr("dy", ".35em")
		.attr("class", "itemLabel")
		.text(function(d) { return d.data.label;})
		.attr("x",  function (d, i) {
	        centroid = arc.centroid(d);
	        midAngle = Math.atan2(centroid[1], centroid[0]);
	        x = Math.cos(midAngle) * pieDimensions.labelRadius;
	        sign = (x > 0) ? 1 : -1
	        labelX = x + (5 * sign)
	        ////console.log(labelX)
	        return labelX;
	    })
	    .attr("y",  function (d, i) {
	        centroid = arc.centroid(d);
	        midAngle = Math.atan2(centroid[1], centroid[0]);
	        y = Math.sin(midAngle) * pieDimensions.labelRadius;
	        return y;
	    })
	    .attr('text-anchor', function (d, i) {
	        centroid = arc.centroid(d);
	        midAngle = Math.atan2(centroid[1], centroid[0]);
	        x = Math.cos(midAngle) * pieDimensions.labelRadius;
	        return (x > 0) ? "start" : "end";
	    })
	    .each(function(d) { this._current = d; }); // store the initial angles;

	g.append("polyline")
		.attr("points", function(d){

        		//figure out X
			        centroid = arc.centroid(d);
			        midAngle = Math.atan2(centroid[1], centroid[0]);
			        x = Math.cos(midAngle) * pieDimensions.labelRadius;
			        sign = (x > 0) ? 1 : -1
			        labelX = x + (5 * sign)

			    // figure out Y
			        centroid = arc.centroid(d);
			        midAngle = Math.atan2(centroid[1], centroid[0]);
			        y = Math.sin(midAngle) * pieDimensions.labelRadius;
			    
                var pos = [labelX, y]

                pos[0] = pos[0] * 0.85 //* (Math.abs(midAngle) < Math.PI ? 1 : -1);


                return [pointerArc.centroid(d), pos, [labelX,y]];
            })
		.each(function(d) { this._current = d; }); // store the initial angles;;


	// attempt to add a value label...

	g.append("text")
		
		// This is the original (working) version
		.attr("transform", function(d) { return "translate(" + labelArc.centroid(d) + ")"; })
		.attr("class", "valueLabel")
		.attr("text-anchor", "middle")
		.text(function(d) { return d.data.percent_label;})	
		.style("fill", "#fff")
		.each(function(d) { this._current = d; }); // store the initial angles;

	//remove on exit
	g.exit().remove();
		
		



});// end of json

// this is the midangle function used by the labels
function midAngle(d){
    return d.startAngle + (d.endAngle - d.startAngle)/2;
}

// ok lets try this
// the change function is within the scope of document.ready, so should have access to the arc variables
// we need to reload the json data, so lets try and put the good stuff in the callback...

function change2() {

	d3.json("results.json", function(error, data) {

		var ps = $('#parameterSetChoice').val() - 1
		//console.log(ps)

		var pie_data = data[ps]['pie_data']
		//console.log(pie_data)

		var pie = d3.pie()
			.value(function(d) { return d.value; }).sort(null)(pie_data)
			;
		//console.log(pie)
		// DATA JOIN
		// Join new data with old elements, if any.
		var g = svg.selectAll(".arc")
			.data(pie)

		// UPDATE
		// Update old elements as needed.
		var path = g.select("path") 
			//.data(pie)
			.transition()
				.duration(500)
				.attrTween("d", arcTween); // Smooth transition with arcTween

		//d3.selectAll("text").data(pie).attr("transform", function(d) { return "translate(" + labelArc.centroid(d) + ")"; }); // recomputing the centroid and translating the text accordingly.
		//d3.selectAll("text").data(pie).transition().duration(500).attrTween("transform", labelarcTween); // Smooth transition with labelarcTween
		var item_label = g.select(".itemLabel")
		//	.data(pie)
			.transition()
				.duration(500)
					.attrTween("x", labelTweenX)
					.attrTween("y", labelTweenY)
					.attrTween('text-anchor',labelTweenTextAnchor)
					.text(function(d) { return d.data.label;});

		var polyline = g.select("polyline")
		//	.data(pie)
			.transition()
				.duration(500)
				.attrTween("points", polylineTweenPoints);

		var value_label = g.select(".valueLabel")
		//	.data(pie)
			.transition()
				.duration(500)
				.attrTween("transform", labelarcTween)
				.text(function(d) { return d.data.percent_label;})	; // Smooth transition with labelarcTween

		
		// ENTER
		// Create new elements as needed.
		//
		// ENTER + UPDATE
		// After merging the entered elements with the update selection,
		// apply operations to both.
		var new_g = g.enter()
			.append("g")
			.attr("class", "arc")
		//append the path - the actual arc, with its colour attribute
		new_g.append("path")
			.attr("d", arc)
			.style("fill", function(d) { return color(d.data.label);})
			.each(function(d) { this._current = d; });// store the initial angles;
		
		//append the text label
		new_g.append("text")
			/*
			// This is the original (working) version
			.attr("transform", function(d) { return "translate(" + labelArc.centroid(d) + ")"; })
			.text(function(d) { return d.data.label;})	
			.style("fill", "#000")
			.each(function(d) { this._current = d; }); // store the initial angles;
			*/
			// this is the experimental version
			.attr("dy", ".35em")
			.attr("class", "itemLabel")
			.text(function(d) { return d.data.label;})
			.attr("x",  function (d, i) {
		        centroid = arc.centroid(d);
		        midAngle = Math.atan2(centroid[1], centroid[0]);
		        x = Math.cos(midAngle) * pieDimensions.labelRadius;
		        sign = (x > 0) ? 1 : -1
		        labelX = x + (5 * sign)
		        ////console.log(labelX)
		        return labelX;
		    })
		    .attr("y",  function (d, i) {
		        centroid = arc.centroid(d);
		        midAngle = Math.atan2(centroid[1], centroid[0]);
		        y = Math.sin(midAngle) * pieDimensions.labelRadius;
		        return y;
		    })
		    .attr('text-anchor', function (d, i) {
		        centroid = arc.centroid(d);
		        midAngle = Math.atan2(centroid[1], centroid[0]);
		        x = Math.cos(midAngle) * pieDimensions.labelRadius;
		        return (x > 0) ? "start" : "end";
		    })
		    .each(function(d) { this._current = d; }); // store the initial angles;

		new_g.append("polyline")
			.attr("points", function(d){

	        		//figure out X
				        centroid = arc.centroid(d);
				        midAngle = Math.atan2(centroid[1], centroid[0]);
				        x = Math.cos(midAngle) * pieDimensions.labelRadius;
				        sign = (x > 0) ? 1 : -1
				        labelX = x + (5 * sign)

				    // figure out Y
				        centroid = arc.centroid(d);
				        midAngle = Math.atan2(centroid[1], centroid[0]);
				        y = Math.sin(midAngle) * pieDimensions.labelRadius;
				    
	                var pos = [labelX, y]

	                pos[0] = pos[0] * 0.85 //* (Math.abs(midAngle) < Math.PI ? 1 : -1);


	                return [pointerArc.centroid(d), pos, [labelX,y]];
	            })
			.each(function(d) { this._current = d; }); // store the initial angles;;


		// attempt to add a value label...

		new_g.append("text")
			
			// This is the original (working) version
			.attr("transform", function(d) { return "translate(" + labelArc.centroid(d) + ")"; })
			.attr("class", "valueLabel")
			.attr("text-anchor", "middle")
			.text(function(d) { return d.data.percent_label;})	
			.style("fill", "#fff")
			.each(function(d) { this._current = d; }); // store the initial angles;

		
		//REMOVE
		g.exit().remove();

	})//end of json
}// end of change2

// these are the functions for the arc tweens in the transition

function arcTween(a) {
  var i = d3.interpolate(this._current, a);
  //console.log(i(0))
  this._current = i(0);
  return function(t) {
    return arc(i(t));
  };
}

function labelarcTween(a) {
  var i = d3.interpolate(this._current, a);
  this._current = i(0);
  return function(t) {
    return "translate(" + labelArc.centroid(i(t)) + ")";
  };
} 

function labelTweenX(a){
	var i = d3.interpolate(this._current, a);
	this._current = i(0);
	return function(t){
		centroid = arc.centroid(i(t));
        midAngle = Math.atan2(centroid[1], centroid[0]);
        x = Math.cos(midAngle) * pieDimensions.labelRadius;
        sign = (x > 0) ? 1 : -1
        labelX = x + (5 * sign)
        ////console.log(labelX)
        return labelX;
	}
}//end of labelTweenX

function labelTweenY(a){
	var i = d3.interpolate(this._current, a);
	this._current = i(0);
	return function(t){
		centroid = arc.centroid(i(t));
	    midAngle = Math.atan2(centroid[1], centroid[0]);
	    y = Math.sin(midAngle) * pieDimensions.labelRadius;
	    return y
	}
} // end of LabelTweenY

function labelTweenTextAnchor(a){
	var i = d3.interpolate(this._current, a);
	this._current = i(0);
	return function(t){
		centroid = arc.centroid(i(t));
	        midAngle = Math.atan2(centroid[1], centroid[0]);
	        x = Math.cos(midAngle) * pieDimensions.labelRadius;
	        return (x > 0) ? "start" : "end";
	}

}//end of LabelTweenTextAnchor

function polylineTweenPoints(a){
	var i = d3.interpolate(this._current, a);
	this._current = i(0);
	return function(t){
		//figure out X
	        centroid = arc.centroid(i(t));
	        midAngle = Math.atan2(centroid[1], centroid[0]);
	        x = Math.cos(midAngle) * pieDimensions.labelRadius;
	        sign = (x > 0) ? 1 : -1
	        labelX = x + (5 * sign)

	    // figure out Y
	        //centroid = arc.centroid(d);
	        midAngle = Math.atan2(centroid[1], centroid[0]);
	        y = Math.sin(midAngle) * pieDimensions.labelRadius;
	    
        var pos = [labelX, y]

        pos[0] = pos[0] * 0.85 //* (Math.abs(midAngle) < Math.PI ? 1 : -1);


        return [pointerArc.centroid(i(t)), pos, [labelX,y]];
	}

} // end of polylineTweenPoints

$('#parameterSetChoice').change(function(){
	change2()
	create_force_layout()
})

//create the initial force layout
create_force_layout()

})// end of document.ready