[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/datetime)
[![License](https://img.shields.io/badge/License-Beerware-yellow)](https://fedoraproject.org/wiki/Licensing/Beerware)

<img src="https://styleguide.torproject.org/static/images/tor-logo/color.svg" data-canonical-src="https://styleguide.torproject.org/static/images/tor-logo/color.svg" width="600" height="100" />

# IP TOR CHECK
## Why?
The purpose of this script is to identify if an IP that you find in your logs is/was used as TOR proxy.
## How ?
The TOR project freely provides the list of current and passed relays composing the TOR network.<br>

To use this script, you just have to modify [ARCHIVE] & [PROXY] sections in setup.ini if needed.<br>
Then you must set the list you will provide to the script.<br>
The list should be set like this:<br>
* `<IP>`  : search `IP` in today's list of relays.
* `[<IP>,<YYYY-MM-DD>]` : search `IP` in consensus list during day `YYYY-MM-DD`.

i.e:<br>
```
'10.10.10.10','125.25.32.1',['10.25.36.45','2023-02-02'],['2001:1600:10:100::201','2023-12-15']
```
Then you can import the script & launch it using `search()` function:
```
>>> import ip_tor_check
>>> ipList=['10.10.10.10','125.25.32.1',['10.25.36.45','2023-02-02'],['2001:1600:10:100::201','2023-12-15']]

>>> jsonFile = ip_tor_check.search('-j', ipList)
>>> ip_tor_check.search('-p', ipList)
>>> ip_tor_check.search(ipList)
```
* -j option will return the result in json format
* -p option will print the result in the console (by default)
* providing only the list is equivalent to -p option

## What ?
If an IP was found as TOR relay, flags are important to understand how you are concerned.<br>
* Guard: means someone from your network tries to connect to TOR network.
* Exit:  means someone tries to reach your network from TOR network.
* none:  means, somehow, someone from your network uses his asset as TOR relay.

## Blind Spot
To circumvent censorship, TOR project also provides what is called BRIDGE relays.<br>
The bridge addresses are not public.<br>
In this case, this script can't help, sorry... :confused:

## License
```
/*
 * ----------------------------------------------------------------------------
 * "THE BEER-WARE LICENSE" (Revision 42):
 * I wrote this file.  As long as you retain this notice you
 * can do whatever you want with this stuff. If we meet some day, and you think
 * this stuff is worth it, you can buy me a beer in return.   Olivier FONT
 * ----------------------------------------------------------------------------
 */
```