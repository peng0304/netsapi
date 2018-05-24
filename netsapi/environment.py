import requests
import json
import time
import re

pollingInterval_seconds = 5

def initEnv(locationID, userID, baseuri):
	
	environmentUrl = '%s/api/action/v0/initEnv'%baseuri
	environmentInfo = json.dumps({"locationId": locationID, "userId": userID})

	try:
		response = requests.post(environmentUrl, data = environmentInfo, headers = {'Content-Type': 'application/json', 'Accept': 'application/json'})
		data = response.json()
        # print(data)
		envID = data['jsonNode']['response']['id']

	except Exception as e:
		raise e

	return envID

def postAction(envID, action, baseuri):
    actionUrl = '%s/api/action/v0/create'%baseuri
    reward = -10^12
    ITN_a = str(action[0]);
    IRS_a = str(action[1]);
    try:
       ITN_time = "%d"%(action[1]*18+6);
    except:
       ITN_time = "1";

    actions = json.dumps({"actions":[{"componentId":"ITN","coverage":ITN_a, "time":ITN_time},{"componentId":"IRS","coverage":IRS_a}], "environmentId": envID});

    try:
        response = requests.post(actionUrl, data = actions, headers = {'Content-Type': 'application/json', 'Accept': 'application/json'});
        data = response.json();
        #print(data);
        # print(data['statusCode'])
        if data['statusCode'] == 400:
			message = data['message']
			#print(message)
			env = message.split()[17]
			#print(env)

			reward = getReward(env, baseuri)

        else:
			reward = getReward(envID, baseuri)

		# 	m = re.search(r'ID\\(\d+)\ to',message)
		# 	print()
		# else
		# 	getReward(envID, baseuri)

    except Exception as e:
		raise e

    return reward

def getReward(envID, baseuri):
	rewardUrl = "%s/api/action/v0/reward/%s"%(baseuri,envID)
	
	try:
		while getStatus(envID, baseuri) != "true":		
			# if getStatus(envID, baseuri)  != "false":
			# 	break
			#print("waiting", envID)
			time.sleep(pollingInterval_seconds);
		reward = requests.post(rewardUrl, headers = {'Content-Type': 'application/json', 'Accept': 'application/json'})
		#print('Cost Per Daly Averted:',reward.text)

	except Exception as e:
		raise e

	return float(reward.text)

def getStatus(envID, baseuri):
    statusUrl = "%s/api/action/v0/status/%s"%(baseuri,envID)
    ret = "_false"
    try:
        response = requests.get(statusUrl, headers = {'Accept': 'application/json'})
        ret = response.text
    except Exception as e:
        raise e
    
    return ret
