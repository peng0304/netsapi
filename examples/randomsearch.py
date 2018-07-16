import numpy as np
from netsapi.environment import *
from netsapi.location import *
from netsapi.visualisation import *

from sys import exit, exc_info, argv
from multiprocessing import Pool, current_process

import timeit;
ts = timeit.time.time()

exp_location, timeout = 'AA', BB
baseuri,userId = "http://XX", 'YY'

locations = showLocations(baseuri)
locationId = getLocationId(locations, exp_location)

realworkercount=int(argv[1]) if len(argv) > 1 else  1; #determines how many requests can actually be concurrently made

def individual_get_score(gene):
    name_s=current_process().name
    if  "-" in name_s:
	    id = np.mod(int(name_s.split("-")[1]),realworkercount)
    else:
            id = -1
    try:
        envId = initEnv(locationId, userId, baseuri);
        reward = postAction(envId, gene, baseuri, timeout)

    except:
        print(exc_info(),gene)
        reward = None;
    
    return reward

def evaluate(data):
    if len(data.shape) == 2: #vector of chromosomes
        pool = Pool(realworkercount)
        result = pool.map(individual_get_score, data)
        pool.close()
        pool.join()
    else:
        result = individual_get_score(data)
    return result

popsize=128
num_paramters=3
num_generations = 5

exp_location
filename = "randomsearch-data-%d-%d-%s.npy"%(ts,popsize,exp_location)

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

        # calculate the reward for each given solution using our own method
        rewards = evaluate(solutions)
        
        print(np.max(rewards),i, num_generations)
        history[i,:,:] = np.hstack((solutions,np.array(rewards).reshape(-1,1)))
        np.save(filename, history)
    except (KeyboardInterrupt, SystemExit):
        print(exc_info())

print("done")
