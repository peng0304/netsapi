from netsapi.location import *
from netsapi.environment import *

import os
from sys import exit, exc_info, argv
from multiprocessing import Pool, current_process
import numpy as np

resolution, timeout, realworkercount = "test", 0, 100
baseuri = "https://nlmodelflask.eu-gb.mybluemix.net"
locationId = "abcd123"
userId = "IndabaXKenyaUser"

def individual_get_score(action):
    name_s=current_process().name
    if  "-" in name_s:
        id = np.mod(int(name_s.split("-")[1]),realworkercount)
    else:
        id = -1

    try:
        envId = initEnv(locationId, userId, resolution, baseuri)
        reward = postAction(envId, action%1, baseuri, False, timeout)
#         print(id, action%1, reward)

    except:
        print(exc_info(),action)
        reward = None;
    
    return -reward

def postActionWrapper(action):
    name_s=current_process().name
    if  "-" in name_s:
        id = np.mod(int(name_s.split("-")[1]),realworkercount)
    else:
            id = -1
    try:
        envId = initEnv(locationId, userId, resolution, baseuri);
        posted = postAction(envId, action, baseuri, True, timeout)

    except:
        print(exc_info(),action)
    
    return envId if posted else None

def getStatusWrapper(envId):
    name_s=current_process().name
    if  "-" in name_s:
        id = np.mod(int(name_s.split("-")[1]),realworkercount)
    else:
        id = -1
    try:
        status = getStatus(envId[0], baseuri)

    except:
        print(exc_info(),envId)
        status = None;
    
    return status

def getRewardWrapper(envId):
    name_s=current_process().name
    if  "-" in name_s:
        id = np.mod(int(name_s.split("-")[1]),realworkercount)
    else:
        id = -1
    try:
        status = getReward(envId[0], baseuri)

    except:
        print(exc_info(),envId)
        status = None;
    
    return status

def map(function, data):
    if len(data.shape) == 2: #vector of chromosomes
        pool = Pool(realworkercount)
        result = pool.map(function, data)
        pool.close()
        pool.join()
    else:
        result = function(data)
    return result

def evaluate(data):
    if len(data.shape) == 2: #vector of chromosomes
        pool = Pool(realworkercount)
        result = pool.map(individual_get_score, data)
        pool.close()
        pool.join()
    else:
        result = individual_get_score(data)
    return result
