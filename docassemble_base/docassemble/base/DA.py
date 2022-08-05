__all__ = []


class Condition:

    def __init__(self, leftside, operator, rightside):
        self.leftside = leftside
        self.operator = operator
        self.rightside = rightside

    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

    def __rand__(self, other):
        return And(other, self)

    def __ror__(self, other):
        return Or(other, self)

    def __invert__(self):
        return Condition(self, 'not', None)

    def __repr__(self):
        return repr(self.leftside) + ' ' + self.operator + ' ' + repr(self.rightside)


class Column:

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def __and__(self, other):
        return Condition(self, 'and', other)

    def __xor__(self, other):
        return Condition(self, 'xor', other)

    def __or__(self, other):
        return Condition(self, 'or', other)

    def __rand__(self, other):
        return Condition(other, 'and', self)

    def __rxor__(self, other):
        return Condition(other, 'xor', self)

    def __ror__(self, other):
        return Condition(other, 'or', self)

    def __invert__(self):
        return Condition(self, 'not', None)

    def __le__(self, other):
        return Condition(self, 'le', other)

    def __ge__(self, other):
        return Condition(self, 'ge', other)

    def __gt__(self, other):
        return Condition(self, 'gt', other)

    def __lt__(self, other):
        return Condition(self, 'lt', other)

    def __eq__(self, other):
        return Condition(self, 'eq', other)

    def __ne__(self, other):
        return Condition(self, 'ne', other)

    def Like(self, rightside):
        return Condition(self, 'like', rightside)

    def In(self, *pargs):
        return Condition(self, 'in', list(pargs))


class Group:

    def __init__(self, *pargs, **kwargs):  # pylint: disable=unused-argument
        self.items = list(pargs)

    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

    def __rand__(self, other):
        return And(other, self)

    def __ror__(self, other):
        return Or(other, self)

    def __invert__(self):
        return Condition(self, 'not', None)

    def __repr__(self):
        return '(' + self.group_type + ' ' + ', '.join(repr(item) for item in self.items) + ')'


class And(Group):

    def __init__(self, *pargs, **kwargs):
        super().__init__(*pargs, **kwargs)
        self.group_type = 'and'


class Or(Group):

    def __init__(self, *pargs, **kwargs):
        super().__init__(*pargs, **kwargs)
        self.group_type = 'or'


class Sessions:
    modtime = Column('modtime')
    filename = Column('filename')
    session = Column('key')
    encrypted = Column('encrypted')
    user_id = Column('user_id')
    email = Column('email')
    first_name = Column('first_name')
    last_name = Column('last_name')
    country = Column('country')
    subdivisionfirst = Column('subdivisionfirst')
    subdivisionsecond = Column('subdivisionsecond')
    subdivisionthird = Column('subdivisionthird')
    organization = Column('organization')
    timezone = Column('timezone')
    language = Column('language')
    last_login = Column('last_login')
