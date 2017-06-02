console.log('hello from analysis.js');


function create_force_layout(){

var ps = $('#parameterSetChoice').val() - 1;
var m = $('#methodChoice').val() - 1;

// declare the svg container as svg, get width and height
d3.select('#force').select('svg').remove();

var svg = d3.select("#force")
	.append("svg")
	.attr("width",600)
	.attr("height",300),
    width = +svg.attr("width"),
    height = +svg.attr("height");

// this is for coloured groups, not implemented yet
var color = d3.scaleOrdinal(d3.schemeCategory20c);

// start the simulation - still need to read the docs on this
var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function(d) { return d.id; }).distance(function(d){return 50;}))
    .force("charge", d3.forceManyBody().strength(function(d){ return -50;}))
    .force("center", d3.forceCenter(width / 2, height / 2));

// read the json file, graph is the json data we get back from the file
d3.json("results.json", function(error, data) {
  // if theres an error reading the data, say so
  if (error) throw error;

  graph = data[ps][m].graph;
  console.log(graph);

  // create the links as their own group with the class 'links'
  var link = svg.append("g")
      .attr("class", "links")
    //select all the lines in the group - append the link data  
    .selectAll("line")
    .data(graph.links)
    // when a new line is added, set the stroke width to the value sent from python
    .enter().append("line")
      .attr("stroke-width", function(d) { return Math.max(1,d.value); });//Math.sqrt(d.value); });

  // create the nodes - each individual one is a group with the class 'node'
  var node = svg.selectAll('.node')
      .data(graph.nodes)

    // when a new one is created - give it the class 'node' and add the actions to it  
    .enter().append("g")
    	.attr("class", "node")
	.call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended));

	// create the circles 
    node.append("circle")
      .attr("r",  function(d) { return Math.max(1,d.radius); })
      .attr("fill", function(d) { return color(d.group); });
    
    // add the alt text  
	node.append("title")
	    .text(function(d) { return d.data.name; });

	// and the label
	node.append("text")
		.attr("dx", 12)
	    .attr("dy", ".35em")
	    .text(function(d) { return d.data.name; });


// link the data to the simulation
// the nodes get attached to the node data from the json (graph.nodes)
// the tick event is linked to the ticked function
  simulation
      .nodes(graph.nodes)
      .on("tick", ticked);
// the links get attached to the link data in the json (graph.links)
  simulation.force("link")
      .links(graph.links);
      //.distance(function(d){return 50});


// this is the function that runs every time the force model ticks
  function ticked() {
  	// the x1, y1, x2, y2 values of the lines get updated to source and target x and y s
    link
        .attr("x1", function(d) { return middle(d.source.x,0,width); })
        .attr("y1", function(d) { return middle(d.source.y,0,height); })
        .attr("x2", function(d) { return middle(d.target.x,0,width); })
        .attr("y2", function(d) { return middle(d.target.y,0,height); });

    node
    	// the nodes get updated with a transform/translate function (the original was just for circles and didnt take the label with it)
        //.attr("cx", function(d) { return d.x; })
        //.attr("cy", function(d) { return d.y; });
        .attr("transform", function(d) { return "translate(" + middle(d.x,d.radius,width-d.radius) + "," + middle(d.y,d.radius,height-d.radius) + ")";});
        //.attr("cx", function(d) { return d.x = Math.max(function(d) { return Math.max(1,d.radius); }, Math.min(width - function(d) { return Math.max(1,d.radius); }, d.x)); })
        //.attr("cy", function(d) { return d.y = Math.max(function(d) { return Math.max(1,d.radius); }, Math.min(height - function(d) { return Math.max(1,d.radius); }, d.y)); });
  }
});

function middle(a,b,c){
	return Math.max(Math.min(a,b), Math.min(Math.max(a,b),c));
}

// these are the dragging functions
// fx and fy are optional attributes of the node that fix a position
// these are set to the x/y of the node at the start of the drag
// the mouse pointer while being dragged
// and released (set to null) when the drag is over

// alphaTarget seems to tell the model whether to keep going
// setting this to 0.3 and restarting the simulation moves the nodes when the drag starts
// setting it to 0 brings the simulation to an end when the drag ends

function dragstarted(d) {
  if (!d3.event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(d) {
  d.fx = d3.event.x;
  d.fy = d3.event.y;
}

function dragended(d) {
  if (!d3.event.active) simulation.alphaTarget(0);
  d.fx = null;
  d.fy = null;
}


}//end of create_force_layout

