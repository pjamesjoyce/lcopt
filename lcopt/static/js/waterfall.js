//set up the variables


var bound_data, chartHeight, segments, stages, unit;

var waterfall = {
    margin : {left:20, right:100, top:20, bottom:20},
    yAxisWidth : 210,
    xAxisHeight : 21,
    chartWidth : 500,
    xScale : d3.scaleLinear(),
    yScale : d3.scaleBand(),
    segmentHeight : 44,
    svg : null,
    colour_plus : 'pink',//'#f0f8ff',
    colour_minus : 'lightgreen',
    labelFormat : d3.format(",.3r") //d3.format("^.2g")
};

waterfall.segmentPadding = waterfall.segmentHeight/3,

//utility functions

function sortNumber(a,b) {
    return a - b;
}


function postOrder(d, total_score, cutoff, m){
  var splice_dict = {};
  d.eachAfter(function(n){

    //fn.y += getRandomIntInclusive(0,30);

    if(n.parent){
        if (!(n.parent.data.activity in splice_dict)){
          splice_dict[n.parent.data.activity] = [];
        }
        for(i in n.parent.children){
          if(n.parent.children[i] == n){
            var item = n.parent.children[i];
            var this_impact = item.data.cum_impact[m] + item.data.impact[m];
            //console.log(n.data.activity)
            //console.log(this_impact/total_score)
            if(Math.abs(this_impact)/Math.abs(total_score) <= cutoff){
              //console.log("child " + i + " of " + n.parent.data.activity + ": " + item.data.activity + " " + item.data.cum_impact + " " + item.data.impact);
              splice_dict[n.parent.data.activity].push(parseInt(i));
            }

          }
        }
       
      }
  });
  for (i in splice_dict){
    splice_dict[i].sort(sortNumber).reverse();
  }
  //console.log(splice_dict);
  d.eachAfter(function(n){
    if(splice_dict[n.data.activity]){
      for(j in splice_dict[n.data.activity]){
        remove_index = splice_dict[n.data.activity][j];
        console.log("removing child " + remove_index + " of " + n.data.activity)
        console.log(n.children[remove_index].data.activity)
        console.log(n.children[remove_index])
        n.children.splice(remove_index,1);

        if (n.children.length == 0){
          //console.log('no children left')
          n.children = null;
        }
        //console.log(n.children);
      }
    }
  });
}

//main bit

function doSetup(ps, m){

    var treeData = bound_data.results[ps].graph;
    unit = bound_data.results[ps].units[m];
    var total_score = treeData.cum_impact[m];

    var nodes = d3.hierarchy(treeData, function(d) {
        return d.technosphere;
      });

    postOrder(nodes, total_score, 0, m);

    var depths = nodes.descendants().map(function(d){return d.depth;});

    partition = d3.partition();

    var full_data = partition(nodes).descendants();

    running_total = 0

    data = []

    for(i in full_data){
      
      this_item = full_data[i];
      this_total = 0

      if (this_item.data.secondary_tags[0] == "other"){
        
        children = this_item.descendants().filter(function(d){ return d.depth - this_item.depth == 1 });
        
        for(d in children){
        
          this_child = children[d];
          this_total += this_child.data.impact[m]

          if (this_child.data.biosphere[0]){
            bio_impact = this_child.data.biosphere[0].impact[m] 
            this_total+=bio_impact
          }
          
        }
        running_total += this_total;
        if (this_total != 0){
          this_entry = {name: this_item.data.activity.split("'")[1], value:this_total};
          data.push(this_entry);  
        }
      }
      }

    var prev_end = 0;
    segments = [];
    stages = [];

    for(d in data){
      name = data[d].name
      value =  data[d].value;
      start = prev_end;
      end = prev_end + value;
      left = Math.min(start, end);
      right = Math.max(start, end)
      this_line = {name: name, value: value, start:start, end: end, left:left, right:right}
      prev_end += value
      segments.push(this_line);
      stages.push(name)
    };
    
    //var processed = process_data(original_data);
    //segments = processed[0],
    //stages = processed[1];

    chartHeight = (waterfall.segmentHeight + waterfall.segmentPadding) * segments.length;

    var minVal = d3.min(segments, function (d) {
            return d.left;
        }),
        maxVal = d3.max(segments, function (d) {
            return d.right;
        });

    waterfall.xScale.range([0, waterfall.chartWidth]).nice();
    waterfall.xScale.domain([minVal, maxVal]);

    waterfall.yScale.domain(stages);
    waterfall.yScale.range([0, chartHeight-waterfall.segmentPadding]);
    //waterfall.yScale.range([0, chartHeight]);


    function setGraphicAttributes(seg, index) {
        seg.x = waterfall.xScale(seg.left); //Math.min(seg.startVal, seg.endVal)
        seg.y = (waterfall.segmentPadding + waterfall.segmentHeight) * index;
        seg.width = Math.abs(waterfall.xScale(seg.value) - waterfall.xScale(0));
        seg.endX = waterfall.xScale(seg.end);
        if (Math.abs(seg.value)/Math.abs(maxVal-minVal) > 0.15){
            seg.labelX = waterfall.xScale(seg.right - Math.abs(seg.value/2));
            seg.labelAnchor = "middle";
        }else{
            seg.labelX = waterfall.xScale(seg.right) + 5;
            seg.labelAnchor = "right";
        }
        
    }


    for(i=0; i<segments.length; i++){
      setGraphicAttributes(segments[i], i)
    }

}


function createSvg(parentElement) {
    d3.select(parentElement).select("svg").remove();
    waterfall.svg = d3.select(parentElement).append("svg").attr("id", "waterfall_svg");

    waterfall.svg.append("g")
        .attr("class", "chart-group")
        .attr("transform", "translate(" + (waterfall.margin.left + waterfall.yAxisWidth) + "," + waterfall.margin.top + ")");

    // setSvgSize
    waterfall.svg.attr("width", waterfall.chartWidth + waterfall.yAxisWidth + waterfall.margin.left + waterfall.margin.right);
    waterfall.svg.attr("height", waterfall.xAxisHeight + chartHeight + waterfall.margin.top + waterfall.margin.bottom);
}

function wrap(text, width) {
    text.each(function() {
        var text = d3.select(this),
            words = text.text().split(/\s+/).reverse(),
            word,
            line = [],
            lineNumber = 0,
            lineHeight = 1.1, // ems
            x = text.attr("x"),
            y = text.attr("y"),
            dy = parseFloat(text.attr("dy")),
            tspan = text.text(null).append("tspan").attr("x", x).attr("y", y).attr("dy", dy + "em");
        while (word = words.pop()) {
            line.push(word);
            tspan.text(line.join(" "));
            if (tspan.node().getComputedTextLength() > width) {
                line.pop();
                tspan.text(line.join(" "));
                line = [word];
                tspan = text.append("tspan").attr("x", x).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
            }
        }
    });
}

function drawXAxis() {
    var tickValues = [], maxTickVal;
    waterfall.svg.select(".x.axis").remove();
    if (chartHeight > 0 && segments && segments.length > 0) {
        //var xAxis = d3.svg.axis()
        //        .scale(waterfall.xScale)
        //        .orient("bottom"),
        var xAxis = d3.axisBottom(waterfall.xScale),
            minVal = d3.min(segments, function (d) {
                return d.end;
            }),
            maxVal = d3.max(segments, function (d) {
                return d.end;
            });
        var lastVal = segments[segments.length-1].end;

        if (minVal > 0) {
            minVal = 0;
        }
        else if (maxVal < 0) {
            maxVal = 0;
        }
        tickValues = [lastVal];
        if (lastVal !== 0 ) {
            addTick(0, tickValues);
        }
        if (maxVal !== 0) {
            addTick(maxVal, tickValues);
        }
        if (minVal !== 0) {
            addTick(minVal, tickValues);
        }
        maxTickVal = d3.max(tickValues);

        xAxis.tickValues(tickValues)
            .tickFormat(function (d) {
                var formatted;
                switch(d) {
                    case maxTickVal :
                        formatted =  waterfall.labelFormat(d) + " " + unit;
                        break;
                    case 0 :
                        formatted = "0";
                        break;
                    default :
                        formatted = waterfall.labelFormat(d);
                }
                return formatted;
            });
        waterfall.svg.select(".chart-group")
            .append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + chartHeight + ")")
            .call(xAxis);

    }
}

// checks to see if the tick values are too close together - very smart!
function addTick( val, tickValues) {
    if ( tickValues.every( function (tv) {
        return (Math.abs(waterfall.xScale(tv) - waterfall.xScale(val)) > 50 );
    }) ) {
        tickValues.push(val);
    }
}


function drawYAxis() {
    var padding = -15;
    waterfall.svg.select(".y.axis").remove();
    if ( chartHeight > 0 ) {
        //var yAxis = d3.svg.axis()
        //        .scale(waterfall.yScale)
        //        .orient("left")
        //        .tickSize(1);
        var yAxis = d3.axisLeft(waterfall.yScale);

        waterfall.svg.select(".chart-group")
            .append("g")
            .attr("class", "y axis")
            .attr("transform", "translate(" + padding + ",0)")
            .call(yAxis)
            .selectAll(".tick text")
            .call(wrap, waterfall.yAxisWidth - 10);
    }
}

function defineEndMarker() {
    // Define marker as red triangle
    waterfall.svg.append("defs").append("marker")
        .attr("id", "arrowhead")
        .attr("viewBox", "0 0 10 10")
        .attr("refX", 10)
        .attr("refY", 5)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M 0 0 L 10 5 L 0 10 z")
        .style("fill", d3.rgb(waterfall.colour_plus).darker(2));
}


function drawStartingLine() {
    waterfall.svg.select(".top.axis").remove();
    waterfall.svg.select(".starting-line").remove();
    if (chartHeight > 0) {
        //var xAxis = d3.svg.axis()
        //    .scale(waterfall.xScale)
        //    .orient("top")
        //    .tickValues([0])
        //    .tickFormat(d3.format("d")),
        var xAxis = d3.axisTop(waterfall.xScale)
            .tickValues([0])
            .tickFormat(d3.format("d")),
            x0 = waterfall.xScale(0),
            chartGroup = waterfall.svg.select(".chart-group");

        chartGroup.append("g")
            .attr("class", "top axis")
            .call(xAxis);

        chartGroup.append("line")
            .attr("class", "starting-line")
            .attr("x1", x0)
            .attr("y1", 0)
            .attr("x2", x0)
            .attr("y2", chartHeight);
    }

}


function drawWaterfall() {
    var chartGroup, barGroup,
        lineColor = d3.rgb(waterfall.colour_plus).darker(2);

    chartGroup = waterfall.svg.select(".chart-group");
    if (segments && segments.length > 0) {

        // Draw bars
        barGroup = chartGroup.selectAll(".bar.g")
            .data(segments);

        barGroup.exit().remove();

        var barGroupEnter = barGroup.enter().append("g").attr("class", "bar g")
        
        barGroupEnter.append("rect");
        barGroupEnter.append("text");
        barGroupEnter.append("line");

        //barGroup
        barGroup.merge(barGroupEnter).select("rect")
          //.append("rect")
            .attr("class", "bar rect")
            .attr("height", waterfall.segmentHeight)
            .attr("x", function (d) {
                return d.x;
            })
            .attr("y", function (d) {
                return d.y;
            })
            .attr("width", function (d) {
                return d.width > 0 ? d.width : 0.1;
            })
            .style("fill", function(d){return d.value>0 ? waterfall.colour_plus : waterfall.colour_minus})//color)
            .style("stroke", function(d){return d.value>0 ? d3.rgb(waterfall.colour_plus).darker(2) : d3.rgb(waterfall.colour_minus).darker(2)}); //lineColor)
        // Label bars
        //.merge(barGroup)
        //barGroup
        barGroup.merge(barGroupEnter).select("text")
        //.append("text")
            .attr("class", "bar text")
            .attr("x", function (d) {
                return d.labelX;
            })
            .style("text-anchor", function (d) {
                return d.labelAnchor;
            })
            .attr("y", function (d) {
                return d.y + (waterfall.segmentHeight / 2);
            })
            .attr("dy", ".5em")
            .text(function (d) {
                return waterfall.labelFormat(d.value);
            });
        // Connect bars
        barGroup.merge(barGroupEnter).select("line")
        //barGroup.append("line")
            .attr("class", "bar line")
            .attr("x1", function (d) {
                return d.endX;
            })
            .attr("y1", function (d) {
                return d.y + waterfall.segmentHeight;
            })
            .attr("x2", function (d) {
                return d.endX;
            })
            .attr("y2", function (d) {
                return d.y + waterfall.segmentHeight + waterfall.segmentPadding;
            })
            .style("stroke", lineColor);
    }
}

function drawEndMarker() {
    var connectors = waterfall.svg.selectAll(".bar.line");
    if (connectors.size() > 0) {
        var lastIndex = connectors.size() - 1;
        //console.log(connectors);
        connectors.filter(function(d, i) { return i === lastIndex; })
                    .attr("marker-end", "url(#arrowhead)");
    }
}


function createWaterfall(ps, m){
    doSetup(ps, m);
    createSvg(".waterfall_div");
    drawXAxis();
    drawYAxis();
    drawStartingLine();
    drawWaterfall();
    defineEndMarker();
    drawEndMarker();  
}

/*
// read the resutls from the json file, store in bound_data, then call the create sunburst function
d3.json("results.json", function(error, data) {
    if (error) throw error;
    bound_data = data;
    createWaterfall(0,0);
});

*/

$(document).ready(function(){
     $('#waterfall_export_button').click(function(){

    var waterfallWidth = waterfall.chartWidth + waterfall.yAxisWidth + waterfall.margin.left + waterfall.margin.right;
    var waterfallHeight = waterfall.xAxisHeight + chartHeight + waterfall.margin.top + waterfall.margin.bottom;
    export_StyledSVG('waterfall_svg', 'waterfall.png', waterfallHeight, waterfallWidth);
  });
})
