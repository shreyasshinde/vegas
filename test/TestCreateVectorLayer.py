'''
Created on May 1, 2013

@author: shre5185
'''
import unittest
from src import CreateVectorLayer as cvl;
import arcpy;


class TestCreateVectorLayer(unittest.TestCase):
    working_dir = "C:\\test";
    test_fgdb = "TestCreateVectorLayer";

    def setUp(self):
        db_path = self.working_dir + "\\" + self.test_fgdb;
        if arcpy.Exists(db_path):
            arcpy.Delete_management(db_path);
            
    def tearDown(self):
        db_path = self.working_dir + "\\" + self.test_fgdb;
        if arcpy.Exists(db_path):
            arcpy.Delete_management(db_path);

    # test
    def atest_create_database(self):
        # create db
        db_path = cvl.create_database(self.working_dir, self.test_fgdb)
        
        # assert
        assert arcpy.Exists(db_path) == True
        
        # cleanup
        arcpy.Delete_management(db_path)
        assert arcpy.Exists(db_path) == False
        
    # test
    def atest_find_coarsest_raster(self):
        rasters = ["C:\Users\shre5185\Documents\MSGIS\MIP\YellowstoneData\Yellowstone.gdb\LandCoverReclas",
           "C:\Users\shre5185\Documents\MSGIS\MIP\YellowstoneData\Yellowstone.gdb\RoadsReclas",
           "C:\Users\shre5185\Documents\MSGIS\MIP\YellowstoneData\Yellowstone.gdb\PostsReclas",
           "C:\Users\shre5185\Documents\MSGIS\MIP\YellowstoneData\Yellowstone.gdb\TrailsReclas",
           "C:\Users\shre5185\Documents\MSGIS\MIP\YellowstoneData\Yellowstone.gdb\SlopeReclas"];
        actual = cvl.find_coarsest_raster(rasters)
        print actual
        #assert actual == raster2 #DEM
        
    
    # test
    def atest_create_feature_class(self):
        # create db
        db_path = cvl.create_database(self.working_dir, self.test_fgdb)
        
        # create test feature class
        test_fc = "testfc"
        fields = [("ID", "INTEGER"), ("VALUE","DOUBLE")]
        actual = cvl.create_feature_class(db_path, test_fc, "POLYGON", None, None, None, fields)
        
        # assert
        assert arcpy.Exists(actual) == True
        
        # cleanup
        arcpy.Delete_management(db_path);
        
    
    # test
    def atest_create_vector_layer_knight(self):
        '''
        rasters = ["C:\Users\shre5185\Documents\MSGIS\MIP\YellowstoneData\Yellowstone.gdb\LandCoverReclas",
                   "C:\Users\shre5185\Documents\MSGIS\MIP\YellowstoneData\Yellowstone.gdb\RoadsReclas",
                   "C:\Users\shre5185\Documents\MSGIS\MIP\YellowstoneData\Yellowstone.gdb\PostsReclas",
                   "C:\Users\shre5185\Documents\MSGIS\MIP\YellowstoneData\Yellowstone.gdb\TrailsReclas",
                   "C:\Users\shre5185\Documents\MSGIS\MIP\YellowstoneData\Yellowstone.gdb\SlopeReclas"
                   ]
        '''
        rasters = ["C:\Users\shre5185\Documents\MSGIS\MIP\YellowstoneData\Yellowstone.gdb\FinalSum"]
        geometry = "knight"
        scale = 10
        
        # create database
        db_path = cvl.create_database(self.working_dir, self.test_fgdb);
        
        nodes_fc = db_path + "\\nodes";
        edges_fc = db_path + "\\edges";

        # test
        cvl.sample_rasters_to_vector(rasters, geometry, scale, nodes_fc, edges_fc);
        assert arcpy.Exists(nodes_fc) == True
        assert arcpy.Exists(edges_fc) == True
        
        # cleanup
        arcpy.Delete_management(nodes_fc)
        arcpy.Delete_management(edges_fc)
        arcpy.Delete_management(db_path);
        
    # test
    def atest_create_vector_layer_queen(self):
        rasters = ["C:\Users\shre5185\Documents\MSGIS\MIP\YellowstoneData\Yellowstone.gdb\FinalSum"]
        geometry = "queen"
        scale = 10
        
        # create database
        db_path = cvl.create_database(self.working_dir, self.test_fgdb);
        
        nodes_fc = db_path + "\\nodes";
        edges_fc = db_path + "\\edges";

        # test
        cvl.sample_rasters_to_vector(rasters, geometry, scale, nodes_fc, edges_fc);
        assert arcpy.Exists(nodes_fc) == True
        assert arcpy.Exists(edges_fc) == True
        
        # cleanup
        arcpy.Delete_management(nodes_fc)
        arcpy.Delete_management(edges_fc)
        arcpy.Delete_management(db_path);
     
    # test
    def atest_create_vector_layer_rook(self):
        rasters = ["C:\Users\shre5185\Documents\MSGIS\MIP\YellowstoneData\Yellowstone.gdb\FinalSum"]
        geometry = "rook"
        scale = 10
        
        # create database
        db_path = cvl.create_database(self.working_dir, self.test_fgdb);
        
        nodes_fc = db_path + "\\nodes";
        edges_fc = db_path + "\\edges";

        # test
        cvl.sample_rasters_to_vector(rasters, geometry, scale, nodes_fc, edges_fc);
        assert arcpy.Exists(nodes_fc) == True
        assert arcpy.Exists(edges_fc) == True
        
        # cleanup
        arcpy.Delete_management(nodes_fc)
        arcpy.Delete_management(edges_fc)
        arcpy.Delete_management(db_path); 
        
    # test
    def test_create_vector_layer_sum(self):
        rasters = ["C:\Users\shre5185\Documents\MSGIS\MIP\YellowstoneData\Yellowstone.gdb\LandCoverReclas",
                   "C:\Users\shre5185\Documents\MSGIS\MIP\YellowstoneData\Yellowstone.gdb\RoadsReclas",
                   "C:\Users\shre5185\Documents\MSGIS\MIP\YellowstoneData\Yellowstone.gdb\PostsReclas",
                   "C:\Users\shre5185\Documents\MSGIS\MIP\YellowstoneData\Yellowstone.gdb\TrailsReclas",
                   "C:\Users\shre5185\Documents\MSGIS\MIP\YellowstoneData\Yellowstone.gdb\SlopeReclas"]
        geometry = "rook"
        scale = 20
        
        # create database
        db_path = cvl.create_database(self.working_dir, self.test_fgdb);
        
        nodes_fc = db_path + "\\nodes";
        edges_fc = db_path + "\\edges";

        # test
        cvl.sample_rasters_to_vector(rasters, geometry, scale, nodes_fc, edges_fc);
        assert arcpy.Exists(nodes_fc) == True
        assert arcpy.Exists(edges_fc) == True
        
        # cleanup
        #arcpy.Delete_management(nodes_fc)
        #arcpy.Delete_management(edges_fc)
        #arcpy.Delete_management(db_path);   
        
    
if __name__ == "__main__":
    unittest.main()
