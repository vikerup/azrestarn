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

This will generate an AzureAD refresh_token, Microsoft Graph API and Azure AD Graph API
JWT and store them in
`.azrestarn_auth.json`. Be mindful of these are authentications tokens and should be
protected.

AzureAD refresh_token is valid for 14d where JWT's only live for 1h. Use `python3 azrestarn.py --refresh` to obtain new JWT's.

All output from `azrestarn.py` is in JSON format and can simply be filtered with `jq`
as shown in examples.

### Examples

```
$ python3 azrestarn.py -h

usage: azrestarn.py [-h] [--proxy] [--login] [--refresh] [--bitlocker]
                    [--computername COMPUTERNAME] [--domain DOMAIN] [--checkbestprac] [--me]
                    [--checkme] [--objectid OBJECTID] [--owneddevices] [--dynamicgroups]
                    [--invite] [--email EMAIL] [--dispname DISPNAME] [--inviteurl INVITEURL]
                    [--invitedusers] [--invitedelete] [--inviteid INVITEID]
                    [--getgrouproles GETGROUPROLES] [--getuser GETUSER] [--getgroup]
                    [--approle] [--memberof] [--groupsettings]
                    [--getmemberobjects GETMEMBEROBJECTS]

azrestarn.py

options:
  -h, --help            show this help message and exit
  --proxy
  --login
  --refresh
  --bitlocker
  --computername COMPUTERNAME
  --domain DOMAIN
  --checkbestprac
  --me
  --checkme
  --objectid OBJECTID
  --owneddevices
  --dynamicgroups
  --invite
  --email EMAIL
  --dispname DISPNAME
  --inviteurl INVITEURL
  --invitedusers
  --invitedelete
  --inviteid INVITEID
  --getgrouproles GETGROUPROLES
  --getuser GETUSER
  --getgroup
  --approle
  --memberof
  --groupsettings
  --getmemberobjects GETMEMBEROBJECTS
```

Check authenticated user properties:

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

Check security settings for tenant:

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

Find all devices registered to the authenticated user:

```
$ python3 azrestarn.py --owneddevices | jq .value[].displayName
"Phone1"
"Phone2"
"Phone3"
"LAPTOP1"
```

Query if bitlocker key exists for specific device:

```
$ python3 azrestarn.py --bitlocker --computername LAPTOP1 --domain lössnus.tld | jq .value[].bitLockerKey

[...]
```

Find all groups that can be joined and check their permissions;

```
$ python3 azrestarn.py --domain domain.tld --getgroup | jq '.value[] | select(.visibility == "Public")' | jq .id -r > /tmp/publicgroups.txt

$ for i in $(cat ../publicgroups.txt); do python3 azrestarn.py --domain domain.tld --getgroup --objectid $i --approle; done

$ for i in $(cat ../publicgroups.txt); do python3 azrestarn.py --domain domain.tld --getmemberobjects $i; done
```

Check for dynamic groups:

```
$ python3 azrestarn.py --dynamicgroups | jq '.value[] | "\(.displayName), \(.membershipRule)"'

"Support, (user.userPrincipalName -startsWith \"support.\")"
```

Invite guest and gain support group permission:

```
$ python3 azrestarn.py --proxy --domain snus.tld --checkbestprac | jq .allowInvitesFrom

"adminsGuestInvitersAndAllMembers"

$ python3 azrestarn.py --domain snus.tld --proxy --invite --email support.snus@skurk.tld --dispname guestinvite-test --inviteurl https://example.tld

{
    "@odata.context":"https://graph.microsoft.com/v1.0/$metadata#invitations/$entity",
    "id":"f2a10860-[...REDACTED...]5a5ba8",
     [...]

$ python3 azrestarn.py --domain snus.tld --proxy --invitedusers

{
    "@odata.context":"https://graph.microsoft.com/v1.0/$metadata#users",
    "value":[{"businessPhones":[],
    "displayName":guestinvite-test",
    "givenName":null,
    "jobTitle":null,
     [...]
```

