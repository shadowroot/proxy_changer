import argparse
import os
import sys

"""
VPN configuration - mainly for 
"""

def update_vpn_config_files(args):
    try:
        files_path = args.vpn_config_files
        login_file  = args.login_file
        for f in os.listdir(files_path):
            if ".ovpn" in f:
                newfilename = files_path + f + ".tmp"
                print("Changing file " + f)
                with open(files_path + f, "r") as openedfile:
                    newfile = open(newfilename, "w")
                    changed = False
                    for line in openedfile:
                        if "auth-user-pass" in line:
                            changed = True
                            line = "auth-user-pass {}\n".format(login_file)
                        newfile.write(line)
                    if not changed:
                        line = "\n\nauth-user-pass {}\n".format(login_file)
                        newfile.write(line)
                    newfile.close()
                os.rename(files_path + f, files_path + f + ".backup")
                os.rename(newfilename, files_path + f)
    except Exception as e:
        print("Updating files failed e={}".format(e), file=sys.stderr)

def create_login_file(args):
    file_path = args.vps_config_files
    try:
        f = open(file_path, 'r')
        os.rename(file_path, file_path+".backup")
    except:
        pass

    try:
        username = args.username
        password = args.password
        with open(file_path, 'w') as login_file:
            login_file.write(username+"\n")
            login_file.write(password+"\n")
    except Exception as e:
        print("Creation of login file failed e={}".format(e), file=sys.stderr)


argparser = argparse.ArgumentParser(description="Create login file")
argparser.add_argument('--username', help="VPN username")
argparser.add_argument('--password', help="VPN Password")
argparser.add_argument('--login-file', default="/etc/openvpn/vpn_login.conf", help="OpenVPN login file path, default=/etc/openvpn/vpn_login.conf")
argparser.add_argument('--vpn-config-files', default="/etc/openvpn/nordvpn/ovpn_tcp/", help="OpenVPN config files, prepared for OpenVPN")
argparser.add_argument('--backup', default=False, help="OpenVPN make backups")

args = argparser.parse_args()

create_login_file(args)
update_vpn_config_files(args)
