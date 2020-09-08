#!/usr/bin/env python3

import requests
import re
import os
import argparse
import sys
import subprocess

def download_file(url,ad_server):
    request = requests.get(url, allow_redirects=True)
    with open(ad_server, 'wb') as f:
        f.write(request.content)       

def create_dnsmasq_conf(ad_server,dns_conf):
    pat = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    with open(ad_server, 'r+') as f, open(dns_conf, 'a') as f2:
        f2.write('## MAZA - List ad blocking\n')
        for line in f.readlines():
            if pat.match(line):
                f2.write('address=/' + line.split()[1] + '/' + line.split()[0] + '\n')
        f2.write('## END MAZA\n')


def update_etc_hosts(dns_conf, hostsfile):
    with open(dns_conf, 'r') as dns_conf, open(hostsfile, 'a') as hostfile:
        for line in  dns_conf.readlines():
            hostfile.write(line)

def empty_dns_conf(dns_conf):
    with open(dns_conf, 'w') as f:
        f.seek(0)
        f.truncate()

def clean_up_etc_hosts(hostsfile, dns_conf):
    with open(hostsfile, "r") as hostsfile, open(dns_conf, 'r') as dns_file:
        hostfile = hostsfile.readlines()
        dnsfile = dns_file.readlines()
        hostsfile.close()
        hosts = open('/etc/hosts', "w")
        for line in hostfile:
            if line not in dnsfile:
                hosts.write(line)

def check_string_in_file(file_to_check, string):
    with open(file_to_check, 'r') as file_to_check:
        for line in file_to_check:
            if string in line:
                return True
    return False

def restart_dnsmasq():
    if os.path.isfile('/usr/local/bin/brew'):
        sys.stdout.write("\033[0;32m")
        subprocess.run(["brew", "services", "stop", "dnsmasq"])
        print("service dnsmasq stopped")
        subprocess.run(["brew", "services", "start", "dnsmasq"])
        print("service dnsmasq started")
        sys.stdout.write("\033[0;0m")
    else:
        sys.stdout.write("\033[0;32m")
        subprocess.run(["systemctl", "stop", "dnsmasq"])
        print("service dnsmasq stopped")
        subprocess.run(["systemctl", "start", "dnsmasq"])
        print("service dnsmasq started")
        subprocess.run(["systemctl", "enable", "dnsmasq"])
        print("service dnsmasq enabled")
        sys.stdout.write("\033[0;0m")

def main():
    url = "https://pgl.yoyo.org/adservers/serverlist.php?showintro=0&mimetype=plaintext"
    conf_dir = os.getenv("HOME") + '/.maza' 
    ad_server = conf_dir + "/adserver_list"
    dns_conf = conf_dir + '/dnsmasq.conf'
    hostsfile = '/etc/hosts'
    dnsmasq_config = '/usr/local/etc/dnsmasq.conf'
    start_tag="## MAZA - List ad blocking"
    RED   = "\033[1;31m"  
    GREEN = "\033[0;32m"
    RESET = "\033[0;0m"

    parser = argparse.ArgumentParser(description="change how the script behave by setting a flag")
    parser.add_argument('--start', action='store_true', help='Activate blocking DNS.')
    parser.add_argument('--stop', action='store_true', help='Deactivate blocking DNS.')
    parser.add_argument('--status', action='store_true', help='Check if it\'s active or not')
    parser.add_argument('--update', action='store_true', help='Update the list of DNS to be blocked')
    parser.add_argument('--install', action='store_true', help='check if dnsmasq is installed and properarly configured')
    args = parser.parse_args()

    if args.start:
        if not os.path.isdir(conf_dir):
            os.mkdir(conf_dir)
            download_file(url,ad_server)
            create_dnsmasq_conf(ad_server,dns_conf)
            update_etc_hosts(dns_conf, hostsfile)
            restart_dnsmasq()
            sys.stdout.write(GREEN)
            print(f"confdir {conf_dir} was created")
            print("enabled")
            sys.stdout.write(RESET)
        else:
            for f_file in os.listdir(conf_dir):
                os.remove(conf_dir + '/' + f_file)
            download_file(url,ad_server)
            sys.stdout.write(GREEN)
            print(f"{ad_server} downloaded")
            create_dnsmasq_conf(ad_server,dns_conf)
            print("dnsmasq config created")
            update_etc_hosts(dns_conf, hostsfile)
            print("files has been updated")
            restart_dnsmasq()
            sys.stdout.write(RESET)
    elif args.stop:
        clean_up_etc_hosts(hostsfile, dns_conf)
        empty_dns_conf(dns_conf)
        sys.stdout.write(RED)
        print("maze disabled")
        sys.stdout.write(RESET)
    elif args.status:
        if check_string_in_file(hostsfile, start_tag):
            sys.stdout.write(GREEN)
            print("enabled")
            sys.stdout.write(RESET)
        else:
            sys.stdout.write(RED)
            print("disabled")
            sys.stdout.write(RESET)
    elif args.update:
        for f_file in os.listdir(conf_dir):
            os.remove(conf_dir + '/' + f_file)
            download_file(url,ad_server)
            create_dnsmasq_conf(ad_server,dns_conf)
            restart_dnsmasq()
            sys.stdout.write(GREEN)
            print("files has been updated, sucessfully")
            sys.stdout.write(RESET)
    elif args.install:
        if not os.path.isfile(dnsmasq_config):
            print(f"{dnsmasq_config} missing.")
            print("Please install dnsmasq and start the service")
        else:
            if  check_string_in_file(dnsmasq_config, dns_conf):
                sys.stdout.write(GREEN)
                print("dnsmasq is configured")
                sys.stdout.write(RESET)
            else:
                with open(dnsmasq_config, 'a') as dnsmasq_conf:
                    dnsmasq_conf.write("conf-file="+ dns_conf)

   

if __name__ == "__main__":
    main()
