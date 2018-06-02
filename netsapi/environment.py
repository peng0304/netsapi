import requests
import json
import time
import re
import random

pollingInterval_seconds = 300

def initEnv(locationID, userID, baseuri):
    
    environmentUrl = '%s/api/action/v0/initEnv'%baseuri
    environmentInfo = json.dumps({"locationId": locationID, "userId": userID})

    try:
        response = requests.post(environmentUrl, data = environmentInfo, headers = {'Content-Type': 'application/json', 'Accept': 'application/json'})
        data = response.json()
        # print(data)
        
        if data['statusCode'] == 200:
            envID = data['jsonNode']['response']['id']
        else:
            message = data['message']
            raise RuntimeError(message)
    except Exception as e:
        raise e
    return envID

def postAction(envID, action, baseuri, pollingInterval = pollingInterval_seconds):
    actionUrl = '%s/api/action/v0/create'%baseuri
    reward = -10^12
    ITN_a = str(action[0]);
    IRS_a = str(action[1]);
    try:
       ITN_time = "%d"%(action[2]*18+6);
    except:
       ITN_time = "1";

    actions = json.dumps({"actions":[{"componentId":"ITN","coverage":ITN_a, "time":"%st"%ITN_time},{"componentId":"IRS","coverage":IRS_a}], "environmentId": envID});

    try:
        response = requests.post(actionUrl, data = actions, headers = {'Content-Type': 'application/json', 'Accept': 'application/json'});
        data = response.json();
        #print(data);
        # print(data['statusCode'])
        if data['statusCode'] == 202:
            reward = getReward(envID, baseuri, pollingInterval)
        else:
            message = data['message']
            #print(message)
            if message == "You have another task in queue with the same environment id":
                env = message.split()[17]
                reward = getReward(env, baseuri, pollingInterval)
            else:
                raise RuntimeError(message)
    except Exception as e:
        raise e

    return reward

def getReward(envID, baseuri, pollingInterval = pollingInterval_seconds ):
    rewardUrl = "%s/api/action/v0/reward/%s"%(baseuri,envID)
    
    try:
        while getStatus(envID, baseuri) != "true":
            # if getStatus(envID, baseuri)  != "false":
            #     break
            #print("waiting", envID)
            time.sleep(random.uniform(pollingInterval/2,pollingInterval));
        reward = requests.post(rewardUrl, headers = {'Content-Type': 'application/json', 'Accept': 'application/json'})
        #print('Cost Per Daly Averted:',reward.text)
        value = float(reward.text)
    except Exception as e:
        raise e

    return value

def getStatus(envID, baseuri):
    statusUrl = "%s/api/action/v0/status/%s"%(baseuri,envID)
    ret = "_false"
    try:
        response = requests.get(statusUrl, headers = {'Accept': 'application/json'})
        ret = response.text
    except Exception as e:
        raise e
    
    return ret
