
function mass_flow(ps){

  console.log(bound_data);

  var units = "kg";

  // set the dimensions and margins of the graph
  var margin = {top: 10, right: 10, bottom: 200, left: 10},
      full_width = 1200,
      full_height = 500,
      width = full_width - margin.left - margin.right,
      height = full_height - margin.top - margin.bottom;

  // format variables
  var formatNumber = d3.format(",.2f"),    // zero decimal places
      format = function(d) { return formatNumber(d) + " " + units; };
      color = d3.scaleOrdinal(d3.schemeCategory20);

  
  var svg = d3.select("#mass_flow_svg")
              .attr("width", width + margin.left + margin.right)
              .attr("height", height + margin.top + margin.bottom);
      
      svg.selectAll("*").remove();

    svg.append("g")
      .attr("transform", 
            "translate(" + margin.left + "," + margin.top + ")");

  // Set the sankey diagram properties
  var sankey = d3.sankey()
      .nodeWidth(6)
      .nodePadding(4)
      .size([width, height]);

  var path = sankey.link();

  // load the data
  var data = bound_data.results[ps][0].mass_flow;
  console.log(data);

  var hierarchy = d3.hierarchy(data, function(d) {
      return d.technosphere;
  });

  console.log(hierarchy);

  d3.tree(hierarchy);

  var raw_nodes = hierarchy.descendants();

  var raw_links = hierarchy.links();

  var nodes = [],
      i = 0,
      node_dict = {};

  raw_nodes.forEach(function(item){



      if(item.data.is_mass && item.data.amount !== 0){
          id = item.data.activity + "_" + item.depth + "_" + item.height;
          tag = item.data.tag;
          activity = item.data.activity;
          if (!item.parent){
            tag = "final";
            activity = "Functional unit";
          }
          nodes.push({"node": i, "name": activity, "tag": tag});
          node_dict[id] = i;
          i++;
      }
      
  });

  var links = [];

  raw_links.forEach(function(item){

      if (item.source.data.is_mass && item.target.data.is_mass && item.target.data.amount !== 0){


          value = item.target.data.amount;

          var flip = false;

          if(value < 0){
              value = Math.abs(value);
              flip = true;
          }

          source_id = item.source.data.activity + "_" + item.source.depth + "_" + item.source.height;
          target_id = item.target.data.activity + "_" + item.target.depth + "_" + item.target.height;
          if(flip){
              source = node_dict[source_id];
              target = node_dict[target_id];
          }else{
              source = node_dict[target_id];
              target = node_dict[source_id];
          }
          
          links.push({
              "source": source,
              "target": target,
              "value": value
          });
      }
  });

  //console.log(nodes);
  //console.log(raw_nodes);
  //console.log(nodes);
  //console.log(node_dict);
  //console.log(raw_links);
  //console.log(links);

  graph = {nodes:nodes, links:links};

sankey
    .nodes(graph.nodes)
    .links(graph.links)
    .layout(2);

// add in the links
var link = svg.append("g").selectAll(".mf_link")
    .data(graph.links)
  .enter().append("path")
    .attr("class", "mf_link")
    .attr("d", path)
    .style("stroke-width", function(d) { return Math.max(1, d.dy); })
    .sort(function(a, b) { return b.dy - a.dy; });

// add the link titles
link.append("title")
      .text(function(d) {
          return d.source.name + " → " + 
              d.target.name + "\n" + format(d.value); });

// add in the nodes
var node = svg.append("g").selectAll(".mf_node")
    .data(graph.nodes)
  .enter().append("g")
    .attr("class", function(d){return "mf_node tag_" + d.tag;})
    .attr("transform", function(d) { 
        return "translate(" + d.x + "," + d.y + ")"; })
    .call(d3.drag()
      .subject(function(d) {
        return d;
      })
      .on("start", function() {
        this.parentNode.appendChild(this);
      })
      .on("drag", dragmove));

// add the rectangles for the nodes
node.append("rect")
    .attr("height", function(d) { return d.dy; })
    .attr("width", sankey.nodeWidth())
    .style("fill", function(d) { 
        return d.color = color(d.name.replace(/ .*/, "")); })
    .style("stroke", function(d) { 
        return d3.rgb(d.color).darker(2); })
  .append("title")
    .text(function(d) { 
        return d.name + "\n" + format(d.value); });

// add in the title for the nodes
node.append("text")
    .attr("x", -6)
    .attr("y", function(d) { return d.dy / 2; })
    .attr("dy", ".35em")
    .attr("text-anchor", "end")
    .attr("transform", null)
    .text(function(d) { return d.name + " (" + format(d.value) + ")"; })
  .filter(function(d) { return d.x < width / 2; })
    .attr("x", 6 + sankey.nodeWidth())
    .attr("text-anchor", "start");

// the function for moving the nodes
function dragmove(d) {
  d3.select(this)
    .attr("transform", 
          "translate(" 
             + (d.x = Math.max(0, Math.min(width - d.dx, d3.event.x))) + "," 
             + (d.y = Math.max(
                0, Math.min(height + margin.bottom - d.dy, d3.event.y))
               ) + ")");
  sankey.relayout();
  link.attr("d", path);
}
}
$(document).ready(function(){
  $('#mass_flow_export_button').click(function(){

    var margin = {top: 10, right: 10, bottom: 200, left: 10},
        full_width = 1200,
        full_height = 500,
        width = full_width - margin.left - margin.right,
        height = full_height - margin.top - margin.bottom;

    var ps = $('#parameterSetChoice option:selected').text();

    export_StyledSVG('mass_flow_svg', 'mass_flow_' + ps + '.png', full_height, full_width);
  });

});
