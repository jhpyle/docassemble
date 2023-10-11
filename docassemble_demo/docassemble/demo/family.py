# do not pre-load
from docassemble.base.util import Individual, DAList

__all__ = ['FamilyMember', 'Children']


class FamilyMember(Individual):

    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)

    def get_entitlements(self):
        if self.survived:
            return [{'person': self, 'portion': 1.0}]
        elif self.married:
            return 


class Children(DAList):
    def init(self, *pargs, **kwargs):
        if not kwargs.get('object_type'):
            kwargs['object_type'] = FamilyMember
        if not kwargs.get('complete_attribute'):
            kwargs['complete_attribute'] = 'complete'
        super().init(*pargs, **kwargs)
