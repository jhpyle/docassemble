from docassemble.base.util import DAList, DAObject

__all__ = ['FishList', 'Fish']

class FishList(DAList):
    def init(self, *pargs, **kwargs):
        self.object_type = Fish
        self.complete_attribute = 'fish_complete'
        super(FishList, self).init(*pargs, **kwargs)

class Fish(DAObject):
    @property
    def fish_complete(self):
        self.common_name
        self.scales
        self.species
    
    def __unicode__(self):
        return self.common_name
