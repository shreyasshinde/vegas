'''
Created on Mar 3, 2013

@author: shreyas shinde, msgis, university of redlands
'''
import arcpy;
import datetime;
import sys;
import os;
import traceback;
import random;



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
# Reads the path to the nodes feature class.
# @param paramIndex: the index of the parameter argument if this was a GUI based application
# @return: the path to the nodes feature class
def get_nodes_fc(paramIndex=0):
    if isConsoleTool():
        nodes_fc = raw_input("Enter the path to the nodes feature class: ");
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
        edges_fc = raw_input("Enter the path to the edges feature class: ");
    else:
        edges_fc = arcpy.GetParameterAsText(paramIndex);
    if edges_fc == "":
        raise Exception("Input argument path to edges feature class cannot be empty.");
    else:
        return edges_fc;
    
#
# Reads the path to the workspace
# @param paramIndex: the index of the parameter argument if this was a GUI based application
# @return: the path to the edges feature class
def get_workspace(paramIndex=0):
    if isConsoleTool():
        workspace = raw_input("Enter the path to the workspace/database: ");
    else:
        workspace = arcpy.GetParameterAsText(paramIndex);
    if workspace == "":
        raise Exception("Input argument path to workspace/database cannot be empty.");
    else:
        return workspace;
        

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
# Applies a random energy to every point in the nodes feature class
# and carries it over the edges feature class.
# @param percent:  the +- percentage of random energy to apply
# @param nodes_fc: the path to the nodes feature class
# @param edges_fc: the path to the edges feature class  
def randomize(percent, nodes_fc, edges_fc, workspace):
    #
    # Algorithm:
    #    1. Open the nodes_fc and read all the node IDs and their values in memory
    #    2. Randomize the values for every node based on +- percent of their original values
    #    3. Update the nodes_fc with new values for every node
    #    4. Iterate over every edge in the edges_fc and update the to and from cost based on the in memory
    #       map of values
    
    # our in-memory cache of node values
    node_values = {};
    
    # need to start an edit session when the feature classes are in a feature dataset
    edit = arcpy.da.Editor(workspace);

    # read all the values in memory    
    fields = ["ROW_ID", "VALUE"]
    arcpy.AddMessage("Reading node values in memory.")
    with arcpy.da.SearchCursor(nodes_fc, fields) as cursor:
        for node in cursor:
            node_values[node[0]] = node[1];
    del cursor;
    
    #print node_values;
    
    # randomize the values within the range
    arcpy.AddMessage("Applying randomization within " + str(percent) + "% range of original value.");
    for key,value in node_values.iteritems():
        if value == 0:
            continue;
        lower = float((100 - percent))/100*float(value);
        upper = float((100 + percent))/100*float(value);
        newvalue = random.randint(int(lower), int(upper)); #this function only works for integer - loss of precision
        node_values[key] = newvalue;
        
    #print node_values;
    
    # update the rows in the nodes_fc
    arcpy.AddMessage("Updating the values of nodes.");
    edit.startEditing(True, True);
    edit.startOperation();
    with arcpy.da.UpdateCursor(nodes_fc, fields) as node_cursor:
        for node in node_cursor:
            node[1] = node_values[node[0]];
            node_cursor.updateRow(node);
    edit.stopOperation();
    del node_cursor;
    
    # iterate over every edge and then update each edge
    fields = ["SRC_ID", "DES_ID", "COST"];
    arcpy.AddMessage("Updating the To-From costs of each edge.");
    edit.startOperation();
    with arcpy.da.UpdateCursor(edges_fc, fields) as edge_cursor:
        for edge in edge_cursor:
            src_id = edge[0];
            des_id = edge[1];
            src_val = node_values[src_id];
            des_val = node_values[des_id]
            edge[2] = abs(des_val - src_val);
            edge_cursor.updateRow(edge);
    edit.stopOperation();
    edit.stopEditing(True);        
    del edge_cursor;  


#
# Main
#
def main():
    try:
        # gets the amount of random energy that needs to be applied
        percent = get_random_percent(0);
        arcpy.AddMessage("Percent = " + str(percent));
        
        # get the path to nodes fc
        nodes_fc = get_nodes_fc(1);
        arcpy.AddMessage("Nodes feature class = " + nodes_fc);
        
        # get the path to edges fc
        edges_fc = get_edges_fc(2);
        arcpy.AddMessage("Edges feature class = " + edges_fc);
        
        # get the workspace
        workspace = get_workspace(3);
        arcpy.AddMessage("Workspace: " + workspace);
        
        # apply random energy
        randomize(percent, nodes_fc, edges_fc, workspace);
        
        
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