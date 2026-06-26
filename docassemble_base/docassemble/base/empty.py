class DAEmpty:
    """An object that silently absorbs any attribute access or operation.

    DAEmpty avoids triggering errors about missing information by returning
    another DAEmpty for any attribute access, returning empty values for
    string conversion and length, and absorbing arithmetic operations.

    Attributes:
        str (str): The string value returned when the object is converted to
            text. Defaults to the empty string.
    """

    def __init__(self, *pargs, **kwargs):  # pylint: disable=unused-argument
        self.str = str(kwargs.get('str', ''))

    def __getattr__(self, thename):
        if thename.startswith('__') or thename == 'str':
            return object.__getattribute__(self, thename)
        return DAEmpty()

    def __str__(self):
        try:
            return object.__getattribute__(self, 'str')
        except:
            return ''

    def __dir__(self):
        return []

    def __contains__(self, item):
        return False

    def __iter__(self):
        the_list = []
        return the_list.__iter__()

    def __len__(self):
        return 0

    def __reversed__(self):
        return []

    def __getitem__(self, index):
        return DAEmpty()

    def __setitem__(self, index, val):
        pass

    def __delitem__(self, index):
        pass

    def __call__(self, *pargs, **kwargs):
        return DAEmpty()

    def __repr__(self):
        return repr('')

    def __add__(self, other):
        return other

    def __sub__(self, other):
        return other

    def __mul__(self, other):
        return other

    def __floordiv__(self, other):
        return other

    def __mod__(self, other):
        return other

    def __divmod__(self, other):
        return other

    def __pow__(self, other):
        return other

    def __lshift__(self, other):
        return other

    def __rshift__(self, other):
        return other

    def __and__(self, other):
        return other

    def __xor__(self, other):
        return other

    def __or__(self, other):
        return other

    def __div__(self, other):
        return other

    def __truediv__(self, other):
        return other

    def __radd__(self, other):
        return other

    def __rsub__(self, other):
        return other

    def __rmul__(self, other):
        return other

    def __rdiv__(self, other):
        return other

    def __rtruediv__(self, other):
        return other

    def __rfloordiv__(self, other):
        return other

    def __rmod__(self, other):
        return other

    def __rdivmod__(self, other):
        return other

    def __rpow__(self, other):
        return other

    def __rlshift__(self, other):
        return other

    def __rrshift__(self, other):
        return other

    def __rand__(self, other):
        return other

    def __ror__(self, other):
        return other

    def __neg__(self):
        return 0

    def __pos__(self):
        return 0

    def __abs__(self):
        return 0

    def __invert__(self):
        return 0

    def __complex__(self):
        return 0

    def __int__(self):
        return int(0)

    def __float__(self):
        return float(0)

    def __oct__(self):
        return oct(0)

    def __hex__(self):
        return hex(0)

    def __index__(self):
        return int(0)

    def __le__(self, other):
        return True

    def __ge__(self, other):
        return self is other or False

    def __gt__(self, other):
        return False

    def __lt__(self, other):
        return True

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other

    def __hash__(self):
        return hash(('',))

    def as_dict(self):
        return self.to_json()

    def to_json(self):
        output = {'_class': 'docassemble.base.util.DAEmpty'}
        try:
            output.update({'str': object.__getattribute__(self, 'str')})
        except Exception:
            pass
        return output
