from docassemble.legal import *

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

print assemble(sentence)

plaintiff.add(user)

print assemble(sentence)

for party in plaintiff:
    print "Party:"
    print party.name


