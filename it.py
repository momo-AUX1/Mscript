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

version 0.5 (planned):
- True STD library

version 0.4 :
- Add support for more built-in functions
- try/except for error handling

version 0.3:
- Added support for dotted names in function calls
- Added support for dotted names in variable assignments

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
import os
from lark.exceptions import UnexpectedInput
sys.tracebacklimit = 0

__VERSION__ = "0.4.6"
__AUTHOR__  = "Momo-AUX1"
__DATE__    = "2025-05-21"

language_definition = open("language.def").read()

def _wrap_error_with_loc(method):
    def wrapper(self, tree):
        try:
            return method(self, tree)
        except Exception as e:
            meta = getattr(tree, "meta", None)
            if meta:
                loc = f"{self.filename}:{meta.line}:{meta.column}"
            else:
                loc = self.filename
            raise type(e)(f"{loc}: {e}")
    return wrapper

class ReturnException(Exception):
    """Unwind the current function frame with a return value."""
    def __init__(self, value):
        self.value = value
    
class BreakException(Exception):
    """Unwind loop with a break."""
    pass

class ContinueException(Exception):
    """Unwind loop with a continue."""
    pass

class MscriptInterpreter(LarkInterpreter):
    """Interpreter for the Mscript language."""
    def __init__(self, filename="<string>"):
        super().__init__()
        self.global_env = {}
        self.env        = self.global_env
        self.functions  = {}
        self.filename   = filename

    def _dispatch_userfunc(self, tree, func):
        """Wrap every node-visit to attach file/line/col on errors."""
        try:
            return super()._dispatch_userfunc(tree, func)
        except Exception as e:
            meta = getattr(tree, "meta", None)
            if meta:
                loc = f"{self.filename}:{meta.line}:{meta.column}"
            else:
                loc = self.filename
            raise type(e)(f"{loc}: {e}")

    def start(self, tree):
        """The main entry point for the interpreter."""
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
        """Assign a value to a variable."""
        name_tok, expr = tree.children
        val = self.visit(expr)
        self.env[str(name_tok)] = val
        return val

    def index_assign(self, tree):
        """Assign a value to an index in a list or dict."""
        container = self.visit(tree.children[0])
        idx       = self.visit(tree.children[1])
        val       = self.visit(tree.children[2])
        container[idx] = val
        return val

    def print_stmt(self, tree):
        """Print the value of an expression."""
        vals = [self.visit(c) for c in tree.children]
        print(*vals)
        return vals[-1] if vals else None
    
    def input_expr(self, tree):
        """Get user input."""
        tok = tree.children[0]
        if not isinstance(tok, Token):
            raise TypeError(f"Expected Token, got {type(tok).__name__}")
        prompt = ast.literal_eval(str(tok))
        return input(prompt)


    def expr_stmt(self, tree):
        """Evaluate an expression."""
        return self.visit(tree.children[0])

    def return_stmt(self, tree):
        """Return a value from a function."""
        val = self.visit(tree.children[0])
        raise ReturnException(val)

    def if_stmt(self, tree):
        """Evaluate an if statement."""
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
        """Evaluate a while statement."""
        cond_tree = tree.children[0]
        block     = tree.children[1]
        while self.visit(cond_tree):
            try:
                for stmt in block.children:
                    self.visit(stmt)
            except ContinueException:
                continue
            except BreakException:
                break

    def for_stmt(self, tree):
        """Evaluate a for statement."""
        var_tok  = tree.children[0]
        iterable = self.visit(tree.children[1])
        block    = tree.children[2]
        for v in iterable:
            self.env[str(var_tok)] = v
            try:
                for stmt in block.children:
                    self.visit(stmt)
            except ContinueException:
                continue
            except BreakException:
                break

    def break_stmt(self, tree):
        """Handle ‘break’."""
        raise BreakException()

    def continue_stmt(self, tree):
        """Handle ‘continue’."""
        raise ContinueException()
    
    def try_stmt(self, tree):
        """
        Execute a `try` block; if an exception is raised, run its `catch` block.
        Optional `catch(e)` binds the exception to e, but only within that block.
        """
        try_block     = tree.children[0]
        catch_clause  = tree.children[1]

        cc_children = catch_clause.children
        if len(cc_children) == 1 and isinstance(cc_children[0], Tree):
            var_name   = None
            catch_block = cc_children[0]
        elif (len(cc_children) == 2
              and isinstance(cc_children[0], Token)
              and isinstance(cc_children[1], Tree)):
            var_name    = str(cc_children[0])
            catch_block = cc_children[1]
        else:
            raise SyntaxError(f"{self.filename}: invalid catch clause")

        try:
            for stmt in try_block.children:
                self.visit(stmt)
        except Exception as exc:
            if var_name:
                had_old = var_name in self.env
                old_val = self.env.get(var_name)
                self.env[var_name] = exc

            for stmt in catch_block.children:
                self.visit(stmt)

            if var_name:
                if had_old:
                    self.env[var_name] = old_val
                else:
                    del self.env[var_name]

    def func_def(self, tree):
        """Define a function."""
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
        """Evaluate a function call."""
        node = tree.children[0]
        if isinstance(node, Tree) and node.data in ("dotted_name", "dotted_name_expr"):
            parts = [str(tok) for tok in node.children]
            name  = ".".join(parts)
        else:
            name  = str(node)
        
        if name.startswith("python."):
            parts = name.split(".")
            obj   = self.global_env.get(parts[0])
            for attr in parts[1:]:
                obj = getattr(obj, attr)
            arg_trees = (tree.children[1].children
                         if len(tree.children)>1
                            and isinstance(tree.children[1], Tree)
                            and tree.children[1].data=='args'
                         else [])
            arg_vals = [self.visit(a) for a in arg_trees]
            return obj(*arg_vals)
        
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
        
        if name == 'bytes':
            arg_nodes = (tree.children[1].children
                         if len(tree.children)>1
                            and isinstance(tree.children[1], Tree)
                            and tree.children[1].data=='args'
                         else [])
            vals = [self.visit(n) for n in arg_nodes]
            if len(vals) == 1:
                v = vals[0]
                if isinstance(v, str):
                    return v.encode()
                return bytes(v)
            elif len(vals) == 2:
                s, enc = vals
                if not isinstance(s, str) or not isinstance(enc, str):
                    raise TypeError('bytes(str, encoding) args must be (str, str)')
                return s.encode(enc)
            else:
                raise TypeError(f"bytes() expects 1 or 2 args, got {len(vals)}")

        if name == 'encode':
            arg_nodes = (tree.children[1].children
                         if len(tree.children)>1
                            and isinstance(tree.children[1], Tree)
                            and tree.children[1].data=='args'
                         else [])
            vals = [self.visit(n) for n in arg_nodes]
            if len(vals) == 1:
                s = vals[0]
                if not isinstance(s, str):
                    raise TypeError('encode() first arg must be a string')
                return s.encode()
            elif len(vals) == 2:
                s, enc = vals
                if not isinstance(s, str) or not isinstance(enc, str):
                    raise TypeError('encode() args must be (str, str)')
                return s.encode(enc)
            else:
                raise TypeError(f"encode() expects 1 or 2 args, got {len(vals)}")
        
        if name == 'read':
            arg_nodes = (tree.children[1].children
                         if len(tree.children)>1
                            and isinstance(tree.children[1], Tree)
                            and tree.children[1].data=='args'
                         else [])
            args = [self.visit(n) for n in arg_nodes]
            if len(args) == 1:
                filename = args[0]
                with open(filename, 'r') as f:
                    return f.read()
            elif len(args) == 2:
                filename, mode = args
                if mode in ('b','bytes','rb'):
                    with open(filename, 'rb') as f:
                        return f.read()
                else:
                    with open(filename, 'r') as f:
                        return f.read()
            else:
                raise TypeError(f"read() expects 1 or 2 args, got {len(args)}")

        if name == 'write':
            arg_nodes = (tree.children[1].children
                         if len(tree.children)>1
                            and isinstance(tree.children[1], Tree)
                            and tree.children[1].data=='args'
                         else [])
            args = [self.visit(n) for n in arg_nodes]
            if len(args) != 2:
                raise TypeError(f"write() expects 2 args, got {len(args)}")
            filename, data = args
            mode = 'wb' if isinstance(data, (bytes, bytearray)) else 'w'
            with open(filename, mode) as f:
                return f.write(data)
        
        if name == 'decode':
            arg_nodes = (tree.children[1].children
                         if len(tree.children)>1
                            and isinstance(tree.children[1], Tree)
                            and tree.children[1].data=='args'
                         else [])
            vals = [self.visit(n) for n in arg_nodes]
            if len(vals) == 1:
                b = vals[0]
                if not isinstance(b, (bytes, bytearray)):
                    raise TypeError('decode() first arg must be bytes')
                return b.decode()
            elif len(vals) == 2:
                b, enc = vals
                if not isinstance(b, (bytes, bytearray)) or not isinstance(enc, str):
                    raise TypeError('decode() args must be (bytes, str)')
                return b.decode(enc)
            else:
                raise TypeError(f"decode() expects 1 or 2 args, got {len(vals)}")

        if name == 'system':
            arg_nodes = (tree.children[1].children
                         if len(tree.children)>1
                            and isinstance(tree.children[1], Tree)
                            and tree.children[1].data=='args'
                         else [])
            vals = [self.visit(n) for n in arg_nodes]
            if len(vals) != 1:
                raise TypeError(f"system() expects 1 arg, got {len(vals)}")
            cmd = vals[0]
            os.system(str(cmd))
            return 
        
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
            meta = getattr(tree, "meta", None)
            if meta:
                loc = f"{self.filename}:{meta.line}:{meta.column}"
            else:
                loc = self.filename
            raise NameError(f"{loc}: Function '{name}' is not defined.")
        params, block = self.functions[name]
        if len(params) != len(arg_trees):
            meta = getattr(tree, "meta", None)
            if meta:
                loc = f"{self.filename}:{meta.line}:{meta.column}"
            else:
                loc = self.filename
            raise TypeError(f"{loc}: {name}() expects {len(params)} args, got {len(arg_trees)}")

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

    @_wrap_error_with_loc
    def add(self, tree): return self.visit(tree.children[0]) + self.visit(tree.children[1])

    @_wrap_error_with_loc
    def sub(self, tree): return self.visit(tree.children[0]) - self.visit(tree.children[1])
    
    @_wrap_error_with_loc
    def mul(self, tree): return self.visit(tree.children[0]) * self.visit(tree.children[1])
    
    @_wrap_error_with_loc
    def div(self, tree): return self.visit(tree.children[0]) / self.visit(tree.children[1])
    
    @_wrap_error_with_loc
    def gt(self, tree): return self.visit(tree.children[0]) > self.visit(tree.children[1])
    
    @_wrap_error_with_loc
    def lt(self, tree): return self.visit(tree.children[0]) < self.visit(tree.children[1])
    
    @_wrap_error_with_loc
    def eq(self, tree): return self.visit(tree.children[0]) == self.visit(tree.children[1])
    
    @_wrap_error_with_loc
    def ne(self, tree): return self.visit(tree.children[0]) != self.visit(tree.children[1])
    
    @_wrap_error_with_loc
    def mod(self, tree): return self.visit(tree.children[0]) % self.visit(tree.children[1])
    
    @_wrap_error_with_loc
    def pow(self, tree): return self.visit(tree.children[0]) ** self.visit(tree.children[1])

    @_wrap_error_with_loc
    def number(self, tree):
        """Parse ints or floats automatically."""
        tok  = tree.children[0]
        text = str(tok)
        return float(text) if "." in text else int(text)
    
    @_wrap_error_with_loc
    def string( self, tree): return ast.literal_eval(tree.children[0])

    @_wrap_error_with_loc
    def bytes_literal(self, tree):  return ast.literal_eval(str(tree.children[0]))

    def var(self, tree):
        """Get the value of a variable, or report its undefinition with file:line:col."""
        tok  = tree.children[0]       
        name = str(tok)
        if name in self.env:
            return self.env[name]
        if name in self.global_env:
            return self.global_env[name]
        line, col = tok.line, tok.column
        raise NameError(f"{self.filename}:{line}:{col}: Variable '{name}' is not defined.")

    def list(self, tree):
        return [self.visit(c) for c in tree.children]

    def pair(self, tree):
        """Parse a key-value pair."""
        k = self.visit(tree.children[0])
        v = self.visit(tree.children[1])
        return (k, v)

    def dict(self, tree):
        return dict(self.visit(c) for c in tree.children)

    def get_item(self, tree):
        """Get an item from a list or dict."""
        container = self.visit(tree.children[0])
        idx       = self.visit(tree.children[1])
        try:
            return container[idx]
        except KeyError as e:
            meta = getattr(tree, "meta", None)
            loc = f"{self.filename}:{meta.line}:{meta.column}" if meta else self.filename
            raise KeyError(f"{loc}: key '{e.args[0]}' not found")
    
    def get_attr(self, tree):
        """Get an attribute from an object."""
        try:
            obj  = self.visit(tree.children[0])
            attr = str(tree.children[1])
            if isinstance(obj, dict) and attr in obj:
                return obj[attr]
            return getattr(obj, attr)
        except AttributeError as e:
            meta = getattr(tree, "meta", None)
            if meta:
                loc = f"{self.filename}:{meta.line}:{meta.column}"
            else:
                loc = self.filename
            raise AttributeError(f"{loc}: {e}")
    
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
        """Import a module or a function from a module."""
        node = tree.children[0]
        if isinstance(node, Tree) and node.data == 'dotted_name':
            names = [str(tok) for tok in node.children]
            name  = ".".join(names)
        else:
            name  = str(node)

        if name == "python":
            import importlib, builtins
            class PythonModuleProxy:
                def __getattr__(self, attr):
                    if hasattr(builtins, attr):
                        return getattr(builtins, attr)
                    return importlib.import_module(attr)
            self.global_env["python"] = PythonModuleProxy()
        else:
            from lark import Lark, UnexpectedInput
            module_file = f"{name}.mscript"

            parser = Lark(language_definition,
                          parser='lalr',
                          propagate_positions=True)
            try:
                text = open(module_file).read()
            except FileNotFoundError:
                meta = getattr(tree, "meta", None)
                if meta:
                    loc = f"{self.filename}:{meta.line}:{meta.column}"
                else:
                    loc = self.filename
                raise SyntaxError(f"{loc}: Module '{name}' not found (could not open '{module_file}')")
            try:
                tree2 = parser.parse(text)
            except UnexpectedInput as e:
                raise SyntaxError(f"{module_file}:{e.line}:{e.column}: "
                                  f"Syntax error in imported module")

            sub = MscriptInterpreter(filename=module_file)
            try:
                sub.visit(tree2)
            except Exception as e:
                meta = getattr(tree, "meta", None)
                if meta:
                    loc = f"{self.filename}:{meta.line}:{meta.column}"
                else:
                    loc = self.filename
                raise type(e)(
                    f"{loc}: error importing '{name}' ({module_file}): {e}"
                )

            self.global_env[name] = sub.global_env
            for fname, (params, block) in sub.functions.items():
                self.functions[f"{name}.{fname}"] = (params, block)
    
    def dotted_name_expr(self, tree):
        """Resolve a dotted name expression."""
        if (len(tree.children) == 1
            and isinstance(tree.children[0], Tree)
            and tree.children[0].data == 'dotted_name'):
            tree = tree.children[0]

        if (len(tree.children) == 1
            and isinstance(tree.children[0], Tree)
            and tree.children[0].data == 'dotted_name'):
            tree = tree.children[0]
        try:
            parts = [str(tok) for tok in tree.children]

            if parts[0] in self.env:
                obj = self.env[parts[0]]
            elif parts[0] in self.global_env:
                obj = self.global_env[parts[0]]
            else:
                meta = getattr(tree, "meta", None)
                loc = f"{self.filename}:{meta.line}:{meta.column}" if meta else self.filename
                raise NameError(f"{loc}: Name '{parts[0]}' is not defined")

            for attr in parts[1:]:
                if isinstance(obj, dict) and attr in obj:
                    obj = obj[attr]
                else:
                    obj = getattr(obj, attr)
            return obj
        except Exception as e:
            meta = getattr(tree, "meta", None)
            if meta:
                loc = f"{self.filename}:{meta.line}:{meta.column}"
            else:
                loc = self.filename
            if parts[0] in self.env and parts[0] != self.filename:
                raise type(e)(f"{loc}: {str(e).replace('dict', parts[0])}")
            raise type(e)(f"{loc} {str(e).replace(loc, "")}")


if __name__ == '__main__':
    argv = sys.argv

    if len(argv) > 5:
        raise Exception(f"Too many arguments expected 2 got {len(argv) - 1}")
    
    if argv[1] == "--version":
        print(f"Mscript Interpreter version {__VERSION__} by {__AUTHOR__} ({__DATE__}) ({platform.system()})")
        sys.exit(0)

    if not argv[1].endswith(".mscript"):
        raise Exception(f"Mscript files must end in .mscript suffix and be the first argument. Got: {argv[1]}")
    
    parser = Lark(language_definition,
                  parser='lalr',
                  propagate_positions=True)
    try:
        text = open(argv[1]).read()
        tree = parser.parse(text)
    except UnexpectedInput as e:
        print(f"{argv[1]}:{e.line}:{e.column}: Syntax error: {e}")
        sys.exit(1)

    interp = MscriptInterpreter(filename=argv[1])
    try:
        interp.visit(tree)
    except Exception as e:
        print(e)
    if "--debug" in argv:
        print(tree.pretty(f"{argv[len(argv)-1] if argv[len(argv)-2] == '--debug' else ""}"))
    
    sys.exit(1)
