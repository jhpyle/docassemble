#! /usr/bin/python
import ast
import sys

mycode = """\
if b < 6:
  a = 77
  c = 72
else:
  a = 66
sys.exit()
"""

mycode = """\
user.foobar.name.last = 77
if b < 6:
  a = 77
  c = 72
else:
  a = 66
"""

class myextract(ast.NodeVisitor):
    def __init__(self):
        self.stack = []
    def visit_Name(self, node):
        self.stack.append(node.id)
        ast.NodeVisitor.generic_visit(self, node)
    def visit_Attribute(self, node):
        self.stack.append(node.attr)
        ast.NodeVisitor.generic_visit(self, node)

class myvisitnode(ast.NodeVisitor):
    def __init__(self):
        self.names = {}
        self.targets = {}
        self.depth = 0;
    def generic_visit(self, node):
        #print ' ' * self.depth + type(node).__name__
        self.depth += 1
        ast.NodeVisitor.generic_visit(self, node)
        self.depth -= 1
    def visit_Assign(self, node):
        for key, val in ast.iter_fields(node):
            if key == 'targets':
                for subnode in val:
                    crawler = myextract()
                    crawler.visit(subnode)
                    self.targets[".".join(reversed(crawler.stack))] = 1
        self.depth += 1
        ast.NodeVisitor.generic_visit(self, node)
        self.depth -= 1
    def visit_Name(self, node):
        self.names[node.id] = 1
        ast.NodeVisitor.generic_visit(self, node)
    # def visit_Assign(self, node):
    #     for key, val in ast.iter_fields(node):
    #         if key == 'targets':
    #             for subnode in val:
    #                 if type(subnode).__name__ == 'Name':
    #                     self.targets[subnode.id] = 1
    #                 elif type(subnode).__name__ == 'Attribute':
    #                     print "Attribute:"
    #                     for key, val in ast.iter_fields(subnode):
    #                         print str(key) + " " + str(val)
    #     ast.NodeVisitor.generic_visit(self, node)

myvisitor = myvisitnode()
t = ast.parse(mycode)
# print ast.dump(t)
# sys.exit()
myvisitor.visit(t)
predefines = set(globals().keys()) | set(locals().keys())
print "Targets:"
print [item for item in myvisitor.targets.keys() if item not in predefines]
definables = set(predefines) | set(myvisitor.targets.keys())
print "Names:"
print [item for item in myvisitor.names.keys() if item not in definables]
# print "Globals:"
# print globals().keys()
# print "Locals:"
# print locals().keys()
# Module(body=[Assign(targets=[Attribute(value=Attribute(value=Attribute(value=Name(id='user', ctx=Load()), attr='foobar', ctx=Load()), attr='name', ctx=Load()), attr='last', ctx=Store())], value=Num(n=77))])
