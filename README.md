# azrestarn

## Gettings started

`azrestarn.py` is a tool designed to help find insecure configurations or best practice
deviations in Azure environemnts.

To authenticate run `python3 azrestarn.py --login`

```
$ python3 azrestarn.py --login
[+] Scope: https://graph.windows.net open https://microsoft.com/devicelogin and use code: CJCCQV3DV

[+] Press any key when authentication is complete...

[+] Scope: https://graph.microsoft.com open https://microsoft.com/devicelogin and use code: DB3U832Q4

[+] Press any key when authentication is complete...
```

This will generate Microsoft Graph API and Azure AD Graph API jwt's and store them in
`.azrestarn_auth.json`. Be mindful of these are authentications tokens and should be
protected.

All output from `azrestarn.py` is in JSON format and can simply be filtered with `jq`
as shown in examples.

### Examples

```
$ python3 azrestarn.py -h
usage: azrestarn.py [-h] [--proxy] [--login] [--bitlocker] [--computername COMPUTERNAME]
                    [--domain DOMAIN] [--checkbestprac] [--me] [--checkme]
                    [--objectid OBJECTID] [--owneddevices] [--dynamicgroups]

azrestarn.py

options:
  -h, --help            show this help message and exit
  --proxy
  --login
  --bitlocker
  --computername COMPUTERNAME
  --domain DOMAIN
  --checkbestprac
  --me
  --checkme
  --objectid OBJECTID
  --owneddevices
  --dynamicgroups
```

```
$ python3 azrestarn.py --me
{
    "@odata.context": "https://graph.microsoft.com/beta/$metadata#users/$entity",
    "id": "asdfasdf-1234-1234-1234-asdfasdf",
    "deletedDateTime": null,
    "accountEnabled": true,
    "ageGroup": null,
    "businessPhones": [],
    "city": "Stockholm",
[...]
```

```
$ python3 azrestarn.py --checkbestprac 
{
  "@odata.context": "https://graph.microsoft.com/beta/$metadata#policies/authorizationPolicy/$entity",
  "id": "authorizationPolicy",
  "allowInvitesFrom": "adminsAndGuestInviters",
  "allowedToSignUpEmailBasedSubscriptions": false,
  "allowedToUseSSPR": true,
  "allowEmailVerifiedUsersToJoinOrganization": false,
  "allowUserConsentForRiskyApps": false,
  "blockMsolPowerShell": false,
  "description": "Used to manage authorization related settings across the company.",
  "displayName": "Authorization Policy",
  "enabledPreviewFeatures": [],
  "guestUserRoleId": "2af84b1e-32c8-42b7-82bc-daa82404023b",
  "permissionGrantPolicyIdsAssignedToDefaultUserRole": [
    "ManagePermissionGrantsForSelf.microsoft-user-default-low"
  ],
  "defaultUserRolePermissions": {
    "allowedToCreateApps": false,
    "allowedToCreateSecurityGroups": true,
    "allowedToCreateTenants": true,
    "allowedToReadBitlockerKeysForOwnedDevice": true,
    "allowedToReadOtherUsers": true
  }
}
```

```
$ python3 azrestarn.py --owneddevices | jq .value[].displayName
"Phone1"
"Phone2"
"Phone3"
"LAPTOP1"
```

```
$ python3 azrestarn.py --bitlocker --computername LAPTOP1 --domain lössnus.tld | jq .value[].bitLockerKey

[...]
```


