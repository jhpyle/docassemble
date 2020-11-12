from docassemble.base.util import Thing, prevent_dependency_satisfaction

__all__ = ['Legume']

class Legume(Thing):
    @prevent_dependency_satisfaction
    def is_tasty(self):
        if self.sweet_index > 5 or self.savory_index > 6:
            return True
        else:
            return False
