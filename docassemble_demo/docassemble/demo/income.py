from docassemble.base.util import DADict

__all__ = ['IncomeDict']


class IncomeDict(DADict):

    def hook_on_gather(self, *pargs, **kwargs):
        if 'benefits' in self.elements and self['benefits'].receives and 'employment' in self.elements and self['employment'].receives and self['benefits'].amount + self['employment'].amount > 2000:
            self.reason_for_benefits  # pylint: disable=pointless-statement
        elif hasattr(self, 'reason_for_benefits'):
            del self.reason_for_benefits

    def hook_after_gather(self, *pargs, **kwargs):
        self.total_amount = sum(y.amount for y in self.values() if y.receives)
