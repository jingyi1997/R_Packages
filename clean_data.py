# -*-coding:utf-8-*-
import requests
from requests.exceptions import HTTPError, ConnectionError
from bs4 import BeautifulSoup,NavigableString
import Queue
import threading
import time
import urllib, urllib2

import json
import numpy as np
from scipy.io import savemat, loadmat

import re
import csv
 



class ThreadUrl(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

        
           
        
 
    def run(self):
        
        while not self.queue.empty():
            requests.adapters.DEFAULT_RETRIES = 5  
            out_num = self.queue.get()
            
            if out_num in package_dict.values():
                package_name = list(package_dict.keys())[list(package_dict.values()).index(out_num)]
            else:
                package_name = list(extra_dict.keys())[list(extra_dict.values()).index(out_num)]
            print(package_name)
            if package_name in package_dict.keys():
                host = 'https://cran.r-project.org/web/packages/' + package_name + '/index.html'
                print("Building the dependency of packages : %s" % (host))
          
                responses = requests.session().get(host)
            
            
                bs = BeautifulSoup(responses.text, "html5lib")
                # find what the package depends on
                pre_imports = bs.find(string = "Imports:")
                pre_depends = bs.find(string = "Depends:")
                imp_dep_packs = []
                if pre_imports:
                    imports = pre_imports.find_next("td").text
                    imports = imports.replace(' ','')
                    imports = imports.replace('\n','')                
                    imports = re.sub(u"\\(.*?\\)", "", imports)
                    imports = imports.split(",")
                               
                else:
                    imports = []
                if pre_depends:
                    depends = pre_depends.find_next("td").text
                    depends = depends.replace(' ','')
                    depends = depends.replace('\n','')               
                    depends = re.sub(u"\\(.*?\\)", "", depends)
                    depends = depends.split(",")
                    
                else:
                    depends = []
                
                imp_dep_packs = imports + depends
                if "datasets" in imp_dep_packs:
                    print("Package %s is wrong" %(package_name))
                    wrong_pack.append(out_num)
                    wrong_pack_name.append(package_name)
            if package_name in extra_dict.keys():
                
                
                host = 'https://stat.ethz.ch/R-manual/R-devel/library/' + package_name +'/DESCRIPTION'     
                print("Building the dependency of packages : %s" % (host))                  
                responses = requests.session().get(host)
                imp_dep_packs = []
                if (responses.status_code == 200):    
                    #print("%s has been searched" % (package_name))
                    package_info = responses.text
                    import_idx = package_info.find("Imports")
                    if import_idx > -1:
                        import_end_idx = package_info.find('\n', import_idx)
               
                        imp = package_info[import_idx + 9:import_end_idx]
                        print(imp)
                    else:
                        imp = ''
                    depend_idx = package_info.find("Depends")
                    if depend_idx > -1:
                        depend_end_idx = package_info.find('\n', depend_idx)
               
                        dep = package_info[depend_idx + 9:depend_end_idx]
                        print(dep)
                    else:
                        dep = ''

                    imp_dep = imp + dep
                    imp_dep = imp_dep.replace(' ','')
                    imp_dep_packs = imp_dep.split(",")
                else:
                    host = 'https://bioconductor.org/packages/release/bioc/html/' + package_name + '.html'
                    responses = requests.session().get(host)
                        
                            
                    if (responses.status_code > 200):
                        host = 'https://bioconductor.org/packages/release/data/experiment/html/' + package_name + '.html'
                        responses = requests.session().get(host)
                        if (responses.status_code > 200):
                            host = 'https://bioconductor.org/packages/release/data/annotation/html/' + package_name + '.html'
                            responses = requests.session().get(host)
                            if (responses.status_code > 200):
                                print("Info of package %s can not be found" %(package_name))
                        else:
                            print("Building the dependency of packages : %s" % (host))   
                    else:
                        print("Building the dependency of packages : %s" % (host))   
	                if (package_name is not "R"):
	                    #print("building dependency")
	                    bs = BeautifulSoup(responses.text, "html5lib")
	                    pre_imports = bs.find(string = "Imports")
	                    pre_depends = bs.find(string = "Depends")
	                    
	                    if pre_imports:
	                        imports = pre_imports.find_next("td").text
	                        imports = imports.replace(' ','')
	                        imports = imports.replace('\n','')                
	                        imports = re.sub(u"\\(.*?\\)", "", imports)
	                        #imports = imports.split(",")
	                                       
	                    else:
	                        #imports = []
	                        imports = ''
	                    if pre_depends:
	                        depends = pre_depends.find_next("td").text
	                        depends = depends.replace(' ','')
	                        depends = depends.replace('\n','')               
	                        depends = re.sub(u"\\(.*?\\)", "", depends)
	                        #depends = depends.split(",")
	                            
	                    else:
	                        #depends = []
	                        depends = ''
	                        
	                    imp_dep_packs = imports + depends
	                    imp_dep_packs = imp_dep_packs.split(",")
	            print(imp_dep_packs)
                if "datasets" in imp_dep_packs:
                    print("Package %s is wrong" %(package_name))
                    wrong_pack.append(out_num)
                    wrong_pack_name.append(package_name)
            self.queue.task_done()            


def main():
    dup_in = np.where(in_nodes == 12783)[0]
    out_num = out_nodes[dup_in]
    out_num = np.unique(out_num)
    queue = Queue.Queue()
    for one_out_num in out_num:        
        queue.put(one_out_num)

    for i in range(10):
        t = ThreadUrl(queue)
        t.setDaemon(True)
        t.start()
     
        #队列清空后再执行其它
    queue.join()
    print("Done!")

if __name__=="__main__":
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

    
    extra_dict['datasets'] = 12782
    
    
    #print(dataset_num)
    
    #wrong_pack = []
    #wrong_pack_name = []
    #main()
    #print(wrong_pack)
    #print(wrong_pack_name)
    #np.savetxt("wrong_pack.txt", wrong_pack)
    wrong_pack = np.loadtxt("wrong_pack.txt")
    wrong_in_node = set(np.where(in_nodes == 12783)[0])
    for wrong_pack_num in wrong_pack:
    	wrong_pack_idx = set(np.where(out_nodes == wrong_pack_num)[0])
    	intersect = list(wrong_in_node.intersection(wrong_pack_idx))[0]
    	print("%d points to %d" %(out_nodes[intersect], in_nodes[intersect]))
    	in_nodes[intersect] = 12782

    print(len(np.unique(extra_dict.values())))
    print(len(extra_dict))

    to_grid = out_nodes[np.where(in_nodes == 12783)[0]]
    print(len(np.unique(to_grid)))
    print(len(to_grid))

    to_datasets = out_nodes[np.where(in_nodes == 12782)[0]]
    print(len(np.unique(to_datasets)))
    print(len(to_datasets))


    raw_input('press enter to continue...')
    np.savetxt("out_nodes.txt", out_nodes)
    np.savetxt("in_nodes.txt", in_nodes)
    f = open('extra_dict.txt','w')
    f.write(str(extra_dict))
    f.close()
