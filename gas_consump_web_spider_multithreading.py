# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 12:23:30 2019

@author: zoed0
"""
from bs4 import BeautifulSoup  
import pandas as pd
import requests
import re
import math
import threading
from queue import Queue

# Get all htmls of models, ex: BMW X4
def chexi():
    url = 'http://www.xiaoxiongyouhao.com/chxi_report_list.php'
    r = requests.get(url)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text)
    chexi_html = soup.find_all('a',attrs = {'href':re.compile("chexiyh")})
    chexi_list = ['http://www.xiaoxiongyouhao.com' + str(x['href']) for x in chexi_html]
    return chexi_list

# for a single html of model, return all its visions' htmls, ex: BMW X4, 2013, 1.6T, sport edition
def chexi_to_chexing(url):
    r = requests.get(url)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text)
    c2c_html = soup.find_all('a',attrs = {'href':re.compile("modelyh")})
    c2c_list = ['http://www.xiaoxiongyouhao.com' + str(x['href']) for x in c2c_html]
    return c2c_list

url = 'https://www.xiaoxiongyouhao.com/modelyh/30712.html'
# for a single vision, return all info: [chexing,min_gas,max_gas,mean_gas]
def info_single(url):
    r = requests.get(url)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text)
    a = soup.find_all('div',attrs = {'class': 'row'})
    for aa in a:
        if aa.find('div',attrs = {'class': "one_box"}):
            print(aa.find('div',attrs = {'class': "one_box"}))
            
    # extract max and min
    a = soup.find_all('div',attrs = {'class': 'col-xs-5'})  
    max_gas = float(a[-1].find('h4').text)
    min_gas = float(a[-2].find('h4').text)
    
    # extract mean gas consumption
    mean_gas = soup.find('h3', attrs= {'class':"h_val", 'style':"float:left;margin-right:10px;"}).text
    mean_gas = float(mean_gas)
    
    #extract official gas consump
    offi_gas = soup.find_all('h4', attrs= {'class':"h_val"})
    official_gas = offi_gas[-2].text.split()[0]
    official_gas = float(official_gas)
    
    # extract car model name
    chexing = soup.find('div',attrs = {'class': 'chexing_name'}).text    
    return [chexing,min_gas,max_gas,mean_gas,official_gas]

def thread_job(l,q):
    chexing_list = []
    for chexi in l:
        chexi_single = chexi_to_chexing(chexi)
        chexing_list.extend(chexi_single)
    q.put(chexing_list)    
        
def multithreading():
    q = Queue()
    length = len(chexi_list)
    n = math.floor(length/5)
    data = [chexi_list[i:i + n] for i in range(0, len(chexi_list), n)]
    threads = []
    for i in range(5):
        t = threading.Thread(target=thread_job,args=(data[i],q))
        t.start()
        threads.append(t)
    for thread in threads:
        thread.join()
    results = []
    for _ in range(5):
        results.append(q.get())
    return(results)
    
multithreading()
#threading.current_thread()
    
#    cx_info = []
#    for cx in chexing_list:
#        cx_single = info_single(cx)
#        cx_info.append(cx_single)
        
# read through all pages
chexi_list = chexi() 

    
cx_df = pd.DataFrame(cx_info,columns=["chexing","min_gas","max_gas","mean_gas","official_gas"])    
cx_df.to_csv('gas_consump_by_model.csv', encoding = "gb18030")   
  
    