﻿(function(e){"object"==typeof exports&&"object"==typeof module?e(require("../../lib/codemirror")):"function"==typeof define&&define.amd?define(["../../lib/codemirror"],e):e(CodeMirror)})(function(e){function j(a,c,d,b){this.line=c;this.ch=d;this.cm=a;this.text=a.getLine(c);this.min=b?b.from:a.firstLine();this.max=b?b.to-1:a.lastLine()}function k(a,c){var d=a.cm.getTokenTypeAt(h(a.line,c));return d&&/\btag\b/.test(d)}function p(a){if(!(a.line>=a.max))return a.ch=0,a.text=a.cm.getLine(++a.line),!0}
function q(a){if(!(a.line<=a.min))return a.text=a.cm.getLine(--a.line),a.ch=a.text.length,!0}function n(a){for(;;){var c=a.text.indexOf(">",a.ch);if(-1==c)if(p(a))continue;else break;if(k(a,c+1)){var d=a.text.lastIndexOf("/",c),d=-1<d&&!/\S/.test(a.text.slice(d+1,c));a.ch=c+1;return d?"selfClose":"regular"}a.ch=c+1}}function o(a){for(;;){var c=a.ch?a.text.lastIndexOf("<",a.ch-1):-1;if(-1==c)if(q(a))continue;else break;if(k(a,c+1)){l.lastIndex=c;a.ch=c;var d=l.exec(a.text);if(d&&d.index==c)return d}else a.ch=
c}}function r(a){for(;;){l.lastIndex=a.ch;var c=l.exec(a.text);if(!c)if(p(a))continue;else break;if(k(a,c.index+1))return a.ch=c.index+c[0].length,c;a.ch=c.index+1}}function m(a,c){for(var d=[];;){var b=r(a),f,g=a.line,i=a.ch-(b?b[0].length:0);if(!b||!(f=n(a)))break;if("selfClose"!=f)if(b[1]){for(var e=d.length-1;0<=e;--e)if(d[e]==b[2]){d.length=e;break}if(0>e&&(!c||c==b[2]))return{tag:b[2],from:h(g,i),to:h(a.line,a.ch)}}else d.push(b[2])}}function s(a,c){for(var d=[];;){var b;a:{for(b=a;;){var f=
b.ch?b.text.lastIndexOf(">",b.ch-1):-1;if(-1==f)if(q(b))continue;else{b=void 0;break a}if(k(b,f+1)){var g=b.text.lastIndexOf("/",f),g=-1<g&&!/\S/.test(b.text.slice(g+1,f));b.ch=f+1;b=g?"selfClose":"regular";break a}else b.ch=f}b=void 0}if(!b)break;if("selfClose"==b)o(a);else{b=a.line;f=a.ch;g=o(a);if(!g)break;if(g[1])d.push(g[2]);else{for(var e=d.length-1;0<=e;--e)if(d[e]==g[2]){d.length=e;break}if(0>e&&(!c||c==g[2]))return{tag:g[2],from:h(a.line,a.ch),to:h(b,f)}}}}}var h=e.Pos,l=RegExp("<(/?)([A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD][A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD-:.0-9\\u00B7\\u0300-\\u036F\\u203F-\\u2040]*)",
"g");e.registerHelper("fold","xml",function(a,c){for(var d=new j(a,c.line,0);;){var b=r(d),f;if(!b||d.line!=c.line||!(f=n(d)))break;if(!b[1]&&"selfClose"!=f)return c=h(d.line,d.ch),(d=m(d,b[2]))&&{from:c,to:d.from}}});e.findMatchingTag=function(a,c,d){var b=new j(a,c.line,c.ch,d);if(!(-1==b.text.indexOf(">")&&-1==b.text.indexOf("<"))){var f=n(b),e=f&&h(b.line,b.ch),i=f&&o(b);if(f&&i&&!(0<(b.line-c.line||b.ch-c.ch))){c={from:h(b.line,b.ch),to:e,tag:i[2]};if("selfClose"==f)return{open:c,close:null,
at:"open"};if(i[1])return{open:s(b,i[2]),close:c,at:"close"};b=new j(a,e.line,e.ch,d);return{open:c,close:m(b,i[2]),at:"open"}}}};e.findEnclosingTag=function(a,c,d){for(var b=new j(a,c.line,c.ch,d);;){var e=s(b);if(!e)break;var g=new j(a,c.line,c.ch,d);if(g=m(g,e.tag))return{open:e,close:g}}};e.scanForClosingTag=function(a,c,d,b){a=new j(a,c.line,c.ch,b?{from:0,to:b}:null);return m(a,d)}});