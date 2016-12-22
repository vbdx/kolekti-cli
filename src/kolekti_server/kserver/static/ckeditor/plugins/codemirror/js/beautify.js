﻿(function(){var t,y,I,H,E,B,C;function i(d,e){for(var i=0;i<e.length;i+=1)if(e[i]===d)return!0;return!1}function L(d){return d.replace(/^\s+|\s+$/g,"")}function v(d,e){return(new O(d,e)).beautify()}function O(d,e){function N(a,b){var c=0;a&&(c=a.indentation_level,!f.just_added_newline()&&a.line_indent_level>c&&(c=a.line_indent_level));return{mode:b,parent:a,last_text:a?a.last_text:"",last_word:a?a.last_word:"",declaration_statement:!1,declaration_assignment:!1,multiline_frame:!1,if_block:!1,else_block:!1,
do_block:!1,do_while:!1,in_case_statement:!1,in_case:!1,case_body:!1,indentation_level:c,line_indent_level:a?a.line_indent_level:c,start_line_index:f.get_line_number(),ternary_depth:0}}function k(b){var c=b.newlines;if(j.keep_array_indentation&&a.mode===y)for(f=0;f<c;f+=1)n(0<f);else if(j.max_preserve_newlines&&c>j.max_preserve_newlines&&(c=j.max_preserve_newlines),j.preserve_newlines&&1<b.newlines){n();for(var f=1;f<c;f+=1)n(!0)}g=b;G[g.type]()}function q(a){a=void 0===a?!1:a;f.just_added_newline()||
(j.preserve_newlines&&g.wanted_newline||a?n(!1,!0):j.wrap_line_length&&f.current_line.get_character_count()+g.text.length+(f.space_before_token?1:0)>=j.wrap_line_length&&n(!1,!0))}function n(b,c){if(!c&&";"!==a.last_text&&","!==a.last_text&&"="!==a.last_text&&"TK_OPERATOR"!==h)for(;a.mode===t&&!a.if_block&&!a.do_block;)s();f.add_new_line(b)&&(a.multiline_frame=!0)}function o(b){b=b||g.text;if(f.just_added_newline())if(j.keep_array_indentation&&a.mode===y&&g.wanted_newline){f.current_line.push("");
for(var c=0;c<g.whitespace_before.length;c+=1)f.current_line.push(g.whitespace_before[c]);f.space_before_token=!1}else f.add_indent_string(a.indentation_level)&&(a.line_indent_level=a.indentation_level);f.add_token(b)}function D(b){a?(v.push(a),z=a):z=N(null,b);a=N(z,b)}function w(a){return i(a,[I,H,E])}function s(){0<v.length&&(z=a,a=v.pop(),z.mode===t&&f.remove_redundant_indentation(z))}function J(){return a.parent.mode===B&&a.mode===t&&(":"===a.last_text&&0===a.ternary_depth||"TK_RESERVED"===h&&
i(a.last_text,["get","set"]))}function u(){return"TK_RESERVED"===h&&i(a.last_text,["var","let","const"])&&"TK_WORD"===g.type||"TK_RESERVED"===h&&"do"===a.last_text||"TK_RESERVED"===h&&"return"===a.last_text&&!g.wanted_newline||"TK_RESERVED"===h&&"else"===a.last_text&&!("TK_RESERVED"===g.type&&"if"===g.text)||"TK_END_EXPR"===h&&(z.mode===H||z.mode===E)||"TK_WORD"===h&&a.mode===C&&!a.in_case&&!("--"===g.text||"++"===g.text)&&"TK_WORD"!==g.type&&"TK_RESERVED"!==g.type||a.mode===B&&(":"===a.last_text&&
0===a.ternary_depth||"TK_RESERVED"===h&&i(a.last_text,["get","set"]))?(D(t),a.indentation_level+=1,"TK_RESERVED"===h&&(i(a.last_text,["var","let","const"])&&"TK_WORD"===g.type)&&(a.declaration_statement=!0),J()||q("TK_RESERVED"===g.type&&i(g.text,["do","for","if","while"])),!0):!1}function b(a){return i(a,"case return do if throw else".split(" "))}function p(a){a=K+(a||0);return 0>a||a>=c.length?null:c[a]}function l(){"TK_RESERVED"===g.type&&(a.mode!==B&&i(g.text,["set","get"]))&&(g.type="TK_WORD");
"TK_RESERVED"===g.type&&a.mode===B&&":"==p(1).text&&(g.type="TK_WORD");u()||g.wanted_newline&&(!w(a.mode)&&("TK_OPERATOR"!==h||"--"===a.last_text||"++"===a.last_text)&&"TK_EQUALS"!==h&&(j.preserve_newlines||!("TK_RESERVED"===h&&i(a.last_text,["var","let","const","set","get"]))))&&n();if(a.do_block&&!a.do_while){if("TK_RESERVED"===g.type&&"while"===g.text){f.space_before_token=!0;o();f.space_before_token=!0;a.do_while=!0;return}n();a.do_block=!1}if(a.if_block)if(!a.else_block&&"TK_RESERVED"===g.type&&
"else"===g.text)a.else_block=!0;else{for(;a.mode===t;)s();a.if_block=!1;a.else_block=!1}if("TK_RESERVED"===g.type&&("case"===g.text||"default"===g.text&&a.in_case_statement)){n();if(a.case_body||j.jslint_happy){if(0<a.indentation_level&&(!a.parent||a.indentation_level>a.parent.indentation_level))a.indentation_level-=1;a.case_body=!1}o();a.in_case=!0;a.in_case_statement=!0}else{if("TK_RESERVED"===g.type&&"function"===g.text){if((i(a.last_text,["}",";"])||f.just_added_newline()&&!i(a.last_text,["[",
"{",":","=",","]))&&!f.just_added_blankline()&&!g.comments_before.length)n(),n(!0);"TK_RESERVED"===h||"TK_WORD"===h?"TK_RESERVED"===h&&i(a.last_text,["get","set","new","return","export"])?f.space_before_token=!0:"TK_RESERVED"===h&&"default"===a.last_text&&"export"===r?f.space_before_token=!0:n():"TK_OPERATOR"===h||"="===a.last_text?f.space_before_token=!0:(a.multiline_frame||!w(a.mode)&&a.mode!==y)&&n()}if("TK_COMMA"===h||"TK_START_EXPR"===h||"TK_EQUALS"===h||"TK_OPERATOR"===h)J()||q();if("TK_RESERVED"===
g.type&&i(g.text,["function","get","set"]))o(),a.last_word=g.text;else{x="NONE";"TK_END_BLOCK"===h?"TK_RESERVED"===g.type&&i(g.text,["else","catch","finally"])?"expand"===j.brace_style||"end-expand"===j.brace_style?x="NEWLINE":(x="SPACE",f.space_before_token=!0):x="NEWLINE":"TK_SEMICOLON"===h&&a.mode===C?x="NEWLINE":"TK_SEMICOLON"===h&&w(a.mode)?x="SPACE":"TK_STRING"===h?x="NEWLINE":"TK_RESERVED"===h||"TK_WORD"===h||"*"===a.last_text&&"function"===r?x="SPACE":"TK_START_BLOCK"===h?x="NEWLINE":"TK_END_EXPR"===
h&&(f.space_before_token=!0,x="NEWLINE");"TK_RESERVED"===g.type&&(i(g.text,m.line_starters)&&")"!==a.last_text)&&(x="else"===a.last_text||"export"===a.last_text?"SPACE":"NEWLINE");if("TK_RESERVED"===g.type&&i(g.text,["else","catch","finally"]))"TK_END_BLOCK"!==h||"expand"===j.brace_style||"end-expand"===j.brace_style?n():(f.trim(!0),"}"!==f.current_line.last()&&n(),f.space_before_token=!0);else if("NEWLINE"===x)if("TK_RESERVED"===h&&b(a.last_text))f.space_before_token=!0;else if("TK_END_EXPR"!==h){if(("TK_START_EXPR"!==
h||!("TK_RESERVED"===g.type&&i(g.text,["var","let","const"])))&&":"!==a.last_text)"TK_RESERVED"===g.type&&"if"===g.text&&"else"===a.last_text?f.space_before_token=!0:n()}else"TK_RESERVED"===g.type&&(i(g.text,m.line_starters)&&")"!==a.last_text)&&n();else a.multiline_frame&&a.mode===y&&","===a.last_text&&"}"===r?n():"SPACE"===x&&(f.space_before_token=!0);o();a.last_word=g.text;"TK_RESERVED"===g.type&&"do"===g.text&&(a.do_block=!0);"TK_RESERVED"===g.type&&"if"===g.text&&(a.if_block=!0)}}}var f,c=[],
K,m,g,h,r,A,a,z,v,x,G,j,M="";G={TK_START_EXPR:function(){u();var b=I;if("["===g.text){if("TK_WORD"===h||")"===a.last_text){"TK_RESERVED"===h&&i(a.last_text,m.line_starters)&&(f.space_before_token=!0);D(b);o();a.indentation_level+=1;j.space_in_paren&&(f.space_before_token=!0);return}b=y;if(a.mode===y&&("["===a.last_text||","===a.last_text&&("]"===r||"}"===r)))j.keep_array_indentation||n()}else"TK_RESERVED"===h&&"for"===a.last_text?b=H:"TK_RESERVED"===h&&i(a.last_text,["if","while"])&&(b=E);if(";"===
a.last_text||"TK_START_BLOCK"===h)n();else if("TK_END_EXPR"===h||"TK_START_EXPR"===h||"TK_END_BLOCK"===h||"."===a.last_text)q(g.wanted_newline);else if(!("TK_RESERVED"===h&&"("===g.text)&&"TK_WORD"!==h&&"TK_OPERATOR"!==h)f.space_before_token=!0;else if("TK_RESERVED"===h&&("function"===a.last_word||"typeof"===a.last_word)||"*"===a.last_text&&"function"===r)j.space_after_anon_function&&(f.space_before_token=!0);else if("TK_RESERVED"===h&&(i(a.last_text,m.line_starters)||"catch"===a.last_text)&&j.space_before_conditional)f.space_before_token=
!0;if("("===g.text&&("TK_EQUALS"===h||"TK_OPERATOR"===h))J()||q();D(b);o();j.space_in_paren&&(f.space_before_token=!0);a.indentation_level+=1},TK_END_EXPR:function(){for(;a.mode===t;)s();a.multiline_frame&&q("]"===g.text&&a.mode===y&&!j.keep_array_indentation);j.space_in_paren&&("TK_START_EXPR"===h&&!j.space_in_empty_paren?(f.trim(),f.space_before_token=!1):f.space_before_token=!0);"]"===g.text&&j.keep_array_indentation?(o(),s()):(s(),o());f.remove_redundant_indentation(z);a.do_while&&z.mode===E&&
(z.mode=I,a.do_block=!1,a.do_while=!1)},TK_START_BLOCK:function(){var c=p(1),d=p(2);d&&(":"===d.text&&i(c.type,["TK_STRING","TK_WORD","TK_RESERVED"])||i(c.text,["get","set"])&&i(d.type,["TK_WORD","TK_RESERVED"]))?i(r,["class","interface"])?D(C):D(B):D(C);c=!c.comments_before.length&&"}"===c.text&&"function"===a.last_word&&"TK_END_EXPR"===h;"expand"===j.brace_style?"TK_OPERATOR"!==h&&(c||"TK_EQUALS"===h||"TK_RESERVED"===h&&b(a.last_text)&&"else"!==a.last_text)?f.space_before_token=!0:n(!1,!0):"TK_OPERATOR"!==
h&&"TK_START_EXPR"!==h?"TK_START_BLOCK"===h?n():f.space_before_token=!0:z.mode===y&&","===a.last_text&&("}"===r?f.space_before_token=!0:n());o();a.indentation_level+=1},TK_END_BLOCK:function(){for(;a.mode===t;)s();var b="TK_START_BLOCK"===h;"expand"===j.brace_style?b||n():b||(a.mode===y&&j.keep_array_indentation?(j.keep_array_indentation=!1,n(),j.keep_array_indentation=!0):n());s();o()},TK_WORD:l,TK_RESERVED:l,TK_SEMICOLON:function(){u()&&(f.space_before_token=!1);for(;a.mode===t&&!a.if_block&&!a.do_block;)s();
o()},TK_STRING:function(){u()?f.space_before_token=!0:"TK_RESERVED"===h||"TK_WORD"===h?f.space_before_token=!0:"TK_COMMA"===h||"TK_START_EXPR"===h||"TK_EQUALS"===h||"TK_OPERATOR"===h?J()||q():n();o()},TK_EQUALS:function(){u();a.declaration_statement&&(a.declaration_assignment=!0);f.space_before_token=!0;o();f.space_before_token=!0},TK_OPERATOR:function(){u();if("TK_RESERVED"===h&&b(a.last_text))f.space_before_token=!0,o();else if("*"===g.text&&"TK_DOT"===h)o();else if(":"===g.text&&a.in_case)a.case_body=
!0,a.indentation_level+=1,o(),n(),a.in_case=!1;else if("::"===g.text)o();else{g.wanted_newline&&("--"===g.text||"++"===g.text)&&n(!1,!0);"TK_OPERATOR"===h&&q();var c=!0,d=!0;i(g.text,["--","++","!","~"])||i(g.text,["-","+"])&&(i(h,["TK_START_BLOCK","TK_START_EXPR","TK_EQUALS","TK_OPERATOR"])||i(a.last_text,m.line_starters)||","===a.last_text)?(d=c=!1,";"===a.last_text&&w(a.mode)&&(c=!0),"TK_RESERVED"===h||"TK_END_EXPR"===h?c=!0:"TK_OPERATOR"===h&&(c=i(g.text,["--","-"])&&i(a.last_text,["--","-"])||
i(g.text,["++","+"])&&i(a.last_text,["++","+"])),(a.mode===C||a.mode===t)&&("{"===a.last_text||";"===a.last_text)&&n()):":"===g.text?0===a.ternary_depth?c=!1:a.ternary_depth-=1:"?"===g.text?a.ternary_depth+=1:"*"===g.text&&("TK_RESERVED"===h&&"function"===a.last_text)&&(d=c=!1);f.space_before_token=f.space_before_token||c;o();f.space_before_token=d}},TK_COMMA:function(){a.declaration_statement?(w(a.parent.mode)&&(a.declaration_assignment=!1),o(),a.declaration_assignment)?(a.declaration_assignment=
!1,n(!1,!0)):f.space_before_token=!0:(o(),a.mode===B||a.mode===t&&a.parent.mode===B?(a.mode===t&&s(),n()):f.space_before_token=!0)},TK_BLOCK_COMMENT:function(){for(var a=g.text,a=a.replace(/\x0d/g,""),b=[],c=a.indexOf("\n");-1!==c;)b.push(a.substring(0,c)),a=a.substring(c+1),c=a.indexOf("\n");a.length&&b.push(a);var d,c=a=!1;d=g.whitespace_before.join("");var h=d.length;n(!1,!0);if(1<b.length){var e;a:{e=b.slice(1);for(var l=0;l<e.length;l++)if("*"!==L(e[l]).charAt(0)){e=!1;break a}e=!0}if(e)a=!0;
else{a:{e=b.slice(1);for(var l=0,j=e.length,k;l<j;l++)if((k=e[l])&&0!==k.indexOf(d)){d=!1;break a}d=!0}d&&(c=!0)}}o(b[0]);for(d=1;d<b.length;d++)n(!1,!0),a?o(" "+L(b[d])):c&&b[d].length>h?o(b[d].substring(h)):f.add_token(b[d]);n(!1,!0)},TK_INLINE_COMMENT:function(){f.space_before_token=!0;o();f.space_before_token=!0},TK_COMMENT:function(){g.wanted_newline?n(!1,!0):f.trim(!0);f.space_before_token=!0;o();n(!1,!0)},TK_DOT:function(){u();"TK_RESERVED"===h&&b(a.last_text)?f.space_before_token=!0:q(")"===
a.last_text&&j.break_chained_methods);o()},TK_UNKNOWN:function(){o();"\n"===g.text[g.text.length-1]&&n()},TK_EOF:function(){for(;a.mode===t;)s()}};e=e?e:{};j={};void 0!==e.braces_on_own_line&&(j.brace_style=e.braces_on_own_line?"expand":"collapse");j.brace_style=e.brace_style?e.brace_style:j.brace_style?j.brace_style:"collapse";"expand-strict"===j.brace_style&&(j.brace_style="expand");j.indent_size=e.indent_size?parseInt(e.indent_size,10):4;j.indent_char=e.indent_char?e.indent_char:" ";j.preserve_newlines=
void 0===e.preserve_newlines?!0:e.preserve_newlines;j.break_chained_methods=void 0===e.break_chained_methods?!1:e.break_chained_methods;j.max_preserve_newlines=void 0===e.max_preserve_newlines?0:parseInt(e.max_preserve_newlines,10);j.space_in_paren=void 0===e.space_in_paren?!1:e.space_in_paren;j.space_in_empty_paren=void 0===e.space_in_empty_paren?!1:e.space_in_empty_paren;j.jslint_happy=void 0===e.jslint_happy?!1:e.jslint_happy;j.space_after_anon_function=void 0===e.space_after_anon_function?!1:
e.space_after_anon_function;j.keep_array_indentation=void 0===e.keep_array_indentation?!1:e.keep_array_indentation;j.space_before_conditional=void 0===e.space_before_conditional?!0:e.space_before_conditional;j.unescape_strings=void 0===e.unescape_strings?!1:e.unescape_strings;j.wrap_line_length=void 0===e.wrap_line_length?0:parseInt(e.wrap_line_length,10);j.e4x=void 0===e.e4x?!1:e.e4x;j.end_with_newline=void 0===e.end_with_newline?!1:e.end_with_newline;j.jslint_happy&&(j.space_after_anon_function=
!0);e.indent_with_tabs&&(j.indent_char="\t",j.indent_size=1);for(A="";0<j.indent_size;)A+=j.indent_char,j.indent_size-=1;var F=0;if(d&&d.length){for(;" "===d.charAt(F)||"\t"===d.charAt(F);)M+=d.charAt(F),F+=1;d=d.substring(F)}h="TK_START_BLOCK";r="";f=new P(A,M);v=[];D(C);this.beautify=function(){var b;m=new Q(d,j,A);c=m.tokenize();for(K=0;b=p();){for(var g=0;g<b.comments_before.length;g++)k(b.comments_before[g]);k(b);r=a.last_text;h=b.type;a.last_text=b.text;K=K+1}b=f.get_code();j.end_with_newline&&
(b=b+"\n");return b}}function R(){var d=0,e=[];this.get_character_count=function(){return d};this.get_item_count=function(){return e.length};this.get_output=function(){return e.join("")};this.last=function(){return e.length?e[e.length-1]:null};this.push=function(i){e.push(i);d+=i.length};this.remove_indent=function(i,k){var q=0;0!==e.length&&(k&&e[0]===k&&(q=1),e[q]===i&&(d-=e[q].length,e.splice(q,1)))};this.trim=function(i,k){for(;this.get_item_count()&&(" "===this.last()||this.last()===i||this.last()===
k);){var q=e.pop();d-=q.length}}}function P(d,e){var i=[];this.baseIndentString=e;this.current_line=null;this.space_before_token=!1;this.get_line_number=function(){return i.length};this.add_new_line=function(d){return 1===this.get_line_number()&&this.just_added_newline()?!1:d||!this.just_added_newline()?(this.current_line=new R,i.push(this.current_line),!0):!1};this.add_new_line(!0);this.get_code=function(){for(var d=i[0].get_output(),e=1;e<i.length;e++)d+="\n"+i[e].get_output();return d=d.replace(/[\r\n\t ]+$/,
"")};this.add_indent_string=function(k){e&&this.current_line.push(e);if(1<i.length){for(var q=0;q<k;q+=1)this.current_line.push(d);return!0}return!1};this.add_token=function(d){this.add_space_before_token();this.current_line.push(d)};this.add_space_before_token=function(){if(this.space_before_token&&this.current_line.get_item_count()){var i=this.current_line.last();" "!==i&&(i!==d&&i!==e)&&this.current_line.push(" ")}this.space_before_token=!1};this.remove_redundant_indentation=function(k){if(!k.multiline_frame&&
!(k.mode===H||k.mode===E))for(var k=k.start_line_index,q=i.length;k<q;)i[k].remove_indent(d,e),k++};this.trim=function(k){k=void 0===k?!1:k;for(this.current_line.trim(d,e);k&&1<i.length&&0===this.current_line.get_item_count();)i.pop(),this.current_line=i[i.length-1],this.current_line.trim(d,e)};this.just_added_newline=function(){return 0===this.current_line.get_item_count()};this.just_added_blankline=function(){return this.just_added_newline()?1===i.length?!0:0===i[i.length-2].get_item_count():!1}}
function Q(d,e,t){function k(){var l;w=0;s=[];if(b>=p)return["","TK_EOF"];var f;f=u.length?u[u.length-1]:new G("TK_START_BLOCK","{");var c=d.charAt(b);for(b+=1;i(c,q);){"\n"===c?(w+=1,s=[]):w&&(c===t?s.push(t):"\r"!==c&&s.push(" "));if(b>=p)return["","TK_EOF"];c=d.charAt(b);b+=1}if(n.test(c)){var k=f=!0,m=n;"0"===c&&b<p&&/[Xx]/.test(d.charAt(b))?(k=f=!1,c+=d.charAt(b),b+=1,m=/[0123456789abcdefABCDEF]/):(c="",b-=1);for(;b<p&&m.test(d.charAt(b));)if(c+=d.charAt(b),b+=1,f&&(b<p&&"."===d.charAt(b))&&
(c+=d.charAt(b),b+=1,f=!1),k&&b<p&&/[Ee]/.test(d.charAt(b)))c+=d.charAt(b),b+=1,b<p&&/[+-]/.test(d.charAt(b))&&(c+=d.charAt(b),b+=1),f=k=!1;return[c,"TK_WORD"]}if(A.isIdentifierStart(d.charCodeAt(b-1))){if(b<p)for(;A.isIdentifierChar(d.charCodeAt(b))&&!(c+=d.charAt(b),b+=1,b===p););return!("TK_DOT"===f.type||"TK_RESERVED"===f.type&&i(f.text,["set","get"]))&&i(c,y)?"in"===c?[c,"TK_OPERATOR"]:[c,"TK_RESERVED"]:[c,"TK_WORD"]}if("("===c||"["===c)return[c,"TK_START_EXPR"];if(")"===c||"]"===c)return[c,
"TK_END_EXPR"];if("{"===c)return[c,"TK_START_BLOCK"];if("}"===c)return[c,"TK_END_BLOCK"];if(";"===c)return[c,"TK_SEMICOLON"];if("/"===c){k="";m=!0;if("*"===d.charAt(b)){b+=1;if(b<p)for(;b<p&&!("*"===d.charAt(b)&&d.charAt(b+1)&&"/"===d.charAt(b+1));){c=d.charAt(b);k+=c;if("\n"===c||"\r"===c)m=!1;b+=1;if(b>=p)break}b+=2;return m&&0===w?["/*"+k+"*/","TK_INLINE_COMMENT"]:["/*"+k+"*/","TK_BLOCK_COMMENT"]}if("/"===d.charAt(b)){for(k=c;"\r"!==d.charAt(b)&&"\n"!==d.charAt(b)&&!(k+=d.charAt(b),b+=1,b>=p););
return[k,"TK_COMMENT"]}}if("`"===c||"'"===c||'"'===c||("/"===c||e.e4x&&"<"===c&&d.slice(b-1).match(/^<([-a-zA-Z:0-9_.]+|{[^{}]*}|!\[CDATA\[[\s\S]*?\]\])\s*([-a-zA-Z:0-9_.]+=('[^']*'|"[^"]*"|{[^{}]*})\s*)*\/?\s*>/))&&("TK_RESERVED"===f.type&&i(f.text,"return case throw else do typeof yield".split(" "))||"TK_END_EXPR"===f.type&&")"===f.text&&f.parent&&"TK_RESERVED"===f.parent.type&&i(f.parent.text,["if","while","for"])||i(f.type,"TK_COMMENT TK_START_EXPR TK_START_BLOCK TK_END_BLOCK TK_OPERATOR TK_EQUALS TK_EOF TK_SEMICOLON TK_COMMA".split(" ")))){f=
c;var g=k=!1;l=c;if("/"===f)for(c=!1;b<p&&(k||c||d.charAt(b)!==f)&&!A.newline.test(d.charAt(b));)l+=d.charAt(b),k?k=!1:(k="\\"===d.charAt(b),"["===d.charAt(b)?c=!0:"]"===d.charAt(b)&&(c=!1)),b+=1;else if(e.e4x&&"<"===f){if(k=/<(\/?)([-a-zA-Z:0-9_.]+|{[^{}]*}|!\[CDATA\[[\s\S]*?\]\])\s*([-a-zA-Z:0-9_.]+=('[^']*'|"[^"]*"|{[^{}]*})\s*)*(\/?)\s*>/g,c=d.slice(b-1),(m=k.exec(c))&&0===m.index){f=m[2];for(l=0;m;){var g=!!m[1],h=m[2],r=!!m[m.length-1]||"![CDATA["===h.slice(0,8);h===f&&!r&&(g?--l:++l);if(0>=
l)break;m=k.exec(c)}f=m?m.index+m[0].length:c.length;b+=f-1;return[c.slice(0,f),"TK_STRING"]}}else for(;b<p&&(k||d.charAt(b)!==f&&("`"===f||!A.newline.test(d.charAt(b))));){l+=d.charAt(b);if(k){if("x"===d.charAt(b)||"u"===d.charAt(b))g=!0;k=!1}else k="\\"===d.charAt(b);b+=1}if(g&&e.unescape_strings)a:{c=l;k=!1;m="";l=0;g="";for(h=0;k||l<c.length;)if(r=c.charAt(l),l++,k){k=!1;if("x"===r)g=c.substr(l,2),l+=2;else if("u"===r)g=c.substr(l,4),l+=4;else{m+="\\"+r;continue}if(!g.match(/^[0123456789abcdefABCDEF]+$/)){l=
c;break a}h=parseInt(g,16);if(0<=h&&32>h)m="x"===r?m+("\\x"+g):m+("\\u"+g);else if(34===h||39===h||92===h)m+="\\"+String.fromCharCode(h);else if("x"===r&&126<h&&255>=h){l=c;break a}else m+=String.fromCharCode(h)}else"\\"===r?k=!0:m+=r;l=m}if(b<p&&d.charAt(b)===f&&(l+=f,b+=1,"/"===f))for(;b<p&&A.isIdentifierStart(d.charCodeAt(b));)l+=d.charAt(b),b+=1;return[l,"TK_STRING"]}if("#"===c){if(0===u.length&&"!"===d.charAt(b)){for(l=c;b<p&&"\n"!==c;)c=d.charAt(b),l+=c,b+=1;return[L(l)+"\n","TK_UNKNOWN"]}f=
"#";if(b<p&&n.test(d.charAt(b))){do c=d.charAt(b),f+=c,b+=1;while(b<p&&"#"!==c&&"="!==c);"#"!==c&&("["===d.charAt(b)&&"]"===d.charAt(b+1)?(f+="[]",b+=2):"{"===d.charAt(b)&&"}"===d.charAt(b+1)&&(f+="{}",b+=2));return[f,"TK_WORD"]}}if("<"===c&&"<\!--"===d.substring(b-1,b+3)){b+=3;for(c="<\!--";"\n"!==d.charAt(b)&&b<p;)c+=d.charAt(b),b++;v=!0;return[c,"TK_COMMENT"]}if("-"===c&&v&&"--\>"===d.substring(b-1,b+2))return v=!1,b+=2,["--\>","TK_COMMENT"];if("."===c)return[c,"TK_DOT"];if(i(c,o)){for(;b<p&&i(c+
d.charAt(b),o)&&!(c+=d.charAt(b),b+=1,b>=p););return","===c?[c,"TK_COMMA"]:"="===c?[c,"TK_EQUALS"]:[c,"TK_OPERATOR"]}return[c,"TK_UNKNOWN"]}var q=["\n","\r","\t"," "],n=/[0-9]/,o="+ - * / % & ++ -- = += -= *= /= %= == === != !== > < >= <= >> << >>> >>>= >>= <<= && &= | || ! ~ , : ? ^ ^= |= :: => <%= <% %> <?= <? ?>".split(" ");this.line_starters="continue try throw return var let const if switch case default for while break function yield import export".split(" ");var y=this.line_starters.concat("do in else get set new catch finally typeof".split(" ")),
w,s,v,u,b,p;this.tokenize=function(){p=d.length;b=0;v=!1;u=[];for(var e,f,c=null,i=[],m=[];!(f&&"TK_EOF"===f.type);){e=k();for(e=new G(e[1],e[0],w,s);"TK_INLINE_COMMENT"===e.type||"TK_COMMENT"===e.type||"TK_BLOCK_COMMENT"===e.type||"TK_UNKNOWN"===e.type;)m.push(e),e=k(),e=new G(e[1],e[0],w,s);m.length&&(e.comments_before=m,m=[]);if("TK_START_BLOCK"===e.type||"TK_START_EXPR"===e.type)e.parent=f,c=e,i.push(e);else if(("TK_END_BLOCK"===e.type||"TK_END_EXPR"===e.type)&&c&&("]"===e.text&&"["===c.text||
")"===e.text&&"("===c.text||"}"===e.text&&"}"===c.text))e.parent=c.parent,c=i.pop();u.push(e);f=e}return u}}var A={};(function(d){var e=RegExp("[ªµºÀ-ÖØ-öø-ˁˆ-ˑˠ-ˤˬˮͰ-ʹͶͷͺ-ͽΆΈ-ΊΌΎ-ΡΣ-ϵϷ-ҁҊ-ԧԱ-Ֆՙա-ևא-תװ-ײؠ-يٮٯٱ-ۓەۥۦۮۯۺ-ۼۿܐܒ-ܯݍ-ޥޱߊ-ߪߴߵߺࠀ-ࠕࠚࠤࠨࡀ-ࡘࢠࢢ-ࢬऄ-हऽॐक़-ॡॱ-ॷॹ-ॿঅ-ঌএঐও-নপ-রলশ-হঽৎড়ঢ়য়-ৡৰৱਅ-ਊਏਐਓ-ਨਪ-ਰਲਲ਼ਵਸ਼ਸਹਖ਼-ੜਫ਼ੲ-ੴઅ-ઍએ-ઑઓ-નપ-રલળવ-હઽૐૠૡଅ-ଌଏଐଓ-ନପ-ରଲଳଵ-ହଽଡ଼ଢ଼ୟ-ୡୱஃஅ-ஊஎ-ஐஒ-கஙசஜஞடணதந-பம-ஹௐఅ-ఌఎ-ఐఒ-నప-ళవ-హఽౘౙౠౡಅ-ಌಎ-ಐಒ-ನಪ-ಳವ-ಹಽೞೠೡೱೲഅ-ഌഎ-ഐഒ-ഺഽൎൠൡൺ-ൿඅ-ඖක-නඳ-රලව-ෆก-ะาำเ-ๆກຂຄງຈຊຍດ-ທນ-ຟມ-ຣລວສຫອ-ະາຳຽເ-ໄໆໜ-ໟༀཀ-ཇཉ-ཬྈ-ྌက-ဪဿၐ-ၕၚ-ၝၡၥၦၮ-ၰၵ-ႁႎႠ-ჅჇჍა-ჺჼ-ቈቊ-ቍቐ-ቖቘቚ-ቝበ-ኈኊ-ኍነ-ኰኲ-ኵኸ-ኾዀዂ-ዅወ-ዖዘ-ጐጒ-ጕጘ-ፚᎀ-ᎏᎠ-Ᏼᐁ-ᙬᙯ-ᙿᚁ-ᚚᚠ-ᛪᛮ-ᛰᜀ-ᜌᜎ-ᜑᜠ-ᜱᝀ-ᝑᝠ-ᝬᝮ-ᝰក-ឳៗៜᠠ-ᡷᢀ-ᢨᢪᢰ-ᣵᤀ-ᤜᥐ-ᥭᥰ-ᥴᦀ-ᦫᧁ-ᧇᨀ-ᨖᨠ-ᩔᪧᬅ-ᬳᭅ-ᭋᮃ-ᮠᮮᮯᮺ-ᯥᰀ-ᰣᱍ-ᱏᱚ-ᱽᳩ-ᳬᳮ-ᳱᳵᳶᴀ-ᶿḀ-ἕἘ-Ἕἠ-ὅὈ-Ὅὐ-ὗὙὛὝὟ-ώᾀ-ᾴᾶ-ᾼιῂ-ῄῆ-ῌῐ-ΐῖ-Ίῠ-Ῥῲ-ῴῶ-ῼⁱⁿₐ-ₜℂℇℊ-ℓℕℙ-ℝℤΩℨK-ℭℯ-ℹℼ-ℿⅅ-ⅉⅎⅠ-ↈⰀ-Ⱞⰰ-ⱞⱠ-ⳤⳫ-ⳮⳲⳳⴀ-ⴥⴧⴭⴰ-ⵧⵯⶀ-ⶖⶠ-ⶦⶨ-ⶮⶰ-ⶶⶸ-ⶾⷀ-ⷆⷈ-ⷎⷐ-ⷖⷘ-ⷞⸯ々-〇〡-〩〱-〵〸-〼ぁ-ゖゝ-ゟァ-ヺー-ヿㄅ-ㄭㄱ-ㆎㆠ-ㆺㇰ-ㇿ㐀-䶵一-鿌ꀀ-ꒌꓐ-ꓽꔀ-ꘌꘐ-ꘟꘪꘫꙀ-ꙮꙿ-ꚗꚠ-ꛯꜗ-ꜟꜢ-ꞈꞋ-ꞎꞐ-ꞓꞠ-Ɦꟸ-ꠁꠃ-ꠅꠇ-ꠊꠌ-ꠢꡀ-ꡳꢂ-ꢳꣲ-ꣷꣻꤊ-ꤥꤰ-ꥆꥠ-ꥼꦄ-ꦲꧏꨀ-ꨨꩀ-ꩂꩄ-ꩋꩠ-ꩶꩺꪀ-ꪯꪱꪵꪶꪹ-ꪽꫀꫂꫛ-ꫝꫠ-ꫪꫲ-ꫴꬁ-ꬆꬉ-ꬎꬑ-ꬖꬠ-ꬦꬨ-ꬮꯀ-ꯢ가-힣ힰ-ퟆퟋ-ퟻ豈-舘並-龎ﬀ-ﬆﬓ-ﬗיִײַ-ﬨשׁ-זּטּ-לּמּנּסּףּפּצּ-ﮱﯓ-ﴽﵐ-ﶏﶒ-ﷇﷰ-ﷻﹰ-ﹴﹶ-ﻼＡ-Ｚａ-ｚｦ-ﾾￂ-ￇￊ-ￏￒ-ￗￚ-ￜ]"),
i=RegExp("[ªµºÀ-ÖØ-öø-ˁˆ-ˑˠ-ˤˬˮͰ-ʹͶͷͺ-ͽΆΈ-ΊΌΎ-ΡΣ-ϵϷ-ҁҊ-ԧԱ-Ֆՙա-ևא-תװ-ײؠ-يٮٯٱ-ۓەۥۦۮۯۺ-ۼۿܐܒ-ܯݍ-ޥޱߊ-ߪߴߵߺࠀ-ࠕࠚࠤࠨࡀ-ࡘࢠࢢ-ࢬऄ-हऽॐक़-ॡॱ-ॷॹ-ॿঅ-ঌএঐও-নপ-রলশ-হঽৎড়ঢ়য়-ৡৰৱਅ-ਊਏਐਓ-ਨਪ-ਰਲਲ਼ਵਸ਼ਸਹਖ਼-ੜਫ਼ੲ-ੴઅ-ઍએ-ઑઓ-નપ-રલળવ-હઽૐૠૡଅ-ଌଏଐଓ-ନପ-ରଲଳଵ-ହଽଡ଼ଢ଼ୟ-ୡୱஃஅ-ஊஎ-ஐஒ-கஙசஜஞடணதந-பம-ஹௐఅ-ఌఎ-ఐఒ-నప-ళవ-హఽౘౙౠౡಅ-ಌಎ-ಐಒ-ನಪ-ಳವ-ಹಽೞೠೡೱೲഅ-ഌഎ-ഐഒ-ഺഽൎൠൡൺ-ൿඅ-ඖක-නඳ-රලව-ෆก-ะาำเ-ๆກຂຄງຈຊຍດ-ທນ-ຟມ-ຣລວສຫອ-ະາຳຽເ-ໄໆໜ-ໟༀཀ-ཇཉ-ཬྈ-ྌက-ဪဿၐ-ၕၚ-ၝၡၥၦၮ-ၰၵ-ႁႎႠ-ჅჇჍა-ჺჼ-ቈቊ-ቍቐ-ቖቘቚ-ቝበ-ኈኊ-ኍነ-ኰኲ-ኵኸ-ኾዀዂ-ዅወ-ዖዘ-ጐጒ-ጕጘ-ፚᎀ-ᎏᎠ-Ᏼᐁ-ᙬᙯ-ᙿᚁ-ᚚᚠ-ᛪᛮ-ᛰᜀ-ᜌᜎ-ᜑᜠ-ᜱᝀ-ᝑᝠ-ᝬᝮ-ᝰក-ឳៗៜᠠ-ᡷᢀ-ᢨᢪᢰ-ᣵᤀ-ᤜᥐ-ᥭᥰ-ᥴᦀ-ᦫᧁ-ᧇᨀ-ᨖᨠ-ᩔᪧᬅ-ᬳᭅ-ᭋᮃ-ᮠᮮᮯᮺ-ᯥᰀ-ᰣᱍ-ᱏᱚ-ᱽᳩ-ᳬᳮ-ᳱᳵᳶᴀ-ᶿḀ-ἕἘ-Ἕἠ-ὅὈ-Ὅὐ-ὗὙὛὝὟ-ώᾀ-ᾴᾶ-ᾼιῂ-ῄῆ-ῌῐ-ΐῖ-Ίῠ-Ῥῲ-ῴῶ-ῼⁱⁿₐ-ₜℂℇℊ-ℓℕℙ-ℝℤΩℨK-ℭℯ-ℹℼ-ℿⅅ-ⅉⅎⅠ-ↈⰀ-Ⱞⰰ-ⱞⱠ-ⳤⳫ-ⳮⳲⳳⴀ-ⴥⴧⴭⴰ-ⵧⵯⶀ-ⶖⶠ-ⶦⶨ-ⶮⶰ-ⶶⶸ-ⶾⷀ-ⷆⷈ-ⷎⷐ-ⷖⷘ-ⷞⸯ々-〇〡-〩〱-〵〸-〼ぁ-ゖゝ-ゟァ-ヺー-ヿㄅ-ㄭㄱ-ㆎㆠ-ㆺㇰ-ㇿ㐀-䶵一-鿌ꀀ-ꒌꓐ-ꓽꔀ-ꘌꘐ-ꘟꘪꘫꙀ-ꙮꙿ-ꚗꚠ-ꛯꜗ-ꜟꜢ-ꞈꞋ-ꞎꞐ-ꞓꞠ-Ɦꟸ-ꠁꠃ-ꠅꠇ-ꠊꠌ-ꠢꡀ-ꡳꢂ-ꢳꣲ-ꣷꣻꤊ-ꤥꤰ-ꥆꥠ-ꥼꦄ-ꦲꧏꨀ-ꨨꩀ-ꩂꩄ-ꩋꩠ-ꩶꩺꪀ-ꪯꪱꪵꪶꪹ-ꪽꫀꫂꫛ-ꫝꫠ-ꫪꫲ-ꫴꬁ-ꬆꬉ-ꬎꬑ-ꬖꬠ-ꬦꬨ-ꬮꯀ-ꯢ가-힣ힰ-ퟆퟋ-ퟻ豈-舘並-龎ﬀ-ﬆﬓ-ﬗיִײַ-ﬨשׁ-זּטּ-לּמּנּסּףּפּצּ-ﮱﯓ-ﴽﵐ-ﶏﶒ-ﷇﷰ-ﷻﹰ-ﹴﹶ-ﻼＡ-Ｚａ-ｚｦ-ﾾￂ-ￇￊ-ￏￒ-ￗￚ-ￜ̀-ͯ҃-֑҇-ׇֽֿׁׂׅׄؐ-ؚؠ-ىٲ-ۓۧ-ۨۻ-ۼܰ-݊ࠀ-ࠔࠛ-ࠣࠥ-ࠧࠩ-࠭ࡀ-ࡗࣤ-ࣾऀ-ःऺ-़ा-ॏ॑-ॗॢ-ॣ०-९ঁ-ঃ়া-ৄেৈৗয়-ৠਁ-ਃ਼ਾ-ੂੇੈੋ-੍ੑ੦-ੱੵઁ-ઃ઼ા-ૅે-ૉો-્ૢ-ૣ૦-૯ଁ-ଃ଼ା-ୄେୈୋ-୍ୖୗୟ-ୠ୦-୯ஂா-ூெ-ைொ-்ௗ௦-௯ఁ-ఃె-ైొ-్ౕౖౢ-ౣ౦-౯ಂಃ಼ಾ-ೄೆ-ೈೊ-್ೕೖೢ-ೣ೦-೯ംഃെ-ൈൗൢ-ൣ൦-൯ංඃ්ා-ුූෘ-ෟෲෳิ-ฺเ-ๅ๐-๙ິ-ູ່-ໍ໐-໙༘༙༠-༩༹༵༷ཁ-ཇཱ-྄྆-྇ྍ-ྗྙ-ྼ࿆က-ဩ၀-၉ၧ-ၭၱ-ၴႂ-ႍႏ-ႝ፝-፟ᜎ-ᜐᜠ-ᜰᝀ-ᝐᝲᝳក-ឲ៝០-៩᠋-᠍᠐-᠙ᤠ-ᤫᤰ-᤻ᥑ-ᥭᦰ-ᧀᧈ-ᧉ᧐-᧙ᨀ-ᨕᨠ-ᩓ᩠-᩿᩼-᪉᪐-᪙ᭆ-ᭋ᭐-᭙᭫-᭳᮰-᮹᯦-᯳ᰀ-ᰢ᱀-᱉ᱛ-ᱽ᳐-᳒ᴀ-ᶾḁ-ἕ‌‍‿⁀⁔⃐-⃥⃜⃡-⃰ⶁ-ⶖⷠ-ⷿ〡-〨゙゚Ꙁ-ꙭꙴ-꙽ꚟ꛰-꛱ꟸ-ꠀ꠆ꠋꠣ-ꠧꢀ-ꢁꢴ-꣄꣐-꣙ꣳ-ꣷ꤀-꤉ꤦ-꤭ꤰ-ꥅꦀ-ꦃ꦳-꧀ꨀ-ꨧꩀ-ꩁꩌ-ꩍ꩐-꩙ꩻꫠ-ꫩꫲ-ꫳꯀ-ꯡ꯬꯭꯰-꯹ﬠ-ﬨ︀-️︠-︦︳︴﹍-﹏０-９＿]");
d.newline=/[\n\r\u2028\u2029]/;d.isIdentifierStart=function(d){return 65>d?36===d:91>d?!0:97>d?95===d:123>d?!0:170<=d&&e.test(String.fromCharCode(d))};d.isIdentifierChar=function(d){return 48>d?36===d:58>d?!0:65>d?!1:91>d?!0:97>d?95===d:123>d?!0:170<=d&&i.test(String.fromCharCode(d))}})(A);C="BlockStatement";t="Statement";B="ObjectLiteral";y="ArrayLiteral";H="ForInitializer";E="Conditional";I="Expression";var G=function(d,e,i,k){this.type=d;this.text=e;this.comments_before=[];this.newlines=i||0;this.wanted_newline=
0<i;this.whitespace_before=k||[];this.parent=null};"function"===typeof define&&define.amd?define([],function(){return{js_beautify:v}}):"undefined"!==typeof exports?exports.js_beautify=v:"undefined"!==typeof window?window.js_beautify=v:"undefined"!==typeof global&&(global.js_beautify=v)})();