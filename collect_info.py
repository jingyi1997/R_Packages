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
    def __init__(self, queue, package_dict):
        threading.Thread.__init__(self)
        self.queue = queue
        self.s = requests.session()
        
        self.package_dict = package_dict
       
        
 
    def run(self):
        package_dict = self.package_dict
        
       
        package_num = len(package_dict)
        requests.adapters.DEFAULT_RETRIES = 5  

        while not self.queue.empty():
            package_name = self.queue.get()
            
            host = 'https://cran.r-project.org/web/packages/' + package_name + '/index.html'
            print("Collecting the information of packages : %s" % (host))
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
                # find the published date of the package
                pre_published = bs.find(string = "Published:")
                
                if pre_published:
                    publish_date = pre_published.find_next("td").text
                    print("The published date of package %s is %s" % (package_name, publish_date))
                    publish_dict[package_name] = publish_date

                title_node = bs.find("h2")

                if title_node:
                    whole_title = title_node.string
                    colon_idx = whole_title.find(":")
                    title = whole_title[colon_idx + 2:]
                    print("The title of package %s is %s" % (package_name, title))
                    title_dict[package_name] = title

                desp_node = bs.find("p")

                if desp_node:
                    desp = desp_node.text
                    if desp:
                        desp = desp.replace('\n', '')

                        print("The description of package %s is %s" % (package_name, desp))
                        desp_dict[package_name] = desp
                    

                authors_node = bs.find(string = "Author:")

                if authors_node:
                    all_authors = authors_node.find_next("td").text
                    all_authors = re.sub(u"\\[.*?\\]", "", all_authors)
                    author_num = len(all_authors.split(","))
                    print("The authors' number of package %s is %d" % (package_name, author_num))
                    author_num_dict[package_name] = author_num


                maintainer_node = bs.find(string = "Maintainer:")

                if maintainer_node:
                    maintainer = maintainer_node.find_next("td").text
                    maintainer = re.sub(u"\\<.*?\\>", "", maintainer)
                    
                    print("The maintainer of package %s is %s" % (package_name, maintainer))
                    maintainer_dict[package_name] = maintainer

            

                
                        

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
    

    test_num = 0
    for package_name in package_dict.keys():
        
        #url = 'https://cran.r-project.org/web/packages/' + package_name + '/index.html'
        queue.put(package_name)
        
        

 
    #开多线程
    


    for i in range(10):
        t = ThreadUrl(queue, package_dict)
        t.setDaemon(True)
        t.start()
 
    #队列清空后再执行其它
    queue.join()

    print(len(publish_dict))
    print(len(title_dict))
    print(len(desp_dict))
    print(len(author_num_dict))
    print(len(maintainer_dict))
    

    f = open('publish_dict.txt','w')
    f.write(str(publish_dict))
    f.close()
    f = open('title_dict.txt','w')
    f.write(str(title_dict))
    f.close()
    f = open('desp_dict.txt','w')
    f.write(str(desp_dict))
    f.close()
    f = open('author_num.txt','w')
    f.write(str(author_num_dict))
    f.close()
    f = open('maintainer.txt','w')
    f.write(str(maintainer_dict))
    f.close()
    
    

    
 
 
if __name__=="__main__":
    start = time.time()
    publish_dict = {}
    title_dict = {}
    desp_dict = {}
    author_num_dict = {}
    maintainer_dict = {}
    old_version_num = {}
    main()
    print("Elapsed Time: %s" % (time.time() - start))