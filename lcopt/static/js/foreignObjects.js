// Our dataset, based on data from 
// http://en.memory-alpha.org/wiki/Portal:Main and 
// collected by Matthew Barsalou, http://preview.tinyurl.com/af7ur8q
over_here_captain = [
    {
        division: "com",
        display_division: "Command",
        display_color: "Gold",
        casualties: 9
    },
    {
        division: "sci",
        display_division: "Sciences",
        display_color: "Blue",
        casualties: 7
    },
    {
        division: "ops",
        display_division: "Operations",        
        display_color: "Red",
        casualties: 24
    }
];

// Define the size of our chart and 
// some common layout properties
cDim = {
    height: 500,
    width: 500,
    barMargin: 10
};

/* 
 *  Chart drawing block
 *  We have to have something to label before
 *  we can label anything.
 */

// Let's precalculate the bar width. We can 
// get away with this because the data set
// is not dynamic.

// Figure out how much space is actually available 
// for the bars.
marginlessWidth = cDim.width - (cDim.barMargin * (over_here_captain.length - 1));
cDim.barWidth = marginlessWidth  / over_here_captain.length;

// Set the height and width of our SVG element
svg = d3.select("svg").attr({
    height: cDim.height,
    width: cDim.width
});

// Set the height and width of our backdrop rect
backdrop = d3.select("#backdrop").attr({
    x:0,
    y:0,
    height: cDim.height,
    width: cDim.width
});

// Store references to our two layers. 
// "Art" is our chart canvas and "labels,"
// funnily enough, is where we're going to 
// put our labels.
art = d3.select("#art");
labels = d3.select("#labels");

// Let's make a scale so the bar data fills the chart space.
// First, we need to get the maximum value of our data set
maxHeight = d3.max(over_here_captain,function(d,i){ return d.casualties });

// Now make the scale function.
barHeight = d3.scale.linear()
                .domain([0,maxHeight])
                .range([0,cDim.height]);

// Join our data to the rectangles
bars = art.selectAll("rect").data(over_here_captain);

bars.enter().append("rect")
    .attr("width",function (d,i) { return cDim.barWidth })
    .attr("height",function (d,i) { return barHeight(d.casualties) } )
    .attr("y",function(d,i) { return cDim.height - barHeight(d.casualties); })
    .attr("x",function(d,i) { return ( cDim.barWidth + cDim.barMargin ) * i; })
    .attr("class",function(d) { return d.division; });

/* 
 *  Label drawing block
 *  Place some simple labels
 */

switches = labels.selectAll("switch").data(over_here_captain)

newSwitches = switches.enter().append("switch");

// Labels for chrome, opera, safari, firefox…
// If the 'requiredFeatures' test passes, this element is displayed
foreignObjects = newSwitches.append("foreignObject")
    .attr("x",function ( d , i ) { return (cDim.barWidth + cDim.barMargin) * i } )
    .attr("y",function ( d , i ) { return cDim.height - barHeight(d.casualties) } )
    .attr("width",function ( d, i ) { return cDim.barWidth } )
    .attr("height",function ( d, i ) { return barHeight(d.casualties); } )
    .attr("requiredFeatures","http://www.w3.org/TR/SVG11/feature#Extensibility");

htmlDOMs = foreignObjects.append("xhtml:body")
    .style("margin",0)
    .style("padding",0);

htmlLabels = htmlDOMs.append("div")
    .attr("class","htmlLabel");

htmlLabels.append("p")
    .attr("class","bar-label")
    .text(function(d,i) { return d.display_division });

htmlLabels.append("p")
    .attr("class","description")
    .html(function(d,i) { 
        return "The " + d.display_division + " division, wearing the <b>" + d.display_color + "</b> uniforms, experienced " + d.casualties + " casualties."; 
    });

// If it fails, show our other labels instead.

newSwitches.append("text")
    .attr("class","label")
    .attr("x",function (d,i) { return ((cDim.barWidth + cDim.barMargin) * i) + (cDim.barWidth / 2); })
    .attr("y",function (d,i) { return cDim.height - barHeight(d.casualties) + 24; })
    .text(function(d,i) { return d.display_division });