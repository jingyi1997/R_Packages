
# -*-coding:utf-8-*-
"""
ayou
"""
 
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
 
 
#AyouBlog类
#get_page_url函数获得所有博客的URL
def build_dicts():
    url = 'https://cran.r-project.org/web/packages/available_packages_by_name.html'
    package_dict = {}

    responses = requests.get(url)
    bs = BeautifulSoup(responses.text, "html5lib")
    # find the list of all packages
    package_nodes = bs.find_all(href = re.compile("index.html"))
    # print(len(package_names)) 12757
    # build the dictionary
    package_num = 0
    for package_node in package_nodes:
        package_dict[package_node.string] = package_num
        package_num = package_num + 1
    # save the dict on the disk
    f = open('dict.txt','w')
    f.write(str(package_dict))
    f.close()
 
 
#ThreadUrl继承线程类
#run函数将QUEUE中的URL逐个取出,然后打开,取得博客详细页面的标题
class ThreadUrl(threading.Thread):
    def __init__(self, queue, in_nodes, out_nodes, package_dict, extra_dict):
        threading.Thread.__init__(self)
        self.queue = queue
        self.s = requests.session()
        self.in_nodes = in_nodes
        self.out_nodes = out_nodes
        self.package_dict = package_dict
        self.extra_dict = extra_dict

        
 
    def run(self):
        package_dict = self.package_dict
        in_nodes = self.in_nodes
        out_nodes = self.out_nodes
        extra_dict = self.extra_dict
        package_num = len(package_dict)
        requests.adapters.DEFAULT_RETRIES = 5  

        while not self.queue.empty():
            package_name = self.queue.get()
            curr_package_num = package_dict[package_name]
            host = 'https://cran.r-project.org/web/packages/' + package_name + '/index.html'
            print("Building the dependency of packages : %s" % (host))
            try:
                responses = self.s.get(host)
            except HTTPError as e:
                print(str(e))
                return str(e)
            except ConnectionError as e:
                print(str(e))
                return str(e)
            try:
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

                for imp_dep_pack in imp_dep_packs:
                    if package_dict.has_key(imp_dep_pack) is False and extra_dict.has_key(imp_dep_pack) is False:
                        print(imp_dep_pack, "does not exist")
                        extra_dict[imp_dep_pack] = package_num 
                        package_num = package_num + 1
                        
                        out_nodes.append(curr_package_num)
                        in_nodes.append(package_num)
                        
                    else:
                        out_nodes.append(curr_package_num)
                        if package_dict.has_key(imp_dep_pack):
                            in_nodes.append(package_dict[imp_dep_pack])
                        else:
                            in_nodes.append(extra_dict[imp_dep_pack])
                        

            except AttributeError as e:
                print(str(e))
                return str(e)
            except NavigableString as e:
                print(str(e))
                return str(e)
            self.queue.task_done()
 
 
def main():
    #创建队列
    queue = Queue.Queue()
 
    #将URL放进队列
    f = open('dict.txt','r')
    a = f.read()
    package_dict = eval(a)
    f.close()
    extra_dict = {}

    test_num = 0
    for package_name in package_dict.keys():
        
        #url = 'https://cran.r-project.org/web/packages/' + package_name + '/index.html'
        queue.put(package_name)
        

 
    #开多线程
    in_nodes = []
    out_nodes = []


    for i in range(10):
        t = ThreadUrl(queue, in_nodes, out_nodes, package_dict, extra_dict)
        t.setDaemon(True)
        t.start()
 
    #队列清空后再执行其它
    queue.join()

    
    print("The dependency of basic packages has been built!")
    print("saving out nodes!")
    np.savetxt("out_nodes.txt", out_nodes, delimiter = ",")
    print("Done!")
    print("saving in nodes!")
    np.savetxt("in_nodes.txt", in_nodes, delimiter = ",")
    print("Done!")
    print("saving extra dict!")
    f = open('extra_dict.txt','w')
    f.write(str(extra_dict))
    f.close()
    print("Done!")

    print("The num of out_nodes are %d" % (len(out_nodes)))
    print("The num of in_nodes are %d" % (len(in_nodes)))
    print(extra_dict.keys())
 
 
if __name__=="__main__":
    start = time.time()
    main()
    print("Elapsed Time: %s" % (time.time() - start))