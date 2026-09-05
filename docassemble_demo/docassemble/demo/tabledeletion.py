from docassemble.base.util import DAList, Individual, word, log

class PeopleList(DAList):
    """Subclass of DAList that demonstrates how to show a message when
    an item is removed from the list."""

    def init(self, *pargs, **kwargs):
        self.object_type = Individual
        self.complete_attribute = 'complete'
        super().init(*pargs, **kwargs)

    def hook_on_remove(self, item, *pargs, **kwargs):
        try:
            log(word(f"Removed {item} from the list"), "success")
        except:
            log(word("Removed"), "success")
