#!/usr/bin/python

import subprocess
import os
import random
import time
import threading
import json
import argparse
from flask import Flask
from flask import request
app = Flask("VPN Controller")

argparser = argparse.ArgumentParser(description="VPN changer")
argparser.add_argument('-l', '--location', help='target_location')
argparser.add_argument('-r', '--random', help='target_location', action='store_true')
argparser.add_argument("--path", default="/etc/openvpn/nordvpn/", help="VPN path")
args = argparser.parse_args()

location_path = args.path
location_file = "current_location"
p_ovpn = None
time_sleep = 60*30
changeVPN_thread = None
running = True
RANDOM_LOCATION = False

def vpn():
    global p_ovpn
    global RANDOM_LOCATION
    if RANDOM_LOCATION:
        current_location = get_random_location()
    else:
        current_location = sameLocation()
    print("Location:" + current_location)
    p_ovpn.terminate()
    p_ovpn = subprocess.Popen(["openvpn", current_location])

def write_location(current_location):
    with open(location_path+location_file, "w") as f_location:
        f_location.write(current_location)

def read_location():
    if os.path.isfile(location_path+location_file):
        with open(location_path+location_file, "r") as f_location:
            current_location = f_location.readline()

    return current_location

def switch_to_location(location):
    global RANDOM_LOCATION
    RANDOM_LOCATION = False
    write_location(location)
    vpn()
    print("Location changed to", location)

def get_random_location():
    current_location = read_location()
    files = os.listdir(location_path)
    files = [x for x in files if ".ovpn" in x and (not current_location or not x.startswith(current_location))]
    file_index = random.randint(0, len(files) - 1)
    current_location = files[file_index][:2]
    write_location(current_location)
    return location_path+files[file_index]

def randomLocation():
    global RANDOM_LOCATION
    RANDOM_LOCATION = True
    current_location = get_random_location()
    print("Location changed to", current_location)
    vpn()

def print_menu():
    print("""
        Set location
            l (country_code)
            country_code ex. de
        
        Random location
            r
            
        Help
            h
            
        Exit
            exit
            q
    """)

def m_exit():
    global running
    running = False
    p_ovpn.terminate()


commands_dict = {"l": switch_to_location, "h": print_menu, "exit": m_exit, "q": m_exit, "r": randomLocation}

def user_command():
    global running
    while running:
        try:
            uinput = input()
            uinput = uinput.strip(' \r\t')
            args = uinput.split(" ")
            if args[0] not in commands_dict:
                print_menu()
            else:
                m_arg =  " ".join(args[1:])
                if not m_arg:
                    commands_dict[args[0]]()
                else:
                    commands_dict[args[0]](" ".join(args[1:]))

        except Exception as ex:
            print(ex.message)


def sameLocation():
    current_location = read_location()
    files = os.listdir(location_path)
    files = [x for x in files if ".ovpn" in x and (not current_location or x.startswith(current_location))]
    file_index = random.randint(0, len(files)-1)
    return location_path+files[file_index]

def changeVPN():
    global running
    global p_ovpn
    global RANDOM_LOCATION
    while running:
        if RANDOM_LOCATION:
            current_location = get_random_location()
        else:
            current_location = sameLocation()
        print("Location:" + current_location)
        p_ovpn = subprocess.Popen(["openvpn", current_location])
        time.sleep(time_sleep)
        p_ovpn.terminate()


@app.route('/', methods=['GET'])
def _root():
    data = {'location': read_location(), 'RANDOM_LOCATION': RANDOM_LOCATION, 'RUNNING': running}
    return json.dump(data)


@app.route('/location', methods=['POST'])
def _post_location_create():
    changed = False
    if request.is_json:
        data = request.get_json()
        if data['location']:
            switch_to_location(data['location'])
            changed = True
            data = {'location': read_location(), 'changed': changed}
    if not changed:
        data = {'error': 'Invalid data'}
    return json.dump(data)


@app.route('/random', methods=['POST'])
def _post_location_random():
    randomLocation()
    data = {'location': read_location()}
    return json.dump(data)



@app.route('/location', methods=['GET'])
def _get_location():
    data = {'location': read_location()}
    return json.dump(data)


def server_runner():
    global app
    app.run('0.0.0.0', 8090)


threading.Thread(target=server_runner)
if args.location:
    write_location(args.location)
if args.random:
    RANDOM_LOCATION = True

changeVPN_thread = threading.Thread(target=changeVPN)
changeVPN_thread.start()


user_command()
changeVPN_thread.join(10)
exit(0)

