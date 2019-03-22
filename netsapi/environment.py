import requests
import json
import time
import re
import random

pollingInterval_seconds = 300

def initEnv(locationID, userID, resolution, baseuri):
    
    environmentUrl = '%s/api/action/v0/initEnv'%baseuri
    environmentInfo = json.dumps({"locationId": locationID, "userId": userID, "resolution": resolution})
    #print(environmentInfo)
    if resolution not in ["low","medium","high","test"]:
        raise RuntimeError("resolution is not test, low, medium, or high")

    try:
        response = requests.post(environmentUrl, data = environmentInfo, headers = {'Content-Type': 'application/json', 'Accept': 'application/json'})
        data = response.json()
        #print(data)
        
        if data['statusCode'] == 200:
            envID = data['data']['response']['id']
        else:
            message = data['message']
            raise RuntimeError(message)
    except Exception as e:
        print(e);
        raise e
    return envID

def postCampaign(envID, campaign, baseuri, nonBlocking = False, pollingInterval = pollingInterval_seconds, seed = None):
    actionUrl = '%s/api/action/v0/create'%baseuri
    reward = -10^12
    intervention_names=['ITN', 'IRS']

    if seed is None:
        seed = random.randint(0,100)

    try:
        interventionlist = []
        for intervention in campaign[0]:
            interventionlist.append( {"modelName":intervention_names[intervention[0]],"coverage":intervention[2], "time":"%s"%intervention[3]} )
        data = json.dumps({"actions":interventionlist,
                             "environmentId": envID, "actionSeed": seed});

        response = requests.post(actionUrl, data = data, headers = {'Content-Type': 'application/json', 'Accept': 'application/json'});
        responseData = response.json();

        if nonBlocking and responseData['statusCode'] == 202:
            return True
        elif responseData['statusCode'] == 202:
            reward = getReward(envID, baseuri, pollingInterval)
        else:
            message = responseData['message']
            #print(message)
            if "Another experiment has been run before" in message:
                env = message.split()[17]
                reward = getReward(env, baseuri, pollingInterval)
            else:
                raise RuntimeError(message)
    except Exception as e:
        print(e);
        reward = float('nan')
    return reward

def postAction(envID, action, baseuri, nonBlocking = False, pollingInterval = pollingInterval_seconds, seed = None):
    actionUrl = '%s/api/action/v0/create'%baseuri
    reward = -10^12
    ITN_a = str(action[0]);
    IRS_a = str(action[1]);
    try:
       ITN_time = "%d"%(action[2]);
    except:
       ITN_time = None;
    try:
       IRS_time = "%d"%(action[3]);
    except:
       IRS_time = None;
    if seed is None:
        seed = random.randint(0,100)

    itnClause = {"modelName":"ITN","coverage":ITN_a } if ITN_time is None else {"modelName":"ITN","coverage":ITN_a, "time":"%s"%ITN_time}
    irsClause = {"modelName":"IRS","coverage":IRS_a } if IRS_time is None else {"modelName":"IRS","coverage":IRS_a, "time":"%s"%IRS_time}

    actions = json.dumps({"actions":[itnClause, irsClause],
                         "environmentId": envID, "actionSeed": seed});

    try:
        response = requests.post(actionUrl, data = actions, headers = {'Content-Type': 'application/json', 'Accept': 'application/json'});
        data = response.json();

        if nonBlocking and data['statusCode'] == 202:
            return True
        elif data['statusCode'] == 202:
            reward = getReward(envID, baseuri, pollingInterval)
        else:
            message = data['message']
            #print(message)
            if "Another experiment has been run before" in message:
                env = message.split()[17]
                reward = getReward(env, baseuri, pollingInterval)
            else:
                raise RuntimeError(message)
    except Exception as e:
        print(e);
        reward = float('nan')
    return reward

def postActionV1(expID, locationId, userId, action, baseuri, pollingInterval = pollingInterval_seconds, seed = random.randint(0,100)):
    actionUrl = '%s/api/v1/experiments/postJob'%baseuri
    reward = -10^12
    ITN_a = str(action[0]);
    IRS_a = str(action[1]);
    try:
       ITN_time = "%d"%(action[2]);
    except:
       ITN_time = "730";
    
    actions = json.dumps({"actions":[{"coverage":ITN_a, "modelName":"ITN", "time":"%s"%ITN_time},{"coverage": IRS_a,"modelName": "IRS","time":"1"}],"experimentid":expID, "locationId":locationId , "userId":userId, "actionSeed": seed });
    try:
        response = requests.post(actionUrl, data = actions, headers = {'Content-Type': 'application/json', 'Accept': 'application/json'});
        data = response.json();
        #print(data);
        # print(data['statusCode'])
        if data['statusCode'] == 202:
            reward = getRewardV1(data['jobId'], baseuri, pollingInterval)
        else:
            message = data['message']
            raise RuntimeError(message)
    except Exception as e:
        print(e);
        value = float('nan')
    return reward


def getReward(envID, baseuri, pollingInterval = pollingInterval_seconds ):
    rewardUrl = "%s/api/action/v0/reward/%s"%(baseuri,envID)
    counter = 10;
    time.sleep(pollingInterval+random.randint(0,6));
    try:
        while getStatus(envID, baseuri) != "true" and counter > 0:
            counter -= 1
            time.sleep(pollingInterval+random.randint(0,6));
        if counter > 0:
            reward = requests.post(rewardUrl, headers = {'Content-Type': 'application/json', 'Accept': 'application/json'})
        #print('Cost Per Daly Averted:',reward.text)
        value = float(reward.text)
    except Exception as e:
        print(e);
        value = float('nan')
    return value

def getRewardV1(expID, baseuri, pollingInterval = pollingInterval_seconds):
    rewardUrl = "%s/api/v1/experiments/reward/%s"%(baseuri,expID)
    counter = 20;
    time.sleep(pollingInterval+random.randint(0,6));
    try:
        while getStatusV1(expID, baseuri) != "true" and counter > 0:
            #print (expID, getStatusV1(expID, baseuri))
            counter -= 1
            time.sleep(pollingInterval+random.randint(0,6));
        if counter > 0:
            reward = requests.post(rewardUrl, headers = {'Content-Type': 'application/json', 'Accept': 'application/json'})
        #print('Cost Per Daly Averted:',reward.text)
        value = float(reward.text)
    except Exception as e:
        print(e);
        value = float('nan')
    return value

def getStatus(envID, baseuri):
    statusUrl = "%s/api/action/v0/status/%s"%(baseuri,envID)
    ret = "_false"
    try:
        response = requests.get(statusUrl, headers = {'Accept': 'application/json'})
        ret = response.text
    except Exception as e:
        ret = "false %s"%(e)
    
    return ret

def getStatusV1(expID, baseuri):
    statusUrl = "%s/api/v1/experiments/status/%s"%(baseuri,expID)
    ret = "_false"
    try:
        response = requests.get(statusUrl, headers = {'Accept': 'application/json'})
        ret = response.text
    except Exception as e:
        ret = "false %s"%(e)
    
    return ret

class TestEnvironment():
    def __init__(self, userID, baseuri, locationId, resolution = "test", timeout = 0, realworkercount = 1):
        
        self._resolution = resolution
        self._timeout = timeout
        self._realworkercount = realworkercount

        self.policyDimension = 2
        self._baseuri =  baseuri
        self._locationId = locationId
        self.userId = userID
    
    def _individual_get_reward(self, action):
        from sys import exc_info
        try:
            reward = initEnv(self._locationId, self.userId, self._resolution, self._baseuri)
        except:
            print(exc_info(),action)
            reward = None;
        
        return -reward

    def evaluateReward(self, data, coverage = 1):
        from multiprocessing import Pool
        if len(data.shape) == 2: #vector of chromosomes
            pool = Pool(self._realworkercount)
            result = pool.map(self._individual_get_reward, data)
            pool.close()
            pool.join()
        else:
            result = _individual_get_score(data)
        return result

