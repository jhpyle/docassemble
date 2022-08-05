from docassemble.base.util import validation_error


def is_multiple_of_four(x):
    if (1.0*x/4) != int(x/4):
        validation_error("The number must be a multiple of four")
    return True
