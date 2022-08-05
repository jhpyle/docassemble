import ast
import re

# import sys

fix_assign = re.compile(r'\.(\[[^\]]*\])')
valid_variable_match = re.compile(r'^[^\d][A-Za-z0-9\_]*$')


class myextract(ast.NodeVisitor):

    def __init__(self):
        self.stack = []
        self.in_subscript = 0
        self.in_params = 0
        self.seen_name = False
        self.seen_complexity = False

    def visit_Name(self, node):
        if not (self.in_subscript > 0 and self.seen_name is True):
            self.stack.append(node.id)
            if self.in_subscript > 0:
                self.seen_name = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Call(self, node):
        self.seen_complexity = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Attribute(self, node):
        self.stack.append(node.attr)
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Subscript(self, node):
        if isinstance(node.slice, ast.Name):
            self.stack.append('[' + str(node.slice.id) + ']')
            self.in_subscript += 1
            self.seen_name = False
        elif isinstance(node.slice, ast.Constant):
            self.stack.append('[' + repr(node.slice.value) + ']')
            self.in_subscript += 1
            self.seen_name = False
        elif isinstance(node.slice, ast.Index):
            if isinstance(node.slice.value, ast.Name):
                self.stack.append('[' + str(node.slice.value.id) + ']')
                self.in_subscript += 1
                self.seen_name = False
            elif isinstance(node.slice.value, ast.Constant):
                self.stack.append('[' + repr(node.slice.value.value) + ']')
                self.in_subscript += 1
                self.seen_name = False
            elif hasattr(node.slice.value, 'n'):
                self.stack.append('[' + repr(node.slice.value.n) + ']')
                self.in_subscript += 1
                self.seen_name = False
            elif hasattr(node.slice.value, 's'):
                self.stack.append('[' + repr(str(node.slice.value.s)) + ']')
                self.in_subscript += 1
                self.seen_name = False
            else:
                self.seen_complexity = 1
        else:
            self.seen_complexity = 1
        ast.NodeVisitor.generic_visit(self, node)
        if hasattr(node.slice, 'slice') and (hasattr(node.slice.value, 'id') or hasattr(node.slice.value, 'n') or hasattr(node.slice.value, 'value')):
            self.in_subscript -= 1


class myvisitnode(ast.NodeVisitor):

    def __init__(self):
        self.names = {}
        self.targets = {}
        self.depth = 0
        self.calls = set()

    def generic_visit(self, node):
        # logmessage(' ' * self.depth + type(node).__name__)
        self.depth += 1
        ast.NodeVisitor.generic_visit(self, node)
        self.depth -= 1

    def visit_Call(self, node):
        self.calls.add(node.func)
        if hasattr(node.func, 'id') and node.func.id in ['showif', 'showifdef', 'value', 'defined'] and len(node.args) and node.args[0].__class__.__name__ == 'Constant' and hasattr(node.args[0], 'value') and re.search(r'^[^\d]', node.args[0].value) and not re.search(r'[^A-Z_a-z0-9\.\"\'\[\] ]', node.args[0].value):
            self.names[node.args[0].value] = 1
        if hasattr(node.func, 'id') and node.func.id in ['define'] and len(node.args) and node.args[0].__class__.__name__ == 'Constant' and hasattr(node.args[0], 'value') and re.search(r'^[^\d]', node.args[0].value) and not re.search(r'[^A-Z_a-z0-9\.\"\'\[\] ]', node.args[0].value):
            self.targets[node.args[0].value] = 1
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Subscript(self, node):
        if node not in self.calls:
            crawler = myextract()
            crawler.visit(node)
            if not crawler.seen_complexity:
                self.names[fix_assign.sub(r'\1', (".".join(reversed(crawler.stack))))] = 1
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Attribute(self, node):
        if node not in self.calls:
            crawler = myextract()
            crawler.visit(node)
            if not crawler.seen_complexity:
                self.names[fix_assign.sub(r'\1', (".".join(reversed(crawler.stack))))] = 1
        ast.NodeVisitor.generic_visit(self, node)

    def visit_ExceptHandler(self, node):
        if node.name is not None and hasattr(node.name, 'id') and node.name.id is not None:
            self.targets[node.name.id] = 1
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Assign(self, node):
        for key, val in ast.iter_fields(node):
            if key == 'targets':
                for subnode in val:
                    if isinstance(subnode, ast.Tuple):
                        for subsubnode in subnode.elts:
                            crawler = myextract()
                            crawler.visit(subsubnode)
                            self.targets[fix_assign.sub(r'\1', ".".join(reversed(crawler.stack)))] = 1
                    else:
                        crawler = myextract()
                        crawler.visit(subnode)
                        self.targets[fix_assign.sub(r'\1', ".".join(reversed(crawler.stack)))] = 1
        self.depth += 1
        # ast.NodeVisitor.generic_visit(self, node)
        self.generic_visit(node)
        self.depth -= 1

    def visit_AugAssign(self, node):
        for key, val in ast.iter_fields(node):
            if key == 'target':
                crawler = myextract()
                crawler.visit(val)
                self.targets[fix_assign.sub(r'\1', ".".join(reversed(crawler.stack)))] = 1
        self.depth += 1
        # ast.NodeVisitor.generic_visit(self, node)
        self.generic_visit(node)
        self.depth -= 1

    def visit_AnnAssign(self, node):
        for key, val in ast.iter_fields(node):
            if key == 'target':
                crawler = myextract()
                crawler.visit(val)
                self.targets[fix_assign.sub(r'\1', ".".join(reversed(crawler.stack)))] = 1
        self.depth += 1
        # ast.NodeVisitor.generic_visit(self, node)
        self.generic_visit(node)
        self.depth -= 1

    def visit_FunctionDef(self, node):
        if hasattr(node, 'name'):
            self.targets[node.name] = 1

    def visit_Import(self, node):
        for alias in node.names:
            if alias.asname is None:
                the_name = alias.name
            else:
                the_name = alias.asname
            while re.search(r'\.', the_name):
                self.targets[the_name] = 1
                the_name = re.sub(r'\.[^\.]+$', '', the_name)
            self.targets[the_name] = 1

    def visit_ImportFrom(self, node):
        for alias in node.names:
            if alias.asname is None:
                the_name = alias.name
            else:
                the_name = alias.asname
            while re.search(r'\.', the_name):
                self.targets[the_name] = 1
                the_name = re.sub(r'\.[^\.]+$', '', the_name)
            self.targets[the_name] = 1

    def visit_GeneratorExp(self, node):
        for comp in node.generators:
            if isinstance(comp.target, ast.Name):
                self.targets[comp.target.id] = 1
            elif isinstance(comp.target, ast.Tuple):
                for subtarget in comp.target.elts:
                    if isinstance(subtarget, ast.Name):
                        self.targets[subtarget.id] = 1
        self.generic_visit(node)

    def visit_Lambda(self, node):
        for arg in node.args.posonlyargs:
            self.targets[arg.arg] = 1
        for arg in node.args.args:
            self.targets[arg.arg] = 1
        for arg in node.args.kwonlyargs:
            self.targets[arg.arg] = 1
        self.generic_visit(node)

    def visit_ListComp(self, node):
        for comp in node.generators:
            if isinstance(comp.target, ast.Name):
                self.targets[comp.target.id] = 1
            elif isinstance(comp.target, ast.Tuple):
                for subtarget in comp.target.elts:
                    if isinstance(subtarget, ast.Name):
                        self.targets[subtarget.id] = 1
        self.generic_visit(node)

    def visit_DictComp(self, node):
        for comp in node.generators:
            if isinstance(comp.target, ast.Name):
                self.targets[comp.target.id] = 1
            elif isinstance(comp.target, ast.Tuple):
                for subtarget in comp.target.elts:
                    if isinstance(subtarget, ast.Name):
                        self.targets[subtarget.id] = 1
        self.generic_visit(node)

    def visit_SetComp(self, node):
        for comp in node.generators:
            if isinstance(comp.target, ast.Name):
                self.targets[comp.target.id] = 1
            elif isinstance(comp.target, ast.Tuple):
                for subtarget in comp.target.elts:
                    if isinstance(subtarget, ast.Name):
                        self.targets[subtarget.id] = 1
        self.generic_visit(node)

    def visit_For(self, node):
        if isinstance(node.target, ast.Name):
            self.targets[node.target.id] = 1
        elif isinstance(node.target, ast.Tuple):
            for subtarget in node.target.elts:
                if isinstance(subtarget, ast.Name):
                    self.targets[subtarget.id] = 1
        self.generic_visit(node)

    def visit_Name(self, node):
        self.names[node.id] = 1
        # ast.NodeVisitor.generic_visit(self, node)
        self.generic_visit(node)


class detectIllegal(ast.NodeVisitor):

    def __init__(self):
        self.illegal = False

    def visit_FunctionDef(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_ExceptHandler(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_ClassDef(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Return(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Delete(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Assign(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_AugAssign(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Print(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_For(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_While(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_If(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_With(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Raise(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_TryExcept(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_TryFinally(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Assert(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Import(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_ImportFrom(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Exec(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Global(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Pass(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Break(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Continue(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_BoolOp(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_BinOp(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_UnaryOp(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Lambda(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_IfExp(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Dict(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Set(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_ListComp(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_SetComp(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_DictComp(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_GeneratorExp(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Yield(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Compare(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Call(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Repr(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_List(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Tuple(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)


class detectIllegalQuery(ast.NodeVisitor):

    def __init__(self):
        self.illegal = False

    def visit_FunctionDef(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_ExceptHandler(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_ClassDef(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Return(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Delete(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Assign(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_AugAssign(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Print(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_For(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_While(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_If(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_With(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Raise(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_TryExcept(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_TryFinally(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Assert(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Import(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_ImportFrom(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Exec(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Global(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Pass(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Break(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Continue(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Lambda(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_IfExp(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Dict(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Set(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_ListComp(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_SetComp(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_DictComp(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_GeneratorExp(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Yield(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Call(self, node):
        try:
            assert node.func.attr in ('In', 'Like', 'And', 'Or')
        except:
            self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Repr(self, node):
        self.illegal = True
        ast.NodeVisitor.generic_visit(self, node)
