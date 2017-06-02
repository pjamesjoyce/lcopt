! function(t, e) {
    "object" == typeof exports && "undefined" != typeof module ? e(exports, require("d3-selection")) : "function" == typeof define && define.amd ? define(["exports", "d3-selection"], e) : e(t.d3 = t.d3 || {}, t.d3)
}(this, function(t, e) {
    "use strict";
    var n, o, r, i, d, u, p, a;
    n = "undefined" == typeof SVGForeignObjectElement ? "tspans" : "foreignobject", o = function(t) {
        var n, o;
        return o = "function" == typeof t, "object" != typeof t || t.nodeType ? !!(t instanceof e.selection || t.nodeType || o || n) || (console.error("invalid bounds specified for text wrapping"), !1) : !(!t.height || !t.width) || (console.error("text wrapping bounds must specify height and width"), !1)
    }, r = function(t) {
        var e, n, o, r;
        for (e = ["height", "width"], "function" == typeof t ? n = t() : t.nodeType ? n = t.getBoundingClientRect() : "object" == typeof t && (n = t), o = Object.create(null), r = 0; r < e.length; r++) o[e[r]] = n[e[r]];
        return o
    }, i = function(t) {
        var e;
        return "function" == typeof t ? e = t() : "number" == typeof t ? e = t : "undefined" == typeof t && (e = 0), "number" == typeof e ? e : void console.error("padding could not be converted into a number")
    }, d = function(t, e) {
        var n;
        return n = {
            height: t.height - 2 * e,
            width: t.width - 2 * e
        }
    }, u = function(t, e) {
        var n;
        return n = d(r(t), i(e))
    }, p = {}, p.foreignobject = function(t, n, o) {
        var r, i, d, u;
        //console.log(t.attr('class'))
        return r = t.text(), i = e.select(t.node().parentNode), t.remove(), d = i.append("foreignObject"), d.attr("requiredFeatures", "http://www.w3.org/TR/SVG11/feature#Extensibility").attr("width", n.width).attr("height", n.height), "number" == typeof o && d.attr("x", o).attr("y", o), u = d.append("xhtml:div"), u.style("height", n.height).style("width", n.width).attr("class",t.attr("class")).html(r), u
    }, p.tspans = function(t, e, n) {
        var o, r, i, d, u, p;
        for (o = t.text().split(" ").reverse(), t.text(""), u = t.append("tspan"), u.attr("dx", 0).attr("dy", 0), d = 0; o.length > 0;) r = o.pop(), u.text(u.text() + " " + r), i = u.node().getComputedTextLength() || 0, i > e.width && (p = u.text().split(" ").slice(0, -1).join(" "), u.text(p), d = u.node().getComputedTextLength() * -1, u = t.append("tspan"), u.attr("dx", d).attr("dy", "1em").text(r));
        "number" == typeof n && t.attr("y", t.attr("y") + n).attr("x", t.attr("x") + n)
    }, a = function() {
        var t, r, d;
        return t = function(t) {
            t.each(function() {
                //console.log(this)
                e.select(this).call(p[n], u(r, d), i(d))
            })
        }, t.bounds = function(e) {
            return e ? o(e) ? (r = e, t) : (console.error("invalid text wrapping bounds"), !1) : r
        }, t.padding = function(e) {
            return e ? "number" == typeof e || "function" == typeof e ? (d = e, t) : (console.error("text wrap padding value must be either a number or a function"), !1) : d
        }, t.method = function(e) {
            return e ? (n = e, t) : n
        }, t
    };
    var c = a;
    t.selection = e.selection, t.select = e.select, t.textwrap = c, Object.defineProperty(t, "__esModule", {
        value: !0
    })
});