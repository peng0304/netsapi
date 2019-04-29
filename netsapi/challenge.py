import os
from sys import exit, exc_info, argv
from multiprocessing import Pool, current_process
import random
import json
import requests

class ChallengeEnvironment():
    def __init__(self, experimentCount = 1000, userID = "KDDChallengeUser", baseuri = "https://nlmodelflask.eu-gb.mybluemix.net", locationId = "abcd123", resolution = "test", timeout = 0, realworkercount = 1):
        
        self._resolution = resolution
        self._timeout = timeout
        self._realworkercount = realworkercount

        self.policyDimension = 2
        self._baseuri =  baseuri
        self._locationId = locationId
        self.userId = userID
        self._experimentCount = experimentCount
        self.experimentsRemaining = experimentCount
    def reset(self):
        self.experimentsRemaining = self._experimentCount
        
    def simplePostAction(self, action):
        actionUrl = '%s/api/action/v0/create'%self._baseuri
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
        seed = random.randint(0,100)
        envID = "none"

        itnClause = {"modelName":"ITN","coverage":ITN_a } if ITN_time is None else {"modelName":"ITN","coverage":ITN_a, "time":"%s"%ITN_time}
        irsClause = {"modelName":"IRS","coverage":IRS_a } if IRS_time is None else {"modelName":"IRS","coverage":IRS_a, "time":"%s"%IRS_time}

        actions = json.dumps({"actions":[itnClause, irsClause],
                             "environmentId": envID, "actionSeed": seed});
        try:
            response = requests.post(actionUrl, data = actions, headers = {'Content-Type': 'application/json', 'Accept': 'application/json'});
            data = response.json();
            reward = -float(data['data'])
        except Exception as e:
            print(e);
            reward = float('nan')
        return reward

    def evaluateReward(self, data, coverage = 1):
        from numpy import ndarray
        print(self.experimentsRemaining, " Evaluations Remaining")
        if self.experimentsRemaining <= 0:
            raise ValueError('You have exceeded the permitted number of Evaluations')
        if type(data) is not ndarray:
            raise ValueError('argument should be a numpy array')
        
        from multiprocessing import Pool
        if len(data.shape) == 2: #array of policies
            self.experimentsRemaining -= data.shape[0]
            pool = Pool(self._realworkercount)
            result = pool.map(self.simplePostAction, data)
            pool.close()
            pool.join()
        else:
            result = self.simplePostAction(data)
            self.experimentsRemaining -= 1
        return result

class ChallengeSeqDecEnvironment():
    def __init__(self, experimentCount = 1000, userID = "KDDChallengeUser", baseuri = "https://seqenvironment.eu-gb.mybluemix.net", locationId = "abcd123", resolution = "test", timeout = 0, realworkercount = 1):

        self._resolution = resolution
        self._timeout = timeout
        self._realworkercount = realworkercount

        self.actionDimension = 2
        self.policyDimension = 5
        self._baseuri =  baseuri
        self._locationId = locationId
        self.userId = userID
        self._experimentCount = experimentCount
        self.experimentsRemaining = self._experimentCount 
        self.reset()
        self.action = []
        self.policy = {}

    def reset(self):
        self.state = 1
        self.done = False
        self.action = []
        self.policy = {}

    def simplePostAction(self, action):
        rewardUrl = '%s/evaluate/action/'%self._baseuri

        try:
            print(action)
            extended_action = {}
            extended_action['action']=action
            extended_action['old'] = self.action
            extended_action['state'] = self.state
            print(extended_action)
            response = requests.post(rewardUrl, data = json.dumps(extended_action), headers = {'Content-Type': 'application/json', 'Accept': 'application/json'});
            data = response.json();
            reward = -float(data['data'])
        except Exception as e:
            print(e);
            reward = float('nan')
        return reward

    def simplePostPolicy(self, policy):
        rewardUrl = '%s/evaluate/policy/'%self._baseuri

        try:
            print(policy)
            response = requests.post(rewardUrl, data = json.dumps(policy), headers = {'Content-Type': 'application/json', 'Accept': 'application/json'});
            data = response.json();
            reward = -float(data['data'])
        except Exception as e:
            print(e);
            reward = float('nan')
        return reward

    def evaluateAction(self, action):
        reward = float("nan")
        print(self.experimentsRemaining, " Evaluations Remaining")
        if self.experimentsRemaining <= 0:
            raise ValueError('You have exceeded the permitted number of Evaluations')
        self.experimentsRemaining -= 1
        
        if ~self.done and self.state <= self.policyDimension:
            reward = self.simplePostAction(action)
            self.action = action
            self.state += 1

        if self.state > self.policyDimension: self.done = True
        return self.state, reward, self.done, {}

    def evaluatePolicy(self, data, coverage = 1):
        print(self.experimentsRemaining, " Evaluations Remaining")
        if self.experimentsRemaining <= 0:
            raise ValueError('You have exceeded the permitted number of Evaluations')

        from multiprocessing import Pool
        if type(data) is list and all([type(i) is dict for i in data]): #list of policies
            self.experimentsRemaining -= len(data)*5
            pool = Pool(self._realworkercount)
            result = pool.map(self.simplePostPolicy, data)
            pool.close()
            pool.join()
        elif type(data) is dict:
            result = self.simplePostPolicy(data)
            self.experimentsRemaining -= 1*5
        else:
            raise ValueError('argument should be a policy (dictionary) or a list of policies')

        return result
