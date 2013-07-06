'''
Created on Jun 28, 2013

@author: shre5185
'''
import unittest
import arcpy;
import src.CreateNetworkDataset as cnd;
import src.CreateVectorLayer as cvl;


class TestCreateNetworkDataset(unittest.TestCase):
    working_dir = "C:\\test";
    test_fgdb = "TestCreateNetworkDataset";
    template_fds = "C:\\VectorBasedMobilityModeling\\Template\\VegasTemplate.gdb\\VectorModel";

    def setUp(self):
        db_path = self.working_dir + "\\" + self.test_fgdb;
        if arcpy.Exists(db_path):
            arcpy.Delete_management(db_path);
            
        # create db
        db_path = cvl.create_database(self.working_dir, self.test_fgdb)
        
        rasters = ["C:\Users\shre5185\Documents\MSGIS\MIP\YellowstoneData\Yellowstone.gdb\FinalSum"]
        geometry = "knight"
        scale = 20
        
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



    def testCreateNetworkDataset(self):
        db_path = self.working_dir + "\\" + self.test_fgdb + ".gdb";
        nodes_fc = db_path + "\\nodes";
        edges_fc = db_path + "\\edges";
        
        # test
        nw_dataset = cnd.create_network_dataset(nodes_fc, edges_fc, self.template_fds, db_path);
        
        # assert
        assert arcpy.Exists(nw_dataset);


if __name__ == "__main__":
    unittest.main()