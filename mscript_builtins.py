# mscript_builtins.py
import ast
import os
import math
import json
import sys
import datetime
import re
import time as _time_mod

def builtin_input(prompt):
    return input(str(prompt))

def builtin_str(x):
    return str(x)

def builtin_int(x):
    return int(x)

def builtin_type(x):
    return type(x).__name__

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

builtins = {
    # core
    'input':       builtin_input,
    'str':         builtin_str,
    'int':         builtin_int,
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
}
