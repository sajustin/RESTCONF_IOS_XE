RESTCONF examples for IOS-XE on Cisco Catalyst

This Python script allows you to communicate with a Cisco Catalyst switch through RESTCONF and Python.
RESTCONF is a new way to configure and automate network devices and supports XML and JSON.
This basic script is created to show the possibilities what you can do with RESTCONF without touching CLI by leveraging YANG models.
Available YANG models on Cisco IOS-XE can be found on following Git https://github.com/YangModels/yang/tree/master/vendor/cisco/xe.

Constructing RESTCONF URIs:
   https://<ADDRESS>/<ROOT>/<DATA STORE>/<[YANG MODULE:]CONTAINER>/<LEAF>[?<OPTION>]
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

    Requirements:
        Python
            - requests
        IOS-XE
            - enable RESTCONF
            - enable HTTPS
