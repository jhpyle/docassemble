from docassemble.base.rtfng.parser.grammar import grammar

class RTFParser(object):

    def __init__(self, rtfData=None):
        if rtfData:
            self.parse(rtfData)

    def parse(self, rtfData):
        """
        # setup the tests to read the test RTF files
        >>> import os.path
        >>> package, module = os.path.split(__file__)
        >>> trunk, package = os.path.split(package)
        >>> basedir = os.path.join(trunk, 'test', 'sources', 'macrtf')
        >>> def getFileData(filename):
        ...   fh = open(os.path.join(basedir, filename))
        ...   data = fh.read()
        ...   fh.close()
        ...   return data

        # simple, single-word content
        #>>> data = getFileData('simpleContent.rtf')
        #>>> try:
        #...   rp = RTFParser(data)
        #...   import pdb;pdb.set_trace()
        #... except Exception, e:
        #...   print e
        #...   print data.splitlines()
        #>>> rp.tokens
        #>>> dir(rp.tokens)
        #>>> rp.tokens.asDict()
        #>>> rp.tokens.items()
        """
        self.tokens = grammar.parseString(rtfData)

class RTFFile(object):
    """

    """
    def __init__(self, filename):
        self.filename = filename
        self._fonts = {}
        self.parsed = None
        self.parse()
        self.buildFontTable()

    def parse(self):
        if hasattr(self.filename, 'read'):
            fh = self.filename
        else:
            fh = open(self.filename)
        if hasattr(self.filename, 'getvalue'):
            data = fh.getvalue()
        else:
            data = fh.read()
        fh.close()
        # pass the string data into the parser
        try:
            parsed = RFTParser.parse(data)
        except ParseException, e:
            msg = "could not parse '%s'[...] : %s"
            raise RTFParseError(msg % (rtfstring[:30], e))
        self.parsed = protocol.validate(parsed)

    def setFonts(self, fontData):
        self._fonts = fontData

    def getFonts(self):
        return self._fonts

    fonts = property(getFonts, setFonts)

    def buildFontTable(self):
        """

        """

def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()

