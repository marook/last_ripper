from unittest import TestCase, main
from lastRipper import MakefileWriter

class FileMock(object):

    def __init__(self):
        self.writes = []

    def write(self, obj):
        self.writes.append(obj)

    @property
    def writesAsString(self):
        return ''.join(self.writes)

class MakefileWriterSmallTest(TestCase):

    def setUp(self):
        self.fileMock = FileMock()
        self.writer = MakefileWriter(self.fileMock)

    def assertWrittenString(self, expectedString):
        self.assertEqual(self.fileMock.writesAsString.strip(), expectedString)

    def testWriteTargetWithoutDependencies(self):
        self.writer.writeTarget('my.file')

        self.assertWrittenString('my.file:')

    def testWriteTargetWithTwoDependencies(self):
        self.writer.writeTarget('my.file', ['first', 'second'])

        self.assertWrittenString('my.file: first second')

    def testWriteRule(self):
        self.writer.writeRule('callMyApp withParam')

        self.assertEqual(self.fileMock.writesAsString, '\tcallMyApp withParam\n')

    def testWriteVar(self):
        self.writer.writeVar('NAME', 'value')

        self.assertEqual(self.fileMock.writesAsString, 'NAME=value\n')

if __name__ == '__main__':
    main()
