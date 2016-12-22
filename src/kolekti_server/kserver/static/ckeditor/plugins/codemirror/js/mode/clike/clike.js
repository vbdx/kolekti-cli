﻿(function(k){"object"==typeof exports&&"object"==typeof module?k(require("../../lib/codemirror")):"function"==typeof define&&define.amd?define(["../../lib/codemirror"],k):k(CodeMirror)})(function(k){function a(b){for(var d={},b=b.split(" "),a=0;a<b.length;++a)d[b[a]]=!0;return d}function f(b,d){if(!d.startOfLine)return!1;for(;;)if(b.skipTo("\\")){if(b.next(),b.eol()){d.tokenize=f;break}}else{b.skipToEnd();d.tokenize=null;break}return"meta"}function n(b,d){return"variable-3"==d.prevToken?"variable-3":
!1}function m(b,d){b.backUp(1);if(b.match(/(R|u8R|uR|UR|LR)/)){var a=b.match(/"([^\s\\()]{0,16})\(/);if(!a)return!1;d.cpp11RawStringDelim=a[1];d.tokenize=o;return o(b,d)}if(b.match(/(u8|u|U|L)/))return b.match(/["']/,!1)?"string":!1;b.next();return!1}function q(b,d){for(var a;null!=(a=b.next());)if('"'==a&&!b.eat('"')){d.tokenize=null;break}return"string"}function o(b,d){var a=d.cpp11RawStringDelim.replace(/[^\w\s]/g,"\\$&");b.match(RegExp(".*?\\)"+a+'"'))?d.tokenize=null:b.skipToEnd();return"string"}
function e(b,d){function a(b){if(b)for(var d in b)b.hasOwnProperty(d)&&e.push(d)}"string"==typeof b&&(b=[b]);var e=[];a(d.keywords);a(d.types);a(d.builtin);a(d.atoms);e.length&&(d.helperType=b[0],k.registerHelper("hintWords",b[0],e));for(var f=0;f<b.length;++f)k.defineMIME(b[f],d)}function u(b,a){for(var e=!1;!b.eol();){if(!e&&b.match('"""')){a.tokenize=null;break}e="\\"==b.next()&&!e}return"string"}k.defineMode("clike",function(b,a){function e(a,b){var c=a.next();if(r[c]){var d=r[c](a,b);if(!1!==
d)return d}if('"'==c||"'"==c)return b.tokenize=f(c),b.tokenize(a,b);if(/[\[\]{}\(\),;\:\.]/.test(c))return i=c,null;if(/\d/.test(c))return a.eatWhile(/[\w\.]/),"number";if("/"==c){if(a.eat("*"))return b.tokenize=m,m(a,b);if(a.eat("/"))return a.skipToEnd(),"comment"}if(w.test(c))return a.eatWhile(w),"operator";a.eatWhile(/[\w\$_\xa1-\uffff]/);if(x)for(;a.match(x);)a.eatWhile(/[\w\$_\xa1-\uffff]/);c=a.current();return u.propertyIsEnumerable(c)?(y.propertyIsEnumerable(c)&&(i="newstatement"),A.propertyIsEnumerable(c)&&
(v=!0),"keyword"):B.propertyIsEnumerable(c)?"variable-3":C.propertyIsEnumerable(c)?(y.propertyIsEnumerable(c)&&(i="newstatement"),"builtin"):D.propertyIsEnumerable(c)?"atom":"variable"}function f(a){return function(b,c){for(var d=!1,h,e=!1;null!=(h=b.next());){if(h==a&&!d){e=!0;break}d=!d&&"\\"==h}if(e||!d&&!E)c.tokenize=null;return"string"}}function m(a,b){for(var c=!1,d;d=a.next();){if("/"==d&&c){b.tokenize=null;break}c="*"==d}return"comment"}function n(a,b,c,d,e){this.indented=a;this.column=b;
this.type=c;this.align=d;this.prev=e}function l(a){return"statement"==a||"switchstatement"==a||"namespace"==a}function s(a,b,c){var d=a.indented;a.context&&(l(a.context.type)&&!l(c))&&(d=a.context.indented);return a.context=new n(d,b,c,null,a.context)}function p(a){var b=a.context.type;if(")"==b||"]"==b||"}"==b)a.indented=a.context.indented;return a.context=a.context.prev}var t=b.indentUnit,o=a.statementIndentUnit||t,q=a.dontAlignCalls,u=a.keywords||{},B=a.types||{},C=a.builtin||{},y=a.blockKeywords||
{},A=a.defKeywords||{},D=a.atoms||{},r=a.hooks||{},E=a.multiLineStrings,F=!1!==a.indentStatements,z=!1!==a.indentSwitch,x=a.namespaceSeparator,w=/[+\-*&%=<>!?|\/]/,i,v;return{startState:function(a){return{tokenize:null,context:new n((a||0)-t,0,"top",!1),indented:0,startOfLine:!0,prevToken:null}},token:function(b,g){var c=g.context;b.sol()&&(null==c.align&&(c.align=!1),g.indented=b.indentation(),g.startOfLine=!0);if(b.eatSpace())return null;i=v=null;var j=(g.tokenize||e)(b,g);if("comment"==j||"meta"==
j)return j;null==c.align&&(c.align=!0);if(";"==i||":"==i||","==i)for(;l(g.context.type);)p(g);else if("{"==i)s(g,b.column(),"}");else if("["==i)s(g,b.column(),"]");else if("("==i)s(g,b.column(),")");else if("}"==i){for(;l(c.type);)c=p(g);for("}"==c.type&&(c=p(g));l(c.type);)c=p(g)}else if(i==c.type)p(g);else if(F&&(("}"==c.type||"top"==c.type)&&";"!=i||l(c.type)&&"newstatement"==i))c="statement","newstatement"==i&&z&&"switch"==b.current()?c="switchstatement":"keyword"==j&&"namespace"==b.current()&&
(c="namespace"),s(g,b.column(),c);if(c="variable"==j)if(!(c="def"==g.prevToken))if(c=a.typeFirstDefinitions){var h;"variable"==g.prevToken||"variable-3"==g.prevToken?h=!0:/\S(?:[^- ]>|[*\]])\s*$|\*$/.test(b.string.slice(0,b.start))&&(h=!0);if(h){var f;a:for(h=g.context;;){if(!h||"top"==h.type){f=!0;break a}if("}"==h.type&&"namespace"!=h.prev.type){f=!1;break a}h=h.prev}h=f&&b.match(/^\s*\(/,!1)}c=h}c&&(j="def");r.token&&(f=r.token(b,g,j),void 0!==f&&(j=f));"def"==j&&!1===a.styleDefs&&(j="variable");
g.startOfLine=!1;g.prevToken=v?"def":j||i;return j},indent:function(a,b){if(a.tokenize!=e&&null!=a.tokenize)return k.Pass;var c=a.context,d=b&&b.charAt(0);l(c.type)&&"}"==d&&(c=c.prev);var h=d==c.type,f=c.prev&&"switchstatement"==c.prev.type;return l(c.type)?c.indented+("{"==d?0:o):c.align&&(!q||")"!=c.type)?c.column+(h?0:1):")"==c.type&&!h?c.indented+o:c.indented+(h?0:t)+(!h&&f&&!/^(?:case|default)\b/.test(b)?t:0)},electricInput:z?/^\s*(?:case .*?:|default:|\{\}?|\})$/:/^\s*[{}]$/,blockCommentStart:"/*",
blockCommentEnd:"*/",lineComment:"//",fold:"brace"}});e(["text/x-csrc","text/x-c","text/x-chdr"],{name:"clike",keywords:a("auto if break case register continue return default do sizeof static else struct switch extern typedef float union for goto while enum const volatile"),types:a("int long char short double float unsigned signed void size_t ptrdiff_t bool _Complex _Bool float_t double_t intptr_t intmax_t int8_t int16_t int32_t int64_t uintptr_t uintmax_t uint8_t uint16_t uint32_t uint64_t"),blockKeywords:a("case do else for if switch while struct"),
defKeywords:a("struct"),typeFirstDefinitions:!0,atoms:a("null true false"),hooks:{"#":f,"*":n},modeProps:{fold:["brace","include"]}});e(["text/x-c++src","text/x-c++hdr"],{name:"clike",keywords:a("auto if break case register continue return default do sizeof static else struct switch extern typedef float union for goto while enum const volatile asm dynamic_cast namespace reinterpret_cast try explicit new static_cast typeid catch operator template typename class friend private this using const_cast inline public throw virtual delete mutable protected alignas alignof constexpr decltype nullptr noexcept thread_local final static_assert override"),
types:a("int long char short double float unsigned signed void size_t ptrdiff_t bool wchar_t"),blockKeywords:a("catch class do else finally for if struct switch try while"),defKeywords:a("class namespace struct enum union"),typeFirstDefinitions:!0,atoms:a("true false null"),hooks:{"#":f,"*":n,u:m,U:m,L:m,R:m,token:function(a,d,e){if(e="variable"==e)if(e="("==a.peek()){if(d=";"==d.prevToken||null==d.prevToken||"}"==d.prevToken)d=(a=/(\w+)::(\w+)$/.exec(a.current()))&&a[1]==a[2];e=d}if(e)return"def"}},
namespaceSeparator:"::",modeProps:{fold:["brace","include"]}});e("text/x-java",{name:"clike",keywords:a("abstract assert break case catch class const continue default do else enum extends final finally float for goto if implements import instanceof interface native new package private protected public return static strictfp super switch synchronized this throw throws transient try volatile while"),types:a("byte short int long float double boolean char void Boolean Byte Character Double Float Integer Long Number Object Short String StringBuffer StringBuilder Void"),
blockKeywords:a("catch class do else finally for if switch try while"),defKeywords:a("class interface package enum"),typeFirstDefinitions:!0,atoms:a("true false null"),hooks:{"@":function(a){a.eatWhile(/[\w\$_]/);return"meta"}},modeProps:{fold:["brace","import"]}});e("text/x-csharp",{name:"clike",keywords:a("abstract as async await base break case catch checked class const continue default delegate do else enum event explicit extern finally fixed for foreach goto if implicit in interface internal is lock namespace new operator out override params private protected public readonly ref return sealed sizeof stackalloc static struct switch this throw try typeof unchecked unsafe using virtual void volatile while add alias ascending descending dynamic from get global group into join let orderby partial remove select set value var yield"),
types:a("Action Boolean Byte Char DateTime DateTimeOffset Decimal Double Func Guid Int16 Int32 Int64 Object SByte Single String Task TimeSpan UInt16 UInt32 UInt64 bool byte char decimal double short int long object sbyte float string ushort uint ulong"),blockKeywords:a("catch class do else finally for foreach if struct switch try while"),defKeywords:a("class interface namespace struct var"),typeFirstDefinitions:!0,atoms:a("true false null"),hooks:{"@":function(a,d){if(a.eat('"'))return d.tokenize=
q,q(a,d);a.eatWhile(/[\w\$_]/);return"meta"}}});e("text/x-scala",{name:"clike",keywords:a("abstract case catch class def do else extends false final finally for forSome if implicit import lazy match new null object override package private protected return sealed super this throw trait try type val var while with yield _ : = => <- <: <% >: # @ assert assume require print println printf readLine readBoolean readByte readShort readChar readInt readLong readFloat readDouble :: #:: "),types:a("AnyVal App Application Array BufferedIterator BigDecimal BigInt Char Console Either Enumeration Equiv Error Exception Fractional Function IndexedSeq Integral Iterable Iterator List Map Numeric Nil NotNull Option Ordered Ordering PartialFunction PartialOrdering Product Proxy Range Responder Seq Serializable Set Specializable Stream StringBuilder StringContext Symbol Throwable Traversable TraversableOnce Tuple Unit Vector Boolean Byte Character CharSequence Class ClassLoader Cloneable Comparable Compiler Double Exception Float Integer Long Math Number Object Package Pair Process Runtime Runnable SecurityManager Short StackTraceElement StrictMath String StringBuffer System Thread ThreadGroup ThreadLocal Throwable Triple Void"),
multiLineStrings:!0,blockKeywords:a("catch class do else finally for forSome if match switch try while"),defKeywords:a("class def object package trait type val var"),atoms:a("true false null"),indentStatements:!1,indentSwitch:!1,hooks:{"@":function(a){a.eatWhile(/[\w\$_]/);return"meta"},'"':function(a,d){if(!a.match('""'))return!1;d.tokenize=u;return d.tokenize(a,d)},"'":function(a){a.eatWhile(/[\w\$_\xa1-\uffff]/);return"atom"}},modeProps:{closeBrackets:{triples:'"'}}});e(["x-shader/x-vertex","x-shader/x-fragment"],
{name:"clike",keywords:a("sampler1D sampler2D sampler3D samplerCube sampler1DShadow sampler2DShadow const attribute uniform varying break continue discard return for while do if else struct in out inout"),types:a("float int bool void vec2 vec3 vec4 ivec2 ivec3 ivec4 bvec2 bvec3 bvec4 mat2 mat3 mat4"),blockKeywords:a("for while do if else struct"),builtin:a("radians degrees sin cos tan asin acos atan pow exp log exp2 sqrt inversesqrt abs sign floor ceil fract mod min max clamp mix step smoothstep length distance dot cross normalize ftransform faceforward reflect refract matrixCompMult lessThan lessThanEqual greaterThan greaterThanEqual equal notEqual any all not texture1D texture1DProj texture1DLod texture1DProjLod texture2D texture2DProj texture2DLod texture2DProjLod texture3D texture3DProj texture3DLod texture3DProjLod textureCube textureCubeLod shadow1D shadow2D shadow1DProj shadow2DProj shadow1DLod shadow2DLod shadow1DProjLod shadow2DProjLod dFdx dFdy fwidth noise1 noise2 noise3 noise4"),
atoms:a("true false gl_FragColor gl_SecondaryColor gl_Normal gl_Vertex gl_MultiTexCoord0 gl_MultiTexCoord1 gl_MultiTexCoord2 gl_MultiTexCoord3 gl_MultiTexCoord4 gl_MultiTexCoord5 gl_MultiTexCoord6 gl_MultiTexCoord7 gl_FogCoord gl_PointCoord gl_Position gl_PointSize gl_ClipVertex gl_FrontColor gl_BackColor gl_FrontSecondaryColor gl_BackSecondaryColor gl_TexCoord gl_FogFragCoord gl_FragCoord gl_FrontFacing gl_FragData gl_FragDepth gl_ModelViewMatrix gl_ProjectionMatrix gl_ModelViewProjectionMatrix gl_TextureMatrix gl_NormalMatrix gl_ModelViewMatrixInverse gl_ProjectionMatrixInverse gl_ModelViewProjectionMatrixInverse gl_TexureMatrixTranspose gl_ModelViewMatrixInverseTranspose gl_ProjectionMatrixInverseTranspose gl_ModelViewProjectionMatrixInverseTranspose gl_TextureMatrixInverseTranspose gl_NormalScale gl_DepthRange gl_ClipPlane gl_Point gl_FrontMaterial gl_BackMaterial gl_LightSource gl_LightModel gl_FrontLightModelProduct gl_BackLightModelProduct gl_TextureColor gl_EyePlaneS gl_EyePlaneT gl_EyePlaneR gl_EyePlaneQ gl_FogParameters gl_MaxLights gl_MaxClipPlanes gl_MaxTextureUnits gl_MaxTextureCoords gl_MaxVertexAttribs gl_MaxVertexUniformComponents gl_MaxVaryingFloats gl_MaxVertexTextureImageUnits gl_MaxTextureImageUnits gl_MaxFragmentUniformComponents gl_MaxCombineTextureImageUnits gl_MaxDrawBuffers"),
indentSwitch:!1,hooks:{"#":f},modeProps:{fold:["brace","include"]}});e("text/x-nesc",{name:"clike",keywords:a("auto if break case register continue return default do sizeof static else struct switch extern typedef float union for goto while enum const volatileas atomic async call command component components configuration event generic implementation includes interface module new norace nx_struct nx_union post provides signal task uses abstract extends"),types:a("int long char short double float unsigned signed void size_t ptrdiff_t"),
blockKeywords:a("case do else for if switch while struct"),atoms:a("null true false"),hooks:{"#":f},modeProps:{fold:["brace","include"]}});e("text/x-objectivec",{name:"clike",keywords:a("auto if break case register continue return default do sizeof static else struct switch extern typedef float union for goto while enum const volatileinline restrict _Bool _Complex _Imaginery BOOL Class bycopy byref id IMP in inout nil oneway out Protocol SEL self super atomic nonatomic retain copy readwrite readonly"),
types:a("int long char short double float unsigned signed void size_t ptrdiff_t"),atoms:a("YES NO NULL NILL ON OFF true false"),hooks:{"@":function(a){a.eatWhile(/[\w\$]/);return"keyword"},"#":f},modeProps:{fold:"brace"}});e("text/x-squirrel",{name:"clike",keywords:a("base break clone continue const default delete enum extends function in class foreach local resume return this throw typeof yield constructor instanceof static"),types:a("int long char short double float unsigned signed void size_t ptrdiff_t"),
blockKeywords:a("case catch class else for foreach if switch try while"),defKeywords:a("function local class"),typeFirstDefinitions:!0,atoms:a("true false null"),hooks:{"#":f},modeProps:{fold:["brace","include"]}})});