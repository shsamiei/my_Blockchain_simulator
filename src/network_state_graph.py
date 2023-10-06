import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import random

def show_network(data,labels):
    pass

def csv_loader():
    data = pd.read_csv("config/network_model.csv")
    data.set_index('node',inplace=True)
    nodes=data.columns.tolist()
    nodeID=[int(i) for i in nodes]
    network_df = pd.DataFrame(data.values,columns=nodeID,index=nodeID)
    print(network_df)
    graph = nx.from_numpy_matrix(network_df.values)
    return network_df,nodeID


def network_creator(nodeID,max_latency):

    dimension= len(nodeID)
    np.random.seed(7)
    x=np.random.randint(2, size=(dimension, dimension))
    np.fill_diagonal(x,0)
    graph = nx.from_numpy_matrix(x)
    for (u, v) in graph.edges():
        np.random.seed(7)
        graph[u][v]['weight'] = random.randint(1,max_latency) 
    network_df= pd.DataFrame(nx.to_numpy_array(graph),columns=nodeID,index=nodeID)
    print("Printing network")
    return network_df