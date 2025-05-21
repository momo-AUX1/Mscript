"""
it.py - Interpreter for the Mscript language.
This module defines the MscriptInterpreter class, which interprets
Mscript code using the Lark parser library.
It is designed to be used with the Lark parser, which is defined in
the language.def file.
The interpreter supports basic constructs such as:
- Variable assignment
- Arithmetic operations
- Control flow (if, while, for)
- Function definitions and calls
- Input and output
- Lists and dictionaries
- Type conversion (str, int, type)
- Built-in functions (input, str, int, type)

version 0.3 (planned):
- Add support for more built-in functions
- try/except for error handling

version 0.2:
- Improved interpreter

version 0.1:
- Initial version
"""

import ast
from lark import Lark, Tree, Token
from lark.visitors import Interpreter as LarkInterpreter
import sys
import platform
sys.tracebacklimit = 0

__VERSION__ = "0.2"
__AUTHOR__  = "Momo-AUX1"
__DATE__    = "2025-05-21"

language_definition = open("language.def").read()

class ReturnException(Exception):
    """Unwind the current function frame with a return value."""
    def __init__(self, value):
        self.value = value

class MscriptInterpreter(LarkInterpreter):
    """Interpreter for the Mscript language."""
    def __init__(self):
        super().__init__()
        self.global_env = {}
        self.env        = self.global_env
        self.functions  = {}

    def start(self, tree):
        for stmt in tree.children:
            if isinstance(stmt, Tree) and stmt.data == 'func_def':
                self.visit(stmt)

        for stmt in tree.children:
            if not (isinstance(stmt, Tree) and stmt.data == 'func_def'):
                try:
                    self.visit(stmt)
                except ReturnException:
                    pass

    def assign(self, tree):
        name_tok, expr = tree.children
        val = self.visit(expr)
        self.env[str(name_tok)] = val
        return val

    def index_assign(self, tree):
        container = self.visit(tree.children[0])
        idx       = self.visit(tree.children[1])
        val       = self.visit(tree.children[2])
        container[idx] = val
        return val

    def print_stmt(self, tree):
        vals = [self.visit(c) for c in tree.children]
        print(*vals)
        return vals[-1] if vals else None
    
    def input_expr(self, tree):
        tok = tree.children[0]
        if not isinstance(tok, Token):
            raise TypeError(f"Expected Token, got {type(tok).__name__}")
        prompt = ast.literal_eval(str(tok))
        return input(prompt)


    def expr_stmt(self, tree):
        return self.visit(tree.children[0])

    def return_stmt(self, tree):
        val = self.visit(tree.children[0])
        raise ReturnException(val)

    def if_stmt(self, tree):
        idx = 0
        n   = len(tree.children)

        cond = self.visit(tree.children[idx])
        idx += 1
        if cond:
            for stmt in tree.children[idx].children:
                self.visit(stmt)
            return
        idx += 1 

        while idx < n:
            node = tree.children[idx]
            if isinstance(node, Tree) and node.data == 'block':
                for stmt in node.children:
                    self.visit(stmt)
                return

            cond  = self.visit(node)
            block = tree.children[idx + 1]
            if cond:
                for stmt in block.children:
                    self.visit(stmt)
                return
            idx += 2

    def while_stmt(self, tree):
        cond_tree = tree.children[0]
        block     = tree.children[1]
        while self.visit(cond_tree):
            for stmt in block.children:
                self.visit(stmt)

    def for_stmt(self, tree):
        var_tok  = tree.children[0]
        iterable = self.visit(tree.children[1])
        block    = tree.children[2]
        for v in iterable:
            self.env[str(var_tok)] = v
            for stmt in block.children:
                self.visit(stmt)

    def func_def(self, tree):
        name_tok = tree.children[0]
        params = []
        block  = None
        for child in tree.children[1:]:
            if isinstance(child, Tree):
                if child.data == 'params':
                    params = [str(p) for p in child.children]
                elif child.data == 'block':
                    block = child

        if block is None:
            raise SyntaxError(f"Function ‘{name_tok}’ has no body")

        self.functions[str(name_tok)] = (params, block)

    def func_call(self, tree):
        name_tok = tree.children[0]
        name     = str(name_tok)
        
        if name == 'input':
            args = (tree.children[1].children
                    if len(tree.children)>1 and isinstance(tree.children[1], Tree) and tree.children[1].data=='args' else [])            
            if len(args) != 1:
                raise TypeError(f"input() expects 1 arg, got {len(args)}")
            prompt = self.visit(args[0])
            return input(str(prompt))

        if name == 'str':
            args = (tree.children[1].children
                    if len(tree.children)>1 and isinstance(tree.children[1], Tree) and tree.children[1].data=='args'
                    else [])
            if len(args) != 1:
                raise TypeError(f"str() expects 1 arg, got {len(args)}")
            return str(self.visit(args[0]))

        if name == 'int':
            args = (tree.children[1].children
                    if len(tree.children)>1 and isinstance(tree.children[1], Tree) and tree.children[1].data=='args'
                    else [])
            if len(args) != 1:
                raise TypeError(f"int() expects 1 arg, got {len(args)}")
            return int(self.visit(args[0]))

        if name == 'type':
            args = (tree.children[1].children
                    if len(tree.children)>1 and isinstance(tree.children[1], Tree) and tree.children[1].data=='args'
                    else [])
            if len(args) != 1:
                raise TypeError(f"type() expects 1 arg, got {len(args)}")
            val = self.visit(args[0])
            return type(val).__name__
        
        if name in ('len','keys','values'):
            args = (tree.children[1].children
                    if len(tree.children)>1 and isinstance(tree.children[1], Tree) and tree.children[1].data=='args'
                    else [])
            if len(args) != 1:
                raise TypeError(f"{name}() expects 1 arg, got {len(args)}")
            obj = self.visit(args[0])
            if name == 'len':
                return len(obj)
            if name == 'keys':
                if not isinstance(obj, dict):
                    raise TypeError("keys() expects a dict")
                return list(obj.keys())
            if name == 'values':
                if not isinstance(obj, dict):
                    raise TypeError("values() expects a dict")
                return list(obj.values())

        if len(tree.children) > 1 and isinstance(tree.children[1], Tree) and tree.children[1].data == 'args':
            arg_trees = tree.children[1].children
        else:
            arg_trees = []

        if name not in self.functions:
            raise NameError(f"Function '{name}' is not defined.")
        params, block = self.functions[name]
        if len(params) != len(arg_trees):
            raise TypeError(f"{name}() expects {len(params)} args, got {len(arg_trees)}")

        arg_vals = [self.visit(a) for a in arg_trees]

        old_env    = self.env
        self.env   = {}
        for pname, pval in zip(params, arg_vals):
            self.env[pname] = pval

        result = None
        for stmt in block.children:
            try:
                self.visit(stmt)
            except ReturnException as ret:
                result = ret.value
                break

        self.env = old_env
        return result

    def add(self, tree): return self.visit(tree.children[0]) + self.visit(tree.children[1])
    def sub(self, tree): return self.visit(tree.children[0]) - self.visit(tree.children[1])
    def mul(self, tree): return self.visit(tree.children[0]) * self.visit(tree.children[1])
    def div(self, tree): return self.visit(tree.children[0]) / self.visit(tree.children[1])
    def gt( self, tree): return self.visit(tree.children[0]) >  self.visit(tree.children[1])
    def lt( self, tree): return self.visit(tree.children[0]) <  self.visit(tree.children[1])
    def eq( self, tree): return self.visit(tree.children[0]) == self.visit(tree.children[1])
    def ne( self, tree): return self.visit(tree.children[0]) != self.visit(tree.children[1])
    def mod(self, tree): return self.visit(tree.children[0]) % self.visit(tree.children[1])
    def pow(self, tree): return self.visit(tree.children[0]) ** self.visit(tree.children[1])


    def number(self, tree):
        """Parse ints or floats automatically."""
        tok  = tree.children[0]
        text = str(tok)
        return float(text) if "." in text else int(text)

    def string( self, tree): return ast.literal_eval(tree.children[0])
    def var(    self, tree):
        name = str(tree.children[0])
        if name in self.env:        return self.env[name]
        if name in self.global_env: return self.global_env[name]
        raise NameError(f"Variable '{name}' is not defined.")

    def list(self, tree):
        return [self.visit(c) for c in tree.children]

    def pair(self, tree):
        k = self.visit(tree.children[0])
        v = self.visit(tree.children[1])
        return (k, v)

    def dict(self, tree):
        return dict(self.visit(c) for c in tree.children)

    def get_item(self, tree):
        container = self.visit(tree.children[0])
        idx       = self.visit(tree.children[1])
        return container[idx]
    
    def true(self, tree):
        return True

    def false(self, tree):
        return False

    def none(self, tree):
        return None
    
    def or_op(self, tree):
        left, right = tree.children
        return self.visit(left) or self.visit(right)

    def and_op(self, tree):
        left, right = tree.children
        return self.visit(left) and self.visit(right)

    def not_op(self, tree):
        (operand,) = tree.children
        return not self.visit(operand)
    
    def in_op(self, tree):
        left, right = tree.children
        return self.visit(left) in self.visit(right)
    
    def import_stmt(self, tree):
        mod_tree = tree.children[0]
        names    = [str(n) for n in mod_tree.children]
        name     = ".".join(names)

        if name == "python":
            import importlib, builtins
            class PythonModuleProxy:
                def __getattr__(self, attr):
                    if hasattr(builtins, attr):
                        return getattr(builtins, attr)
                    return importlib.import_module(attr)
            self.global_env["python"] = PythonModuleProxy()
        else:
            from lark import Lark
            parser = Lark(language_definition, parser='lalr')
            code   = open(f"{name}.mscript").read()
            tree2  = parser.parse(code)
            sub    = MscriptInterpreter()
            sub.visit(tree2)
            self.global_env[name] = sub.global_env


if __name__ == '__main__':
    argv = sys.argv

    if len(argv) > 3:
        raise Exception(f"Too many arguments expected 2 got {len(argv) - 1}")
    
    if argv[1] == "--version":
        print(f"Mscript Interpreter version {__VERSION__} by {__AUTHOR__} ({__DATE__}) ({platform.system()})")
        sys.exit(0)

    if not argv[1].endswith(".mscript"):
        raise Exception(f"Mscript files must end in .mscript suffix and be the first argument. Got: {argv[1]}")
    
    parser = Lark(language_definition, parser='lalr')
    tree   = parser.parse(open(argv[1]).read())
    MscriptInterpreter().visit(tree)
    if "--debug" in argv:
        print(tree.pretty())
