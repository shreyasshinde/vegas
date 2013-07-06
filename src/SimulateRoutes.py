'''
Created on May 22, 2013

@author: shreyas shinde, university of redlands
This module simulates routes between two input points
using ArcGIS Network Analyst and the Randomize tool by iteratively
applying some random values to each of cost of an edge.
'''

import datetime;
import sys;
import os;
import traceback;
import arcpy;
import multiprocessing;
import shutil;

#
# Returns the path to the source point from which the paths need
# to be calculated.
# @return: path to a point feature class
def get_source_point(paramIndex=0):
    if isConsoleTool():
        source_pt = str(raw_input("Enter coordinates of source point (x y): "));
    else:
        source_pt = str(arcpy.GetParameterAsText(paramIndex));
    if source_pt == "":
        raise Exception("Error: Input argument path to source point cannot be empty.");
    else:
        return source_pt;
    
#
# Returns the path to the destination point to which the paths need
# to be calculated.
# @return: path to a point feature class
def get_dest_point(paramIndex=0):
    if isConsoleTool():
        dest_pt = str(raw_input("Enter path to destination point (x y): "));
    else:
        dest_pt = str(arcpy.GetParameterAsText(paramIndex));
    if dest_pt == "":
        raise Exception("Error: Input argument path to destination point cannot be empty.");
    else:
        return dest_pt;
    
#
# Returns the path to the network dataset on which the routing will take place.
# @return: path to a point feature class
def get_network_dataset_path(paramIndex=0):
    if isConsoleTool():
        nd_path = str(raw_input("Enter path to network dataset: "));
    else:
        nd_path = str(arcpy.GetParameterAsText(paramIndex));
    if nd_path == "":
        raise Exception("Error: Input argument path to network dataset cannot be empty.");
    else:
        return nd_path;
    
#
# Reads the percent random energy parameter
# @param paramIndex: the index of the parameter argument if this was a GUI based application
# @return: the percentage of random energy to apply 
def get_random_percent(paramIndex=0):
    if isConsoleTool():
        percent = int(raw_input("Enter the percentage of random energy to apply (usually between 5-20): "));
    else:
        percent = int(arcpy.GetParameterAsText(paramIndex));
    if percent == "":
        raise Exception("Input argument percentage of random energy cannot be empty.");
    else:
        return percent;
    
#
# Reads the percent random energy parameter
# @param paramIndex: the index of the parameter argument if this was a GUI based application
# @return: the number of CPU cores
def get_cpu_cores(paramIndex=0):
    if isConsoleTool():
        cores = str(raw_input("Enter the number of CPU cores you would like this tool to utilize (default=4): "));
    else:
        cores = str(arcpy.GetParameterAsText(paramIndex));
    if cores == "":
        return 4; # default
    else:
        return int(cores);  
    
#
# Reads the number of iterations for which the simulation will be run.
# @param paramIndex: the index of the parameter argument if this was a GUI based application
# @return: the number of iterations
def get_iterations(paramIndex=0):
    if isConsoleTool():
        iterations = str(raw_input("Enter the number of iterations that the simulation should execute (default=999): "));
    else:
        iterations = str(arcpy.GetParameterAsText(paramIndex));
    if iterations == "":
        return 1000; # default
    else:
        return int(iterations); 
    
#
# Reads the percent random energy parameter
# @param paramIndex: the index of the parameter argument if this was a GUI based application
# @return: the number of CPU cores
def get_output_routes_fc_path(paramIndex=0):
    if isConsoleTool():
        path = str(raw_input("Enter the path to the output feature class where the simulated routes will be stored: "));
    else:
        path = str(arcpy.GetParameterAsText(paramIndex));
    if path == "":
        raise Exception("Input argument path to output feature class cannot be empty.");
    else:
        return path; 
    
#
# Get path to a working directory where all the processing will take place.
# 
def get_working_dir(paramIndex=0):
    if isConsoleTool():
        path = str(raw_input("Enter the path to a working directory: "));
    else:
        path = str(arcpy.GetParameterAsText(paramIndex));
    if path == "":
        raise Exception("Input argument path to working directory cannot be empty.");
    else:
        return path;
    
#
# Get path to a vegas toolbox.
# 
def get_vegas_toolbox(paramIndex=0):
    if isConsoleTool():
        path = str(raw_input("Enter the path to VEGAS toolbox: "));
    else:
        path = str(arcpy.GetParameterAsText(paramIndex));
    if path == "":
        raise Exception("Input argument path to VEGAS toolbox cannot be empty.");
    else:
        return path;    


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
# A private function for the worker processes to process the number of simulations assigned to them.
# Each worker will do a chunk of work for the whole simulation but setting up the route solver layer,
# computing the route, applying the randomness and then re-generating the route and finally
# writing all the routes to an output feature class.
# @param parameters: a dictionary object containing all the parameters required for the worker simulation  
# @return: a string array of size 2 where first is a paths to routes processed by worker, the second is the path to the repeated count of each edge  
def simulate_for_worker(parameters):
    '''
    Algorithm:
        1. Unpack parameters
        2. Create a new route layer on the network dataset using the 'Cost' impedance attribute
        3. Add network location to the route layer based on the source pt and destination pt
    '''
    # check out network extension license
    arcpy.CheckOutExtension("Network");
    
    randomness = parameters["randomness"];    
    iterations = parameters["iterations"];
    fds_name = parameters["feature_dataset_name"];
    network_ds_name = parameters["network_dataset_name"];
    loc_fc_name = parameters["locations_fc_name"];
    fgdb_name = parameters["database_name"]; 
    working_dir = parameters["working_directory"];
    worker_id = parameters["worker_id"];
    toolbox = parameters["toolbox"];
    
    # frequency of the occurance of each edge in the routes
    edge_frequency = {};
    
    arcpy.AddMessage("Worker (" + worker_id + ") - working directory: " + working_dir);
    
    # derived parameters
    network_ds_path = os.path.join(working_dir, fgdb_name, fds_name, network_ds_name);
    fds_path = os.path.join(working_dir, fgdb_name, fds_name);
    fgdb_path = os.path.join(working_dir, fgdb_name);
    loc_fc_path = os.path.join(working_dir, fgdb_name, fds_name, loc_fc_name);
    
    arcpy.AddMessage("Worker (" + worker_id + ") - fds path: " + fds_path);
    arcpy.AddMessage("Worker (" + worker_id + ") - fds path: " + fgdb_path);
    arcpy.AddMessage("Worker (" + worker_id + ") - locations fc path: " + loc_fc_path);
    
    # make a route layer
    result = arcpy.na.MakeRouteLayer(network_ds_path,"Route","Cost");
    route_layer = result.getOutput(0);
    
    # get the names of all the sublayers within the route layer. find the 'Stops' layer.
    sub_layer_names = arcpy.na.GetNAClassNames(route_layer);
    stops_layer_name = sub_layer_names["Stops"];
    
    # load stops into the 'Stops' layer from our 'locations' feature class
    arcpy.na.AddLocations(route_layer,stops_layer_name,loc_fc_path,"","");
    
    solved_routes_fc = fds_path + "\\routes"; #the fc where the route of each iteration will be stored

    # create a table from the edge_frequency dictionary to keep track for the repeated edges
    arcpy.AddMessage("Worker (" + worker_id + ") - creating the repeated frequency table.");
    arcpy.management.CreateTable(fgdb_path, "repeated");
    repeated_table_path = os.path.join(fgdb_path, "repeated");
    arcpy.AddField_management(repeated_table_path, "FeatureID", "LONG");
    arcpy.AddField_management(repeated_table_path, "Repeated", "LONG");
    
    # import the toolbox that applies the random energy
    arcpy.ImportToolbox(toolbox);

    # make the iterations
    for i in xrange(iterations):
        arcpy.AddMessage("Worker (" + worker_id + ") - iteration: " + str(i));
        
        # apply the random energy
        arcpy.AddMessage("Worker (" + worker_id + ") - applying random energy." );
        arcpy.Randomize_tools(randomness, os.path.join(fds_path, "nodes"), os.path.join(fds_path, "edges"), fgdb_path);
        
        # re-build the network
        arcpy.na.BuildNetwork(network_ds_path);
    
        # solve
        arcpy.na.Solve(route_layer, "HALT", "TERMINATE");
        arcpy.AddMessage("Worker (" + worker_id + ") - solving route." );
        traversedEdges = arcpy.na.CopyTraversedSourceFeatures(route_layer,"in_memory").getOutput(0);
        arcpy.AddMessage("Worker (" + worker_id + ") - creating edge frequency table." );
        with arcpy.da.SearchCursor(traversedEdges, ("SourceOID")) as cursor:
            for row in cursor:
                edge_id = row[0];
                if edge_id in edge_frequency:
                    # increment repeated count
                    edge_frequency[edge_id] = edge_frequency[edge_id] + 1;
                else:
                    # this edge occurred for the first time
                    edge_frequency[edge_id] = 1;
        del cursor;
            
        # get the 'Routes' sub-layer from the route layer
        routes_sub_layer = arcpy.mapping.ListLayers(route_layer,sub_layer_names["Routes"])[0];
        arcpy.AddMessage("Worker (" + worker_id + ") - routes sub layer: " + str(routes_sub_layer));
        
        # copy the layer as a output
        if arcpy.Exists(solved_routes_fc):
            arcpy.management.Append([routes_sub_layer], solved_routes_fc);
        else:
            arcpy.management.CopyFeatures(routes_sub_layer, solved_routes_fc); 

        # delete the in memory feature class            
        arcpy.Delete_management("in_memory\\Junctions", "");
        arcpy.Delete_management("in_memory\\Turns", "");
        arcpy.Delete_management("in_memory\\Edges", "");
            
        # inserting the edges repeated frequency 
        with arcpy.da.InsertCursor(repeated_table_path, ("FeatureID", "Repeated")) as cursor:
            for edge_id in edge_frequency:
                cursor.insertRow((edge_id, edge_frequency[edge_id]));
        del cursor;
        
    # iterations are complete
    return (solved_routes_fc, repeated_table_path);
    
    
#
# This function simuates the routes between source and destination points using the underlying network
# dataset iteratively applying the random noise to the cost of edge traversal. This function splits
# the simulation into many cores and the resultant routes are written to the output feature class.
# @param source_pt: the point from which the routes will start 
# @param dest_pt: the point to which the routes will end
# @param network_ds_path: the path to the network dataset
# @param randomness: the percentage of randomness to apply to each node
# @param cores: the number of parallel threads that should run this simulation. Default = 4
# @param iterations: the number of times the simulation needs to be run
# @param output_routes_fc: the path to the output feature class where the simulated routes will be located 
# @param working_dir: a path to a working directory where the temporary data processing will occur
# @return: path to the output routes feature for the worker
def simulate(source_pt, dest_pt, network_ds_path, randomness, iterations=1000, cores=4, working_dir=None, toolbox=None, output_routes_fc=None):
    '''
    Help: http://resources.arcgis.com/en/help/main/10.1/index.html#/Make_Route_Layer/00480000000n000000/
    Algorithm:
        1. Create copies of the original network dataset based on the input cores
        2. Create as many processes as the number of cores
        3. Every process should be given its working space with a copy of the network dataset
           and the number of iterations it needs to perform.
        4. The output of the process should be the path to the feature class where the routes
           are stored.
        5. Once all the processes have completed their respective iterations, the main
           process should copy all their respective simulated routes into the master
           output feature class.
    '''
    # derive paths to feature dataset & fgdb
    network_ds_name = os.path.basename(network_ds_path);
    fds_path = os.path.dirname(network_ds_path);
    edges_fc_path = fds_path + "\\edges";
    fds_name = os.path.basename(fds_path);
    fgdb_path = os.path.dirname(fds_path);
    fgdb_name = os.path.basename(fgdb_path);
    arcpy.AddMessage("Feature dataset path = " + str(fds_path));
    arcpy.AddMessage("File GDB path = " + str(fgdb_path));
    
    # create a new feature class inside the feature dataset to contain the source and destination points
    locations_fc_path = fds_path + "\\locations";
    if arcpy.Exists(locations_fc_path):
        arcpy.DeleteFeatures_management(locations_fc_path); 
    else:
        locations_fc_path = arcpy.CreateFeatureclass_management(fds_path, "locations", "POINT");
    cursor = arcpy.da.InsertCursor(locations_fc_path, ("SHAPE@XY"));
    source_pt = source_pt.split(); # as the input comes with a space seperated coordinates
    pt = arcpy.Point();
    pt.X = source_pt[0];
    pt.Y = source_pt[1];
    cursor.insertRow([pt]);
    dest_pt = dest_pt.split(); # as the input comes with a space seperated coordinates
    pt = arcpy.Point();
    pt.X = dest_pt[0];
    pt.Y = dest_pt[1];
    cursor.insertRow([pt]);
    del cursor;
    
    # in the working directory create a worker directory for each core
    for i in xrange(cores):
        worker_path = os.path.join(working_dir, "worker" + str(i));
        if not os.path.exists(worker_path):
            os.mkdir(worker_path);
        else:
            # delete and re-create
            shutil.rmtree(worker_path);
            os.mkdir(worker_path);
            
        # copy the fgdb into each worker directory
        arcpy.Copy_management(fgdb_path, os.path.join(worker_path, fgdb_name));

    # create a pool of workers
    pool = multiprocessing.Pool(processes=cores);

    # to capture the results of all the workers    
    results = [];
    
    # submit as many jobs as there are cores
    for i in xrange(cores):
        # define the parameters sent to the worker function
        parameters = {};
        parameters["randomness"] = randomness;    
        parameters["iterations"] = iterations/cores; # every core gets 1/cores times the number of iterations that must be computed
        parameters["feature_dataset_name"] = fds_name;
        parameters["network_dataset_name"] = network_ds_name;
        parameters["database_name"] = fgdb_name;    
        parameters["locations_fc_name"] = "locations";
        parameters["worker_id"] = str(i);
        parameters["working_directory"] = os.path.join(working_dir, "worker" + str(i));
        parameters["toolbox"] = toolbox;
        
        # submit job
        future_result = pool.apply_async(func=simulate_for_worker, args=(parameters,));
        results.append(future_result);
    
    # every worker will return the path to the output routes fc
    for result in results:
        (worker_routes_fc, repeated_fc) = result.get();
        arcpy.AddMessage("Worker output: " + str(worker_routes_fc));
        
        # we copy all the routes (features) from this output into the master output
        arcpy.AddMessage("Copying route features from worker to master.");
        if arcpy.Exists(output_routes_fc):
            arcpy.Append_management([worker_routes_fc], output_routes_fc);
        else:
            arcpy.CopyFeatures_management(worker_routes_fc, output_routes_fc);
            
        # iterate over every edge in the edges FC and update their repeated count
        arcpy.AddMessage("Updating the 'repeated' field of each attribute.");
        edge_frequency = {};
        # read the edge_frequency table for this worker
        with arcpy.da.SearchCursor(repeated_fc, ("FeatureID", "Repeated")) as cursor:
            for row in cursor:
                edge_frequency[row[0]] = row[1];
            del cursor;
        # update the repeated count for the edges
        edit = arcpy.da.Editor(fgdb_path);
        edit.startEditing(True, True);
        edit.startOperation();
        with arcpy.da.UpdateCursor(edges_fc_path, ("OBJECTID", "REPEATED")) as cursor:
            for row in cursor:
                obj_id = row[0];
                if obj_id in edge_frequency:
                    row[1] += edge_frequency[obj_id];
                    cursor.updateRow(row);
            del cursor;
        edit.stopOperation();
        edit.stopEditing(True); 
        
    # at this point every worker should have finished generating all the routes
    # and copied them into the master (output) routes feature class so we
    # terminate the pool and release all the processes
    pool.close();
    pool.terminate();
    
    # delete the worker folders
    for i in xrange(cores):
        worker_path = os.path.join(working_dir, "worker" + str(i));
        if os.path.exists(worker_path):
            shutil.rmtree(worker_path);
    
    
    arcpy.AddMessage("Output feature class '" + output_routes_fc + "' have the simulated routes! Simulation is complete!"); 
    arcpy.AddMessage("Done!");       
    return output_routes_fc;
        

#
# Main
#
def main():
    try:
        # read the source point
        source_pt = get_source_point(0);
        arcpy.AddMessage("Source point: " + str(source_pt));
        # read the destination point
        dest_pt = get_dest_point(1);
        arcpy.AddMessage("Destination point: " + str(dest_pt));
        # read the path to network dataset
        nd_path = get_network_dataset_path(2);
        arcpy.AddMessage("Network dataset: " + str(nd_path));
        # read the percentage of random noise to be added to the node value
        rand_percent = get_random_percent(3);
        arcpy.AddMessage("Randomness %: " + str(rand_percent));
        # read the number of iterations
        iterations = get_iterations(4);
        arcpy.AddMessage("Iterations: " + str(iterations));
        # read the number of cores
        cores = get_cpu_cores(5);
        arcpy.AddMessage("Cores: " + str(cores));
        # read path to working directory
        working_dir = get_working_dir(6);
        arcpy.AddMessage("Working directory: " + working_dir);
        # read path to vegas toolbox
        toolbox = get_vegas_toolbox(7);
        arcpy.AddMessage("Vegas toolbox: " + toolbox);
        # read the path to a feature class that contains all the routes
        output_routes_path = get_output_routes_fc_path(8);
        arcpy.AddMessage("Output routes feature class: " + output_routes_path);
        
        # simulate the paths
        output_routes_fc = simulate(source_pt, dest_pt, nd_path, rand_percent, iterations, cores, working_dir, toolbox, output_routes_path);
        
        # set the output parameter
        arcpy.SetParameterAsText(9, output_routes_fc);
    except Exception as e:
        arcpy.AddError(str(e));
        exc_type, exc_obj, exc_tb = sys.exc_info()
        arcpy.AddError(traceback.extract_tb(exc_tb));


#
# Call the main function
#   
if __name__ == '__main__':
    #Check out the Network Analyst extension license
    arcpy.CheckOutExtension("Network")
    main();
