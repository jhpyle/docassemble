def is_multiple_of_four(x):
    if x/4 != int(x/4):
        raise Exception("The number must be a multiple of four")
    return True
