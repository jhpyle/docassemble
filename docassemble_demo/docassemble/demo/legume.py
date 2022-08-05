from docassemble.base.util import Thing, prevent_dependency_satisfaction

__all__ = ['Legume']


class Legume(Thing):

    @prevent_dependency_satisfaction
    def is_tasty(self):
        return bool(self.sweet_index > 5 or self.savory_index > 6)
