from netmiko import ConnectHandler
from dotenv import load_dotenv
import os
import re
import ipaddress
import time
import socket

def get_text_from_file(filename):
    try:
        with open(filename, 'r') as file:
            text = file.read()
            return text
    except FileNotFoundError:
        print("file not found")
        return ""

def get_frodo_connection(frodo_ip, username, password):
    switch = {
        'device_type': 'hp_comware',
        'ip': frodo_ip,
        'username': username,
        'password': password,
    }
    try:
        connection = ConnectHandler(**switch)
        print("connected to " + frodo_ip)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    return connection

def configure_frodo(connection, command_set):
    prompt_pattern = r'.*'
    print(f'sending comand set {command_set}')
    for command in command_set:
        print(f'sending command {command}')
        response = connection.send_command(command, expect_string=prompt_pattern)
        print('RESPONSE\n' + response)
        time.sleep(1)

def get_ips_from_urls(urls: list)-> list:
    ip_list = []
    for url in urls:
        ip_address = socket.gethostbyname(url)
        ip_list.append(ip_address)
    return ip_list

def get_ips_from_peer_list(peer_list):
    return [ip for ip in peer_list if '172.24.' in ip]

target_frodo = '172.24.198.6' # lamb frodo
load_dotenv()
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
vsi = 'SMALL-LIBRARIES-ANNEXE'
pwid = '31030004'

frodo_urls = get_text_from_file('frodo_urls.txt').split()
print(frodo_urls)
config_string = ''
config_string +=f'sys\nvsi {vsi}\npwsignaling ldp\n'
config_string += f'peer {target_frodo} pw-id {pwid} pw-class imcethpw\n'
config_string += 'exit\nexit\nexit\nmpls ldp\n'
config_string += f'targeted-peer {target_frodo}\nend\ndis l2vpn vsi name {vsi} verb\nsa sa fo'
config_list = config_string.split('\n')

for frodo in frodo_urls:
    connection = get_frodo_connection(frodo, username=username, password=password)
    configure_frodo(connection, config_list)
    connection.disconnect()
    print("disconnected")
