import re

match_mako = re.compile('<%|\$\{')

print match_mako.match('Were you injured in ${ jurisdiction.state }?')

foob = """[CENTER] This is a line and everything
asdfasdfasdf asdf asdf asdf asdf asd f


"""

foob = re.sub(r'\[CENTER\] *(.+?)\n\n', r'\\begingroup\centering \1\par\endgroup\n\n', foob, flags=re.MULTILINE | re.DOTALL)
print "asdf\n" + foob
