import sys
import os
import json
import requests
import ipaddress
import re
from datetime import date
import tarfile
import configparser
import warnings
warnings.filterwarnings("ignore")
def updateCheckup(urlToday, torRelayList):

    data = requests.head(urlToday)

    if data.headers['x-backend'] in torRelayList and data.headers['last-modified'] == torRelayList[data.headers['x-backend']]:
        print("TOR relay list is up-to-date.")
        return(False, False)
    elif data.headers['x-backend'] not in torRelayList or data.headers['last-modified'] != torRelayList[data.headers['x-backend']]:
        xBackend, lastModified = data.headers['x-backend'], data.headers['last-modified']
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
def checkIPToday(ipaddress,option):
    for i in range(len(relayList['relays'])):
        for Ip in relayList['relays'][i]['or_addresses']:
            if re.search(ipaddress, Ip.rsplit(':',1)[0]) and option == '-p':
                print("* %s found as TOR relay with port %s and flags: %s" %(Ip.rsplit(':',1)[0], Ip.rsplit(':',1)[1], relayList['relays'][i]['flags']))
                return (False, False, False)
            elif re.search(ipaddress, Ip.rsplit(':',1)[0]) and option == '-j':
                return (True, Ip.rsplit(':', 1)[1], relayList['relays'][i]['flags'])
            elif option == '-p':
                print("* %s not found as TOR relay." % ipaddress)
                return (False, False, False)
            else:
                return (False, False, False)
def checkIPInPast(ipaddress,providedDate,option,archiveFolder):
    if str(providedDate) != str(date.today()):
        dateArchive = providedDate.split(sep="-", maxsplit=2)
        archivePath = archiveFolder+"consensuses-"+dateArchive[0]+"-"+dateArchive[1]+"/"+dateArchive[2]
        found = 0
        for file in os.listdir(archivePath):
            with open(archivePath+"/"+file, 'r') as f:
                info = f.read()
                if re.search(ipaddress, info) and option == '-p':
                    print("* %s found as TOR relay during: %s, search in archive to find flags." % (ipaddress, providedDate))
                    return (False, False, False)
                    break
                elif re.search(ipaddress, info) and option == '-j':
                    return(True, ipaddress, False)
                elif option == '-p':
                    pass
                else:
                    return (False, False, False)
        if found == 0:
            print("* %s not found as TOR relay during %s." % (ipaddress, providedDate))
    else:
        isFound, portFound, flagsFound = checkIPToday(ipaddress, option)
def checkArchivePath(providedDate, pathToCheck, urlInPast, archiveFolder):
    dateArchive = providedDate.split(sep="-", maxsplit=2)
    archivePath=pathToCheck+"consensuses-"+dateArchive[0]+"-"+dateArchive[1]+"/"+dateArchive[2]

    if os.path.isdir(archivePath):
        pass
    else:
        print("Folder %s doesn't exist" % archivePath)
        print("Creating...")
        try:
            dateArchive = providedDate.split(sep="-", maxsplit=2)
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
def jsonCreation(jsonData, ip='', portFound='', flagsFound=''):
    jsonData['count'] += 1
    relayInfo = {'ip': ip,
                 'port': portFound,
                 'flags': flagsFound
                }
    jsonData['relays'].append(relayInfo)

    return(jsonData)
def search(*args):

    if (len(args) == 0 or len(args) >2) or (len(args) == 1 and list != type(args[0])) or (len(args) == 2 and ((args[0] != '-j') and args[0] != '-p' and type(args[0]) != list)):
        print("Please provide 2 arguments max:")
        print("* option : ")
        print("  * -p: to print the result on screen.")
        print("  * -j: to get the result in json format.")
        print("(Not mandatory, -p is set by default)")
        print("* a python list with <IP> or list with <IP>,<YYYY-MM-DD>")
        print("")
        print("i.e: listIP=['10.10.10.10','125.25.32.1',['10.25.36.45','2023-02-02'],['2001:1600:10:100::201','2023-12-15']")
        print("     script.launch('-j', listIP)")
        print("     script.launch('-p', listIP)")
        print("     script.launch(listIP)")
        sys.exit(0)
    else:
        if type(args[0]) == list:
            option='-p'
        elif args[0] == '-p':
            option='-p'
        else:
            option='-j'

        count = 0
        ipList = []
        if len(args) == 1:
            j = 0
        else:
            j = 1

        for i in range(j,len(args)):
            for value in args[i]:
                if "," in value:
                    array=value.split(',')
                    ipList.append([value[0],value[1]])
                else:
                    ipList.append(value)

        config = configparser.ConfigParser()
        config.read('setup.ini')
        urlToday = config['TOR_URL']['urltoday']
        torRelayList = config['TOR_RELAY_LIST']
        archiveFolder = config['ARCHIVE']['archiveFolder']
        urlInPast = config['TOR_URL']['urlinpast']

        xBackend, lastModified = updateCheckup(urlToday, torRelayList)

        if xBackend and lastModified:
            if xBackend in torRelayList:
                config.remove_option('TOR_RELAY_LIST', xBackend)
                config.set('TOR_RELAY_LIST', xBackend, lastModified)
            else:
                config.set('TOR_RELAY_LIST', xBackend, lastModified)
            with open('setup.ini', 'wt') as configFile:
                config.write(configFile)
                configFile.close()
                print("TOR relay list updated")

        with open('torRelayJson', "r") as file:
            valuesInFile = file.read()
            file.close()
            global relayList
            relayList = json.loads(valuesInFile)



            if str(relayList['version']) != str(config['CHECKUP']['torversion']):
                print("/!\ Script written for TOR relay json version %s." % config['CHECKUP']['torversion'])
                print("Current version: %s" % relayList['version'])
                print("PLease make sur everything is OK & modify the torVersion variable in conf file.")

        jsonData = {
            'count':0,
            'relays': []
        }
        for ip in ipList:
            if type(ip) == str:
                checkIPFormat(ip)
                isFound, portFound, flagsFound = checkIPToday(ip, option)
                if isFound:
                    jsonData = jsonCreation(jsonData, ip, portFound,flagsFound)
                pass
            elif type(ip) == list and len(ip) == 2:
                checkIPFormat(ip[0])
                checkDateFormat(ip[1])
                checkArchivePath(ip[1], archiveFolder, urlInPast, archiveFolder)
                isFound = checkIPInPast(ip[0], ip[1], option, archiveFolder)#, torRelayList)
                if isFound:
                    jsonData = jsonCreation(jsonData, ip[0], portFound=False,flagsFound=False)
            else:
                print("Provide <IP> or <IP>,<YYYY-MM-DD>")
                pass
    if option == '-j':
        return(json.dumps(jsonData))

    return True