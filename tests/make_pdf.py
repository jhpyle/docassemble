#! /usr/bin/env python3
import sys
import os
import re
import subprocess

first_part = """\
\\documentclass[letterpaper]{article}
\\usepackage[left=0.5in,right=0.5in,top=0.5in,bottom=0.5in,heightrounded]{geometry}
\\usepackage{fancyvrb}
\\usepackage{graphicx}
\\usepackage{xcolor}
\\usepackage{adjustbox}
\\definecolor{barelyvisible}{gray}{0.99}
\\usepackage{calc}
\\newlength{\\mywidth}
\\newlength{\\myheight}
\\setlength{\\mywidth}{\\dimexpr(\\textwidth-16pt)\\relax}
\\setlength{\\myheight}{\\dimexpr(\\textheight-1in)\\relax}

\\begin{document}
"""

middle_part = """\
\\includegraphics[width=\\mywidth, height=\\myheight, keepaspectratio=true]{%s.png}

\\adjustbox{scale=0.01}{
  \\begin{minipage}[t][0.in][t]{\\mywidth}
  {\\color{barelyvisible}\\tiny
    \\VerbatimInput{%s.json}
  }
  \\end{minipage}
}
"""

end_part = """\
\\end{document}
"""

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.exit("You need to provide the name of a directory")
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        sys.exit("You need to provide the name of a directory")
    with open(directory + ".tex", "w", encoding="utf-8") as fp:
        fp.write(first_part)
        on_first = True
        for f in sorted(os.listdir(directory)):
            if f.endswith('png'):
                base_name = os.path.join(directory, re.sub(r'\.png$', '', f))
                if not on_first:
                    fp.write("\\newpage\n")
                else:
                    on_first = False
                fp.write(middle_part % (base_name, base_name))
        fp.write(end_part)
    try:
        subprocess.run(['pdflatex', directory])
        returnval = 0
    except subprocess.CalledProcessError as err:
        returnval = err.returncode
    if returnval != 0:
        sys.exit("Call to pdflatex returned code " + str(returnval))
    for path in (directory + '.tex', directory + '.log', directory + '.aux'):
        if os.path.exists(path):
            os.remove(path)
