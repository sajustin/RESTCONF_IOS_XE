#!/usr/bin/env python

# This Python script allows you to communicate with a Cisco Catalyst switch through RESTCONF and Python.
# RESTCONF is a new way to configure and automate network devices and supports XML and JSON.
# This basic script is created to show the possibilities what you can do with RESTCONF without touching CLI by leveraging YANG models.
# Available YANG models on Cisco IOS-XE can be found on following Git https://github.com/YangModels/yang/tree/master/vendor/cisco/xe.

# Constructing RESTCONF URIs:
#   https://<ADDRESS>/<ROOT>/<DATA STORE>/<[YANG MODULE:]CONTAINER>/<LEAF>[?<OPTION>]
# For now, you can show/change the hostname and show/change/add VLAN's through a Python shell.
"""
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

"""


try:
    import requests
except ImportError:
    raise AnsibleError("Python requests module is required for this plugin.")
import json
from requests.auth import HTTPBasicAuth
import urllib3
import pprint
import re
import traceback



# Suppressing warnings for non-secure connection
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class IosXeRest(object):

    # The three parameters required for making the connection to the switch
    def __init__(self):
        self.ip = ""
        self.username = ""
        self.password = ""

    # Create a connection to the switch
    def make_call(self, method, container, leaf="", payload=""):
        try:
            return requests.request(method, self.ip + container + leaf, auth = HTTPBasicAuth(self.username, self.password), headers = {
                'accept': "application/yang-data+json",
                'content-type': "application/yang-data+json",
            }, verify=False, data=payload)

        except requests.exceptions.Timeout: # If timeout occurs, print message
            print('0h-ooh, connection was not made, time out occured.')

        except requests.exceptions.ConnectionError: # If there is a connection error, print message
            print('Hmm, something went wrong.')
            #traceback.print_exc()

    def get_container_capabilities(self, container):
        return self.make_call('GET', container).json()

    # Return the hostname in JSON format
    def get_hostname(self):
        return self.make_call('GET', 'Cisco-IOS-XE-native:native/' ,'hostname').json()

    # Sets the hostname and returns True if switch response was OK
    def set_hostname(self, hostname):  # Change HOSTNAME JSON
        payload = json.dumps({"Cisco-IOS-XE-native:hostname": hostname})
        if self.make_call('PUT', 'Cisco-IOS-XE-native:native/' ,'hostname', payload).status_code == 204:
            return True

    # Return the interfaces in JSON format
    def get_interface(self):
        return self.make_call('GET', 'ietf-interfaces:interfaces').json()["ietf-interfaces:interfaces"]["interface"]

    # Print list of available interfaces
    def print_available_interfaces(self):
        interfaces = self.get_interface()
        print("The nentwork device has the following interfaces: \n")
        for interface in interfaces:
            print("  * {name:25}".format(name=interface["name"]))
        return interfaces

    # Return the interfaces state in JSON format
    def get_interface_state(self):
        return self.make_call('GET', 'ietf-interfaces:interfaces-state').json()

    # Return the interfaces statistics in JSON format
    def get_interface_statistics(self):
        return self.make_call('GET', 'ietf-interfaces:statistics').json()

    # Configures the interfaces with an IP address
    def configure_interface_ip(self, interface, ip):
        # build RESTCONF URI
        uri = "Cisco-IOS-XE-native:native/interface/{i}/ip/address/primary".format(i=interface)
        #print("\n the following RESTCONF URI will be used to configure the IP address on the requested interface : " + self.ip +uri + "\n")

        # build JSON payload
        payload = "{\"primary\": {\"address\": \""+str(ip["address"])+"\", \"mask\": \""+str(ip["mask"])+"\"}}"
        #print("\n the following payload will be sent: \n")
        #pprint.pprint(payload)

        call = self.make_call('PATCH', uri ,"", payload)
        #print("Network Device HTTP response: " +str(call))
        if call.status_code == 204:
            return True

    # Configures the interface's description
    def configure_interface_description(self,interface,description):
        uri = "Cisco-IOS-XE-native:native/interface/{i}/description".format(i=interface)
        #print("\n the following RESTCONF URI will be used to configure the description on the requested interface : " + self.ip +uri + "\n")
        payload = "{\"description\": \""+description+"\"}"
        #print("\n the following payload will be sent: \n")
        #pprint.pprint(payload)

        call = self.make_call('PATCH', uri ,"", payload)
        #print("Network Device HTTP response: " + str(call))
        if call.status_code == 204:
            return True

    # Return the list of configured VLANs in JSON format
    def get_vlan_list(self):
        uri = "Cisco-IOS-XE-native:native/vlan/Cisco-IOS-XE-vlan:vlan-list"
        return self.make_call('GET', uri).json()

    # Configures a new VLAN
    def configure_vlan(self,vlan):
        uri = "Cisco-IOS-XE-native:native/vlan/Cisco-IOS-XE-vlan:vlan-list"
        payload = "{\"Cisco-IOS-XE-vlan:vlan-list\": {\"id\": \""+str(vlan["id"])+"\", \"name\": \""+str(vlan["name"])+"\"}}"
        call = self.make_call('PATCH', uri ,"", payload)
        print(call)
        if call.status_code == 204:
            return True

# Separates class for user Inpout - separates switch logic
class GuiShell(IosXeRest):

    def user_credentials(self):
        while not self.ip:
            self.ip = input("The IPv4 address of the switch: ")
        self.ip = "https://" + self.ip + "/restconf/data/"
        while not self.username:
            self.username = input("The username: ")
        while not self.password:
            self.password = input("The password: ")
        return True


    def pretty_verify_container(self):
        contaier = input('Which container would you like to check? ')
        pprint.pprint(self.get_container_capabilities(contaier))


    # Get the hostname of the device
    def pretty_get_hostname(self):
        hostname = self.get_hostname()
        print("The current hostname of the device is '{h}'.".format(h=hostname['Cisco-IOS-XE-native:hostname']))

    # Change the hostname of the device
    def pretty_change_hostname(self):
        hostname = input('New hostname: ')
        if self.set_hostname(hostname) is True:
            print("Great, the new hostname is '{h}'.".format(h=hostname))

    # Print ip address of configured interfaces
    def pretty_get_interfaces(self):
        interfaces = self.get_interface()
        #interfaces_state = self.get_interface_state()['ietf-interfaces:interfaces-state']['interface']
        #pprint.pprint(interfaces)
        print("The following interfaces are configured with an IP address: \n")

        for item in interfaces:
            if item['ietf-ip:ipv4'] or item['ietf-ip:ipv6']:
                print("interface " + str(item['name']) + ": ")
                print("     description: " + str(item['description']))
                print("     IP address : " + str(item['ietf-ip:ipv4']['address'][0]['ip']) + "\n     Netmask : " + str(item['ietf-ip:ipv4']['address'][0]['netmask']))

    # Configures an interface
    def pretty_configure_interface(self):

        all_int = self.print_available_interfaces()

        # Ask User which interface to configure
        sel_int = input('Which Interface would you like to configure? ')

        # Validate interface input
        # Must be an interface on the device AND NOT be the Management Interface
        while not sel_int in [intf["name"] for intf in all_int]:
             print("INVALID:  Select an available interface.")
             print("          Choose another Interface")
             sel_int = input("Which Interface do you want to configure? ")

        # Convert to RESTCONF format
        int_type = re.search(r"([a-zA-Z]+)",sel_int).group(0)
        int_nb = re.search(r"(\d).*",sel_int).group(0)
        int_nb_format = int_nb.replace("/","%2F")
        interface_name = int_type +"="+int_nb_format

        description = input('Enter a description for this interface: ')
        ip = {}
        ip["address"] = input('What IP address do you want to set? ')
        ip["mask"] = input('What Subnet Mask do you want to set? ')

        self.configure_interface_ip(interface_name, ip)
        if (self.configure_interface_description(interface_name,description)):
            print('interface '+ sel_int + ' has successfully been configured with IPv4: '+ ip["address"]+ "\n")

    def pretty_get_vlan(self):

        vlan_list = self.get_vlan_list()['Cisco-IOS-XE-vlan:vlan-list']

        print("\n")
        for item in vlan_list:
            try:
                print("vlan: {id} with name : {n}".format(id=item['id'], n=item['name']))
            except:
                print("vlan: {id}".format(id=item['id']))
        print('\n')

    def pretty_configure_vlan(self):

        vlan = {}
        vlan["id"] = input('What is the VLAN id? ')
        vlan["name"] = input('What is the name of the VLAN? ')

        if self.configure_vlan(vlan):
            print("The VLAN {v} with name {n} has successfully been configured".format(v=vlan["id"], n=vlan["name"]))

    def pretty_configure_access_port(self):
        return True


    # Python Shell 'GUI'
    def menu(self):
        menu_items = " 1. Show the hostname \n 2. Change the hostname \n 3. Get interface with configured IP address \n 4. Configure an IP address on interface \n 5. Get list of configured VLANs \n 6. Configure a new VLAN \n 7. Verify the output of a YANG container \n  Make your choice: "
        while True:
            input("\nPress Enter to continue...\n")
            print("Choose between the followig possibilities:")
            try:
                choice = int(input('\n' + menu_items))

                if choice == 1:
                    self.pretty_get_hostname()
                if choice == 2:
                    self.pretty_change_hostname()
                if choice == 3:
                    self.pretty_get_interfaces()
                if choice == 4:
                    self.pretty_configure_interface()
                if choice == 5:
                    self.pretty_get_vlan()
                if choice == 6:
                    self.pretty_configure_vlan()
                if choice == 7:
                    self.pretty_verify_container()
                if choice == 8:
                    self.pretty_configure_access_port()


            except:
                print('Please provide a number please.')
                traceback.print_exc()
                continue

# initialisation

a = GuiShell()
print("\nWelcome, this script can be used to push some basic configurations on a Cisco switch running IOS-XE via RESTCONF. \n")
print("Please make sure the following requirements are met: \n")
print("     - Only run this scrip with a Python 3 interpreter.\n     - Make sure you have enabled the restconf interface on the switch.\n     - Make sure HTTP(S) is enable on the switch.\n")
if a.user_credentials() is True:
    a.menu()
