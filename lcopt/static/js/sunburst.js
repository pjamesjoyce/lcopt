 $(document).ready(function(){ var width = 1000,
        height = 600,
        radius = (Math.min(width, height) / 2) - 10;
  
    var formatNumber = d3.format(",.3r");
    var formatPercentage = d3.format(",.1%");

    var bound_data;


    d3.json("results.json", function(error, data) {
        if (error) throw error;
        bound_data = data;
        //console.log(bound_data);
        create_sunburst();
    });

    var legend_dimensions = {width:150, height:height};
  
    var x = d3.scaleLinear()
        .range([0, 2 * Math.PI]);
  
    var y = d3.scaleSqrt()
        .range([0, radius]);
  
    var color = d3.scaleOrdinal(d3.schemeCategory20);
  
    var partition = d3.partition();

    var break1 = 0.2, //0.5
        break2 = 0.6;
    var show1 = 0.2,
        show2 = 0.6;

    var rscale; 
    //rscale = d3.scaleLinear().domain([0, break1*radius, break2*radius, 1.0*radius]).range([0, show1*radius, show2*radius, 1.0*radius]);
    rscale = d3.scaleLinear().domain([0, radius]).range([0, radius]);

    var arc = d3.arc()
        .startAngle(function(d) { return Math.max(0, Math.min(2 * Math.PI, x(d.x0))); })
        .endAngle(function(d) { return Math.max(0, Math.min(2 * Math.PI, x(d.x1))); })
        //.innerRadius(function(d) { return  Math.max(0, y(d.y0)) * rscale(d.y/100); })
        //.outerRadius(function(d) { return Math.max(0, y(d.y1)) * rscale((d.y + d.dy)/100); });
        .innerRadius(function(d) {  return rscale(Math.max(0, y(d.y0))); })
        .outerRadius(function(d) {  return rscale(Math.max(0, y(d.y1))); });
    


  
    function create_sunburst(){
    //var svg = d3.select("body").append("svg")
      //console.log('create sunburst');
      //console.log('bound_data');
      //console.log(bound_data);
        var svg = d3.select("#sunburst")        
            .attr("width", width)
            .attr("height", height);
            svg.selectAll("*").remove();
            svg.append('circle').attr('id', 'tipfollowscursor').attr("transform", "translate(" + width * 0.05 + "," + (height * 0.2) + ")");
            svg = svg.append("g")
            .attr("transform", "translate(" + (0.45* width) + "," + (height / 2) + ")");

        //svg.append('circle').attr('id', 'tipfollowscursor')    .attr('r',5) /*  to debug */
        svg.append("g")
          .attr("class", "legendNew_sb")
          .attr("transform", 
            "translate(" + (0.35*width) + "," + (-height / 2)+ ")")
          .attr("height", height +"px");
          

        var ps = $('#parameterSetChoice').val() - 1;
        var m = $('#methodChoice').val() - 1;
      
        //d3.json("/results.json", function(error, root) {
          //if (error) throw error;
          
          root = d3.hierarchy(bound_data.results[ps][m].dropped_graph, function(d){return d.technosphere; });
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

          //root = d3.hierarchy(root.results[ps][m].dropped_graph, function(d){return d.technosphere});
          //console.log(root)
          //console.log(partition(root))
          root.sum(function(d) { if (d.biosphere[0]){bio_impact = d.biosphere[0].impact;}else{bio_impact=0;} return d.impact + bio_impact; });
          svg.selectAll("path")
              .data(partition(root).descendants())
            .enter().append("path")
              .attr("d", arc)
              .style("fill", function(d) { return color(d.data.activity); })//return color((d.children ? d : d.parent).data.activity); })
              .style("stroke", function(d){
                var startAngle = Math.max(0, Math.min(2 * Math.PI, x(d.x1))),
                    endAngle = Math.max(0, Math.min(2 * Math.PI, x(d.x0)));
                if(startAngle === Math.PI*2 &&   endAngle === Math.PI*2){
                  return "none";
                }else{
                  return "black";
                }
              })
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
        var legend = d3.legendColor()
          .labelFormat(d3.format(".2f"))
          //.useClass(true)
          .title("")
          .titleWidth(100)
          .scale(color)
          .labels(function(d){return d.domain[d.i].split("'")[1];});
          //.cellFilter(function(d){ console.log(d);return d.data.depth == 1})
          //.orient('horizontal');

        svg.select(".legendNew_sb")
          .call(legend);

      
  
      function click(d) {
        svg.transition()
            .duration(350)
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

  });
 