(function(mod) {
  if (typeof exports == "object" && typeof module == "object") { // CommonJS
    console.log( 'module type is CommonJS' );
    mod(
      require("../yaml/yaml"),
      require("../python/python")
    );
  } else if (typeof define == "function" && define.amd) { // AMD
    console.log( 'module type is AMD' );
    define([
      "../yaml/yaml",
      "../python/python"
    ], mod);
  } else { // Plain browser env
    console.log( 'module type is browser' );
    mod( CodeMirror );
  }
})(function(CodeMirror) {
  "use strict";

  CodeMirror.defineMode("yamlmixed", function(){
    let outer = CodeMirror.getMode( {}, "yaml" );
    let inner = CodeMirror.getMode( {}, "python" );

    let innerOptions = {
      open: /^code: /,
      close: /\n[^\s]/,
      mode: inner,
      // delimStyle: 'delim',
      // innerStyle: 'inner',
    };

    return CodeMirror.multiplexingMode( outer, innerOptions );
  });

  CodeMirror.defineMIME("text/x-yaml", "yamlmixed");
  CodeMirror.defineMIME("text/yaml", "yamlmixed");
});
