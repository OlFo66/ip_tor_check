import sys
import os
import json
import requests
import ipaddress
import re
from datetime import date
import tarfile
import configparser

def updateCheckup(urlToday, torRelayList):

    data = requests.head(urlToday)

    if data.headers['x-backend'] in torRelayList and data.headers['last-modified'] == torRelayList[data.headers['x-backend']]:
        print("TOR relay list is up-to-date.")
        return(False, False)
    elif data.headers['x-backend'] not in torRelayList or data.headers['last-modified'] != torRelayList[data.headers['x-backend']]:
        xBackend, lastModified = data.headers['x-backend'], data.headers['last-modified']
        #print("0: %s - %s" % (xBackend, lastModified))
        try:
            data = requests.get(urlToday)
            torInfo = data.json()
            with open('torRelayJson', "w") as file:
                file.write(json.dumps(torInfo))
                file.close()
            return(str(xBackend), str(lastModified))
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
                    print("* %s found as TOR relay during: %s, search in archive to find flags." % (ipaddress, providedDate))
                    break
                else:
                    pass
    else:
        checkIPToday(ipaddress, relayList)
def checkArchivePath(providedDate, pathToCheck):
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

    config = configparser.ConfigParser()
    config.read('setup.ini')
    urlToday = config['TOR_URL']['urltoday']
    torRelayList = config['TOR_RELAY_LIST']
    archiveFolder = config['ARCHIVE']['archiveFolder']

    xBackend, lastModified = updateCheckup(urlToday, torRelayList)

    if xBackend and lastModified:
        if xBackend in torRelayList:
            print("Updating last-modified of %s with: %s" % (xBackend, lastModified))
            config.remove_option('TOR_RELAY_LIST', xBackend)
            config.set('TOR_RELAY_LIST', xBackend, lastModified)
        else:
            print("%s not found in list" % xBackend)
            config.set('TOR_RELAY_LIST', xBackend, lastModified)
        with open('setup.ini', 'wt') as configFile:
            config.write(configFile)
            configFile.close()

    with open('torRelayJson', "r") as file:
        valuesInFile = file.read()
        file.close()
        relayList = json.loads(valuesInFile)

        if str(relayList['version']) != str(config['CHECKUP']['torversion']):
            print("/!\ Script written for TOR relay json version %s." % config['CHECKUP']['torversion'])
            print("Current version: %s" % relayList['version'])
            print("PLease make sur everything is OK & modify the torVersion variable in conf file.")

    ipList = ['2001:1600:10:100::201', '104.53.221.159', ['86.59.21.38','2023-09-17'], '10.10.10.10']
    for ip in ipList:
        if type(ip) == str:
            checkIPFormat(ip)
            checkIPToday(ip, relayList)
            pass
        elif type(ip) == list and len(ip) == 2:
            checkIPFormat(ip[0])
            checkDateFormat(ip[1])
            checkArchivePath(ip[1], archiveFolder)
            checkIPInPast(ip[0], ip[1])
        else:
            print("Provide <IP> or <IP>,<YYYY-MM-DD>")
    pass