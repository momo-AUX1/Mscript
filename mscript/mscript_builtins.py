# mscript_builtins.py
import ast
import os
import math
import json
import sys
import datetime
import re
import time as _time_mod
import ctypes
import platform as _py_platform
import random as _py_random # probably better if i prefixed everything under _py_ for readability 

def builtin_input(prompt):
    return input(str(prompt))

def builtin_str(x):
    return str(x)

def builtin_int(x):
    return int(x)

def builtin_float(x):
    return float(x)

def builtin_type(x):
    return type(x).__name__

def builtin_range(start, end):
    if not (isinstance(start, int) and isinstance(end, int)):
        raise TypeError("range() integer arguments expected")
    return list(__builtins__['range'](start, end))

def builtin_bytes(v, encoding=None):
    if encoding is None:
        if isinstance(v, str):
            return v.encode()
        return bytes(v)
    if not isinstance(v, str):
        raise TypeError('bytes(str, encoding) args must be (str, str)')
    return v.encode(encoding)

def builtin_encode(s, encoding=None):
    if encoding is None:
        if not isinstance(s, str):
            raise TypeError('encode() first arg must be a string')
        return s.encode()
    if not isinstance(s, str) or not isinstance(encoding, str):
        raise TypeError('encode() args must be (str, str)')
    return s.encode(encoding)

def builtin_read(filename, mode='r'):
    if mode in ('b','bytes','rb'):
        return open(filename, 'rb').read()
    return open(filename, 'r').read()

def builtin_write(filename, data):
    mode = 'wb' if isinstance(data, (bytes, bytearray)) else 'w'
    return open(filename, mode).write(data)

def builtin_decode(b, encoding=None):
    if encoding is None:
        if not isinstance(b, (bytes, bytearray)):
            raise TypeError('decode() first arg must be bytes')
        return b.decode()
    if not isinstance(b, (bytes, bytearray)) or not isinstance(encoding, str):
        raise TypeError('decode() args must be (bytes, str)')
    return b.decode(encoding)

def builtin_system(cmd):
    os.system(str(cmd))

def builtin_len(x):
    return len(x)

def builtin_keys(d):
    if not isinstance(d, dict):
        raise TypeError("keys() expects a dict")
    return list(d.keys())

def builtin_values(d):
    if not isinstance(d, dict):
        raise TypeError("values() expects a dict")
    return list(d.values())

# ——— math —————————————————————————————————————————————
def builtin_sin(x):             return math.sin(x)
def builtin_cos(x):             return math.cos(x)
def builtin_tan(x):             return math.tan(x)
def builtin_log(x, base=None):  return math.log(x) if base is None else math.log(x, base)
def builtin_log10(x):           return math.log10(x)
def builtin_exp(x):             return math.exp(x)
def builtin_sqrt(x):            return math.sqrt(x)
def builtin_floor(x):           return math.floor(x)
def builtin_ceil(x):            return math.ceil(x)
def builtin_pow(x, y):          return math.pow(x, y)

# ——— json —————————————————————————————————————————————
def builtin_json_loads(s):
    if not isinstance(s, str):
        raise TypeError("json_loads() expects a JSON string")
    return json.loads(s)

def builtin_json_dumps(obj, **kwargs):
    return json.dumps(obj, **kwargs)

# ——— sys ——————————————————————————————————————————————
def builtin_sys_argv():
    return sys.argv.copy()

def builtin_sys_exit(code):
    sys.exit(code)

def builtin_getenv(name, default=None):
    return os.environ.get(str(name), default)

def builtin_setenv(name, value):
    os.environ[str(name)] = str(value)

def builtin_unsetenv(name):
    os.environ.pop(str(name), None)

# ——— date/time ———————————————————————————————————————
def builtin_date_today():
    return datetime.date.today()

def builtin_datetime_now():
    return datetime.datetime.now()

def builtin_strftime(dt, fmt):
    if not hasattr(dt, 'strftime'):
        raise TypeError("strftime() expects a datetime/date/time object")
    return dt.strftime(fmt)

def builtin_parse_date(date_str, fmt):
    return datetime.datetime.strptime(date_str, fmt)

# ——— regex —————————————————————————————————————————————
def builtin_re_search(pattern, string):
    return re.search(pattern, string)

def builtin_re_match(pattern, string):
    return re.match(pattern, string)

def builtin_re_findall(pattern, string):
    return re.findall(pattern, string)

def builtin_re_sub(pattern, repl, string):
    return re.sub(pattern, repl, string)

# ——— time ——————————————————————————————————————————————
def builtin_sleep(seconds):
    return _time_mod.sleep(seconds)

def builtin_time():
    return _time_mod.time()

# ——— attribute operations —————————————————————————————————————
def builtin_set_attr(obj, attr, value):
    if not isinstance(attr, str):
        raise TypeError("set_attr() attribute name must be a string")
    setattr(obj, attr, value)
    return None

def builtin_has_attr(obj, attr):
    if not isinstance(attr, str):
        raise TypeError("has_attr() attribute name must be a string")
    return hasattr(obj, attr)

def builtin_del_attr(obj, attr):
    if not isinstance(attr, str):
        raise TypeError("del_attr() attribute name must be a string")
    if not hasattr(obj, attr):
        raise AttributeError(f"Attribute '{attr}' not found")
    delattr(obj, attr)
    return None

# ——— foreign-function interface (FFI) —————————————————————————————————

_ffi_ctype_map = {
    "void":   ctypes.c_void_p,
    "int":    ctypes.c_int,
    "uint":   ctypes.c_uint,
    "short":  ctypes.c_short,
    "ushort": ctypes.c_ushort,
    "long":   ctypes.c_long,
    "ulong":  ctypes.c_ulong,
    "float":  ctypes.c_float,
    "double": ctypes.c_double,
    "char*":  ctypes.c_char_p,
    "void*":  ctypes.c_void_p,
    "size_t": ctypes.c_size_t
}

def builtin_ffi_open(path):
    return ctypes.CDLL(str(path))

def builtin_ffi_sym(lib, name):
    return getattr(lib, str(name))

def builtin_ffi_set_ret(func, ret_type):
    try:
        func.restype = _ffi_ctype_map[str(ret_type)]
    except KeyError:
        raise TypeError(f"Unknown return type '{ret_type}'")
    return None

def builtin_ffi_set_args(func, arg_types):
    try:
        func.argtypes = [_ffi_ctype_map[str(t)] for t in arg_types]
    except KeyError as e:
        raise TypeError(f"Unknown argument type '{e.args[0]}'")
    return None

def builtin_ffi_buffer(size):
    return ctypes.create_string_buffer(size)

def builtin_ffi_buffer_ptr(buf):
    return ctypes.byref(buf)

def builtin_ffi_read_uint32(buf):
    return ctypes.cast(buf, ctypes.POINTER(ctypes.c_uint32)).contents.value

def builtin_ffi_buffer_offset(buf, offset):
    return ctypes.byref(buf, offset)

def builtin_ffi_read_uint8(buf, offset=0):
    return ctypes.cast(ctypes.byref(buf, offset),
                       ctypes.POINTER(ctypes.c_uint8)).contents.value
def builtin_ffi_read_int8(buf, offset=0):
    return ctypes.cast(ctypes.byref(buf, offset),
                       ctypes.POINTER(ctypes.c_int8)).contents.value
def builtin_ffi_read_uint16(buf, offset=0):
    return ctypes.cast(ctypes.byref(buf, offset),
                       ctypes.POINTER(ctypes.c_uint16)).contents.value
def builtin_ffi_read_int16(buf, offset=0):
    return ctypes.cast(ctypes.byref(buf, offset),
                       ctypes.POINTER(ctypes.c_int16)).contents.value
def builtin_ffi_read_int32(buf, offset=0):
    return ctypes.cast(ctypes.byref(buf, offset),
                       ctypes.POINTER(ctypes.c_int32)).contents.value
def builtin_ffi_read_float(buf, offset=0):
    return ctypes.cast(ctypes.byref(buf, offset),
                       ctypes.POINTER(ctypes.c_float)).contents.value
def builtin_ffi_read_double(buf, offset=0):
    return ctypes.cast(ctypes.byref(buf, offset),
                       ctypes.POINTER(ctypes.c_double)).contents.value
def builtin_ffi_write_uint8(buf, value, offset=0):
    ptr = ctypes.cast(ctypes.byref(buf, offset),
                      ctypes.POINTER(ctypes.c_uint8))
    ptr.contents.value = value
def builtin_ffi_write_int8(buf, value, offset=0):
    ptr = ctypes.cast(ctypes.byref(buf, offset),
                      ctypes.POINTER(ctypes.c_int8))
    ptr.contents.value = value
def builtin_ffi_write_uint16(buf, value, offset=0):
    ptr = ctypes.cast(ctypes.byref(buf, offset),
                      ctypes.POINTER(ctypes.c_uint16))
    ptr.contents.value = value
def builtin_ffi_write_int16(buf, value, offset=0):
    ptr = ctypes.cast(ctypes.byref(buf, offset),
                      ctypes.POINTER(ctypes.c_int16))
    ptr.contents.value = value
def builtin_ffi_write_int32(buf, value, offset=0):
    ptr = ctypes.cast(ctypes.byref(buf, offset),
                      ctypes.POINTER(ctypes.c_int32))
    ptr.contents.value = value
def builtin_ffi_write_float(buf, value, offset=0):
    ptr = ctypes.cast(ctypes.byref(buf, offset),
                      ctypes.POINTER(ctypes.c_float))
    ptr.contents.value = value
def builtin_ffi_write_double(buf, value, offset=0):
    ptr = ctypes.cast(ctypes.byref(buf, offset),
                      ctypes.POINTER(ctypes.c_double))
    ptr.contents.value = value
def builtin_ffi_write_uint32(buf, value, offset=0):
    ptr = ctypes.cast(
        ctypes.byref(buf, offset),
        ctypes.POINTER(ctypes.c_uint32)
    )
    ptr.contents.value = value

# ——— Platform builtins —————————————————————————————————————————————
def builtin_platform_system():
    return _py_platform.system()

def builtin_platform_node():
    return _py_platform.node()

def builtin_platform_release():
    return _py_platform.release()

def builtin_platform_version():
    return _py_platform.version()

def builtin_platform_machine():
    return _py_platform.machine()

def builtin_platform_processor():
    return _py_platform.processor()

def builtin_platform_platform():
    return _py_platform.platform()

# ——— Random builtins ——————————————————————————————————————————————
def builtin_random_random():
    return _py_random.random()

def builtin_random_randint(a, b):
    return _py_random.randint(a, b)

def builtin_random_uniform(a, b):
    return _py_random.uniform(a, b)

def builtin_random_choice(seq):
    return _py_random.choice(seq)

def builtin_random_shuffle(seq):
    _py_random.shuffle(seq)
    return None

def builtin_random_seed(s):
    _py_random.seed(s)
    return None

# ——— string operations —————————————————————————————————————————————
def builtin_str_upper(s):
    if not isinstance(s, str):
        raise TypeError('upper() expects a string')
    return s.upper()

def builtin_str_lower(s):
    if not isinstance(s, str):
        raise TypeError('lower() expects a string')
    return s.lower()

def builtin_str_strip(s, chars=None):
    if not isinstance(s, str):
        raise TypeError('strip() expects a string')
    return s.strip(chars) if chars is not None else s.strip()

def builtin_str_lstrip(s, chars=None):
    if not isinstance(s, str):
        raise TypeError('lstrip() expects a string')
    return s.lstrip(chars) if chars is not None else s.lstrip()

def builtin_str_rstrip(s, chars=None):
    if not isinstance(s, str):
        raise TypeError('rstrip() expects a string')
    return s.rstrip(chars) if chars is not None else s.rstrip()

def builtin_str_find(s, sub):
    if not isinstance(s, str) or not isinstance(sub, str):
        raise TypeError('find() expects two strings')
    return s.find(sub)

def builtin_str_replace(s, old, new, count=-1):
    if not isinstance(s, str) or not isinstance(old, str) or not isinstance(new, str):
        raise TypeError('replace() expects three strings')
    return s.replace(old, new, count)

def builtin_str_split(s, sep=None):
    if not isinstance(s, str):
        raise TypeError('split() expects a string')
    return s.split(sep)

def builtin_str_join(seq, sep):
    if not isinstance(sep, str):
        raise TypeError('join() separator must be a string')
    return sep.join(seq)

def builtin_str_substring(s, start, end=None):
    if not isinstance(s, str):
        raise TypeError('substring() expects a string')
    return s[start:end] if end is not None else s[start:]

builtins = {
    # core
    'input':       builtin_input,
    'str':         builtin_str,
    'int':         builtin_int,
    'float':       builtin_float,
    'type':        builtin_type,
    'bytes':       builtin_bytes,
    'encode':      builtin_encode,
    'read':        builtin_read,
    'write':       builtin_write,
    'decode':      builtin_decode,
    'system':      builtin_system,
    'len':         builtin_len,
    'keys':        builtin_keys,
    'values':      builtin_values,
    'set_attr':    builtin_set_attr,
    'has_attr':    builtin_has_attr,
    'del_attr':    builtin_del_attr,
    'range':       builtin_range,

    # math (internal)
    '_sin':         builtin_sin,
    '_cos':         builtin_cos,
    '_tan':         builtin_tan,
    '_log':         builtin_log,
    '_log10':       builtin_log10,
    '_exp':         builtin_exp,
    '_sqrt':        builtin_sqrt,
    '_floor':       builtin_floor,
    '_ceil':        builtin_ceil,
    '_pow':         builtin_pow,

    # json (internal)
    '_json_loads':  builtin_json_loads,
    '_json_dumps':  builtin_json_dumps,

    # sys (internal)
    '_argv':        builtin_sys_argv,
    'exit':         builtin_sys_exit,
    '_getenv':      builtin_getenv,
    '_setenv':      builtin_setenv,
    '_unsetenv':    builtin_unsetenv,

    # date/time (internal)
    '_date_today':    builtin_date_today,
    '_datetime_now':  builtin_datetime_now,
    '_strftime':      builtin_strftime,
    '_parse_date':    builtin_parse_date,

    # regex (internal)
    '_re_search':    builtin_re_search,
    '_re_match':     builtin_re_match,
    '_re_findall':   builtin_re_findall,
    '_re_sub':       builtin_re_sub,

    # time (internal)
    '_sleep':        builtin_sleep,
    '_time':         builtin_time,

    # FFI (internal)
    "_ffi_open":       builtin_ffi_open,
    "_ffi_sym":        builtin_ffi_sym,
    "_ffi_set_ret":    builtin_ffi_set_ret,
    "_ffi_set_args":   builtin_ffi_set_args,
    "_ffi_buffer":       builtin_ffi_buffer,
    "_ffi_buffer_ptr":   builtin_ffi_buffer_ptr,
    "_ffi_read_uint32":  builtin_ffi_read_uint32,
    "_ffi_buffer_offset":    builtin_ffi_buffer_offset,
    "_ffi_read_uint8":       builtin_ffi_read_uint8,
    "_ffi_read_int8":        builtin_ffi_read_int8,
    "_ffi_read_uint16":      builtin_ffi_read_uint16,
    "_ffi_read_int16":       builtin_ffi_read_int16,
    "_ffi_read_int32":       builtin_ffi_read_int32,
    "_ffi_read_float":       builtin_ffi_read_float,
    "_ffi_read_double":      builtin_ffi_read_double,
    "_ffi_write_uint8":      builtin_ffi_write_uint8,
    "_ffi_write_int8":       builtin_ffi_write_int8,
    "_ffi_write_uint16":     builtin_ffi_write_uint16,
    "_ffi_write_int16":      builtin_ffi_write_int16,
    "_ffi_write_int32":      builtin_ffi_write_int32,
    "_ffi_write_float":      builtin_ffi_write_float,
    "_ffi_write_double":     builtin_ffi_write_double,

    # platform (internal)
    "_platform_system":    builtin_platform_system,
    "_platform_node":      builtin_platform_node,
    "_platform_release":   builtin_platform_release,
    "_platform_version":   builtin_platform_version,
    "_platform_machine":   builtin_platform_machine,
    "_platform_processor": builtin_platform_processor,
    "_platform_platform":  builtin_platform_platform,

    # random (internal)
    "_random_random":   builtin_random_random,
    "_random_randint":  builtin_random_randint,
    "_random_uniform":  builtin_random_uniform,
    "_random_choice":   builtin_random_choice,
    "_random_shuffle":  builtin_random_shuffle,
    "_random_seed":     builtin_random_seed,

    # string (internal)
    '_string_upper':     builtin_str_upper,
    '_string_lower':     builtin_str_lower,
    '_string_strip':     builtin_str_strip,
    '_string_lstrip':    builtin_str_lstrip,
    '_string_rstrip':    builtin_str_rstrip,
    '_string_find':      builtin_str_find,
    '_string_replace':   builtin_str_replace,
    '_string_split':     builtin_str_split,
    '_string_join':      builtin_str_join,
    '_string_substring': builtin_str_substring,
}
