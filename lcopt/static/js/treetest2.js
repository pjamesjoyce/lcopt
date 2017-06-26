// set the dimensions and margins of the diagram
var margin = {top: 50, right: 20, bottom: 100, left: 20},
  level_width = 200;
  level_height = 120;
  //height = 800 - margin.top - margin.bottom;

var max_stroke_width = 20;

var height, width;

var nodeSizes = {
  'input': [50,85],
  'intermediate' : [0,0],
  'other' : [75,120],
  'biosphere': [50,85],
};

//var cutoff = 0.01;

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

function elbow(d) {
  return "M" + d.parent.x + "," + d.parent.y
      + "v" + (d.y - d.parent.y)*0.6
      + "H" + d.x
      + "V" + d.y;
}

function collapse(d) {
    ////console.log(d.cum_impact)
    if (d.children) {
      d.children.forEach(collapse)
    }
    if (d.data.cum_impact == 0) {
      
      d._children = d.children;
      //d.technosphere.forEach(collapse);
      d.children = null;
    }
    if(d.data.cum_impact == 0 && d.data.impact == 0){
      //console.log(d.data.activity + " blank input")
      //console.log(d)

    }
  }

function sortNumber(a,b) {
    return a - b;
}

function postOrder(d, total_score, cutoff){
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
            var this_impact = item.data.cum_impact + item.data.impact;
            //console.log(n.data.activity)
            //console.log(this_impact/total_score)
            if(this_impact/total_score <= cutoff){
              ////console.log("child " + i + " of " + n.parent.data.activity + ": " + item.data.activity + " " + item.data.cum_impact + " " + item.data.impact);
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
        //console.log("removing child " + remove_index + " of " + n.data.activity)
        //console.log(n.children[remove_index].data.activity)
        //console.log(n.children[remove_index])
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


function count_occurences(item, array){
  var count = 0;
  for(var i=0; i<array.length; i++){
    if(array[i] == item){
      count++;
    }
  }
  return count;
}


function draw_tree(){
  
  var ps = $('#parameterSetChoice').val() - 1;
  var m = $('#methodChoice').val() - 1;
  var cutoff = $('#cutoff').val() / 100;
  //console.log(cutoff)

  ////console.log(data[0][0].graph);
  //console.log(bound_data);
  var treeData = bound_data.results[ps][m].graph;
  var method_unit = bound_data.results[ps][m].unit;
  var total_score = treeData.cum_impact;
  ////console.log(treeData)
  //  assigns the data to a hierarchy using parent-child relationships
  var nodes = d3.hierarchy(treeData, function(d) {
    return d.technosphere;
    });
  //console.log(treeData);
  //console.log(nodes);

  ////console.log(nodes)
  postOrder(nodes, total_score, cutoff);
  ////console.log(nodes)

  var depths = nodes.descendants().map(function(d){return d.depth;});
  //console.log(depths);
  var max_depth = Math.max(...depths) + 1;

  var widths = [];

  for(i=0; i<max_depth; i++){
    //console.log(i, max_depth)
   widths.push(count_occurences(i,depths));
  }

  //console.log(widths)
  var max_width = Math.max(...widths);

  height = level_height * max_depth - margin.top - margin.bottom;
  width = level_width * max_width  - margin.left - margin.right;

  // declares a tree layout and assigns the size
  var treemap = d3.tree()
    .size([width, height]);
  // maps the node data to the tree layout
  console.log(nodes);
  nodes = treemap(nodes);
  //console.log(nodes)

  /*var k = 0
  nodes.each(function(n){
    n.y -= k;
    k += 10;
  })*/

  

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
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // adds the links between the nodes
  var link = g.selectAll(".link")
    .data( nodes.descendants().slice(1))
    .enter().append("path")
    .attr("class", function(d){
      hasImpact = d.data.cum_impact+d.data.impact ? 'impactTrue' : 'impactFalse';
      return "link " + hasImpact;
    })
    .attr("d", elbow)
    .attr("stroke-width", function(d){
      ////console.log(d.data.cum_impact);
      ////console.log(d.data.activity, d.data.impact, d.data.cum_impact);
      if (d.data.cum_impact){
        return Math.max(d.data.cum_impact/total_score * max_stroke_width,1);
      }else if(d.data.impact){
        return Math.max(d.data.impact/total_score * max_stroke_width,1);
      }else{
        return 1;
      }
    });

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
      ////console.log(d)
      return "translate(" + (d.x - nodeSizes[d.data.tag][1]/2) + "," + (d.y - nodeSizes[d.data.tag][0]/2) + ")"; 
    });

    

  // adds the circle to the node
  //node.append("circle")
  //  .attr("r", function(d){return nodeSizes[d.data.tag]})
  //  .attr("class", function(d){return d.data.tag});

  // adds a rectangle to the node
  node.append("rect")
    .attr("width", function(d){return nodeSizes[d.data.tag][1];})
    .attr("height", function(d){return nodeSizes[d.data.tag][0];})
    .attr("class", function(d){return d.data.tag;});

  

  // adds the text to the node
  node.append("text")
    .attr("dy", ".35em")
    //.attr("x", function(d) { return d.data.technosphere ? (nodeSizes[d.data.tag][1]/2) :0 ; })
    .attr("class", function(d){
      if(d.data.tag == "other"){
        return "name_label";
      }else{
        return "input_label";
      }
    })
    .attr("style", "font-weight: bold;")
    .attr("x", function(d) {
        return nodeSizes[d.data.tag][1]*0.5 ;
    })
    .attr("y", function(d) {
        var this_type = 'other';//d.data.tag;
        if(this_type == 'other'){
          return nodeSizes[d.data.tag][0]*0.5 ;  
        }else{
          return nodeSizes[d.data.tag][0] * 1.5;
        }
    })
    .style("text-anchor", function(d) { 
    //return d.technosphere ? "end" : "start"; })
    return "middle" ;})
    .text(function(d) {
      if (d.data.tag == "intermediate"){
        return '';
      }else{
      var re = /'(.*)'/;
      var str = d.data.activity;
      myArray = str.match(re);
      impact = d.data.impact;
      bio = d.data.biosphere[0] ? d.data.biosphere[0].impact:0;
      //total_impact = impact + bio + d.data.cum_impact
      total_impact = d.data.cum_impact + d.data.impact;

      return myArray[1] //+ " [" + total_impact.toFixed(3).replace(/\.?0*$/,'') + "]" ; 
    }
    });

  node.append("text")
    .attr("dy", ".35em")
    //.attr("x", function(d) { return d.data.technosphere ? (nodeSizes[d.data.tag][1]/2) :0 ; })
    .attr("x", function(d) {
        return nodeSizes[d.data.tag][1]*0.5 ;
    })
    .attr("y", function(d) {
        var this_type = 'other';//d.data.tag;
        if(this_type == 'other'){
          return nodeSizes[d.data.tag][0]*0.8 ;  
        }else{
          return nodeSizes[d.data.tag][0] * 2.2;
        }
    })
    .attr('class', function(d){
      if(d.data.tag == 'other'){
        return 'process_amount';
      }else{
        return 'input_amount';
      }
    })
    .style("text-anchor", function(d) { 
    //return d.technosphere ? "end" : "start"; })
    return "middle" ;})
    .text(function(d) {
      if (d.data.tag == "intermediate"){
        return '';
      }else{
      var re = /'(.*)'/;
      var str = d.data.activity;
      myArray = str.match(re);
      impact = d.data.impact;
      bio = d.data.biosphere[0] ? d.data.biosphere[0].impact:0;
      //total_impact = impact + bio + d.data.cum_impact
      total_impact = d.data.cum_impact + d.data.impact;

      //replace is for getting rif of trailing zeros
      return  total_impact.toPrecision(2).replace(/\.?0*$/,'') + " " + method_unit; 
    }
    });
    var wrap_height = nodeSizes.other[0],
        wrap_width = nodeSizes.other[1];

    var wrap = d3.textwrap().bounds({height: wrap_height, width: wrap_width}).padding(10);

    var wrap_height_i = nodeSizes.input[0],
        wrap_width_i = nodeSizes.input[1];

    var wrap_input = d3.textwrap().bounds({height: wrap_height_i, width: wrap_width_i}).padding(5);

    d3.selectAll('.name_label').call(wrap);

    d3.selectAll('.input_label').call(wrap_input);

    


}

$(document).ready(function(){

  ////console.log ('hello world')
  $('#tree_export_button').click(function(){
    export_StyledSVG('simaProTree', 'tree.png', height + margin.top + margin.bottom, width);
  });

});


