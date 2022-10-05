#!/usr/bin/python3

import requests
import argparse
import json
import sys
import os

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser(description='azrestarn.py')

parser.add_argument("--proxy", required=False, action='store_true')
parser.add_argument("--login", required=False, action='store_true')
parser.add_argument("--refresh", required=False, action='store_true')
parser.add_argument("--bitlocker", required=False, action='store_true')
parser.add_argument("--computername", required=False, type=str)
parser.add_argument("--domain", required=False, type=str)
parser.add_argument("--checkbestprac", required=False, action='store_true')
parser.add_argument("--me", required=False,action='store_true')
parser.add_argument("--checkme", required=False, action='store_true')
parser.add_argument("--objectid", required=False, type=str)
parser.add_argument("--owneddevices", required=False, action='store_true')
parser.add_argument("--dynamicgroups", required=False, action='store_true')
parser.add_argument("--invite", required=False, action='store_true')
parser.add_argument("--email", required=False, type=str)
parser.add_argument("--dispname", required=False, type=str)
parser.add_argument("--inviteurl", required=False, type=str)
parser.add_argument("--invitedusers", required=False, action='store_true')
parser.add_argument("--invitedelete", required=False, action='store_true')
parser.add_argument("--inviteid", required=False, type=str)
parser.add_argument("--getgrouproles", required=False, type=str)
parser.add_argument("--getuser", required=False, type=str)
parser.add_argument("--getgroup", required=False, action='store_true')
parser.add_argument("--approle", required=False, action='store_true')
parser.add_argument("--memberof", required=False, action='store_true')
parser.add_argument("--groupsettings", required=False, action='store_true')
parser.add_argument("--getmemberobjects", required=False, type=str)
args = parser.parse_args()

proxy = args.proxy
login = args.login
refresh = args.refresh
bitlocker = args.bitlocker
computername = args.computername
domain = args.domain
checkbestprac = args.checkbestprac
me = args.me
checkme = args.checkme
objectid = args.objectid
owneddevices = args.owneddevices
dynamicgroups = args.dynamicgroups
invite = args.invite
email = args.email
dispname = args.dispname
inviteurl = args.inviteurl
invitedusers = args.invitedusers
invitedelete = args.invitedelete
inviteid = args.inviteid
getgrouproles = args.getgrouproles
getuser = args.getuser
getgroup = args.getgroup
approle = args.approle
memberof = args.memberof
groupsettings = args.groupsettings
getmemberobjects = args.getmemberobjects

if proxy:
    proxies = {
                  "http"  : "http://127.0.0.1:8080",
                  "https" : "http://127.0.0.1:8080"
                }
else:
    proxies = None

def _mslogin_devicecode():
    scope = "https://graph.microsoft.com"
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
    print("[+] Fetching AzureAD PRT token. Will be valid for 14d", "open https://microsoft.com/devicelogin and use code:",jsonResponse["user_code"],"\n")
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
        template = {'prt': '', 'https://graph.windows.net/.default': '', 'https://graph.microsoft.com/.default': ''}
        with open(".azrestarn_auth.json", "w") as outfile:
            json.dump(template, outfile)
    
    with open('.azrestarn_auth.json','r') as f:
        dic = json.load(f)
    
    tokens = {
        "prt": jsonResponse_code["refresh_token"]
    }
    with open(".azrestarn_auth.json", "w") as outfile:
        dic.update(tokens)
        json.dump(dic, outfile)

def _mslogin_refresh(domain,scope):
    if domain == None:
        print("[+] Please specify --domain parameter. Ex ecorp.com or ecorp.onmicrosoft.com")
        sys.exit(1)
    if os.path.exists(".azrestarn_auth.json"):
        with open('.azrestarn_auth.json','r') as f:
            dic = json.load(f)
        prt = dic["prt"]
        url = "https://login.microsoftonline.com/{}/oauth2/v2.0/token".format(domain)
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36", 
            "Accept": "*/*", 
            "Content-Type": "application/x-www-form-urlencoded", 
            "Connection": "close"
        }
        data = {
            "client_id": "1950a258-227b-4e31-a9cf-717495945fc2", 
            "grant_type": "refresh_token",
            "refresh_token": prt,
            "scope": scope
        }
        response = requests.post(url, headers=headers, data=data, proxies=proxies, verify=False)
        jsonResponse = response.json()

        with open('.azrestarn_auth.json','r') as f:
            dic = json.load(f)
        
        try:
            tokens = {
                scope: jsonResponse["access_token"]
            }
        except:
            print("[zError:\n", jsonResponse["error_description"])
            sys.exit(1)

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
        access_token = dic["https://graph.windows.net/.default"]
        url = "https://graph.windows.net/{}/devices?api-version=1.61-internal&$filter=startswith(displayName, '{}')".format(domain,computername) 
        headers= {"Authorization": "Bearer " + str(access_token)}
        response = requests.get(url=url, headers=headers, proxies=proxies, verify=False)
        print(json.dumps(response.json(), indent=4))

def _check_bestprac():
    if os.path.exists(".azrestarn_auth.json"):
        with open('.azrestarn_auth.json','r') as f:
            dic = json.load(f)
        access_token = dic["https://graph.microsoft.com/.default"]
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
        access_token = dic["https://graph.microsoft.com/.default"]
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
        access_token = dic["https://graph.microsoft.com/.default"]
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
        access_token = dic["https://graph.microsoft.com/.default"]
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
        access_token = dic["https://graph.microsoft.com/.default"]
        url = "https://graph.microsoft.com/v1.0/groups?$filter=groupTypes/any(s:s eq 'DynamicMembership')&$top=999"
        headers = {
            "Authorization": "Bearer " + str(access_token)
            }
        response = requests.get(url=url, headers=headers, proxies=proxies, verify=False)
        print(json.dumps(response.json(), indent=4))

def _inviteUser():
    if email == None:
        print("[+] Please specify --email parameter for the user you want to invite.")
        sys.exit(1)
    if dispname == None:
        print("[+] Please specify --dispname parameter for the user you want to invite.")
        sys.exit(1)
    if inviteurl == None:
        print("[+] Please specify --inviteurl parameter for the user you want to invite.")
        sys.exit(1)
    if os.path.exists(".azrestarn_auth.json"):
        with open('.azrestarn_auth.json','r') as f:
            dic = json.load(f)
        access_token = dic["https://graph.microsoft.com/.default"]
        url = "https://graph.microsoft.com/v1.0/invitations"
        headers = {
            "Authorization": "Bearer " + str(access_token),
            "Content-type": "application/json"
            }
        data = {
            "invitedUserDisplayName": dispname,
            "invitedUserEmailAddress": email,
            "sendInvitationMessage": "true",
            "invitedUserMessageInfo": {
                                    "ccRecipients": [ {"@odata.type": "microsoft.graph.recipient"} ],
                                    "customizedMessageBody": "Test",
                                    "messageLanguage": "en-US"
                                    },
            "inviteRedirectUrl": inviteurl,
            "inviteRedeemUrl": inviteurl,
            "invitedUserType": "Guest"
            }
        response = requests.post(url=url, headers=headers, json=data, proxies=proxies, verify=False)
        print(json.dumps(response.json(), indent=4))

def _invitedUsers():
    if os.path.exists(".azrestarn_auth.json"):
        with open('.azrestarn_auth.json','r') as f:
            dic = json.load(f)
        access_token = dic["https://graph.microsoft.com/.default"]
        url = "https://graph.microsoft.com/v1.0/users?$filter=externalUserState eq 'PendingAcceptance'"
        headers = {
            "Authorization": "Bearer " + str(access_token)
            }
        response = requests.get(url=url, headers=headers, proxies=proxies, verify=False)
        print(json.dumps(response.json(), indent=4))

def _inviteDelete(inviteid):
    if inviteid == None:
        print("[+] Please specify --inviteid for the invite to delete. Hint: --invitedusers.")
        sys.exit(1)
    if os.path.exists(".azrestarn_auth.json"):
        with open('.azrestarn_auth.json','r') as f:
            dic = json.load(f)
        access_token = dic["https://graph.microsoft.com/.default"]
        url = "https://graph.microsoft.com/v1.0/users/{}".format(inviteid)
        headers = {
            "Authorization": "Bearer " + str(access_token)
            }
        response = requests.delete(url=url, headers=headers, proxies=proxies, verify=False)
        print(json.dumps(response.json(), indent=4))

def _getGroupRoles(groupobjectid):
    if groupobjectid == None:
        print("[+] Please specify --groupobjectid")
        sys.exit(1)
    if os.path.exists(".azrestarn_auth.json"):
        with open('.azrestarn_auth.json','r') as f:
            dic = json.load(f)
        access_token = dic["https://graph.microsoft.com/.default"]
        url = "https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignments?$filter=principalId eq '{}'".format(groupobjectid)
        headers = {
            "Authorization": "Bearer " + str(access_token)
            }
        response = requests.get(url=url, headers=headers, proxies=proxies, verify=False)
        print(json.dumps(response.json(), indent=4))

def _getuser(objectid):
    if objectid == None:
        print("[+] Please specify --getuser -objectid-")
        sys.exit(1)
    if os.path.exists(".azrestarn_auth.json"):
        with open('.azrestarn_auth.json','r') as f:
            dic = json.load(f)
        access_token = dic["https://graph.microsoft.com/.default"]
        url = "https://graph.microsoft.com/v1.0/users/{}".format(objectid)
        headers = {
            "Authorization": "Bearer " + str(access_token)
            }
        response = requests.get(url=url, headers=headers, proxies=proxies, verify=False)
        print(json.dumps(response.json(), indent=4))

def _getgroup(objectid):
    if objectid:
        objectid = objectid
    else: objectid = ""
    if approle:
        prop = "/appRoleAssignments"
    elif memberof:
        prop = "/memberOf"
    else: prop = ""
    if os.path.exists(".azrestarn_auth.json"):
        with open('.azrestarn_auth.json','r') as f:
            dic = json.load(f)
        access_token = dic["https://graph.microsoft.com/.default"]
        url = "https://graph.microsoft.com/beta/groups/{}{}?$top=999".format(objectid,prop)
        headers = {
            "Authorization": "Bearer " + str(access_token),
            "ConsistencyLevel": "eventual"
            }
        response = requests.get(url=url, headers=headers, proxies=proxies, verify=False)
        print(json.dumps(response.json(), indent=4))

def _getmemberobjects(objectid):
    if os.path.exists(".azrestarn_auth.json"):
        with open('.azrestarn_auth.json','r') as f:
            dic = json.load(f)
        access_token = dic["https://graph.microsoft.com/.default"]
        url = "https://graph.microsoft.com/beta/groups/{}/getMemberObjects".format(objectid)
        headers = {
            "Authorization": "Bearer " + str(access_token),
            "Content-type": "application/json",
            "ConsistencyLevel": "eventual"
            }
        data = {
            "securityEnabledOnly": "true"
            }
        response = requests.post(url=url, headers=headers, json=data, proxies=proxies, verify=False)
        print(json.dumps(response.json(), indent=4))

def _groupsettings():
    if os.path.exists(".azrestarn_auth.json"):
        with open('.azrestarn_auth.json','r') as f:
            dic = json.load(f)
        access_token = dic["https://graph.microsoft.com/.default"]
        url = "https://graph.microsoft.com/v1.0/groupSettings"
        headers = {
            "Authorization": "Bearer " + str(access_token)
            }
        response = requests.get(url=url, headers=headers, proxies=proxies, verify=False)
        print(json.dumps(response.json(), indent=4))
    
if login:
    _mslogin_devicecode()
    _mslogin_refresh(domain,"https://graph.windows.net/.default")
    _mslogin_refresh(domain,"https://graph.microsoft.com/.default")
if refresh: 
    _mslogin_refresh(domain,"https://graph.windows.net/.default")
    _mslogin_refresh(domain,"https://graph.microsoft.com/.default")
if bitlocker: _find_bitlocker_key(domain,computername)
if checkbestprac: _check_bestprac()
if me: _checkMe()
if checkme: _checkMeGroups(objectid)
if owneddevices: _checkOwnedDevices()
if dynamicgroups: _checkDynamicGroups()
if invite: _inviteUser()
if invitedusers: _invitedUsers()
if invitedelete: _inviteDelete(inviteid)
if getgrouproles: _getGroupRoles(getgrouproles)
if getuser: _getuser(getuser)
if getgroup: _getgroup(objectid)
if getmemberobjects: _getmemberobjects(getmemberobjects)
if groupsettings: _groupsettings()

