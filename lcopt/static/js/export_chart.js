function setDPI(canvas, dpi) {
    // Set up CSS size if it's not set up already
    if (!canvas.style.width)
        canvas.style.width = canvas.width + 'px';
    if (!canvas.style.height)
        canvas.style.height = canvas.height + 'px';

    var scaleFactor = dpi / 96;
    canvas.width = Math.ceil(canvas.width * scaleFactor);
    canvas.height = Math.ceil(canvas.height * scaleFactor);
    var ctx = canvas.getContext('2d');
    ctx.scale(scaleFactor, scaleFactor);
}

var ContainerElements = ["svg","g", "foreignObject"],
        RelevantStyles ={
                         "rect":["fill","stroke","stroke-width"],
                         "path":["fill","stroke","stroke-width"],
                         "circle":["fill","stroke","stroke-width"],
                         "line":["stroke","stroke-width"],
                         "polyline":["stroke", "stroke-width", "fill", "opacity"],
                         "text":["fill","font-size","text-anchor", "font-family"],
                         "polygon":["stroke","fill"],
                         "foreignObject":["font-family", "font-size", "color"], 
                         "DIV":["font-size", "font-family", "color", "text-align"]
                     };


function read_Element(ParentNode, OrigData){
    var Children = ParentNode.childNodes;
    var OrigChildDat = OrigData.childNodes;     

    for (var cd = 0; cd < Children.length; cd++){
        var Child = Children[cd];

        var TagName = Child.tagName;
        if (ContainerElements.indexOf(TagName) != -1){
            read_Element(Child, OrigChildDat[cd]);
        } else if (TagName in RelevantStyles){
            var StyleDef = window.getComputedStyle(OrigChildDat[cd]);

            var StyleString = "";
            for (var st = 0; st < RelevantStyles[TagName].length; st++){
                StyleString += RelevantStyles[TagName][st] + ":" + StyleDef.getPropertyValue(RelevantStyles[TagName][st]) + "; ";
            }

            Child.setAttribute("style",StyleString);
        }
    }

}

function export_StyledSVG(svg_id, filename, height, width){

    var SVGElem =  document.getElementById(svg_id);

    var oDOM = SVGElem.cloneNode(true);
    read_Element(oDOM, SVGElem);

    var data = new XMLSerializer().serializeToString(oDOM);
    console.log(data);
    var imgData = 'data:image/svg+xml;base64,' + btoa(data);


    var canvas = document.getElementById('export_canvas');
    canvas.width = width;
    canvas.height = height;
    setDPI(canvas, 400);

    var context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height);
    var imageObj = new Image();
    imageObj.onload = function() {
        context.drawImage(imageObj, 0, 0);
        var dt = canvas.toDataURL('image/png');
        var download = document.createElement('a');
        download.href = dt;
        download.download = filename;
        download.click();
        download.parentNode.revoveChild(download);
      };
    imageObj.src = imgData;
}
