import numpy as np
from scipy.io import savemat, loadmat
import csv
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

out_nodes = out_nodes.reshape(out_nodes.shape[0], 1)
in_nodes = in_nodes.reshape(in_nodes.shape[0], 1)

links = np.concatenate((out_nodes, in_nodes), axis = 1)
print(links.shape)
raw_input('press enter to continue...')

with open('links.csv', 'wb') as f:
    writer = csv.writer(f)
    writer.writerow(['Source', 'Target'])
    writer.writerows(links)


with open('nodes.csv', 'wb') as f:
    writer = csv.writer(f)
    writer.writerow(['Node', 'Name'])
    for package_name, package_num in package_dict.items():
        writer.writerow([package_num, package_name])
    for package_name, package_num in extra_dict.items():
        writer.writerow([package_num, package_name])