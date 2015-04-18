import types

user_dict = dict()
def foo(user_dict):
    exec('from ' + 'docassemble.legal' + ' import *', user_dict)

foo(user_dict)
user_dict['user'] = user_dict['Individual']('user')
user_dict['a'] = True
user_dict['b'] = 1
user_dict['c'] = 'asdf'
user_dict['d'] = set()
user_dict['e'] = list()
user_dict['f'] = dict()
for key in user_dict:
    if type(user_dict[key]) in [types.ModuleType, types.FunctionType, types.TypeType]:
        continue
    if key == "__builtins__":
        continue
    print key, type(user_dict[key])
