import unittest
import filecmp
import covidIndiaStateBulletins as co
import os

testDir = 'tests/'

class tests(unittest.TestCase):

    def setUp(self):
        self.samplePDFlink = 'http://www.orimi.com/pdf-test.pdf'
        self.sampleNewPDF = testDir + 'sampleNew.pdf'
        self.samplePDF = testDir + 'sample.pdf'
        co.downloadPDF(self.samplePDFlink, self.sampleNewPDF)

    def test_downloadPDF(self):
        isSame = filecmp.cmp(self.sampleNewPDF, self.samplePDF, shallow=False)
        self.assertTrue(isSame)

    def tearDown(self):
        try:
            os.remove(self.sampleNewPDF)
        except FileNotFoundError:
            pass

if __name__ == '__main__':
    unittest.main()
