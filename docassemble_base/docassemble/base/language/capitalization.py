from .core import (
    language_function_constructor,
    update_language_function,
    ensure_definition,
)

def capitalize_default(a, **kwargs):  # pylint: disable=unused-argument
    ensure_definition(a)
    if not isinstance(a, str):
        a = str(a)
    if a and len(a) > 1:
        return a[0].upper() + a[1:]
    return a

capitalize = language_function_constructor('capitalize')

update_language_function('*', 'capitalize', capitalize_default)
