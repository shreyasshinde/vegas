'''
Created on Nov 4, 2012

@author: shreyas shinde, msgis, university of redlands
'''

import arcpy;
import arcpy.da;
import datetime;
import sys;
import os;
import traceback;
import numpy;

#
# Reads the paths to input rasters from the console.
# @return: an array of input raster paths 
#
def get_input_rasters(paramIndex=0):
    rasters = [];
    if isConsoleTool():
        # get from console
        path = str(raw_input("Enter path to input raster or type DONE to finish the input: ")).lower();
        while path != "done" and path != "DONE":
            rasters.append(path);
            path = raw_input("Enter path to input raster or type DONE to finish the input: "); 
    else:
        rasters_param = arcpy.GetParameterAsText(paramIndex);
        rasters = rasters_param.split(';');
            
    if len(rasters) == 0:
        raise Exception("Error: Input rasters cannot be empty.");
    return rasters; 
        


#
# Reads the input geometry from the console.
# @return: a string representing the input geometry;
#          can be rook, queen or knight
#
def get_input_geometry(paramIndex=0):
    if isConsoleTool():
        geometry = str(raw_input("Enter sampling geometry (Rook, Queen, Knight): ")).lower();
    else:
        geometry = arcpy.GetParameterAsText(paramIndex);
    if geometry == None or (geometry != "Rook" and geometry != "Queen" and geometry != "Knight"):
        raise Exception("Error: Incorrect sampling geometry. Values: Rook, Queen or Knight.");
    return geometry;


#
# Reads the input scale from the console.
# @return: an integer representing the input scale;
#          format = 1:10 or 1:20
#
def get_input_scale(paramIndex=0):
    if isConsoleTool():
        scale = raw_input("Enter sampling resolution (like 10, 20, etc.):");
    else:
        scale = arcpy.GetParameterAsText(paramIndex);
    if scale == None or scale == "":
        raise Exception("Error: Input sampling resolution cannot be empty.");
    return int(scale);

#
# Reads the path to the nodes feature class.
# @param paramIndex: the index of the parameter argument if this was a GUI based application
# @return: the path to the nodes feature class
def get_nodes_fc(paramIndex=0):
    if isConsoleTool():
        nodes_fc = raw_input("Enter the path to the output nodes feature class: ");
    else:
        nodes_fc = arcpy.GetParameterAsText(paramIndex);
    if nodes_fc == "":
        raise Exception("Input argument path to nodes feature class cannot be empty.");
    else:
        return nodes_fc;
    

#
# Reads the path to the edges feature class
# @param paramIndex: the index of the parameter argument if this was a GUI based application
# @return: the path to the edges feature class
def get_edges_fc(paramIndex=0):
    if isConsoleTool():
        edges_fc = raw_input("Enter the path to the output edges feature class: ");
    else:
        edges_fc = arcpy.GetParameterAsText(paramIndex);
    if edges_fc == "":
        raise Exception("Input argument path to edges feature class cannot be empty.");
    else:
        return edges_fc;
#
# Prints the script usage and help.
#
def print_help():
    print "This script tool is converts the input rasters into a vector " \
          + "by creating a set of vertices and edges from the coarsest raster " \
          + "and the geometry and scale."
    print
          

# 
# Iterates over all the input rasters and finds the coarsest 
# raster and returns its path.
# @return: a string path of the coarsest raster
def find_coarsest_raster(raster_paths):
    if raster_paths == None:
        raise Exception("Input array of rasters cannot be empty or null.");
  
    # to determine coarseness, we check the resolution of a raster cell
    # smallest number is coarsest  
    coarsest_raster = "";
    coarsest_res = 0;
    for raster_path in raster_paths:
        desc = arcpy.Describe(raster_path);
        # gets the cell resolution in this raster
        res = desc.meanCellWidth * desc.meanCellHeight;
        if res > coarsest_res:
            coarsest_raster = raster_path;
            coarsest_res = res;
            
    print "Coarsest raster: " + coarsest_raster;
    return coarsest_raster;

#
# Deletes each ndarray in the list to free memory
# @param list_of_ndarray: list of NumPy arrays
def free_ndarray(list_of_ndarray=[]):
    for ndarray in list_of_ndarray:
        del ndarray;
        
#
# Creates the nodes feature class where the sample nodes from the grid will be stored.
# @param nodes_fc_path: path to the nodes feature class 
def create_nodes_feature_class(nodes_fc_path, spatialReference=None):
    db_path = os.path.dirname(nodes_fc_path);
    nodes_fc_name = os.path.basename(nodes_fc_path);
    
    # fields for nodes
    nodes_fc_fields = [("ROW_ID", "INTEGER"), ("VALUE","DOUBLE")];
    create_feature_class(db_path, nodes_fc_name, "POINT", "DISABLED", "DISABLED", spatialReference, nodes_fc_fields);
    

#
# Creates the nodes feature class where the sample nodes from the grid will be stored.
# @param edges_fc_path: path to the edges feature class 
def create_edges_feature_class(edges_fc_path, spatialReference=None):
    db_path = os.path.dirname(edges_fc_path);
    edges_fc_name = os.path.basename(edges_fc_path);
    
    # edges will contain to and from costs, an identifier for each edge and field to count how many times it was repeated
    edges_fc_fields = [("SRC_ID", "INTEGER"),("DES_ID", "INTEGER"),("COST", "DOUBLE"),("REPEATED", "LONG")]
    create_feature_class(db_path, edges_fc_name, "POLYLINE", "DISABLED", "DISABLED", spatialReference, edges_fc_fields)
        

#
# Creates a new feature class in a temporary directory with
# the given name and type. The optional dictionary object 
# attributes can be used to define feature class attributes
# @param db_path: the path to the database - should be path to FGDB
# @param name: name of the feature class 
# @param type: type of feature class namely POINT,MULTIPOINT,POLYGON,POLYLINE
# @param attributes: optional attributes to create in the feature class 
# @return: the path to the created feature class
# @raise exception:  if the feature class could not be created for whatever reason
def create_feature_class(db_path, name, geometry_type="POINT", hasM="DISABLED", hasZ="DISABLED", spatialReference=None, fields=[]):
    if geometry_type not in ["POINT", "MULTIPOINT", "POLYGON", "POLYLINE" ]:
        raise Exception("Invalid feature class type.");
    
    # create the FC in the FGDB
    arcpy.CreateFeatureclass_management (db_path, name, geometry_type, [], hasM, hasZ, spatialReference);
    
    fc_name = os.path.join(db_path, name);
    
    # create the attributes if specified
    for field in fields:
        arcpy.AddField_management(fc_name, field[0], field[1]);
                                  
    return fc_name;
    
#
# A utility function to return a directory name from the current
# date time string.
# @return a datetime string as directory name
def create_dirname_from_datetime():
    dt = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S");
    return str(dt);


#
# Creates a new file geodatabase with the specified name in the input directory
# @param dir_path: a directory where the database will be created
# @param db_name: the name of the database 
# @return: full path to the created database 
def create_database(dir_path, db_name):
    arcpy.env.overwriteOutput = True;
    dataset = os.path.join(dir_path, db_name + ".gdb");
    if False == arcpy.Exists(dataset):
        arcpy.CreateFileGDB_management(dir_path, db_name + ".gdb");
    return os.path.join(dir_path, db_name + ".gdb");


#
# Creates the nodes and edges based on the input rasters, geometry and scale.
# The function samples the input rasters and sets the values for each node. 
# The cost for each edge is computed based on the difference of cost on the connecting
# nodes
# @param rasters: an array of input rasters
# @param geometry: a string - queen, knight or rook
# @param scale: the scale at which the rasters should be sampled
# @param nodes_fc: the feature class path where the nodes should be stored. Should contain a field VALUE (FLOAT)
# @param edges_fc: the feature class path where the edges should be stored. Should contain fields TO_FROM, FROM_TO, EDGE_ID 
def sample_rasters_to_vector(rasters, geometry, scale, nodes_fc, edges_fc):
    #
    # algorithm:-
    #     1. find the coarsest raster from the input rasters - this will be used as the basis of the vector network
    #     2. get resolution and coordinates of the raster
    #     3. compute the dimensions of the scaled vector network
    # data structures:
    #     1. nodes => map of every sampled node: {xcoord_ycoord, ((x,y),id,src_value)}
    #     2. edges => array of every edge created between nodes: [(source_coords, dest_coords, source_id, dest_id, src_to_des_cost, des_to_src_cost)]
    #     We will first create an in-memory representation of all the nodes and edges. After all nodes and edges have been sampled,
    #     we insert them into a feature class.
    
    # spatial reference of the nodes and edges feature class
    spatialRef = arcpy.Describe(rasters[0]).spatialReference;
    
    # create the feature classes
    arcpy.AddMessage("Creating output nodes & edges feature classes.")
    create_nodes_feature_class(nodes_fc, spatialRef);
    create_edges_feature_class(edges_fc, spatialRef);
    
    geometry = geometry.lower();
    scale = long(scale);
    
    # find the coarsest raster
    arcpy.AddMessage("Finding coarsest raster.");
    coarsest_raster = find_coarsest_raster(rasters);
    
    # compute the rows, cols, resolution of the selected raster
    desc = arcpy.Describe(coarsest_raster);
    rows = float(desc.height);
    cols = float(desc.width);
    
    # get the coordinates of the corners of the raster
    arcpy.AddMessage("Computing coordinates of the raster.");
    ymax = float(arcpy.GetRasterProperties_management(coarsest_raster, "TOP").getOutput(0));
    ymin = float(arcpy.GetRasterProperties_management(coarsest_raster, "BOTTOM").getOutput(0)); 
    xmin = float(arcpy.GetRasterProperties_management(coarsest_raster, "LEFT").getOutput(0)); 
    xmax = float(arcpy.GetRasterProperties_management(coarsest_raster, "RIGHT").getOutput(0));
    
    dX = (xmax-xmin)/cols;
    arcpy.AddMessage("dX:" + str(dX));
    dY = (ymax-ymin)/rows;
    arcpy.AddMessage("dY:" + str(dY));
    
    # these are the values that need to get the next coordinate of a node
    scaledDX = scale*dX;
    scaledDY = scale*dY;
    
    # get the number of nodes that we will be creating from the raster based on scale
    no_of_col_nodes = int(cols/scale);
    no_of_row_nodes = int(rows/scale);
    
    # map of nodes that will need to be inserted in the FC
    # the key to the map is xcoord_ycoord and the src_value is the ((x,y),src_value) tuple
    nodes = {};
    edges = [];
    
    # read all the rasters in memory
    rasterScanner = RasterScanner(rasters);
    
    # create the nodes and edges while sampling the input raster for the src_value of the nodes
    src_node_id = 0;
    for yrun in range(0, no_of_row_nodes):
        # read the input rasters by rows - so that we can get the underlying
        # src_value of the node
        # Note: NumPy arrays need to be deleted
        row_number = int(yrun*scale);
        arcpy.AddMessage("Processing row {0}/{1}.".format(row_number, rows));
         
        
        # array of nodes and edges that will need to be inserted in the FC
        for xrun in range(0, no_of_col_nodes):
            # coordinates of the point
            xcoord = xmin + (scaledDX*xrun);
            ycoord = ymin + (scaledDY*yrun);
            
            # sample the underlying raster and get the src_value of the node
            # TODO: currently adding the src_value of each raster
            index = xrun; 
            col_number = scale*index;
            src_value = rasterScanner.sample_rasters(row_number, col_number);
            
            src = (xcoord, ycoord);    
            src_node_id += 1;
            
            # add the node to our map
            nodes_key = str(xcoord) + "_" + str(ycoord); #key = x_y
            nodes[nodes_key] = (src, src_node_id, src_value);
            
            # creating the edges
            # all geometries have the following edges in common
            if xrun > 0:
                # node to the left of current node
                xcoord_left_node = xmin + ((xrun-1)*scaledDX);
                ycoord_left_node = ycoord;
                
                # sample the src_value at this new node
                nodes_key = str(xcoord_left_node) + "_" + str(ycoord_left_node);
                des_value = nodes[nodes_key][2]; #rasterScanner.sample_rasters(yrun*scale, scale*(index-1));
                des_node_id = nodes[nodes_key][1];
                des = (xcoord_left_node, ycoord_left_node);
                
                # create the edge
                #array_of_edge_nodes = arcpy.Array([arcpy.Point(xcoord_left_node, ycoord_left_node), arcpy.Point(xcoord,ycoord)])
                #edge = arcpy.Polyline(array_of_edge_nodes); #constructs the line from the nodes
                
                # compute the cost of the edge
                src_to_des_cost = abs(des_value - src_value);
                #des_to_src_cost = src_value - des_value;
                
                #edge_id += 1;
                edges.append((src, des, src_node_id, des_node_id, src_to_des_cost)); 
            
            if yrun > 0:
                # node to the bottom of the current node
                xcoord_bot_node = xcoord;
                ycoord_bot_node = ymin + ((yrun-1)*scaledDY);
                
                # create the edge
                #array_of_edge_nodes = arcpy.Array([arcpy.Point(xcoord_bot_node, ycoord_bot_node), arcpy.Point(xcoord,ycoord)])
                #edge = arcpy.Polyline(array_of_edge_nodes);
                
                # sample the src_value at this new node
                nodes_key = str(xcoord_bot_node) + "_" + str(ycoord_bot_node);
                des_value = nodes[nodes_key][2]; #rasterScanner.sample_rasters((yrun-1)*scale, scale * (index));
                des_node_id = nodes[nodes_key][1];
                des = (xcoord_bot_node, ycoord_bot_node);
                
                # compute the cost of the edge
                src_to_des_cost = abs(des_value - src_value);
                #des_to_src_cost = src_value - des_value;
                
                # add edge to our list
                edges.append((src, des, src_node_id, des_node_id, src_to_des_cost));
            
            # for queen and knight geometries, we need to create the diagonal edges
            if geometry == "queen" or geometry == "knight":
                if yrun > 0 and xrun < no_of_col_nodes-1:
                    # node diagonal from current node to lower right node (\)
                    xcoord_lowerright = xmin + (scaledDX*(xrun+1));
                    ycoord_lowerright = ymin + (scaledDY*(yrun-1));
                    
                    # create the edge
                    #array = arcpy.Array([arcpy.Point(xcoord, ycoord), arcpy.Point(xcoord_lowerright, ycoord_lowerright)])
                    #edge = arcpy.Polyline(array);
                    
                    # sample the src_value at this node
                    nodes_key = str(xcoord_lowerright) + "_" + str(ycoord_lowerright);
                    des_value = nodes[nodes_key][2]; #rasterScanner.sample_rasters((yrun-1)*scale, scale * (index+1));
                    des_node_id = nodes[nodes_key][1];
                    des = (xcoord_lowerright, ycoord_lowerright);
                    
                    # compute cost of the dge
                    src_to_des_cost = abs(des_value - src_value);
                    #des_to_src_cost = src_value - des_value;
                    
                    # add edge to our list
                    #edge_id += 1;
                    edges.append((src, des, src_node_id, des_node_id, src_to_des_cost));
                    
                if xrun > 0 and yrun > 0:
                    # node diagonal from lower left node to current node  (/)
                    xcoord_lowerright = xmin + (scaledDX*(xrun-1));
                    ycoord_lowerright = ymin + (scaledDY*(yrun-1));
                    
                    # create the edge
                    #array = arcpy.Array([arcpy.Point(xcoord_lowerright, ycoord_lowerright), arcpy.Point(xcoord, ycoord)])
                    #edge = arcpy.Polyline(array);
                    
                    # sample the src_value at this node
                    nodes_key = str(xcoord_lowerright) + "_" + str(ycoord_lowerright); 
                    des_value = nodes[nodes_key][2]; #rasterScanner.sample_rasters((yrun-1)*scale, scale * (index-1));
                    des_node_id = nodes[nodes_key][1];
                    des = (xcoord_lowerright, ycoord_lowerright);
                    
                    # compute cost of the edge
                    src_to_des_cost = abs(des_value - src_value);
                    #des_to_src_cost = src_value - des_value;
                    
                    # add edge to our list
                    #edge_id += 1;
                    edges.append((src, des, src_node_id, des_node_id, src_to_des_cost));
            
            # for knight we need compute additional diagonals two cells below
            if geometry == "knight":
                if yrun > 1 and xrun < no_of_col_nodes-1:
                    # node diagonal from current point to the two rows lower on the right side (\\)
                    xcoord_lowerright = xmin + (scaledDX*(xrun+1));
                    ycoord_lowerright = ymin + (scaledDY*(yrun-2));
                    
                    # create the edge
                    #array = arcpy.Array([arcpy.Point(xcoord, ycoord), arcpy.Point(xcoord_lowerright, ycoord_lowerright)])
                    #edge = arcpy.Polyline(array);
                    
                    # sample the src_value at this node
                    nodes_key = str(xcoord_lowerright) + "_" + str(ycoord_lowerright);
                    des_value = nodes[nodes_key][2]; #rasterScanner.sample_rasters((yrun-2)*scale, scale * (index+2));
                    des_node_id = nodes[nodes_key][1];
                    des = (xcoord_lowerright, ycoord_lowerright);
                    
                    # compute cost of the edge
                    src_to_des_cost = abs(des_value - src_value);
                    #des_to_src_cost = src_value - des_value;
                    
                    # add edge to our list
                    #edge_id += 1;
                    edges.append((src, des, src_node_id, des_node_id, src_to_des_cost));
                
                if xrun > 0 and yrun > 1:
                    # node diagonal from the current point to the two points lower on the left side (//)
                    xcoord_lowerleft = xmin + (scaledDX*(xrun-1));
                    ycoord_lowerleft = ymin + (scaledDY*(yrun-2));
                    
                    # create the edge
                    #array = arcpy.Array([arcpy.Point(xcoord_lowerleft, ycoord_lowerleft), arcpy.Point(xcoord, ycoord)])
                    #edge = arcpy.Polyline(array);
                    
                    # sample the src_value at this node
                    nodes_key = str(xcoord_lowerleft) + "_" + str(ycoord_lowerleft);
                    des_value =  nodes[nodes_key][2]; #rasterScanner.sample_rasters((yrun-2)*scale, scale * (index-2));
                    des_node_id = nodes[nodes_key][1];
                    des = (xcoord_lowerleft, ycoord_lowerleft);
                    
                    # compute cost of the edge
                    src_to_des_cost = abs(des_value - src_value);
                    #des_to_src_cost = src_value - des_value;
                    
                    # add edge to our list
                    #edge_id += 1;
                    edges.append((src, des, src_node_id, des_node_id, src_to_des_cost));
                
    # cleanup
    #arcpy.AddMessage("Deleting read rasters from memory.");
    rasterScanner.cleanup();
    rasterScanner = None;
    
    # done editing the databases and commit the transaction
    arcpy.AddMessage("Creating a cursor to add nodes.")
    nodesCursor = arcpy.da.InsertCursor(nodes_fc, ("SHAPE@XY", "ROW_ID", "VALUE"));
    
    arcpy.AddMessage("Inserting nodes.");
    for node in nodes.values():
        nodesCursor.insertRow(node);
    
    # delete the cursort that inserts rows
    del nodesCursor;
        
    # open cursors to insert edges
    arcpy.AddMessage("Creating a cursor to add edges.");
    edgesCursor = arcpy.da.InsertCursor(edges_fc, ("SHAPE@", "SRC_ID", "DES_ID", "COST", "REPEATED"));
            
    # add the nodes and edges to the fc 
    arcpy.AddMessage("Inserting edges.");    
    for edge in edges:
        array = arcpy.Array([arcpy.Point(edge[0][0], edge[0][1]), arcpy.Point(edge[1][0], edge[1][1])])
        line = arcpy.Polyline(array);
        edgesCursor.insertRow((line, edge[2], edge[3], edge[4], 0));
        del line;
    
    # delete the cursor that inserts edges
    del edgesCursor;
    arcpy.AddMessage("Sampling complete.");
    

#
# Creates a new feature dataset within a database path.
# @param db_path: path to the geodatabase
# @param feature_dataset: the name of the feature dataset
# @param spatial_reference: the spatial reference of the feature dataset 
def create_feature_dataset(db_path, feature_dataset, spatial_reference):
    arcpy.CreateFeatureDataset_management(db_path, feature_dataset, spatial_reference);
    return os.path.join(db_path, feature_dataset);


#
# Normalizes an input path from C:\arcgis\test to C:\\arcgis\\test.
# @param path: input path to be normalized
def normalize_path(path):
    paths = os.path.split(path);
    return paths[0] + "\\" + paths[1];

#
# The main entry point into the script for console application
#    
def main():
    try: 
        # read the input raster paths
        rasters = get_input_rasters(0);
        arcpy.AddMessage("Input rasters: " + str(rasters));
        
        # read the input geometry
        geometry = get_input_geometry(1);
        arcpy.AddMessage("Sampling geometry: " + geometry)
        
        # read the input scale
        scale = get_input_scale(2);
        arcpy.AddMessage("Sampling resolution: " + str(scale))
        
        # create a feature class to store the vertices
        # and another to store the edges
        nodes_fc_path = get_nodes_fc(3);
        edges_fc_path = get_edges_fc(4);
        arcpy.AddMessage("Path to nodes feature class: " + nodes_fc_path);
        arcpy.AddMessage("Path to edges feature class: " + edges_fc_path);
        
        # create the nodes and edges along with sampling the value
        sample_rasters_to_vector(rasters, geometry, scale, nodes_fc_path, edges_fc_path);
        
        # set the output parameters
        arcpy.SetParameterAsText(5, nodes_fc_path);
        arcpy.SetParameterAsText(6, edges_fc_path);
        
        arcpy.AddMessage("Done!");
    except Exception as e:
        arcpy.AddError(str(e));
        exc_type, exc_obj, exc_tb = sys.exc_info()
        arcpy.AddError(traceback.extract_tb(exc_tb));
 

#
# A function that indicates if the script is run as a stand alone 
# console tool or through a ArcMap GUI.
# @return: True if the script is being run in console mode, False otherwise 
def isConsoleTool():
    if arcpy.GetParameterAsText(0) == "":
        return True;
    else:
        return False;    

#
# A class that reads rows of raster based on the input
# geometry specified by the client. This class reads +-2 rows
# of all rasters at a time.
class RasterScanner(object):
    scale = 0;
    raster_paths = [];
    list_of_ndarray = [];
    
    #
    # Constructs new
    # 
    def __init__(self, raster_paths):
        self.raster_paths = [];
        self.list_of_ndarray = [];
        self.raster_paths = raster_paths;
        
        # read all the rasters for the given row
        for raster in raster_paths:
            arcpy.AddMessage("Raster: " + raster);
            try:
                ndarray = arcpy.RasterToNumPyArray(in_raster=raster);
                #print "Row number " + str(row_number) + ", shape = " + str(ndarray.shape);
                self.list_of_ndarray.append(ndarray);
            except:
                # do nothing'
                pass
                    
    
    #
    # Returns the cell value at the index for each raster row in the list
    # @return: a list of cell values from different rasters
    def get_value(self, row, col):
        values = [];
        for array in self.list_of_ndarray:
            try:
                values.append(array[row][col]);
            except:
                pass
        return values;
    
    #
    # Cleans up all the scanned rasters
    def cleanup(self):
        for array in self.list_of_ndarray:
            del array;
                
    #
    # Samples the input list of NumPy raster arrays by using the sampling function
    # and returns the sampled value.
    # @param index: the cell location to sample
    # @param sampling_function: an optional function that is given the actual values of the rasters to combine
    #                           if this function is not provided a simple additive function is used 
    # @return the combined value of the sampled rasters 
    def sample_rasters(self, row, col, sampling_func=None):
        # extract the value of the cell from all ndarrays
        values = self.get_value(row, col);
        print values;
        
        # invoke the sampling function if provided
        value = 0.0;
        if sampling_func != None:
            value = sampling_func(values);
        else:
            # default additive function
            #print "Sum: " + str(values);
            value = float(sum(values)); 
            print "Sample value at ({0},{1})={2}".format(row, col, value);
        return value;
    
 
#
# Call the main function
#   
if __name__ == '__main__':
    main()
