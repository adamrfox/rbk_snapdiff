#!/usr/bin/python
from __future__ import print_function

import sys
import getopt
import getpass
import requests
import base64
import json
import urllib3
urllib3.disable_warnings()

def usage():
    sys.stderr.write("Usage: rbk_snapdiff.py [-hDs] [-t token] [-c creds] command rubrik netapp\n")
    sys.stderr.write("-h | --help : Prints usage\n")
    sys.stderr.write("-D | --DEBUG : Enables Debug mode\n")
    sys.stderr.write("-s | --share : Shows share level status.  Note: Only used with the 'status' command\n")
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
    SHARES = False

    optlist, args = getopt.getopt(sys.argv[1:], 'hDst:c:', ['--help', '--DEBUG', '--shares', '--token=', '--creds='])
    for opt, a in optlist:
        if opt in ['-h', '--help']:
            usage()
        if opt in ['-D', '--DEBUG']:
            DEBUG = True
        if opt in ['-s', '--shares']:
            SHARES = True
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
        auth_s = user + ":" + password
        auth_headers = {'Authorization': 'Basic ' + base64.encodebytes(auth_s.encode()).decode().replace('\n','')}
    else:
        auth_headers = {'Authorization': 'Bearer ' + token, 'accept': 'application/json', 'Content-type': 'application/json'}
    dprint(str(auth_headers))
    nas_host_data = requests.get('https://'+ rubrik_host + '/api/v1/host?name=' + ntap, headers=auth_headers, verify=False, timeout=timeout)
    nas_host = json.loads(nas_host_data.content.decode('utf-8'))
    dprint(str(nas_host))
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
    dprint("host_id: " + host_id)
    if not ntap_user:
        ntap_user = python_input("NTAP API User: ")
    ntap_api_password = getpass.getpass("NTAP API Password [" + ntap_user + "]: ")
    if cmd.lower() == "status":
        if sd_status:
            print(ntap + " : enabled")
        else:
            print(ntap + " : disabled")
        if SHARES:
            print("---------------------------")
            done = False
            cur = ""
            while not done:
                if cur:
                    api_endpoint = '/host/share&cursor=' + cur
                else:
                    api_endpoint = '/host/share'
                sh_data = requests.get('https://' + rubrik_host + '/api/internal' + api_endpoint, headers=auth_headers, verify=False, timeout=timeout)
                sh = json.loads(sh_data.content.decode('utf-8'))
                for share in sh['data']:
                    if share['hostId'] != host_id:
                        continue
                    try:
                        share['hostShareParameters']['isNetAppSnapDiffEnabled']
                    except:
                        print(share['exportPoint'] + ' : disabled')
                        continue
                    if share['hostShareParameters']['isNetAppSnapDiffEnabled']:
                        print(share['exportPoint'] + " : enabled")
                    else:
                        print(share['exportPoint'] + " : disabled")
                if sh['hasMore']:
                    cur = sh['nextCursor']
                else:
                    done = True
    elif cmd.lower() == "enable" or cmd.lower() == "disable":
        payload = {"hostname": ntap, "nasConfig": {"vendorType": "NETAPP", "apiUsername": ntap_user, "apiPassword": ntap_api_password}}
        if cmd.lower() == "enable":
            payload['nasConfig']['isNetAppSnapDiffEnabled'] = True
        else:
            payload['nasConfig']['isNetAppSnapDiffEnabled'] = False
        payload = json.dumps(payload)
        dprint(str(payload))
        result_data = requests.patch('https://' + rubrik_host + '/api/v1/host/' + host_id, headers=auth_headers, data=payload, verify=False, timeout=timeout)
        dprint(str(result_data.content))
        result = json.loads(result_data.content.decode('utf-8'))
        if result['nasBaseConfig']['isNetAppSnapDiffEnabled']:
            print(ntap + " : enabled")
        else:
            print(ntap + " : disabled")
    else:
        sys.stderr.write("Valid commands: ['status', 'enable', 'disable']")
        exit(2)






