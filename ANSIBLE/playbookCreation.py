import csv, yaml, ipaddress, subprocess
from netmiko import ConnectHandler

def getCommand(command):
    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout.strip()
    return output

def writeYaml(data, fileName):
    with open(fileName+".yaml", 'w',) as file:
        yaml.dump(data, file, sort_keys=False)

#To determine which playbook to run when .csv comes in.
def determineDevice():
    with open('/var/lib/jenkins/workspace/Lab11PoC/ANSIBLE/config_requirements.csv', newline='') as file:
        csvreader = csv.DictReader(file)
        for row in csvreader:
            name = row['\ufeffHostname']
            extracted_word = name.split('-')[0]
            if extracted_word == "EDGE":
                return "edge"
            elif extracted_word == "SERVER":
                return "server"
            elif extracted_word == "CORE":
                return "core"
#To determine the router array list variable for the createVarPlaybook 
def uniqueHostnames():
    unique = set()
    unique_list = []
    with open('/var/lib/jenkins/workspace/Lab11PoC/ANSIBLE/config_requirements.csv', newline='') as file:
        csvreader = csv.DictReader(file)
        for row in csvreader:
            hostname = row['\ufeffHostname']
            if hostname not in unique:
                unique.add(hostname)
                unique_list.append(hostname)
    return unique_list

def createVarPlaybookEDGE():
    data = {'edgeConfig': []}
    routers = uniqueHostnames()
    for i in routers:
        interfaceIPs = []
        OSPFIPs = []
        interfaceNames = []
        processID = ""
        IPv6_ip = []
        ipv4_neighbor = ""
        ipv6_neighbor = ""
        remote_as = ""
        local_as = ""
        IPv4_network = ""
        IPv4_mask = ""
        IPv6_network = ""
        ospfv3 = []
        with open('/var/lib/jenkins/workspace/Lab11PoC/ANSIBLE/config_requirements.csv', newline='') as file:
            csvreader = csv.DictReader(file)
            for row in csvreader:
                interface_name = row['Interface Name']
                hostname = row['Hostname']
                interface_type = row['Interface Type']
                IP = row['IPv4/Subnet']
                ospf_enabled = row['OSPFv1 Enabled']
                ospf_process_id = row['OSPF Process ID']
                IPv6 = row['IPv6/Subnet']
                ospfv3_enabled = row['OSPFv3 Enabled']
                bgpv4_enabled = row['BGPv4 Enabled']
                bgpv6_enabled = row['BGPv6 Enabled']
                redistribution_v4 = row['Redistribution v4']
                redistribution_v6 = row['Redistribution v6']
                ipAddress = ipaddress.ip_interface(IP).ip
                fullNetwork = ipaddress.ip_interface(IP).network
                network = ipaddress.ip_network(fullNetwork).network_address
                if IPv6 != "autoconfig":    
                    ipAddressv6 = ipaddress.ip_interface(IPv6).ip
                    fullNetworkv6 = ipaddress.ip_interface(IPv6).network
                mask = fullNetwork.netmask
                hostmask = fullNetwork.hostmask
                if hostname == i:
                    processID = ospf_process_id
                    if ospf_enabled == "yes":
                        OSPFIPs.append(str(network)+" "+str(hostmask))
                    if interface_type == 'FastEthernet':
                        interfaceNames.append(interface_name)
                        interfaceIPs.append(str(ipAddress)+" "+str(mask))
                        IPv6_ip.append(IPv6)
                    if ospfv3_enabled == "yes":
                        ospfv3.append("ipv6 ospf "+ospf_process_id+" area "+row['OSPF Area']+"\n "+"ipv6 enable")
                    else:
                        if row['Hostname'] == "EDGE-BOULDER":
                            ospfv3.append("ipv6 enable")
                        else:
                            ospfv3.append(" ")
                    if bgpv4_enabled == "yes":
                        ipv4_neighbor = row['IPv4 Neighbor']
                    if bgpv6_enabled == "yes":
                        ipv6_neighbor = row['IPv6 Neighbor']
                    if bgpv4_enabled == "yes" or bgpv6_enabled == "yes":
                        remote_as = row['remote AS']
                        local_as = row['local AS']
                    if redistribution_v4 == "yes":
                        IPv4_network = network
                        IPv4_mask = mask
                    if redistribution_v6 == "yes":
                        IPv6_network = str(fullNetworkv6)


            data['edgeConfig'].append({
                'hostname': i,
                'interfaceName': interfaceNames,
                'interfaceIP': interfaceIPs,
                'processID': processID,
                'ospfNetwork': OSPFIPs,
                'ospfArea': row['OSPF Area'],
                'ipv6': IPv6_ip,
                'IPv4Neighbor': ipv4_neighbor,
                'IPv6Neighbor': ipv6_neighbor,
                'remote_AS': remote_as,
                'local_AS': local_as,
                'IPv4Network': str(IPv4_network),
                'IPv4Mask': str(IPv4_mask),
                'IPv6Network': str(IPv6_network),
                'ospfv3': ospfv3
                })
    writeYaml(data, '/var/lib/jenkins/workspace/Lab11PoC/ANSIBLE/roles/edge/vars/main')

def createVarPlaybookCORE():
    data = {'coreConfig': []}
    routers = uniqueHostnames()
    for i in routers:
        interfaceIPs = []
        OSPFIPs = []
        interfaceNames = []
        processID = ""
        IPv6_ip = []
        IPv4_network = ""
        IPv4_mask = ""
        IPv6_network = ""
        ospfv3 = []
        with open('/var/lib/jenkins/workspace/Lab11PoC/ANSIBLE/config_requirements', newline='') as file:
            csvreader = csv.DictReader(file)
            for row in csvreader:
                interface_name = row['Interface Name']
                hostname = row['Hostname']
                interface_type = row['Interface Type']
                IP = row['IPv4/Subnet']
                ospf_enabled = row['OSPFv1 Enabled']
                ospf_process_id = row['OSPF Process ID']
                IPv6 = row['IPv6/Subnet']
                ospfv3_enabled = row['OSPFv3 Enabled']
                ipAddress = ipaddress.ip_interface(IP).ip
                fullNetwork = ipaddress.ip_interface(IP).network
                network = ipaddress.ip_network(fullNetwork).network_address
                mask = fullNetwork.netmask
                hostmask = fullNetwork.hostmask
                if hostname == i:
                    processID = ospf_process_id
                    if ospf_enabled == "yes":
                        OSPFIPs.append(str(network)+" "+str(hostmask))
                    if interface_type == 'FastEthernet':
                        interfaceNames.append(interface_name)
                        interfaceIPs.append(str(ipAddress)+" "+str(mask))
                        IPv6_ip.append(IPv6)
                    if ospfv3_enabled == "yes":
                        ospfv3.append("ipv6 ospf "+ospf_process_id+" area "+row['OSPF Area'])
            data['coreConfig'].append({
                'hostname': i,
                'interfaceName': interfaceNames,
                'interfaceIP': interfaceIPs,
                'processID': processID,
                'ospfNetwork': OSPFIPs,
                'ospfArea': row['OSPF Area'],
                'ipv6': IPv6_ip,
                'ospfv3': ospfv3
                })
    writeYaml(data, '/var/lib/jenkins/workspace/Lab11PoC/ANSIBLE/roles/core/vars/main')

def createVarPlaybookSERVER():
    data = {'serverConfig': []}
    routers = uniqueHostnames() 
    for i in routers:
        interfaceIPs = []
        OSPFIPs = []
        interfaceNames = []
        processID = ""
        IPv6_ip = []
        IPv4_network = ""
        IPv4_mask = ""
        IPv6_network = ""
        ospfv3 = []
        description = []
        with open('/var/lib/jenkins/workspace/Lab11PoC/ANSIBLE/config_requirements', newline='') as file:
            csvreader = csv.DictReader(file)
            for row in csvreader:
                interface_name = row['Interface Name']
                hostname = row['Hostname']
                interface_type = row['Interface Type']
                IP = row['IPv4/Subnet']
                ospf_enabled = row['OSPFv1 Enabled']
                ospf_process_id = row['OSPF Process ID']
                IPv6 = row['IPv6/Subnet']
                ospfv3_enabled = row['OSPFv3 Enabled']
                descrip = row['Description']
                ipAddress = ipaddress.ip_interface(IP).ip
                fullNetwork = ipaddress.ip_interface(IP).network
                network = ipaddress.ip_network(fullNetwork).network_address
                mask = fullNetwork.netmask
                hostmask = fullNetwork.hostmask
                if hostname == i:
                    processID = ospf_process_id
                    description.append(descrip)
                    if ospf_enabled == "yes":
                        OSPFIPs.append(str(network)+" "+str(hostmask))
                    if interface_type == 'FastEthernet':
                        interfaceNames.append(interface_name)
                        interfaceIPs.append(str(ipAddress)+" "+str(mask))
                        IPv6_ip.append(IPv6)
                    if ospfv3_enabled == "yes":
                        ospfv3.append("ipv6 ospf "+ospf_process_id+" area "+row['OSPF Area'])
            data['serverConfig'].append({
                'hostname': i,
                'interfaceName': interfaceNames,
                'interfaceIP': interfaceIPs,
                'processID': processID,
                'ospfNetwork': OSPFIPs,
                'ospfArea': row['OSPF Area'],
                'ipv6': IPv6_ip,
                'ospfv3': ospfv3,
                'description': description
                })
    writeYaml(data, '/var/lib/jenkins/workspace/Lab11PoC/ANSIBLE/roles/server/vars/main')



def sshInfo():
    csv_file = "/var/lib/jenkins/workspace/Lab11PoC/ANSIBLE/sshInfo.csv"
    data = {}

    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            router_name = row["Routers"]
            router_data = {
                "Device_Type": row["Device_Type"],
                "IP": row["IP"],
                "Username": row["Username"],
                "Password": row["Password"] 
            }
            data[router_name] = router_data

    return data 

def sendConfigs():
    routers = sshInfo()
    hostnames = uniqueHostnames()
    for i in routers:
        device = {
            'device_type': routers[i]['Device_Type'],
            'host': routers[i]['IP'],
            'username': routers[i]['Username'],
            'password': routers[i]['Password'],
        }
        for j in hostnames:
            if i == j:
                with ConnectHandler(**device) as connection:
                    with open("/var/lib/jenkins/workspace/Lab11PoC/ANSIBLE/CFGS/"+i+".txt", 'r') as file:
                        config_commands = file.readlines()
                    output = connection.send_config_set(config_commands)
                    print(output)

template = determineDevice()
if template == "core":
    createVarPlaybookCORE()
    getCommand(["ansible-playbook", "/var/lib/jenkins/workspace/Lab11PoC/ANSIBLE/site.yaml", "--tags", "core"])
elif template == "edge":
    createVarPlaybookEDGE()
    getCommand(["ansible-playbook", "/var/lib/jenkins/workspace/Lab11PoC/ANSIBLE/site.yaml", "--tags", "edge"])
elif template == "server":
    createVarPlaybookSERVER()
    getCommand(["ansible-playbook", "/var/lib/jenkins/workspace/Lab11PoC/ANSIBLE/site.yaml", "--tags", "server"])
sendConfigs()
