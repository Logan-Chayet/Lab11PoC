import csv, yaml, ipaddress, subprocess
from netmiko import ConnectHandler

def getCommand(command):
    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout.strip()
    return output

def writeYaml(data, fileName):
    with open(fileName+".yaml", 'w',) as file:
        yaml.dump(data, file, sort_keys=False)

def createVarPlaybook():
    data = {'lab7Config': []}
    routers = ['R1','R2','R3']
    for i in routers:
        interfaceIPs = []
        OSPFIPs = []
        interfaceNames = []
        loopback = ""
        processID = ""
        with open('/var/lib/jenkins/workspace/Lab11PoC/ANSIBLE/config_requirements.csv', newline='') as file:
            csvreader = csv.DictReader(file)
            for row in csvreader:
                interface_name = row['Interface Name']
                hostname = row['\ufeffHostname']
                interface_type = row['Interface Type']
                IP = row['IP/Subnet']
                ospf_enabled = row['OSPF Enabled']
                ospf_process_id = row['OSPF Process ID']
                ipAddress = ipaddress.ip_interface(IP).ip
                fullNetwork = ipaddress.ip_interface(IP).network
                network = ipaddress.ip_network(fullNetwork).network_address
                mask = fullNetwork.netmask
                hostmask = fullNetwork.hostmask
                if hostname == i:
                    processID = ospf_process_id
                    if ospf_enabled == "Yes":
                        OSPFIPs.append(str(network)+" "+str(hostmask))
                    if interface_type != 'Loopback':
                        #print(ipAddress,network,mask)
                        interfaceNames.append(interface_name)
                        interfaceIPs.append(str(ipAddress)+" "+str(mask))
                    else:
                        loopback = str(ipAddress)+" "+str(mask)

            data['lab7Config'].append({
                'hostname': i,
                'loopbackName': "loopback 1",
                'loopbackIP': loopback,
                'interfaceName': interfaceNames,
                'interfaceIP': interfaceIPs,
                'processID': processID,
                'ospfNetwork': OSPFIPs,
                'ospfArea': "0",
                })
    writeYaml(data, '/var/lib/jenkins/workspace/Lab11PoC/ANSIBLE/roles/router/vars/main')

def getRouterIPs(routers):
    IPs = []
    for i in routers:
        with open('config_requirements.csv', newline='') as file:
            csvreader = csv.DictReader(file)
            for row in csvreader:
                if i == row['\ufeffHostname'] and row['Interface Type'] != 'Loopback' and row['Interface Name'] == '0/0':
                    IP = str(ipaddress.ip_interface(row['IP/Subnet']).ip) 
                    IPs.append(IP)
    return IPs

def sendConfigs():
    routers = ['R1','R2','R3']
    IPs = getRouterIPs(routers)

    for i in range(len(IPs)):
        device = {
            'device_type': 'cisco_ios',
            'host': IPs[i],
            'username': 'admin',
            'password': 'password',
        }
        with ConnectHandler(**device) as connection:
            with open("/var/lib/jenkins/workspace/Lab11PoC/ANSIBLE/CFGS/"+routers[i]+".txt", 'r') as file:
                config_commands = file.readlines()
            output = connection.send_config_set(config_commands)
            print(output)

createVarPlaybook()
getCommand(["ansible-playbook", "/var/lib/jenkins/workspace/Lab11PoC/ANSIBLE/site.yaml"])
sendConfigs()
