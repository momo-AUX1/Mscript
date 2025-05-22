**Mscript Interpreter**  
**it.py** – Interpreter for the Mscript language  
**Version:** 0.7.0  
**Author:** Momo-AUX1  
**Date:** 2025-05-21

---

## Table of Contents

* [Overview](#overview)  
* [Features](#features)  
* [Requirements](#requirements)  
* [Installation](#installation)  
* [Usage](#usage)  
  * [Interactive REPL](#interactive-repl)  
  * [Running Scripts](#running-scripts)  
* [Standard Library](#standard-library)  
* [Python Interoperability](#python-interoperability)  
* [Language Grammar](#language-grammar)  
* [Built-in Functions](#built-in-functions)  
* [Examples](#examples)  
  * [Hello World](#hello-world)  
  * [FFI Example](#foreign-function-interface-ffi)  
  * [Python Interop Example](#python-interop-example)  
* [Version History](#version-history)  
* [Roadmap](#roadmap)  
* [Contributing](#contributing)  
* [License](#license)  

---

## Overview

Mscript is a small, Python-powered scripting language with braces-based blocks and built-in support for variables, arithmetic, control flow, functions, data structures, I/O, FFI, and seamless Python interop. This repository provides:

* **it.py** – the Lark-based interpreter  
* **language.def** – the grammar definition  
* **mscript_builtins.py** – core built-ins  
* **std/** – standard library modules written in Mscript  


## Visual Studio Code Extension

For enhanced language support, install the [Mscript VS Code Extension](https://marketplace.visualstudio.com/items?itemName=Momo-AUX1.Mscript) from the Visual Studio Marketplace.
---

## Features

* Variable assignment and lookup  
* Arithmetic (`+`, `-`, `*`, `/`, `%`, `**`)  
* Control flow: `if` / `elif` / `else`, `while`, `for`, `break`, `continue`  
* First-class functions, with parameters and `return`  
* Lists and dictionaries  
* Module import (`import "std/..."` or `import python`)  
* Exception handling: `try` / `catch`  
* Built-in functions: `input`, `print`, `str`, `int`, `type`, file I/O, math, JSON, regex, time, environment, FFI, and more  
* REPL with history  
* Foreign Function Interface (FFI) to call C libraries via `ctypes`  
* **Seamless Python interop**: any Python package installed via `pip` is immediately accessible under the `python` module  

---

## Requirements

* Python 3.7+  
* [Lark parser](https://github.com/lark-parser/lark)  

Install Lark with:

```bash
pip install lark
````

---

## Installation

Install via PyPI:

```bash
pip install mscript-lang
```

Or clone the repo:

```bash
git clone https://github.com/momo-AUX1/Mscript.git
cd mscript
```

---

## Usage

### Interactive REPL

Start the REPL with no arguments:

```bash
mscript
```

You'll see:

```
Mscript REPL 0.6.9 by Momo-AUX1 (type Ctrl-D to exit)
>>>
```

Type Mscript statements or expressions; results and errors print immediately.

### Running Scripts

Run a `.mscript` file:

```bash
mscript myscript.mscript
```

* `--version`: print interpreter version and exit
* `--debug`: show parse tree

---

## Standard Library

A collection of Mscript modules installed under `std/`, importable via:

```mscript
import "std/module_name"
```

Included modules:

* **datetime.mscript**: `today()`, `now()`, `strftime()`, `parse()`
* **ffi.mscript**: `load()`, `sym()`, `func()`, `buffer()`, `buffer_ptr()`, `offset()`, read/write helpers
* **json.mscript**: `loads()`, `dumps()`
* **math.mscript**: `sin()`, `cos()`, `tan()`, `log()`, `log10()`, `exp()`, `sqrt()`, `floor()`, `ceil()`, `pow()`, constants `PI`, `E`
* **platform.mscript**: `system()`, `node()`, `release()`, `version()`, `machine()`, `processor()`, `full()`
* **random.mscript**: `random()`, `seed()`, `randint()`, `uniform()`, `choice()`, `shuffle()`
* **re.mscript**: `search()`, `match()`, `findall()`, `sub()`
* **string.mscript**: `upper()`, `lower()`, `strip()`, `lstrip()`, `rstrip()`, `find()`, `replace()`, `split()`, `join()`, `substring()`
* **sys.mscript**: `argv()`, `getenv()`, `setenv()`, `unsetenv()`, `platform` proxy
* **time.mscript**: `sleep()`, `time()`

---

## Python Interoperability

Mscript exposes a special `python` module that proxies into Python’s ecosystem:

```mscript
import python

# call built-in Python functions
hi = python.print
hi("mscript!")   # prints to stdout

# import any pip-installed package
req = python.requests.get("https://api.example.com").text
print req
```

* **Any** library installed in your Python environment (via `pip install …`) can be imported and used directly in Mscript using `import python`.
* Access modules, functions, classes, and attributes exactly as in normal Python.

---

## Language Grammar

Defined in **language.def** (LALR):

```ebnf
?start: statement+

?statement: assign | index_assign | print_stmt | if_stmt | while_stmt
          | for_stmt | func_def | return_stmt | expr_stmt | import_stmt
          | break_stmt | continue_stmt | try_stmt

# (see full grammar in language.def)
```

---

## Built-in Functions

| Category  | Examples                                                                    |
| --------- | --------------------------------------------------------------------------- |
| Core      | `input`, `print`, `str()`, `int()`, `type()`, `len()`, `keys()`, `values()` |
| File I/O  | `read()`, `write()`, `system()`                                             |
| Math      | `_sin()`, `_cos()`, `_log()`, `_sqrt()`, `_pow()`                           |
| JSON      | `_json_loads()`, `_json_dumps()`                                            |
| Regex     | `_re_search()`, `_re_findall()`, `_re_sub()`                                |
| Date/Time | `_date_today()`, `_datetime_now()`, `_strftime()`                           |
| Env/Sys   | `_getenv()`, `_setenv()`, `exit()`                                          |
| FFI       | `_ffi_open()`, `_ffi_sym()`, `_ffi_buffer()`, `_ffi_read_uint32()`          |
| Random    | `_random_random()`, `_random_choice()`, `_random_shuffle()`                 |
| Platform  | `_platform_system()`, `_platform_platform()`                                |

See **mscript\_builtins.py** for full list.

---

## Examples

### Hello World

```mscript
# hello.mscript
x = "hello world"
print str.upper(x)
```

**Run:**

```bash
mscript hello.mscript
# Output: HELLO WORLD
```

### Foreign Function Interface (FFI)

```mscript
import "std/ffi"

SDL = ffi.load("libSDL2.dylib")
SDL_Init = ffi.func(SDL, "SDL_Init", "int", ["uint"])
SDL_Quit = ffi.func(SDL, "SDL_Quit", "void", [])

if SDL_Init(32) != 0 {
    print "SDL_Init failed!"
    exit(1)
}
# ...
SDL_Quit()
```

### Python Interop Example

```mscript
import python

# use Python’s `math` module
print python.math.sqrt(2)

# HTTP request via `requests` (must be installed in your env)
resp = python.requests.get("https://httpbin.org/ip").json()
print resp["origin"]

# define function pointers directly to Mscript variables
hello = python.print

# use them as if they were our own
hello("world!")

```

---

## Version History

* **0.6.9** – Current release (2025-05-22)
* **0.6.0** – Supporting more built-ins, enhancements to error handling
* **0.5.0** – True standard library
* **0.4.0** – Added more built-ins, `try`/`except` support
* **0.3.0** – Dotted names in functions and assignments
* **0.2.0** – Core interpreter improvements
* **0.1.0** – Initial release

---

## Roadmap

* Package manager
* Expanded standard library
* Module namespace support
* Advanced debugging tools

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.