import argparse
import numpy as np
from netsapi.environment import *
from netsapi.location import *
from netsapi.visualisation import *

from sys import exit, exc_info, argv
from multiprocessing import Pool, current_process

import timeit;
ts = timeit.time.time()

#exp_location, timeout = 'new_rach_int_100000', 1800-800
#exp_location, timeout = 'new_rach_int_100',  5
#exp_location, timeout = 'gamb_int_100000',  1800-800

#baseuri,userId = "http://localhost:9877", '6e5d79ae637f41508228b28d0c5523f4' #couchdb
#baseuri,userId = "http://9.12.248.199:9877", '7d5cd735f31245c8b98bad49f37d072c' #couchdb
#realworkercount=int(argv[1]) if len(argv) > 1 else  1; #determines how many requests can actually be concurrently made

parser = argparse.ArgumentParser()
parser.add_argument('--uri', default="http://localhost:9877", help='the uri to be used for the task clerk')
parser.add_argument('--user', default="6e5d79ae637f41508228b28d0c5523f4", help='the userId provided upon registation')
parser.add_argument('--location', default="rach_int_100", help='the scenario file used for the experiments')
parser.add_argument('--timeout', default=1, help='a value proportional to the delay needed between polling', type=int)
parser.add_argument('--batch', default=1, help='the number of jobs submitted concurrently', type=int)
parser.add_argument('--resolution', default="test", help='the population resolution used for the experiments (low|medium|high|test)')

args = parser.parse_args()
exp_location, timeout, baseuri, userId, realworkercount, resolution = args.location, args.timeout, args.uri, args.user, args.batch, args.resolution

locations = showLocations(baseuri)
locationId = getLocationId(locations, exp_location)

def individual_get_score(gene):
    name_s=current_process().name
    if  "-" in name_s:
	    id = np.mod(int(name_s.split("-")[1]),realworkercount)
    else:
            id = -1
    try:
        envId = initEnv(locationId, userId, resolution, baseuri);
        reward = postAction(envId, gene, baseuri, timeout)

    except:
        print(exc_info(),gene)
        reward = None;
    
    return reward

def evaluateBlocking(data):
    if len(data.shape) == 2: #vector of chromosomes
        pool = Pool(realworkercount)
        result = pool.map(individual_get_score, data)
        pool.close()
        pool.join()
    else:
        result = individual_get_score(data)
    return result

def evaluateNonBlocking(data, coverage):
    try:
        completed = []
        envs = push(data, singletonPostNonBlocking)
        while len(completed) < coverage*data.shape[1]:
            statii = push(np.array(envs).reshape(-1,1), singletonUpdate)
            completed = [i for i,v in enumerate(statii) if v == 'true']
            print(len(completed), envs)
        rewardz = push(np.array(envs).reshape(-1,1)[completed], singletonReward)
        val = solutions[completed], rewardz
    except:
        print(exc_info(),data)
        val = None, None
    return val

def singletonPostNonBlocking(data):
    name_s=current_process().name
    posted = False
    if  "-" in name_s:
	    id = np.mod(int(name_s.split("-")[1]),realworkercount)
    else:
        id = -1
    try:
        envId = initEnv(locationId, userId, resolution, baseuri);
        posted = postAction(envId, data, baseuri, True)

    except:
        print(exc_info(),data)
    
    return envId if posted else None

def singletonUpdate(envId):
    name_s=current_process().name
    if  "-" in name_s:
	    id = np.mod(int(name_s.split("-")[1]),realworkercount)
    else:
        id = -1
    try:
        status = getStatus(envId[0], baseuri)
        print(id,status)

    except:
        print(exc_info(),envId)
        status = None;
    
    return status

def singletonReward(envId):
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


def push(data,function):
    if len(data.shape) == 2: #vector
        pool = Pool(realworkercount)
        result = pool.map(function, data)
        pool.close()
        pool.join()
    else: #array
        result = function(data)
    return result

popsize=4
num_paramters=3
num_generations = 2

exp_location
filename = "newRandomREMY-data-%d-%d-%s.npy"%(ts,popsize,exp_location)

x = np.arange(0.01, .99, 0.01)
y = np.arange(0.01, .99, 0.01)
t = np.arange(20)

xx, yy, tt = np.meshgrid(x, y, t)
allsolutions = np.vstack((xx.flatten(),yy.flatten(), tt.flatten())).T

history=  np.empty(shape=(num_generations, popsize, num_paramters+1))
for i in range(num_generations):
    try:
        # ask for a set of random candidate solutions to be evaluated
        solutions = allsolutions[np.random.choice(allsolutions.shape[0],popsize),:];
        #solutions = np.ones((popsize,3))*np.array([.2,.3,14])
        # calculate the reward for each given solution using our own method
        doneSolutions, doneRewards = evaluateNonBlocking(solutions, .5)
        # get best parameter, reward from ES
        print(np.max(doneRewards),i, num_generations)
        print(doneSolutions,doneRewards)
        #history[i,:,:] = np.hstack((doneSolutions,doneRewards))
        #np.save(filename, history)
    except (KeyboardInterrupt, SystemExit):
        print(exc_info())

print("done")
