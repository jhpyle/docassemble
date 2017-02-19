import docassemble.base.parse
import ast
t=ast.parse("(foo, bar) = (1, 2)")
myvisitor = docassemble.base.parse.myvisitnode()
myvisitor.visit(t)
print str(myvisitor.targets.keys())
