// set the dimensions and margins of the diagram
var margin = {top: 50, right: 20, bottom: 30, left: 20},
  width = 1200 - margin.left - margin.right,
  height = 600 - margin.top - margin.bottom;

// declares a tree layout and assigns the size
var treemap = d3.tree()
  .size([width, height]);

var nodeSizes = {
  'input': [25,25],
  'intermediate' : [0,0],
  'other' : [50,75],
  'biosphere': [25,25],
}

// load the external data

function link1 (d) {
       return "M" + d.x + "," + d.y
       + "C" + (d.x + d.parent.x) / 2 + "," + d.y
       + " " + (d.x + d.parent.x) / 2 + "," + d.parent.y
       + " " + d.parent.x + "," + d.parent.y;
       }

function link2(d) {
  return "M" + d.y + "," + d.x
      + "C" + (d.y + d.parent.y) / 2 + "," + d.x
      + " " + (d.y + d.parent.y) / 2 + "," + d.parent.x
      + " " + d.parent.y + "," + d.parent.x;
}

function link3(d) {
  return "M" + d.parent.y + "," + d.parent.x
      + "C" + (d.parent.y + d.y) / 2 + "," + d.parent.x
      + " " + (d.parent.y + d.y) / 2 + "," + d.x
      + " " + d.y + "," + d.x;
}

function link4(d) {
  return "M" + d.parent.x + "," + d.parent.y
      + "C" + d.parent.x  + "," + (d.parent.y + d.y) / 2
      + " " + d.x + "," + (d.parent.y + d.y) / 2
      + " " + d.x + "," + d.y;
}

function link5(d) {
  return "M" + d.parent.x + "," + (d.parent.y + nodeSizes[d.parent.data.tag][0]/2)
      + "C" + d.parent.x  + "," + (d.parent.y + d.y) / 2
      + " " + d.x + "," + (d.parent.y + d.y) / 2
      + " " + d.x + "," + (d.y - nodeSizes[d.data.tag][0]/2);
}


function draw_tree(){
  
  var ps = $('#parameterSetChoice').val() - 1
  var m = $('#methodChoice').val() - 1

  //console.log(data[0][0].graph);
console.log(bound_data)
  var treeData = bound_data.results[ps][m].graph
  //console.log(treeData)
  //  assigns the data to a hierarchy using parent-child relationships
  var nodes = d3.hierarchy(treeData, function(d) {
    return d.technosphere;
    });



  // maps the node data to the tree layout
  nodes = treemap(nodes);

  var total_score = treeData.cum_impact

  // append the svg object to the body of the page
  // appends a 'group' element to 'svg'
  // moves the 'group' element to the top left margin


  //var svg = d3.select("body").append("svg")
  //svg.remove();
  var svg = d3.select("#simaProTree");
      svg.selectAll("*").remove();
      svg.attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom),
      g = svg.append("g")
      .attr("transform",
        "translate(" + margin.left + "," + margin.top + ")");

  // adds the links between the nodes
  var link = g.selectAll(".link")
    .data( nodes.descendants().slice(1))
    .enter().append("path")
    .attr("class", function(d){
      hasImpact = d.data.cum_impact+d.data.impact ? 'impactTrue' : 'impactFalse';
      return "link " + hasImpact
    })
    .attr("d", link5)
    .attr("stroke-width", function(d){
      //console.log(d.data.cum_impact);
      if (d.data.cum_impact){
        return Math.max(d.data.cum_impact/total_score * 10,1)
      }else{
        return 1
      }
    })

    //.attr("d", function(d) {
    //   return "M" + d.x + "," + d.y
    //   + "C" + (d.x + d.parent.x) / 2 + "," + d.y
    //   + " " + (d.x + d.parent.x) / 2 + "," + d.parent.y
    //   + " " + d.parent.x + "," + d.parent.y;
    //   });

  // adds each node as a group
  var node = g.selectAll(".node")
    .data(nodes.descendants())
    .enter().append("g")
    .attr("class", function(d) { 
      return "node" + 
      (d.technosphere ? " node--internal" : " node--leaf"); })
    .attr("transform", function(d) { 
      //console.log(nodeSizes[d.data.tag])
      return "translate(" + (d.x - nodeSizes[d.data.tag][1]/2) + "," + (d.y - nodeSizes[d.data.tag][0]/2) + ")"; 
    });

    

  // adds the circle to the node
  //node.append("circle")
  //  .attr("r", function(d){return nodeSizes[d.data.tag]})
  //  .attr("class", function(d){return d.data.tag});

  // adds a rectangle to the node
  node.append("rect")
    .attr("width", function(d){return nodeSizes[d.data.tag][1]})
    .attr("height", function(d){return nodeSizes[d.data.tag][0]})
    .attr("class", function(d){return d.data.tag});

  

  // adds the text to the node
  node.append("text")
    .attr("dy", ".35em")
    //.attr("x", function(d) { return d.data.technosphere ? (nodeSizes[d.data.tag][1]/2) :0 ; })
    .attr("x", function(d) { return nodeSizes[d.data.tag][1]/2 })
    .attr("y", function(d) { return nodeSizes[d.data.tag][0]/2 })
    .style("text-anchor", function(d) { 
    //return d.technosphere ? "end" : "start"; })
    return "middle" })
    .text(function(d) {
      if (d.data.tag == "intermediate"){
        return ''
      }else{
      var re = /'(.*)'/;
      var str = d.data.activity;
      myArray = str.match(re);
      impact = d.data.impact
      bio = d.data.biosphere[0] ? d.data.biosphere[0]['impact']:0;
      //total_impact = impact + bio + d.data.cum_impact
      total_impact = d.data.cum_impact + d.data.impact

      return myArray[1] + " [" + total_impact.toFixed(3).replace(/\.?0*$/,'') + "]" ; 
    }
    });

}


