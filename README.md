# RESTCONF examples for IOS-XE on Cisco Catalyst

This Python script allows you to communicate with a Cisco Catalyst switch through RESTCONF and Python.
RESTCONF is a new way to configure and automate network devices and supports XML and JSON.
This basic script is created to show the possibilities what you can do with RESTCONF without touching CLI by leveraging YANG models.
Available YANG models on Cisco IOS-XE can be found on following Git https://github.com/YangModels/yang/tree/master/vendor/cisco/xe.

## Getting Started

Constructing RESTCONF URIs:

```
https://<ADDRESS>/<ROOT>/<DATA STORE>/<[YANG MODULE:]CONTAINER>/<LEAF>[?<OPTION>]
```


For now, you can show/change the hostname and show/change/add VLAN's through a Python shell.

    This Python script leverages RESTCONF to:
        - Display the hostname of the network device
        - Update the hostname of a network device
        - Retrieve a list of interfaces configured with an IP address on a device
        - Updates the IP address on an interface
        - Retrieve a list of configured VLANs
        - Configure a new VLAN

    This script has been tested with Python 3.5, however may work with other versions.
    This script targets the RESTCONF that leverages a Catalyst 9300 as
    a target.


### Prerequisites

Requirements:

Python
* requests

IOS-XE
* enable RESTCONF
* enable HTTPS

```
switch(config)restconf
switch(config)ip http server
switch(config)ip http authentication local
switch(config)ip http secure-server
```

### Using the script

```
python3 IosXeRest.py

Please make sure the following requirements are met:

     - Only run this scrip with a Python 3 interpreter.
     - Make sure you have enabled the restconf interface on the switch.
     - Make sure HTTP(S) is enable on the switch.

The IPv4 address of the switch: <IP_ADDRESS>
The username: <USERNAME>
The password: <PASSWORD>

Press Enter to continue...

Choose between the followig possibilities:

 1. Show the hostname
 2. Change the hostname
 3. Get interface with configured IP address
 4. Configure an IP address on interface
 5. Get list of configured VLANs
 6. Configure a new VLAN
 7. Verify the output of a YANG container
  Make your choice:

```
