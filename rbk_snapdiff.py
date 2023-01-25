#!/usr/bin/python
from __future__ import print_function

import sys
import getopt
import getpass
import rubrik_cdm
import urllib3
urllib3.disable_warnings()

def usage():
    sys.stderr.write("Usage: rbk_snapdiff.py [-hD] [-t token] [-c creds] command rubrik netapp\n")
    sys.stderr.write("-h | --help : Prints usage\n")
    sys.stderr.write("-D | --DEBUG : Enables Debug mode\n")
    sys.stderr.write("-c | -- creds : Allows the Rubrik credentials to be put on the CLI [user:password\n")
    sys.stderr.write("-t | -- token : Specify a Rubrik API token on the CLI.  This is mandatory of MFA is enabled\n")
    sys.stderr.write("command : ['status', 'enable', 'disable']\n")
    sys.stderr.write("rubrik : Name/IP of Rubrik\n")
    sys.stderr.write("netapp : Name/IP of NetApp SVM (not cluster management)\n")
    exit(0)

def dprint(message):
    if DEBUG:
        print(message + "\n")

def python_input (message):
    if int(sys.version[0]) > 2:
        value = input(message)
    else:
        value = raw_input(message)
    return(value)


if __name__ == "__main__":
    DEBUG = False
    cmd = ""
    token = ""
    user = ""
    password = ""
    ntap_api_user = ""
    ntap_api_password = ""
    ntap = ""
    timeout = 360
    host_id = ""
    sd_status = False

    optlist, args = getopt.getopt(sys.argv[1:], 'hDt:c:', ['--help', '--DEBUG', '--token=', '--creds='])
    for opt, a in optlist:
        if opt in ['-h', '--help']:
            usage()
        if opt in ['-D', '--DEBUG']:
            DEBUG = True
        if opt in ['-t', '--token']:
            token = a
        if opt in ['-c', '--creds']:
            (user, password) = a.split(':')

    try:
        (cmd, rubrik_host, ntap) = args
    except:
        usage()
    if not token:
        if not user:
            user = python_input("Rubrik User: ")
        if not password:
            password = getpass.getpass("Rubrik Password: ")
        rubrik = rubrik_cdm.Connect(rubrik_host, user, password)
    else:
        rubrik = rubrik_cdm.Connect(rubrik_host, api_token=token)
    nas_host = rubrik.get('v1', '/host?name=' + ntap, timeout=timeout)
    if nas_host['data'][0]['nasBaseConfig']['vendorType'] != "NETAPP":
        sys.stderr.write(ntap + " is not an integrated NTAP array\n")
        exit(1)
    try:
        ntap_user = nas_host['data'][0]['nasBaseConfig']['apiUsername']
    except:
        ntap_user = python_input("NTAP API User: ")
    try:
        sd_status = nas_host['data'][0]['nasBaseConfig']['isNetAppSnapDiffEnabled']
    except:
        sd_status = False
    host_id = nas_host['data'][0]['id']
    if not ntap_user:
        ntap_user = python_input("NTAP API User: ")
    ntap_api_password = getpass.getpass("NTAP API Password [" + ntap_user + "]: ")
    if cmd.lower() == "status":
        if sd_status:
            print(ntap + " : enabled")
        else:
            print(ntap + " : disabled")
    elif cmd.lower() == "enable" or cmd.lower() == "disable":
        payload = {'hostname': ntap, 'nasConfig': {'vendorType': 'NETAPP', 'apiUsername': ntap_user, 'apiPassword': ntap_api_password}}
        if cmd.lower() == "enable":
            payload['nasConfig']['isNetAppSnapDiffEnabled'] = True
        else:
            payload['nasConfig']['isNetAppSnapDiffEnabled'] = False
        result = rubrik.patch('v1', '/host/' + host_id, config=payload, timeout=timeout)
        if result['nasBaseConfig']['isNetAppSnapDiffEnabled']:
            print(ntap + " : enabled")
        else:
            print(ntap + " : disabled")
    else:
        sys.stderr.write("Valid commands: ['status', 'enable', 'disable']")
        exit(2)






