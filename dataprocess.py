#coding=utf8

'''
@author: Chenxu Wang
'''
import json
import datetime
import os

import numpy as np
from matplotlib import pyplot as plt

'''
group the browsing records of a certain user to a specific server
'''
def usergroup(datapath):
    sites = {} # used to store all the browsing records to a web server sites, specified by 'site_id'
    sites_objects = {} # used to store the indices of objects
    sites_obj_index = {}
    filelist = os.listdir(datapath)
    for filename in filelist: 
        print filename  
        jsonfile = open(datapath + filename, 'r')
        for line in jsonfile:
            s = json.loads(line)
            site_id = s['site_id']
            if site_id not in sites_obj_index:
                sites_objects[site_id] = {}
                sites_obj_index[site_id] = 1
            if s['request'] not in sites_objects[site_id]:
                sites_objects[site_id][s['request']] = sites_obj_index[site_id]
                sites_obj_index[site_id] = sites_obj_index[site_id] + 1
            if site_id not in sites: # the current site_id is not in the sites
                users = {} # used to store all the browsing records of a user
                users[s['remote_addr']] = [(sites_objects[site_id][s['request']], datetime.datetime.strptime(s['time_local'], '%d/%b/%Y:%H:%M:%S +0000'))] # the records contain "request" and "time_local"
                sites[site_id] = users 
            else:            
                users = sites[site_id]
                if s['remote_addr'] not in users: # new user
                    users[s['remote_addr']] = [(sites_objects[site_id][s['request']], datetime.datetime.strptime(s['time_local'], '%d/%b/%Y:%H:%M:%S +0000'))]
                else: # old user
                    t = datetime.datetime.strptime(s['time_local'], '%d/%b/%Y:%H:%M:%S +0000') 
                    users[s['remote_addr']].append((sites_objects[site_id][s['request']], t))
    print 'There are total', len(sites), 'sites'
    for site_id in sites.keys():
        sitesf = open('./dataset/' + site_id, 'w')
        sitesf.write('Total ' + str(len(sites_objects[site_id])) + ' objects\n')
        users = sites[site_id]
        for user in users.keys():
            sitesf.write(user + "," + str(len(users[user])) + '\n')
            obj_str = str(users[user][0][0])
            time_str = str(users[user][0][1])   
            obvs = users[user]         
            for i in range(1, len(obvs)):
                obj_str = obj_str + ',' + str(obvs[i][0])
                time_str = time_str + ',' + str((obvs[i][1]-obvs[i-1][1]).seconds)
            sitesf.write(obj_str + '\n')
            sitesf.write(time_str + '\n')
        sitesf.close()

#===============================================================================
# This function is used to get the arrival rates for each web server
#===============================================================================
def get_arrival_rates(datapath):
    sites_arr_rates = {}
    filelist = os.listdir(datapath)
    start_time = datetime.datetime.strptime('29/Dec/2015:00:00:00 +0000', '%d/%b/%Y:%H:%M:%S +0000')
    for filename in filelist: 
        print filename  
        jsonfile = open(datapath + filename, 'r')
        for line in jsonfile:
            s = json.loads(line)
            site_id = s['site_id']
            if site_id not in sites_arr_rates:
                sites_arr_rates[site_id] = [0 for i in range(24*3600)] # there are total 24*3600 seconds in a single day
                access_time = datetime.datetime.strptime(s['time_local'], '%d/%b/%Y:%H:%M:%S +0000')
                sites_arr_rates[site_id][(access_time-start_time).seconds] += 1
            else:
                access_time = datetime.datetime.strptime(s['time_local'], '%d/%b/%Y:%H:%M:%S +0000')
                sites_arr_rates[site_id][(access_time-start_time).seconds] += 1
    return sites_arr_rates

def plot_arrival_rate(arr_rate, site_id):
    t = np.array(arr_rate[0:8246])
    plt.plot(range(len(t)), t)
    plt.xlabel('time (sec)')
    plt.ylabel('arrival rate (req/s)')
    plt.grid(True)
    plt.savefig('./figs/ArrivalRates/'+site_id+'.png')
    plt.close()
        
if __name__ == '__main__':
#     rates = get_arrival_rates("E:/datasets/normaldata1/")
#     print len(rates)
#     for site_id in rates.keys():
#         plot_arrival_rate(rates[site_id], site_id)
    usergroup("E:/datasets/normaldata1/")
    print 'succeed!'