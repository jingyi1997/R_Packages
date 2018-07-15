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
    def __init__(self, queue, in_nodes, out_nodes, package_dict, extra_dict):
        threading.Thread.__init__(self)
        self.queue = queue
        self.s = requests.session()
        self.in_nodes = in_nodes
        self.out_nodes = out_nodes
        self.package_dict = package_dict
        self.extra_dict = extra_dict
        print("initializing...")
        
 
    def run(self):
        
        package_dict = self.package_dict
        extra_dict = self.extra_dict
        in_nodes = self.in_nodes
        out_nodes = self.out_nodes
       
        
        requests.adapters.DEFAULT_RETRIES = 5  
    
        while not self.queue.empty():
            package_name = self.queue.get()
            curr_package_num = extra_dict[package_name]
            host = 'https://stat.ethz.ch/R-manual/R-devel/library/' + package_name +'/DESCRIPTION'
            
           
            responses = self.s.get(host)
            if (responses.status_code == 200):	
                print("%s has been searched" % (package_name))
            else:
                
                host = 'https://bioconductor.org/packages/release/bioc/html/' + package_name + '.html'
                responses = self.s.get(host)
            	
            		
            	if (responses.status_code > 200):
            		host = 'https://bioconductor.org/packages/release/data/experiment/html/' + package_name + '.html'
	                responses = self.s.get(host)
	            	if (responses.status_code > 200):
	            		host = 'https://bioconductor.org/packages/release/data/annotation/html/' + package_name + '.html'
	            		responses = self.s.get(host)
		            	if (responses.status_code > 200):
		            		print("Info of package %s can not be found" %(package_name))
	        if (package_name is not "R"):
	        	print("building dependency")
	        	bs = BeautifulSoup(responses.text, "html5lib")
	        	pre_imports = bs.find(string = "Imports")
                pre_depends = bs.find(string = "Depends")
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
                print(imp_dep_packs)
                # for imp_dep_pack in imp_dep_packs:
                #     if package_dict.has_key(imp_dep_pack) is False and extra_dict.has_key(imp_dep_pack) is False:
                #         print(imp_dep_pack, "does not exist")
                                       
                #     else:
                #         print(imp_dep_pack)

                

                
                
            
            self.queue.task_done()
def main():
    queue = Queue.Queue()
    #创建队列

 
    #将URL放进队列
    f = open('dict.txt','r')
    a = f.read()
    package_dict = eval(a)
    f.close()
    f = open('extra_dict.txt','r')
    a = f.read()
    extra_dict = eval(a)
    f.close()
    
    in_nodes = []
    out_nodes = []

    
    for package_name in extra_dict.keys():
        
        #url = 'https://cran.r-project.org/web/packages/' + package_name + '/index.html'
        #print("The num of package %s is %d" %(package_name, package_num))
        queue.put(package_name)
    print("starting threads...")
    for i in range(10):
        t = ThreadUrl(queue, in_nodes, out_nodes, package_dict, extra_dict)
        print("initialized")
        t.setDaemon(True)
        t.start()
 
    #队列清空后再执行其它
    queue.join()


if __name__=="__main__":
    start = time.time()
    main()
    print("Elapsed Time: %s" % (time.time() - start))        

 
    
