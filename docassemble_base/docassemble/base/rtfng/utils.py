"""
Utility functions for rtf-ng.
"""
import os
from unittest import TestCase
from StringIO import StringIO

from docassemble.base.rtfng.Elements import Document, Section

def importModule(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def fileIsTest(path, skipFiles=[]):
    if not os.path.isfile(path):
        return False
    filename = os.path.basename(path)
    if filename in skipFiles:
        return False
    if filename.startswith('test') and filename.endswith('.py'):
        return True

def find(start, func, skip=[]):
    for item in [os.path.join(start, x) for x in os.listdir(start)]:
        if func(item, skip):
            yield item
        if os.path.isdir(item):
            for subItem in find(item, func, skip):
                yield subItem

def findTests(startDir, skipFiles=[]):
    return find(startDir, fileIsTest, skipFiles)

class RTFTestCase(TestCase):
    """
    This class may look like it's doing a bit of magic, so let me explain:

        * an external script needs to be able to call methods on this class to
          get the generated RTF data;
        * there's no reason the script and the tests can't make use of the same
          RTF-generating code;
        * these two facts are the reason for the 'make_*()' methods;
        * each test that is run knows it's own name (e.g., the test runner
          keeps track of each test and what it's called);
        * thus, the appropriate make_ method can be determined by the test
          method that called it (as long as we name them with the same suffix);
        * also, since the name is all that is needed to get the reference data
          (since we're also naming the reference files with that same suffix),
          that can be determined without hard-coding filenames;
        * with all of these facts, we can generalize some code since there's no
          need to have any test-specific code in the test_*() methods;
        * this means that each test method can make the same, parameterless
          doTest() call (the only thing that changes is the name, and only the
          name is needed to generate/get the necessary data).
    """

    def initializeDoc():
        doc = Document()
        section = Section()
        doc.Sections.append(section)
        return (doc, section, doc.StyleSheet)

    initializeDoc = staticmethod(initializeDoc)

    def setUp(self):
        base = ('test', 'sources', 'rtfng')
        self.sourceDir = os.path.join(*base)

    def getReferenceData(self, name):
        fh = open(os.path.join(self.sourceDir, name + '.rtf'))
        data = fh.read()
        fh.close()
        return data

    def getTestName(self):
        if hasattr(self, '_testMethodName'):
            return self._testMethodName.split('test_')[1]
        return self._TestCase__testMethodName.split('test_')[1]

    def getTestData(self, doc):
        result = StringIO()
        doc.write(result)
        testData = result.getvalue()
        result.close()
        return testData

    def callMake(self):
        return getattr(self, 'make_%s' % self.getTestName())()

    def getData(self):
        name = self.getTestName()
        doc = self.callMake()
        testData = self.getTestData(doc)
        refData = self.getReferenceData(name)
        return (testData, refData)

    def doTest(self):
        testData, refData = self.getData()
        self.assertEqual(testData, refData)

