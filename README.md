# rbk_snapdiff
A project to enable/disable SnapDiff on a Rubrik Cluster via API

This is a quick script to turn on Rubrik's ability to use NetApp SnapDiff functionality via API.
Note:  This script used the Rubrik Python SDK.  This will need to be installed in order for it to work via pip:
<pre>
pip install rubrik-cdm
</pre>

<pre>
Usage: rbk_snapdiff.py [-hD] [-t token] [-c creds] command rubrik netapp
-h | --help : Prints usage
-D | --DEBUG : Enables Debug mode
-c | -- creds : Allows the Rubrik credentials to be put on the CLI [user:password
-t | -- token : Specify a Rubrik API token on the CLI.  This is mandatory of MFA is enabled
command : ['status, 'enable', 'disable']
rubrik : Name/IP of Rubrik
netapp : Name/IP of NetApp SVM (not cluster management)
</pre>
