import os
import requests
import json
import docker
import time
import datetime
import socket

PUBLIC_API_KEY = os.getenv('PUBLIC_API_KEY')
SECRET_API_KEY = os.getenv('SECRET_API_KEY')

MACHINE_ID = os.getenv('MACHINE_ID')

CONSOLE_URL = os.getenv('WEBSITE')

REQUEST_HEADERS = {
    'x-bee-public': PUBLIC_API_KEY,
    'x-bee-secret': SECRET_API_KEY
}

SOFTWARE_VERSION = '0.0.1'

STARTUP_TIME = int(time.mktime(datetime.datetime.now().timetuple()) * 1000)

def getCurrentConfig():
    filename = 'test/.opencanary.conf'

    with open(filename) as file:
        currentConfig = json.load(file)
    return currentConfig

def get_ip_address():
    return socket.gethostbyname(socket.gethostname())

def getWebdata():
    response = requests.get(CONSOLE_URL + '/api/machines/' + MACHINE_ID, headers=REQUEST_HEADERS)
    machine = response.json()
    return machine

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

def activate_machine(machine):
    machineConf = getCurrentConfig()
    machineConf['device.node_id'] = machine['_id']

    machine['config'] = machineConf
    machine['status'] = 'activated'
    machine['location'] = 'Arrived'

    newMachine = {
        'config': machine['config'],
        'status': machine['status'],
        'name': machine['name'],
        'location': machine['location']
    }

    print("New Online Config")
    print(newMachine['config'])

    requests.put(CONSOLE_URL + '/api/machines/' + MACHINE_ID, json=newMachine, headers=REQUEST_HEADERS)

def main():
    machine = getWebdata()
    if (machine['status'] == "unactivated"):
        print("Activating Machine...")
        activate_machine(machine)
    newMachine = {
        'startup_time': STARTUP_TIME 
    }
    response = requests.put(CONSOLE_URL + '/api/machines/' + MACHINE_ID, json=newMachine, headers=REQUEST_HEADERS)
    while True:
        time.sleep(10)
        machine = getWebdata()
        if (machine['status'] == 'need update'):
            print('Update Requested')
            newMachine = {
                'last_seen': int(time.mktime(datetime.datetime.now().timetuple()) * 1000),
                'ip_address': get_ip_address(),
                'status': 'updated',
                'software_version': SOFTWARE_VERSION
            }
            response = requests.put(CONSOLE_URL + '/api/machines/' + MACHINE_ID, json=newMachine, headers=REQUEST_HEADERS)
            break
        newMachine = {
            'last_seen': int(time.mktime(datetime.datetime.now().timetuple()) * 1000),
            'ip_address': get_ip_address(),
            'status': 'running',
            'software_version': SOFTWARE_VERSION
        }
        response = requests.put(CONSOLE_URL + '/api/machines/' + MACHINE_ID, json=newMachine, headers=REQUEST_HEADERS)
        compareConfigs(getCurrentConfig(), getWebdata())

    print('Finished main')

main()





