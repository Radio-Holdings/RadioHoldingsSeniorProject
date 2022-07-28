"""Implementation of all commands.
"""
import os


"""
    CONNECT NODE:
    *3 <NODE_NUMBER>

    DISCONNECT NODE:
    *1 <NODE_NUMBER>

    DISCONNECT ALL Nodes:
    *71

    RECONNECT ALL LINKS:
    *74

    SYSTEM CONNECTION STATUS:
    *73
    
    SYSTEM TIME
    *81
"""
def connect_to_node(node_number):
    print(f"Connecting to node {node_number}.")
    command = "sudo asterisk -rx \"rpt fun 1999 *3{}\"".format(node_number)
    print("Command executed: ", command)
    os.system(command)

def disconnect_from_all_nodes():
    print(f"Disconnecting from all nodes.")
    command = "sudo asterisk -rx \"rpt fun 1999 *71\""
    print("Command executed: ", command)
    os.system(command)

def disconnect_from_node(node_number):
    print(f"Disconnecting from node {node_number}.")
    command = "sudo asterisk -rx \"rpt fun 1999 *1{}\"".format(node_number)
    print("Command executed: ", command)
    os.system(command)

def announce_connection_status():
    print("Announcing connection status")
    command = "sudo asterisk -rx \"rpt fun 1999 *73\""
    print("Command executed: ", command)
    os.system(command)

def announce_system_time():
    print("Announcing system time")
    command = "sudo asterisk -rx \"rpt fun 1999 *81\""
    print("Command executed: ", command)
    os.system(command)

def reconnect_all_previous_links():
    print("reconnecting all previous links")
    command = "sudo asterisk -rx \"rpt fun 1999 *74\""
    print("Command executed: ", command)
    os.system(command)