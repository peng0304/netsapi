import requests
import json



def showLocations(baseuri):
    locationUrl = '%s/api/locations/v0/viewLocations'%baseuri
    try:
        response = requests.get(locationUrl, headers = {'Accept': 'application/json'})
        data = response.json()
        for name in data:
            print(name["names"])
        
        return data
    
    except Exception as e:
        raise e


def getLocationId(location, name):
    for i in location:
        if i['names'] == name:
            locationId = i['locationId']
            print('locationId = ', locationId )
        if locationId is None:
            print("%s not found"%name)

return locationId
