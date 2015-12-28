(TeX-add-style-hook
 "Legal-Template"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("$documentclass$" "$if(fontsize)$$fontsize$" "$endif$$if(lang)$$lang$" "$endif$$if(papersize)$$papersize$" "$endif$$for(classoption)$$classoption$$sep$" "$endfor$")))
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("fontenc" "T1") ("inputenc" "utf8") ("geometry" "$for(geometry)$$geometry$$sep$" "$endfor$") ("hyperref" "setpagesize=false" "unicode=false" "xetex" "unicode=true") ("ulem" "normalem") ("bidi" "RTLdocument") ("babel" "$lang$")))
   (TeX-run-style-hooks
    "latex2e"
    "$documentclass$"
    "$documentclass$10"
    "ifthen"
    "setspace"
    "amssymb"
    "amsmath"
    "ifxetex"
    "ifluatex"
    "fixltx2e"
    "fontenc"
    "inputenc"
    "$fontfamily$"
    "lmodern"
    "eurosym"
    "mathspec"
    "xltxtra"
    "xunicode"
    "fontspec"
    "upquote"
    "microtype"
    "calc"
    "geometry"
    "natbib"
    "biblatex"
    "listings"
    "fancyvrb"
    "longtable"
    "booktabs"
    "graphicx"
    "hyperref"
    "ulem"
    "bidi"
    "polyglossia"
    "babel")
   (TeX-add-symbols
    '("LR" 1)
    '("RL" 1)
    "euro"
    "headerlines"
    "tightlist"
    "oldparagraph"
    "oldsubparagraph")
   (LaTeX-add-environments
    "RTL"
    "LTR")
   (LaTeX-add-bibliographies
    "$biblio-files$")
   (LaTeX-add-lengths
    "mynegspace"
    "myindentamount")))

