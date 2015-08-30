# This is a Python module in which you can write your own Python code,
# if you want to.
#
# Include this module in a docassemble interview by writing:
# ---
# modules:
#   - docassemble.citizenship_attestation.objects
# ---
#
# Then you can do things like:
# ---
# objects:
#   - favorite_fruit: Fruit
# ---
# question: |
#   When I eat ${ indefinite_article(favorite_fruit.name) }, 
#   I think, "${ favorite_fruit.eat() }"  Do you agree?
# yesno: agrees_favorite_fruit_is_good
# ---
# question: What is the best fruit?
# fields:
#   - Fruit Name: favorite_fruit.name
# ---

class Fruit(DAObject):
    def eat():
        return("Yum, that " + self.name + " was good!")
