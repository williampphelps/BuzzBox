import os
import requests
import json
import docker
import time

def getCurrentConfig():
    filename = 'test/.opencanary.conf'

    with open(filename) as file:
        currentConfig = json.load(file)
    return currentConfig


def getWebdata():
    website = os.getenv("WEBSITE")
    machine_id = os.getenv("MACHINE_ID")
    url = website + 'api/machines/' + machine_id
    r = requests.get(url)
    webdata = r.json()
    return webdata

def compareConfigs(currentConfig, webdata):
    if currentConfig != webdata['config']:
        filename = 'test/.opencanary.conf'
        with open(filename, "w") as outfile:
            json.dump(webdata['config'], outfile)
        restartDockerContainer()

def restartDockerContainer():
    client = docker.from_env()

    container = client.containers.get("beetriggered-opencanary-1")
    container.restart()

def checkIfBrandNew():
    webdata = getWebdata()
    
    if webdata['status'] == "brandnew":
        website = os.getenv("WEBSITE")
        machine_id = os.getenv("MACHINE_ID")
        url = website + 'api/machines/' + machine_id
        data = getCurrentConfig()
        # data = json.dumps(data)
        requests.put(url, json={'config': data, 'status': 'running'})
        return False
    return True

def run():
    print('run was called.')
    compareConfigs(getCurrentConfig(), getWebdata())

def main():
    while True:
        print("loop")
        if checkIfBrandNew():
            run()
            
        time.sleep(10)


main()





