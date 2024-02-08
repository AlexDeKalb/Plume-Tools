import os
import requests
import paramiko
import time
import psutil
from bs4 import BeautifulSoup
from ipaddress import ip_network, ip_address
import urllib3
import json

def plumeAuth():        #Gen Auth for PLUME API
    authUrl = 'https://piranha-int.tau.dev-charter.net/api/Customers/login?client_id=0oa1tsl0szbtfH9hw357'
    authData = {"email":{abstracted},"password":{abstracted}}
    auth = requests.post(url=authUrl, data=authData).json()['id']
    authString = {'Authorization':f'{auth}'}
    return authString

def plumegetCustID(routerMac):      #GET INFO
    authString = plumeAuth()
    getCustID_URL = f"https://piranha-int.tau.dev-charter.net/api/Nodes/{routerMac}?client_id=0oa1tsl0szbtfH9hw357"
    cust_get = requests.get(url=getCustID_URL, headers = authString).json()
    customer_id = cust_get['customerId']
    location_id = cust_get['locationId']
    items = {'customerId':customer_id,'locationId':location_id}
    return items
    
def disableWiFi(routerMac):
    authString = plumeAuth()
    items = plumegetCustID(routerMac)
    customer_id = items['customerId']
    location_id = items['locationId']
    disablewifi = {"enabled": True}
    sshenURL = f"https://piranha-int.tau.dev-charter.net/api/Customers/{customer_id}/locations/{location_id}/wifiNetwork"
    requests.patch(url=sshenURL, json=disablewifi, headers=authString)
    
def getWiFiNetworks(routerMac):
    authString = plumeAuth()
    items = plumegetCustID(routerMac)
    customer_id = items['customerId']
    location_id = items['locationId']
    url = f"https://piranha-int.tau.dev-charter.net/api/Customers/{customer_id}/locations/{location_id}/wifiNetworks"
    response = requests.get(url, headers=authString)
    if response.status_code == 200:
        wifi_networks = response.json()
        if not wifi_networks:
            with open('log.txt', 'a') as f:
                f.write(f"{routerMac}'s WiFi is {wifi_networks}\n")
                disableWiFi(routerMac)
                f.write(f"{routerMac}'s WiFi was enabled, but has been disabled\n")
            return 1
        else:
            return 0
    else:
        # handle error
        pass

def devplumeAuth():        #Gen Auth for PLUME API
    authUrl = 'https://piranha-dev3.tau.dev-charter.net/api/Customers/login?client_id=0oa1tsl0szbtfH9hw357'
    authData = {"email":"robot-testing-user@charter.com","password":"Robot@Testing"}
    auth = requests.post(url=authUrl, data=authData).json()['id']
    authString = {'Authorization':f'{auth}'}
    return authString

def devplumegetCustID(routerMac):      #GET INFO
    authString = devplumeAuth()
    getCustID_URL = f"https://piranha-dev3.tau.dev-charter.net/api/Nodes/{routerMac}?client_id=0oa1tsl0szbtfH9hw357"
    cust_get = requests.get(url=getCustID_URL, headers = authString).json()
    customer_id = cust_get['customerId']
    location_id = cust_get['locationId']
    items = {'customerId':customer_id,'locationId':location_id}
    return items
    
def devdisableWiFi(routerMac):
    authString = devplumeAuth()
    items = devplumegetCustID(routerMac)
    customer_id = items['customerId']
    location_id = items['locationId']
    disablewifi = {"enabled": True}
    sshenURL = f"https://piranha-dev3.tau.dev-charter.net/api/Customers/{customer_id}/locations/{location_id}/wifiNetwork"
    requests.patch(url=sshenURL, json=disablewifi, headers=authString)
    
def devgetWiFiNetworks(routerMac):
    authString = devplumeAuth()
    items = devplumegetCustID(routerMac)
    customer_id = items['customerId']
    location_id = items['locationId']
    url = f"https://piranha-dev3.tau.dev-charter.net/api/Customers/{customer_id}/locations/{location_id}/wifiNetworks"
    response = requests.get(url, headers=authString)
    if response.status_code == 200:
        wifi_networks = response.json()
        if not wifi_networks:
            with open('log.txt', 'a') as f:
                f.write(f"{routerMac}'s WiFi is {wifi_networks}\n")
                devdisableWiFi(routerMac)
                f.write(f"{routerMac}'s WiFi was enabled, but has been disabled\n")
            return 1
        else:
            return 0
    else:
        # handle error
        pass



# Set the base URL for the Snipe-IT API
BASE_URL = 'https://inventory.scp-lab.dev-charter.net:8443/api/v1'
# Set your Snipe-IT API token
API_TOKEN = abstracted
# Set the headers for the API requests
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {API_TOKEN}'
}


# Get all assets from Snipe-IT
assets_response = requests.get(f'{BASE_URL}/hardware', headers=headers)
assets_data = json.loads(assets_response.text)
#print(assets_data)

# # Print raw asset data
# print("Raw asset data:")
#print(json.dumps(assets_data, indent=2))

# # Get all routers
routers = [asset for asset in assets_data['rows'] if asset['category']['name'] == 'Router']

# # Filter routers to only include those that belong to a location that does not contain "wlan" in its name
routers = [router for router in routers if 'location' in router and router['location'] is not None and 'wlan' in router['location']['name'].lower()]

# # Print selected routers
#print("Selected routers:")
#for router in routers:
#    print(f"  {router['name']}")

# # Get the MAC addresses of the routers from the custom field and format them to be in lowercase and without colons
mac_addresses = [router['custom_fields']['MAC Address']['value'].lower().replace(':', '') for router in routers if 'MAC Address' in router['custom_fields'] and router['custom_fields']['MAC Address']['value'] != '']
#print(mac_addresses)

for macs in mac_addresses: 
    try: 
        getWiFiNetworks(macs)
    except:
        try:
            devgetWiFiNetworks(macs)
        except:
            print(f"An exception occurred for {macs}")
