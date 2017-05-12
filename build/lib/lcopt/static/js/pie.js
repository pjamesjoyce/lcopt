$(document).ready(function(){
	//console.log(data)

	var cDim = {
	    height: 500,
	    width: 1024,
	    innerRadius: 0,
	    outerRadius: 125,
	    labelRadius: 175
	}

	var color = d3.scaleOrdinal(d3.schemeCategory20c)
		//.range(["#2C93E8","#838690","#F56C4E"]);

	var pie = d3.pie()
		.value(function(d) { return d.value; })(data[0]);

	var arc = d3.arc()
		.outerRadius(cDim.outerRadius)
		.innerRadius(cDim.innerRadius);
		
	var labelArc = d3.arc()
		.outerRadius(cDim.outerRadius)
		.innerRadius(cDim.outerRadius);

	var svg = d3.select("#myPie")
		.append("svg")
		.attr("width", cDim.width)
		.attr("height", cDim.height)
			.append("g")
			.attr("transform", "translate(" + cDim.width/2 + "," + cDim.height/2 +")"); // Moving the center point. 1/2 the width and 1/2 the height

	var g = svg.selectAll("arc")
		.data(pie)
		.enter().append("g")
		.attr("class", "arc");

	g.append("path")
		.attr("d", arc)
		.style("fill", function(d) { return color(d.data.label);});

	/*g.append("text")
	.attr("transform", function(d) { return "translate(" + labelArc.centroid(d) + ")"; })
	.text(function(d) { return d.data.label;})	
	.style("fill", "#000");*/


	// second version of labels
	svg.append("g")
		.attr("class", "labelName");

	var text = svg.select(".labelName").selectAll("text")
        .data(pie, function(d){return d.data.label });

    text.enter()
        .append("text")
        .attr("dy", ".35em")
        .text(function(d) {
            return d.data.label;//+": "+d.value+"%");
        })
        .attr("x",  function (d, i) {
	        centroid = arc.centroid(d);
	        midAngle = Math.atan2(centroid[1], centroid[0]);
	        x = Math.cos(midAngle) * cDim.labelRadius;
	        sign = (x > 0) ? 1 : -1
	        labelX = x + (5 * sign)
	        //console.log(labelX)
	        return labelX;
	    })
	    .attr("y",  function (d, i) {
	        centroid = arc.centroid(d);
	        midAngle = Math.atan2(centroid[1], centroid[0]);
	        y = Math.sin(midAngle) * cDim.labelRadius;
	        return y;
	    })
	    .attr('text-anchor', function (d, i) {
	        centroid = arc.centroid(d);
	        midAngle = Math.atan2(centroid[1], centroid[0]);
	        x = Math.cos(midAngle) * cDim.labelRadius;
	        return (x > 0) ? "start" : "end";
	    })
        //.attr("transform", function(d) { return "translate(" + labelArc.centroid(d) + ")"; })

    /*function midAngle(d){
        return d.startAngle + (d.endAngle - d.startAngle)/2;
    }*/


    /* --- POLYLINES ---*/

    svg.append("g")
		.attr("class", "lines");

    var polyline = svg.select(".lines").selectAll("polyline")
        .data(pie, function(d){ return d.data.label });

    polyline.enter()
        .append("polyline")
        .attr("points", function(d){

        		//figure out X
			        centroid = arc.centroid(d);
			        midAngle = Math.atan2(centroid[1], centroid[0]);
			        x = Math.cos(midAngle) * cDim.labelRadius;
			        sign = (x > 0) ? 1 : -1
			        labelX = x + (5 * sign)
			        //console.log(labelX)
			        
			    
			    // figure out Y
			        centroid = arc.centroid(d);
			        midAngle = Math.atan2(centroid[1], centroid[0]);
			        y = Math.sin(midAngle) * cDim.labelRadius;
			    
        		//console.log(arc.centroid(d))
                var pos = [labelX, y]

                console.log(d.data.label)
                console.log(midAngle)
                console.log("\n")

                //console.log(Math.PI)

                pos[0] = pos[0] * 0.85 //* (Math.abs(midAngle) < Math.PI ? 1 : -1);

                //console.log([arc.centroid(d), [labelX,y], pos])

                return [labelArc.centroid(d), pos, [labelX,y]];
            });

    polyline.exit()
        .remove();
    
    function midAngle(d){
        return d.startAngle + (d.endAngle - d.startAngle)/2;
    }

    function updatePie(data, paramset){
	console.log(paramset)
	var pie = d3.pie()
		.value(function(d) { newval = d.value * Math.random(); console.log(newval); return newval; })(data[paramset]);

	path = d3.select("#pie").selectAll("path").data(pie); // Compute the new angles
	path.attr("d", arc); // redrawing the path
	//d3.selectAll("text").data(pie).attr("transform", function(d) { return "translate(" + labelArc.centroid(d) + ")"; })
}


	

} // end of function

