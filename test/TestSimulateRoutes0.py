'''
Created on May 22, 2013

@author: shre5185
'''
import unittest
from rnd import SimulateRoutes0 as sr;

class Test(unittest.TestCase):
    
    


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testSimulate(self):
        source_pt = "495857.026  4979032.640";
        dest_pt = "567461.776  4894990.640";
        network_ds_path = r"C:\VegasRun\master\vegas.gdb\VectorModel\VectorModel_ND";
        randomness = 20;
        iterations = 1;
        cores = 1;
        output_routes_fc = r"C:\VegasRun\master\vegas.gdb\routes";
        working_dir = r"C:\VegasRun";
        toolbox = r"C:\Users\shre5185\Documents\MSGIS\MIP\YellowstoneData\VectorMobilityModeling.tbx";
        sr.simulate(source_pt, dest_pt, network_ds_path, randomness, iterations, cores, working_dir, toolbox, output_routes_fc);


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testSimulate']
    unittest.main()