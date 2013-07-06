'''
Created on May 6, 2013

@author: shre5185
'''
import unittest
import arcpy;
from src import Randomize as rand;
from src import CreateVectorLayer as cvl;

class TestRandomize(unittest.TestCase):
    working_dir = "C:\\test";
    test_fgdb = "TestRandomize";

    def setUp(self):
        db_path = self.working_dir + "\\" + self.test_fgdb;
        if arcpy.Exists(db_path):
            arcpy.Delete_management(db_path);
            
        # create db
        db_path = cvl.create_database(self.working_dir, self.test_fgdb)
        
        rasters = ["C:\Users\shre5185\Documents\MSGIS\MIP\YellowstoneData\Yellowstone.gdb\FinalSum"]
        geometry = "knight"
        scale = 10
        
        # create database
        db_path = cvl.create_database(self.working_dir, self.test_fgdb);
        
        nodes_fc = db_path + "\\nodes";
        edges_fc = db_path + "\\edges";

        # test
        cvl.sample_rasters_to_vector(rasters, geometry, scale, nodes_fc, edges_fc);
            
    def tearDown(self):
        db_path = self.working_dir + "\\" + self.test_fgdb;
        if arcpy.Exists(db_path):
            arcpy.Delete_management(db_path);


    def test_randomize(self):
        db_path = self.working_dir + "\\" + self.test_fgdb + ".gdb";
        percent = 20;
        nodes_fc = db_path + "\\nodes";
        edges_fc = db_path + "\\edges";
        rand.randomize(percent, nodes_fc, edges_fc, db_path);
        pass


if __name__ == "__main__":
    unittest.main()