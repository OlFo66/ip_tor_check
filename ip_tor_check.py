import sys
import os
import json
import requests
from setup import *
import ipaddress
import re
from datetime import date
import tarfile

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
def checkIPFormat(address):
    try:
        ipaddress.ip_address(address)
        pass
    except:
        print("%s not a valid IP" % address)
        sys.exit(2)
def checkDateFormat(providedDate):
    try:
        date.fromisoformat(providedDate)
    except:
        print("Error: %s is not a valid date." % providedDate)
        sys.exit(3)
    pass
def checkIPToday(ipaddress,relayList):
    for i in range(len(relayList['relays'])):
        for Ip in relayList['relays'][i]['or_addresses']:
            if re.search(ipaddress, Ip.rsplit(':',1)[0]):
                print("* %s found as TOR relay with port %s and flags: %s" %(Ip.rsplit(':',1)[0], Ip.rsplit(':',1)[1], relayList['relays'][i]['flags']))
            else:
                pass
def checkIPInPast(ipaddress,providedDate):
    if str(providedDate) != str(date.today()):
        dateArchive = providedDate.split(sep="-", maxsplit=2)
        archivePath = archiveFolder+"consensuses-"+dateArchive[0]+"-"+dateArchive[1]+"/"+dateArchive[2]

        for file in os.listdir(archivePath):
            with open(archivePath+"/"+file, 'r') as f:
                info = f.read()
                if re.search(ipaddress, info):
                    print("* %s found as TOR relay during: %s" % (ipaddress, providedDate))
                    break
                else:
                    pass
    else:
        checkIPToday(ipaddress, relayList)
def checkArchivePath(providedDate, pathToCheck=archiveFolder):
    dateArchive = providedDate.split(sep="-", maxsplit=2)
    archivePath=pathToCheck+"consensuses-"+dateArchive[0]+"-"+dateArchive[1]+"/"+dateArchive[2]

    if os.path.isdir(archivePath):
        pass
    else:
        print("Folder %s doesn't exist" % archivePath)
        try:
            #dateArchive = providedDate.split(sep="-", maxsplit=2)
            urlZip = urlInPast+"consensuses-"+dateArchive[0]+"-"+dateArchive[1]+".tar.xz"
            localZipFile = archiveFolder+"/"+dateArchive[0]+"-"+dateArchive[1]+".tar.xz"
            archiveData = requests.get(urlZip)
            if archiveData.status_code == 200:
                with open(localZipFile, 'wb') as localZip:
                    for chunk in archiveData:
                        localZip.write(chunk)
                    localZip.close()
                localFolders = tarfile.open(localZipFile, 'r:xz')
                localFolders.extractall(path=archiveFolder)
                localFolders.close()
                os.remove(localZipFile)
        except:
            print("Error while downloading or uncompressing archive.")

if __name__ == '__main__':
    updateCheckup()
    with open('torRelayList', "r") as file:
        valuesInFile = file.read()
        file.close()
        relayList = json.loads(valuesInFile)

    ipToCheck = ['2001:1600:10:100::201', ['86.59.21.38','2023-10-17'], '104.53.221.159', '10.10.10.10']
    for ip in ipToCheck:
        if type(ip) == str:
            checkIPFormat(ip)
            checkIPToday(ip, relayList)
            pass
        elif type(ip) == list and len(ip) == 2:
            checkIPFormat(ip[0])
            checkDateFormat(ip[1])
            checkArchivePath(ip[1])
            checkIPInPast(ip[0], ip[1])
        else:
            print("Provide <IP> or <IP>,<YYYY-MM-DD>")
    pass