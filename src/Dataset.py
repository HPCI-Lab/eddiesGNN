import numpy as np
import os
import torch
from torch_geometric.data import Data
from torch_geometric.data import Dataset
import xarray as xr

class PilotDataset(Dataset):

    # root: Where the dataset should be stored and divided into processed/ and raw/
    def __init__(self, root, mesh_path, transform=None, pre_transform=None, pre_filter=None):
        self.mesh_path = mesh_path
        super().__init__(root, transform, pre_transform, pre_filter)

    @property
    # If you directly return the names of the files, the '.' will be in /data/bsc/raw/
    # If you return os.listdir, the '.' will be where "Dataset.py" is
    def raw_file_names(self):
        return os.listdir(self.root + '/raw')

    @property
    # Return a list of graph files in the processed/ folder.
    # If these files:
    #   don't exist: process() will start and create them
    #   exist: process() will be skipped
    def processed_file_names(self):
        return os.listdir(self.root + '/processed')
    
    # Read the raw data and convert it into graph representations that are going to be saved into the processed/ folder.
    # This function is triggered as soon as the PilotDataset is instantiated
    def process(self):
        
        # Get the adjacency info(common for all our graphs)
        edge_index = self._get_adjacency_info()
        
        node_feats = None
        edge_index = None
        labels = None
        
        for raw_path in self.raw_paths:
            file_name = raw_path.split('/')[-1]
            year = file_name.split('_')[2]
            month = file_name.split('_')[3]
            day = file_name.split('_')[4].split('.')[0]
            
            #print(f'    Year {year}, Month {month}, Day {day}...')
            
            raw_data = xr.open_dataset(raw_path)

            # Get node features
            #node_feats = self._get_node_features(raw_data)
            
            # Get labels info
            #labels = self._get_labels(raw_data)

            # Create the Data object
            data = Data(
                #x=node_feats,                       # node features
                edge_index=edge_index,              # edge connectivity
                #y=labels,                           # labels for classification
            )

            #print(os.path.join(self.processed_dir, f'year_{year}_cyclone_{cyclone}.pt'))
            # TODO customize this to fit the type of eddy information we're going to store
            torch.save(data, os.path.join(self.processed_dir, f'year_{year}_month_{month}_day_{day}.pt'))

        print("    Shape of node feature matrix:", np.shape(node_feats))
        print("    Shape of graph connectivity in COO format:", np.shape(edge_index))
        print("    Shape of labels:", np.shape(labels))


    # Return a matrix with shape=[num_nodes, num_node_features]
    # Features here are the SSH information
    def _get_node_features(self, data):

        all_nodes_feats =[]

        # TODO for every node, append its SSH information to the above list

        all_nodes_feats = np.asarray(all_nodes_feats)
        return torch.tensor(all_nodes_feats, dtype=torch.float)

    # TODO it should be undirected, see utils.to_undirected() to make it undirected
    # Return the graph connetivity in COO format with shape=[2, num_edges]
    def _get_adjacency_info(self):        
        mesh = xr.open_dataset(self.mesh_path)
        return torch.tensor(mesh.edges.values.T, dtype=torch.long)

    # Download the raw data into raw/, or the folder specified in self.raw_dir
    def download(self):
        pass

    # Returns the number of examples in the dataset
    def len(self):
        return len(self.processed_file_names)
    
    # Implements the logic to load a single graph - TODO we'll have to redefine this
    def get(self, year, month, day):
        data = torch.load(os.path.join(self.processed_dir, f'year_{year}_month_{month}_day_{day}.pt'))
        return data
