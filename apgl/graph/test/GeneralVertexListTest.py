
from apgl.graph.GeneralVertexList import GeneralVertexList
from apgl.graph.test.AbstractVertexListTest import AbstractVertexListTest
from apgl.util.PathDefaults import PathDefaults 
import unittest
import logging

class GeneralVertexListTest(unittest.TestCase, AbstractVertexListTest):
    def setUp(self):
        self.VListType = GeneralVertexList
        self.numVertices = 10
        self.vList = GeneralVertexList(self.numVertices)
        self.emptyVertex = None
        self.initialise()

    def testConstructor(self):
        self.assertEquals(self.vList.getNumVertices(), self.numVertices)

    def testSaveLoad(self):
        try:
            vList = GeneralVertexList(self.numVertices)
            vList.setVertex(0, "abc")
            vList.setVertex(1, 12)
            vList.setVertex(2, "num")

            tempDir = PathDefaults.getTempDir()
            fileName = tempDir + "vList"

            vList.save(fileName)

            vList2 = GeneralVertexList.load(fileName)

            for i in range(self.numVertices):
                self.assertEquals(vList.getVertex(i), vList2.getVertex(i))
        except IOError as e:
            logging.warn(e)
            pass 



if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(VertexListTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
