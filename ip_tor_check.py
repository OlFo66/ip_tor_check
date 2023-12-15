import sys
import json
import requests
from setup import *
import ipaddress

# Check if the relay list is up-to-date
# And if the version of the json schema changed.

def updateCheckup():
    data = requests.head(urlToday)

    if data.headers['last-modified'] == lastModified:
        print("TOR relay list up to date.")
        pass
    else:
        print("TOR relay list out to date")
        try:
            data = requests.get(urlToday)
            torInfo = data.json()

            with open('torRelayList', "w") as file:
                file.write(json.dumps(torInfo))

            with open("setup.py", "rt") as file:
                x=file.read()

            with open("setup.py", "wt") as file:
                x = x.replace(lastModified,data.headers['last-modified'])
                file.write(x)
            print("TOR relay list updated")

            if torInfo['version'] != str(torVersion):
                print("/!\ Script written for TOR relay json version %s." % torVersion)
                print("Current version: %s" % torInfo['version'])
                print("PLease make sur everything is OK & modify the torVersion variable in conf file.")

        except:
            print("Issue while trying to download tor relay list.")
            sys.exit(1)

def checkProvidedIp(address):
    try:
        ipaddress.ip_address(address)
        pass
    except:
        print("%s not a valid IP" % address)
        sys.exit(2)

def checkIPToday(ipaddress,relayList):
    for i in range(len(relayList['relays'])):
        for Ip in relayList['relays'][i]['or_addresses']:
            if re.search(ipaddress, Ip.rsplit(':',1)[0]):
                print("* %s found as TOR relay with port %s and flags: %s" %(Ip.rsplit(':',1)[0], Ip.rsplit(':',1)[1], relayList['relays'][i]['flags']))
            else:
                pass

def checkIPInPast(ipaddress,date):
    pass

if __name__ == '__main__':
    updateCheckup()

    with open('torRelayList', "r") as file:
        valuesInFile = file.read()
        file.close()
        relayList = json.loads(valuesInFile)

    ipToCheck = ['2001:1600:10:100::201', '104.53.221.159', '10.10.10.10', ['azs','azs2']]
    for ip in ipToCheck:
        if type(ip) == str:
            checkProvidedIp(ip)
            checkIPToday(ip, relayList)
        elif type(ip) == list and len(ip) == 2:
            checkProvidedIp(ip[0])
            checkIPInPast(ip[0], ip[1])
        else:
            print("Provide <IP> or <IP>,<YYYY-MM-DD>")
    pass