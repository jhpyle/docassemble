# do not pre-load
from docassemble.base.util import current_context, Individual, log

__all__ = ['AltIndividual']


class AltIndividual(Individual):

    def __str__(self):
        if current_context().inside_of != 'standard':
            return self.name.full()
        return self.name.familiar()
