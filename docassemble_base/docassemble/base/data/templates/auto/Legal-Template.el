(TeX-add-style-hook
 "Legal-Template"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("$if(documentclass)$$documentclass$$else$article$endif$" "$if(fontsize)$$fontsize$$else$12pt$endif$" "$if(lang)$$lang$" "$endif$$if(papersize)$$papersize$$else$letterpaper$endif$$for(classoption)$" "$classoption$$sep$$endfor$")))
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("fontenc" "T1") ("inputenc" "utf8") ("geometry" "$for(geometry)$$geometry$$sep$" "$endfor$" "left=1in" "right=1in" "top=1in" "bottom=1in" "heightrounded") ("hyperref" "setpagesize=false" "unicode=false" "xetex" "unicode=true") ("ulem" "normalem") ("bidi" "RTLdocument") ("babel" "$lang$")))
   (TeX-run-style-hooks
    "latex2e"
    "$if(documentclass)$$documentclass$$else$article$endif$"
    "$if(documentclass)$$documentclass$$else$article$endif$10"
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
    "mathptmx"
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
    "myfontfamily"
    "myfontsize"
    "euro"
    "tightlist"
    "oldparagraph"
    "oldsubparagraph")
   (LaTeX-add-environments
    "RTL"
    "LTR")
   (LaTeX-add-bibliographies
    "$biblio-files$")
   (LaTeX-add-lengths
    "defaulttopmargin"
    "defaultbottommargin"
    "defaultheadheight"
    "newtop"
    "maxheaderfirst"
    "thisheaderheight"
    "maxheader"
    "maxheaderboth"
    "backup"
    "myindentamount")
   (LaTeX-add-saveboxes
    "headerbox")))

