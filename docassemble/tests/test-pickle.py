import pickle
from docassemble.legal import *

def moo():
    sentence = '${ plaintiff.as_noun().capitalize() }, ${ plaintiff }, ${ plaintiff.does_verb("is") } bringing this lawsuit against ${ defendant.as_noun() }, ${ op }'

    user = Individual('user')

    user.name.first = "Jonathan"
    user.name.last = "Pyle"

    spouse = Individual('spouse')

    spouse.name.first = "Jill"
    spouse.name.last = "Bean"

    op = Person('op')
    op.name = "Philadelphia Legal Assistance"

    defendant = PartyList('defendant')
    defendant.add(op)

    plaintiff = PartyList('plaintiff')

    plaintiff.add(spouse)
    c = 1
    a = 3
    thelocals = locals()
    output = open('foobar.pickle', 'wb')
    pickle.dump(thelocals, output)

def foo():
    the_input = open('foobar.pickle', 'r')
    foo = pickle.load(the_input)
    return(foo)

moo()
the_dict = dict()
the_dict.update(foo())
result = eval('plaintiff', the_dict)
print result
