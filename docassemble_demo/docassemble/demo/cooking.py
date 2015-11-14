from docassemble.base.core import DAObject

class Recipe(DAObject):
    def summary(self):
        return "#### Ingredients:\n\n" + self.ingredients + "\n\n#### Instructions:\n\n" + self.instructions
