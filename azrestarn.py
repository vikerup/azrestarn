#!/usr/bin/python3

import requests
import argparse
import json
import sys
import os
from pathlib import Path

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


parser = argparse.ArgumentParser(description='yolo')

parser.add_argument("--proxy", required=False, action='store_true')
parser.add_argument("--login", required=False, action='store_true')
parser.add_argument("--bitlocker", required=False, action='store_true')
parser.add_argument("--computername", required=False, type=str)
parser.add_argument("--domain", required=False, type=str)
parser.add_argument("--checkbestprac", required=False, action='store_true')
parser.add_argument("--me", required=False,action='store_true')
parser.add_argument("--checkme", required=False, action='store_true')
parser.add_argument("--objectid", required=False, type=str)
parser.add_argument("--owneddevices", required=False, action='store_true')
parser.add_argument("--dynamicgroups", required=False, action='store_true')
args = parser.parse_args()

proxy = args.proxy
login = args.login
bitlocker = args.bitlocker
computername = args.computername
domain = args.domain
checkbestprac = args.checkbestprac
me = args.me
checkme = args.checkme
objectid = args.objectid
owneddevices = args.owneddevices
dynamicgroups = args.dynamicgroups

if proxy:
    proxies = {
                  "http"  : "http://127.0.0.1:8080",
                  "https" : "http://127.0.0.1:8080"
                }
else:
    proxies = None

def _mslogin_devicecode(scope):
    url = "https://login.microsoftonline.com/common/oauth2/devicecode?api-version=1.0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36", 
        "Accept": "*/*", 
        "Content-Type": "application/x-www-form-urlencoded", 
        "Connection": "close"
    }
    data = {
        "client_id": "1950a258-227b-4e31-a9cf-717495945fc2", 
        "resource": scope
    }
    response = requests.post(url, headers=headers, data=data, proxies=proxies, verify=False)
    jsonResponse = response.json()
    device_code = jsonResponse["device_code"]
    print("[+] Scope:", scope, "open https://microsoft.com/devicelogin and use code:",jsonResponse["user_code"],"\n")
    input("[+] Press any key when authentication is complete...\n")
    url_code = "https://login.microsoftonline.com/Common/oauth2/token?api-version=1.0"
    headers_code = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36", 
        "Accept": "*/*", 
        "Content-Type": "application/x-www-form-urlencoded", 
        "Connection": "close"
        }
    data_code = {
        "client_id": "1950a258-227b-4e31-a9cf-717495945fc2", 
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code", 
        "code": jsonResponse["device_code"]
        }
    response_code = requests.post(url_code, headers=headers_code, data=data_code, proxies=proxies, verify=False)
    jsonResponse_code = response_code.json()

    if not os.path.exists('.azrestarn_auth.json'):
        template = {'https://graph.windows.net': 'temp', 'https://graph.microsoft.com': ''}
        with open(".azrestarn_auth.json", "w") as outfile:
            json.dump(template, outfile)
    
    with open('.azrestarn_auth.json','r') as f:
        dic = json.load(f)
    
    tokens = {
        scope: jsonResponse_code["access_token"]
    }
    with open(".azrestarn_auth.json", "w") as outfile:
        dic.update(tokens)
        json.dump(dic, outfile)

def _find_bitlocker_key(domain,computername):
    if computername == None:
        print("[+] Please specify --computername parameter. Ex LAPTOP001 or LAPTOP (aka startswith)")
        sys.exit(1)
    if domain == None:
        print("[+] Please specify --domain parameter. Ex ecorp.com or ecorp.onmicrosoft.com")
        sys.exit(1)
    if os.path.exists(".azrestarn_auth.json"):
        with open('.azrestarn_auth.json','r') as f:
            dic = json.load(f)
        access_token = dic["https://graph.windows.net"]
        url = "https://graph.windows.net/{}/devices?api-version=1.61-internal&$filter=startswith(displayName, '{}')".format(domain,computername) 
        headers= {"Authorization": "Bearer " + str(access_token)}
        response = requests.get(url=url, headers=headers, proxies=proxies, verify=False)
        print(json.dumps(response.json(), indent=4))

def _check_bestprac():
    if os.path.exists(".azrestarn_auth.json"):
        with open('.azrestarn_auth.json','r') as f:
            dic = json.load(f)
        access_token = dic["https://graph.microsoft.com"]
        url = "https://graph.microsoft.com/beta/policies/authorizationPolicy/authorizationPolicy"
        headers = {
            "ConsistencyLevel": "eventual",
            "Authorization": "Bearer " + str(access_token)
            }
        response = requests.get(url=url, headers=headers, proxies=proxies, verify=False)
        print(json.dumps(response.json(), indent=4))

def _checkMe():
    if os.path.exists(".azrestarn_auth.json"):
        with open('.azrestarn_auth.json','r') as f:
            dic = json.load(f)
        access_token = dic["https://graph.microsoft.com"]
        url = "https://graph.microsoft.com/beta/me" 
        headers= {
            "Authorization": "Bearer " + str(access_token),
            "ConsistencyLevel": "eventual"
            }
        response = requests.get(url=url, headers=headers, proxies=proxies, verify=False)
        print(json.dumps(response.json(), indent=4))

def _checkMeGroups(meObjectId):
    if meObjectId == None:
        print("[+] Please specify --objectid parameter. Find it with --me.")
        sys.exit(1)
    if os.path.exists(".azrestarn_auth.json"):
        with open('.azrestarn_auth.json','r') as f:
            dic = json.load(f)
        access_token = dic["https://graph.microsoft.com"]
        url = "https://graph.microsoft.com/v1.0/users/{}/memberOf".format(meObjectId)
        headers = {
            "Authorization": "Bearer " + str(access_token),
            "ConsistencyLevel": "eventual"
            }
        response = requests.get(url=url, headers=headers, proxies=proxies, verify=False)
        print(json.dumps(response.json(), indent=4))

def _checkOwnedDevices():
    if os.path.exists(".azrestarn_auth.json"):
        with open('.azrestarn_auth.json','r') as f:
            dic = json.load(f)
        access_token = dic["https://graph.microsoft.com"]
        url = "https://graph.microsoft.com/v1.0/me/ownedDevices"
        headers = {
            "Authorization": "Bearer " + str(access_token)
            }
        response = requests.get(url=url, headers=headers, proxies=proxies, verify=False)
        print(json.dumps(response.json(), indent=4))

def _checkDynamicGroups():
    if os.path.exists(".azrestarn_auth.json"):
        with open('.azrestarn_auth.json','r') as f:
            dic = json.load(f)
        access_token = dic["https://graph.microsoft.com"]
        url = "https://graph.microsoft.com/v1.0/groups?$filter=groupTypes/any(s:s eq 'DynamicMembership')&$top=999"
        headers = {
            "Authorization": "Bearer " + str(access_token)
            }
        response = requests.get(url=url, headers=headers, proxies=proxies, verify=False)
        print(json.dumps(response.json(), indent=4))
    
if login:
    _mslogin_devicecode("https://graph.windows.net")
    _mslogin_devicecode("https://graph.microsoft.com")
if bitlocker: _find_bitlocker_key(domain,computername)
if checkbestprac: _check_bestprac()
if me: _checkMe()
if checkme: _checkMeGroups(objectid)
if owneddevices: _checkOwnedDevices()
if dynamicgroups: _checkDynamicGroups()

