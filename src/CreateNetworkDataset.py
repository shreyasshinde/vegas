'''
Created on Mar 3, 2013

@author: shreyas shinde, msgis, university of redlands
'''

import arcpy;
import datetime;
import sys;
import os;
import traceback;




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


def mainConsole():
    return;

def create_network_dataset(nodes_fc, edges_fc, template_dataset, fgdb_path):
    # Copy the template dataset into the working directory
    arcpy.AddMessage("Copying template network dataset into the destination geodatabase.");
    dir, fds_name = os.path.split(template_dataset); 
    arcpy.Copy_management(template_dataset, fgdb_path + "\\" + fds_name);
    
    # Copy the input nodes and edges features into the destination dataset
    arcpy.AddMessage("Copying nodes and edges features.")
    arcpy.env.overwriteOutput = True;
    dest_nodes_fc = fgdb_path + "\\" + fds_name + "\\nodes";
    arcpy.AddMessage("Destination nodes feature class: " + dest_nodes_fc);
    arcpy.Append_management([nodes_fc], dest_nodes_fc);
    dest_edges_fc = fgdb_path + "\\" + fds_name + "\\edges";
    arcpy.AddMessage("Destination edges feature class: " + dest_edges_fc);
    arcpy.Append_management([edges_fc], dest_edges_fc);
    
    # Rebuild the network dataset
    arcpy.AddMessage("Building network.")
    arcpy.CheckOutExtension("Network");
    nw_dataset = fgdb_path + "\\" + fds_name + "\\" + fds_name + "_ND";
    arcpy.na.BuildNetwork(nw_dataset);
    
    # return the network dataset path
    return nw_dataset;


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
# Reads the path to the template dataset that contains the network dataset
# @param paramIndex: the index of the parameter argument if this was a GUI based application
# @return: the path to the network template dataset
def get_template_dataset(paramIndex=0):
    if isConsoleTool():
        fds_path = raw_input("Enter the path to the dataset that contains the template network dataset: ");
    else:
        fds_path = arcpy.GetParameterAsText(paramIndex);
    if fds_path == "":
        raise Exception("Input argument path to dataset cannot be empty.");
    else:
        return fds_path;
    

#
# Reads the path to the destination fgdb where the network dataset will be created
# @param paramIndex: the index of the parameter argument if this was a GUI based application
# @return: the path to the destination fgdb
def get_fgdb_path(paramIndex=0):
    if isConsoleTool():
        fgdb_path = raw_input("Enter the path to file geodatabase where the network dataset will be created: ");
    else:
        fgdb_path = arcpy.GetParameterAsText(paramIndex);
    if fgdb_path == "":
        raise Exception("Input argument path to database cannot be empty.");
    else:
        return fgdb_path;

#
# Switches between tool and console mode
#
def main():
    try:
        # nodes fc
        nodes_fc =  get_nodes_fc(0);
        arcpy.AddMessage("Nodes: " + nodes_fc);
        
        # edges fc
        edges_fc = get_edges_fc(1);
        arcpy.AddMessage("Edges: " + edges_fc);
        
        # path to template fds that contains the network dataset
        template_dataset = get_template_dataset(2);
        arcpy.AddMessage("Template dataset: " + template_dataset);
        
        # path to destination fgdb where the network dataset will be created
        fgdb_path = get_fgdb_path(3);     
        arcpy.AddMessage("Destination fgdb path: " + fgdb_path);  
        
        # create the network dataset
        nw_dataset_path = create_network_dataset(nodes_fc, edges_fc, template_dataset, fgdb_path);
        
        # set the output parameters
        arcpy.SetParameterAsText(4, nw_dataset_path);
        arcpy.AddMessage("Network built! " + nw_dataset_path);
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
# Call the main function
#   
if __name__ == '__main__':
    #Check out the Network Analyst extension license
    arcpy.CheckOutExtension("Network")
    main();

