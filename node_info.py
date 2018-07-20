
import numpy as np
from scipy.io import savemat, loadmat
import csv
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
