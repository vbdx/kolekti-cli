﻿(function(a){"object"==typeof exports&&"object"==typeof module?a(require("../../lib/codemirror")):"function"==typeof define&&define.amd?define(["../../lib/codemirror"],a):a(CodeMirror)})(function(a){a.registerHelper("fold","markdown",function(c,d){function g(b){return(b=c.getTokenTypeAt(a.Pos(b,0)))&&/\bheader\b/.test(b)}function h(b,a,c){return(a=a&&a.match(/^#+/))&&g(b)?a[0].length:(a=c&&c.match(/^[=\-]+\s*$/))&&g(b+1)?"="==c[0]?1:2:i}var i=100,j=c.getLine(d.line),e=c.getLine(d.line+1),k=h(d.line,
j,e);if(k!==i){for(var l=c.lastLine(),b=d.line,f=c.getLine(b+2);b<l&&!(h(b+1,e,f)<=k);)++b,e=f,f=c.getLine(b+2);return{from:a.Pos(d.line,j.length),to:a.Pos(b,c.getLine(b).length)}}})});