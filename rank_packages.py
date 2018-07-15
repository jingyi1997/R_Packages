import numpy as np
from scipy.io import savemat, loadmat
out_nodes = np.loadtxt('out_nodes.txt', dtype = np.int32)
in_nodes = np.loadtxt('in_nodes.txt', dtype = np.int32)
extra_out_nodes = np.loadtxt('extra_out_nodes.txt', dtype = np.int32)
extra_in_nodes = np.loadtxt('extra_in_nodes.txt', dtype = np.int32)

out_nodes = np.concatenate((out_nodes, extra_out_nodes))
in_nodes = np.concatenate((in_nodes, extra_in_nodes))

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

total_pack_num = len(package_dict) + len(extra_dict)
print(total_pack_num)
print(np.max(in_nodes))
print(np.max(out_nodes))

pack_matrix = np.zeros((total_pack_num, total_pack_num), dtype = np.int32)
pack_matrix[in_nodes, out_nodes] = 1

def PageRank(G, beta, page_num): 
    # build M
    out_node_num = np.sum(G, axis = 0, dtype = np.float32)
    print(out_node_num.shape)
    M = np.tile(out_node_num, (page_num, 1))
    M[M == 0] = -1
    M = 1 / M
    M[G == 0] = 0
    # initialize vector r
    r_old = np.full((page_num), 1 / float(page_num))
    while True:
        r_new = M.dot(r_old) * beta
        S = np.sum(r_new)
        r_new = r_new + np.full((page_num), (1 - S) / float(page_num))
        error = np.sum(np.abs(r_old - r_new))
        print(error)
      
        if error < 0.0000001:
        	savemat('pageRank.mat', {'pageRank': r_new})
        	break
        r_old = r_new

#PageRank(pack_matrix, 0.85, total_pack_num)

r_new = loadmat('pageRank.mat')['pageRank']
r_new = np.squeeze(r_new)
rank_package = np.argsort(-r_new)

rank_score = r_new[rank_package]

for pop_package in rank_package[:20]:
	if pop_package in package_dict.values():
		print(list(package_dict.keys())[list(package_dict.values()).index(pop_package)])
	else:
		print(list(extra_dict.keys())[list(extra_dict.values()).index(pop_package)])