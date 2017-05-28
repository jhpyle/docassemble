def retrieve_ein(name):
    if name.text == 'ABC Incorporated':
        return "54-54349343"
    elif name.text == "XYZ Incorporated":
        return "32-84398493"
    raise Exception("Could not retrieve EIN for " + name.text)
