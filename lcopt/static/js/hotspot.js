 $(document).ready(function(){ 

    // set the dimensions of the chart
    var width = 1300,
        height = 1000,
        pie_diameter = 600,
        pie_margin = 50,
        radius = pie_diameter/2; 

    // and the legend
    var legend_dimensions = {width:150, height:height};

    // set the x and y scales  
    var x = d3.scaleLinear()
        .range([0, 2 * Math.PI]);
  
    var y = d3.scaleSqrt()
        .range([0, radius]);
  
    // set the colour scales
    // var color = d3.scaleOrdinal(d3.schemeCategory20);

    var color30_default = ["#1abd44", "#923bc1", "#94d957", "#317dff", "#4f9100", "#d28aff", "#006f0c", "#a20083", "#00bf7a", "#c60040",
                           "#49dcc4", "#ed373b", "#01a6ed", "#d44805", "#469aff", "#be6b00", "#62d3ff", "#9f1d3a", "#009c90", "#ff5fa0",
                           "#bfcf5f", "#55498a", "#ffad58", "#8c3063", "#abd19c", "#ffa2e2", "#784810", "#fab87f", "#936343", "#d38a89"];
    var color30_fancy =  ["#80deb3", "#f794a4", "#52e4e3", "#f9a089", "#5ef1ff", "#d699bf", "#8cffeb", "#dab8ff", "#e0f3a6", "#97a9f1",
                          "#e9e597", "#71b6f9", "#ffd9a0", "#41d1fc", "#d79d98", "#2dd4e5", "#ffceed", "#81cf9b", "#bea0d7", "#e0ffc4",
                          "#72b4d8", "#93b67c", "#c4e1ff", "#8ab59a", "#ffd1d4", "#58bbb6", "#f7ffe2", "#97aec8", "#baffe7", "#aef5ff"];
    var color30_intense = ["#008da0", "#ff6c2a", "#7b4af8", "#cbc900", "#cf40f3", "#00b040", "#6f00a2", "#e3c53b", "#0044a2", "#ff9517", 
                           "#8495ff", "#bd9e00", "#ff66ef", "#576c00", "#e601a2", "#78d6ca", "#ff455a", "#0176c6", "#b90034", "#aad0a1",
                           "#520055", "#e1bbda", "#731000", "#c386ff", "#431911", "#b3b8ff", "#8a004b", "#006590", "#ff5fae", "#321b48"];

    var color30_brewer = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33", "#a65628", "#f781bf", "#999999", "#8dd3c7",
                          "#ffffb3", "#bebada", "#fb8072", "#80b1d3", "#fdb462", "#b3de69", "#fccde5", "#d9d9d9]", "#fbb4ae", "#b3cde3",
                          "#ccebc5", "#decbe4", "#fed9a6", "#ffffcc", "#e5d8bd", "#fddaec", "#f2f2f2", "#a6cee3", "#1f78b4", "#b2df8a"];

    var color30_d3v4 = ["#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c", "#98df8a", "#d62728", "#ff9896", "#9467bd", "#c5b0d5", 
                        "#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#7f7f7f", "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5",
                        "#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33", "#a65628", "#f781bf", "#999999", "#8dd3c7"];

    var color = d3.scaleOrdinal();
    color.range(color30_d3v4);
    
  
    // what is partition?  
    var partition = d3.partition();

    // set the breaks which determine the size of the outer rings
    // break 1 and 2 are the breaks in the scale, show 1 and 2 are how far along the scale those breaks appear
    var break1 = 0.5,
        break2 = 0.6;
    var show1 = 0.2,
        show2 = 0.6;

    // create the radius scale based on the breaks above
    var rscale; 
    rscale = d3.scaleLinear().domain([0, break1*radius, break2*radius, 1.0*radius]).range([0, show1*radius, show2*radius, 1.0*radius]);
    
    // create the format functions for the labels
    var formatNumber = d3.format(",.3r"),
        formatPercentage = d3.format(",.1%");

    // create a varable for the data from the json file
    var bound_data;

    var current_level = 0;

    // read the resutls from the json file, store in bound_data, then call the create sunburst function
    d3.json("results.json", function(error, data) {
        if (error) throw error;
        bound_data = data;
        //console.log(bound_data);
        create_sunburst();
    });

    // create the arc function for the pie chart
    var arc = d3.arc()
        .startAngle(function(d) { return Math.max(0, Math.min(2 * Math.PI, x(d.x0))); })
        .endAngle(function(d) { return Math.max(0, Math.min(2 * Math.PI, x(d.x1))); })
        .innerRadius(function(d) {  return rscale(Math.max(0, y(d.y0))); })
        .outerRadius(function(d) {  return rscale(Math.max(0, y(d.y1))); });
    
    function create_sunburst(){
        // create the svg container in the DOM
        var svg = d3.select("#sunburst")        
            .attr("width", width)
            .attr("height", height);
            svg.selectAll("*").remove();
            // this is where the tooltip will show up in the figure
            svg.append('circle').attr('id', 'tipfollowscursor').attr("transform", "translate(" + pie_diameter * 0.05 + "," + (pie_diameter * 0.2) + ")");
            
            // this is the g where the chart will be added
            svg = svg.append("g")
            .attr("transform", "translate(" + (radius + pie_margin) + "," + (radius + pie_margin) + ")");

        //svg.append('circle').attr('id', 'tipfollowscursor')    .attr('r',5) /*  to debug */

        // this is the g where the legend will go
        svg.append("g")
          .attr("class", "legendNew_sb")
          .attr("id", "legend_box")
          .attr("transform", 
            "translate(" + (radius + pie_margin*2) + "," + (-radius)+ ")")
          .attr("height", height +"px");
          
        // these are the variables to pick the result set to plot
        var ps = $('#parameterSetChoice').val() - 1;
        var m = $('#methodChoice').val() - 1;
      
        // set the root of the data  
        root = d3.hierarchy(bound_data.results[ps][m].dropped_graph, function(d){return d.technosphere; });
        //console.log(root)
        unit = bound_data.results[ps][m].unit;

        /* Initialize tooltip */
        tip = d3.tip().attr('class', 'd3-tip').html(function(d) { 
            message = "<span class=\"tip_title\">";
            name = d.data.activity.split("'")[1];
            value = formatNumber(d.value);

            message += name;
            message += "</span><br><span class=\"tip_value\">";
            message += value;
            message += " " + unit;
            message += "</span>";
            if (d.parent){
              percent = formatPercentage(d.value/d.parent.value);
              parent = d.parent.data.activity.split("'")[1];
              message += "<br><span class=\"tip_detail\">";
              message += percent;
              message += " of ";
              message += parent;
              message += "</span>";
            }

            total_percent = formatPercentage(d.value/bound_data.results[ps][m].score);

            message += "<br><span class=\"tip_total\">";
            message += total_percent;
            message += " of total</span>";



            return message;
        });

          /* Invoke the tip in the context of your visualization */
          svg.call(tip);

          root.sum(function(d) { if (d.biosphere[0]){bio_impact = d.biosphere[0].impact;}else{bio_impact=0;} return d.impact + bio_impact; });

          var full_data = partition(root).descendants();
          var filtered_data = full_data.filter(function(x){return x.x0 != x.x1});
          // partition changes the tree into a list of objects
          svg.selectAll("path")
              .data(filtered_data)
            .enter().append("path")
              .attr("d", arc)
              .style("fill", function(d) {
                activity_name = d.data.activity.split("'")[1];
                return color(d.depth + ". " + activity_name ) 
               })//return color(d.data.activity); })//return color((d.children ? d : d.parent).data.activity); })
              /*.style("stroke", function(d){
                var startAngle = Math.max(0, Math.min(2 * Math.PI, x(d.x1))),
                    endAngle = Math.max(0, Math.min(2 * Math.PI, x(d.x0)));
                if(startAngle === Math.PI*2 &&   endAngle === Math.PI*2){
                  return "none";
                }else{
                  return "black";
                }
              })*/
              .style("stroke", "black")
              .attr("data-legend", function(d){ return d ;})
              .on("click", click)
              .on('mouseover', mouseover)
              /*.on('mouseover', function (d) {
                  var target = d3.select('#tipfollowscursor')
                      .attr('cx', d3.event.offsetX)
                      .attr('cy', d3.event.offsetY) // 5 pixels above the cursor
                      .node();
                  tip.show(d, target);
              })*/
              .on('mousemove', mouseover)
              .on('mouseout', tip.hide);
            //.append("title")
              //.text(function(d) { return d.data.activity + "\n" + formatNumber(d.value); });
        //});
        var current_level = 0;
        var my_descendants = root.descendants();
        var me = root.data.activity;

        var legend = d3.legendColor()
          .labelFormat(d3.format(".2f"))
          .title("")
          .titleWidth(100)
          .scale(color)
          .labels(function(d){return d.domain[d.i];})
          .cellFilter(function(d){
            var legend_items = my_descendants.filter(function(x){return x.x0 != x.x1;});
            var my_descendant_names = legend_items.map(function(x){return x.depth + ". " + x.data.activity.split("'")[1];});
            return $.inArray(d.data, my_descendant_names) >= 0;
          });

        svg.select(".legendNew_sb")
          .call(legend);
        legend_levels();

      
      function legend_levels(){
        $legenditems = $("#legend_box > g > g");

        var last_item_level = -1;
        var downshift = 0;
        var shift = 30;

        var legenditems_d3 = d3.select('#legend_box').selectAll('.cell');

        legenditems_d3.each(function(d,i){
          
          var this_item = d3.select(this);


          bits = this_item.select("text")
            //.attr("style", "font-family: 'Muli', sans-serif; font-size: 75%;")
            .html().split(".");
          
          var item_level = parseInt(bits[0]);
          
          var translation_bits = this_item.attr("transform").split(/\(|, |\)/);

          if(item_level != last_item_level){
            //console.log("new level at " + bits[1]);
            downshift += shift;
            new_translation = translation_bits[0] + "(" + translation_bits[1] + ", " + (parseInt(translation_bits[2]) + downshift) + ")";
            title_translation = "translate(0,-5)";
            this_item.attr("transform", new_translation);

            var text_g = this_item.append("text")
              .text('Level ' + (item_level + 1))
              .attr("transform", title_translation)
              //.attr("style", "fill:grey; font-family: 'Muli', sans-serif; font-size: 75%;")
              .attr("class", "label legend_subtitle");

          }else{
            new_translation = translation_bits[0] + "(" + translation_bits[1] + ", " + (parseInt(translation_bits[2]) + downshift) + ")";
            this_item.attr("transform", new_translation);
          }

          last_item_level = item_level;

          this_item.select("text").html(bits[1]);

        });

      }

      function click(d) {
                
        my_descendants = d.descendants();
        
        var legendbox = svg.select(".legendNew_sb");
        
        legendbox.selectAll("*").remove();
        legendbox.call(legend);
        legend_levels();

        svg.transition()
            .duration(350)
            .ease(d3.easeExp)
            .tween("scale", function() {
              var xd = d3.interpolate(x.domain(), [d.x0, d.x1]),
                  yd = d3.interpolate(y.domain(), [d.y0, 1]),
                  yr = d3.interpolate(y.range(), [d.y0 ? 20 : 0, radius]);
              return function(t) { x.domain(xd(t)); y.domain(yd(t)).range(yr(t)); };
            })
          .selectAll("path")
            .attrTween("d", function(d) { return function() { return arc(d); }; })
            .styleTween("stroke", function() { return fix_strokes; })
            //.style("stroke", "black")
            .on("end", fix_strokes);
      }

      function reset(){
        my_descendants = root.descendants();
        
        var legendbox = svg.select(".legendNew_sb");
        
        legendbox.selectAll("*").remove();
        legendbox.call(legend);
        legend_levels();

        svg.transition()
            .duration(1000)
            .ease(d3.easeExp)
            .tween("scale", function() {
              var xd = d3.interpolate(x.domain(), [0, 1]),
                  yd = d3.interpolate(y.domain(), [0, 1]),
                  yr = d3.interpolate(y.range(), [0, radius]);
              return function(t) { x.domain(xd(t)); y.domain(yd(t)).range(yr(t)); };
            })
          .selectAll("path")
            .attrTween("d", function(d) { return function() { return arc(d); }; })
            .styleTween("stroke", function() { return fix_strokes; })
            //.style("stroke", "black")
            .on("end", fix_strokes);
      }



      function strokeTween(d){
        //console.log(d);

        return "green";
      }

      function fix_strokes(d){
        
        svg.selectAll("path")
            .style("stroke", function(d){
                  var startAngle = Math.max(0, Math.min(2 * Math.PI, x(d.x1))),
                      endAngle = Math.max(0, Math.min(2 * Math.PI, x(d.x0)));
                  if(startAngle === endAngle){
                    return "none";
                  }else{
                    //console.log(startAngle, endAngle)
                    return "black";
                  }
                });
      }

      function mouseover(d){
        
        var target = d3.select('#tipfollowscursor')
            //.attr('cx', d3.event.offsetX)
            //.attr('cy', d3.event.offsetY + 100) // 5 pixels above the cursor

            .node();

       
        my_tip = tip.show(d, target);
        
      }
      function mouseout(d){
        
        tip.hide();
      }
    
      d3.select(self.frameElement).style("height", height + "px");
      reset();

  }

  //create_sunburst()

  $('#parameterSetChoice').change(function(){
    create_sunburst();
    //create_force_layout()
  });

  $('#methodChoice').change(function(){
    create_sunburst();
    //create_force_layout()
  });

  $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
    var target = $(e.target).attr("href"); // activated tab
    if (target=="#tab-hotspots"){
      create_sunburst();
    }
    else if(target=="#tab-table"){
      update_table();
    }
    else if(target=="#tab-stackedbar"){
      update_stack_bar();
    }
  });

  $('.radio').change(function(){
    if($("#radio_small").prop("checked") === true){
      //console.log("small");
      break1 = 0.4;
      break2 = 0.6;
      show1 = 0.1;
      show2 = 0.9;
    }else if($("#radio_large").prop("checked") === true){
      //console.log("large");
      break1 = 0.5;
      break2 = 0.6;
      show1 = 0.2;
      show2 = 0.6;
    }else if($("#radio_tiny").prop("checked") === true){
      //console.log("tiny");
      break1 = 0.4;
      break2 = 0.6;
      show1 = 0.1;
      show2 = 0.98;
    }else{
      //console.log("hidden");
      break1 = 0.4;
      break2 = 0.6;
      show1 = 0.1;
      show2 = 1;
    }
    rscale = d3.scaleLinear().domain([0, break1*radius, break2*radius, 1.0*radius]).range([0, show1*radius, show2*radius, 1.0*radius]);
    create_sunburst();
  });

  

 
  $('#hotspot_export_button').click(function(){

    var ps = $('#parameterSetChoice option:selected').text();
    var m = $('#methodChoice option:selected').text();

    export_StyledSVG('sunburst', 'hotspot_chart_' + ps + '_' + m + '.png', height, width);
  });



  });
 