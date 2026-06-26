# do not pre-load
def retrieve_ein(name):
    if name.text == 'ABC Incorporated':
        return "54-54349343"
    if name.text == "XYZ Incorporated":
        return "32-84398493"
    raise ValueError("Could not retrieve EIN for " + name.text)
