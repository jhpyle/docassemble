from docassemble.base.util import explain

__all__ = ['wrong_vegetable']


def wrong_vegetable(vegetable):
    if vegetable == 'turnip':
        explain("You also said your favorite vegetable was turnip.")
        return True
    explain("You also said your favorite vegetable was " + vegetable + ".")
    return False
