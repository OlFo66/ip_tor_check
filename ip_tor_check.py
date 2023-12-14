import sys
import json
import requests
from setup import *

# Check if the relay list is up-to-date
# And if the version of the json schema changed.

def checkup():
    data = requests.head(url)

    if data.headers['last-modified'] == lastModified:
        print("TOR relay list up to date.")
        pass
    else:
        print("TOR relay list out to date")
        try:
            data = requests.get(url)
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

if __name__ == '__main__':
    checkup()
