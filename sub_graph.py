# get information of nodes and save as 'nodes_info.csv'
import numpy as np
from scipy.io import savemat, loadmat
import csv
import networkx as nx 
out_nodes = np.loadtxt('out_nodes.txt', dtype = np.int32)
in_nodes = np.loadtxt('in_nodes.txt', dtype = np.int32)


#print(out_nodes.shape)
#print(in_nodes.shape)

f = open('dict.txt','r')
a = f.read()
package_dict = eval(a)
f.close()
f = open('extra_dict.txt','r')
a = f.read()
extra_dict = eval(a)
f.close()

f = open('closeness.txt','r')
a = f.read()
Closeness_Centrality = eval(a)
f.close()
f = open('betweenness.txt','r')
a = f.read()
Betweenness_Centrality = eval(a)
f.close()
f = open('in_degree.txt','r')
a = f.read()
in_degree = eval(a)
f.close()
f = open('out_degree.txt','r')
a = f.read()
out_degree = eval(a)
f.close()
G = nx.DiGraph()
G.add_nodes_from(package_dict.values())
G.add_nodes_from(extra_dict.values())

tuple_arr = []
for idx, in_node in enumerate(in_nodes):
	out_node = out_nodes[idx]
	
	tuple_arr.append((out_node, in_node))

G.add_edges_from(tuple_arr)
print('Computing Closeness_Centrality...')
Closeness_Centrality = nx.closeness_centrality(G)
f = open('closeness.txt','w')
f.write(str(Closeness_Centrality))
f.close()
print(len(Closeness_Centrality))
print('Computing Betweenness_Centrality...')
Betweenness_Centrality = nx.betweenness_centrality(G)
f = open('betweenness.txt','w')
f.write(str(Betweenness_Centrality))
f.close()
print(len(Betweenness_Centrality))
print('Computing in_degree...')
in_degree = G.in_degree()
f = open('in_degree.txt','w')
f.write(str(in_degree))
f.close()
print(len(in_degree))
print('Computing out_degree...')
out_degree = G.out_degree()
f = open('out_degree.txt','w')
f.write(str(out_degree))
f.close()
print(len(out_degree))

write to 'nodes_info.csv'

with open('nodes_info.csv', 'wb') as f:
    writer = csv.writer(f)
    writer.writerow(['Node', 'Label', 'in_degree', 'out_degree', 'clossness', 'betweenness'])
    for package_name, package_num in package_dict.items():
        writer.writerow([package_num, package_name, in_degree[package_num][1], \
        	out_degree[package_num][1], Closeness_Centrality[package_num], Betweenness_Centrality[package_num]])
    for package_name, package_num in extra_dict.items():
        writer.writerow([package_num, package_name, in_degree[package_num][1], \
        	out_degree[package_num][1], Closeness_Centrality[package_num], Betweenness_Centrality[package_num]])
        	
        	
import pandas as pd 
nodes_info = pd.read_csv('nodes_info.csv')
print(nodes_info.columns)
part_nodes_info = nodes_info[(nodes_info['in_degree'] > 0) | (nodes_info['out_degree'] > 0)]
print(part_nodes_info.columns)
part_nodes_info.to_csv('part_nodes_info.csv', index = False)
part_nodes_id = np.array(part_nodes_info['Id'])
out_nodes = out_nodes.reshape(out_nodes.shape[0], 1)
in_nodes = in_nodes.reshape(in_nodes.shape[0], 1)

links = np.concatenate((out_nodes, in_nodes), axis = 1)
print(links.shape[0])
link_num = 0
for i in range(links.shape[0]):
	if links[i][0] in part_nodes_id and links[i][1] in part_nodes_id:
		link_num = link_num +1
print(link_num)


