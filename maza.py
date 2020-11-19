#!/usr/bin/env python3

import requests
import re
import os
import argparse
import sys
import subprocess

def parser():
    parser = argparse.ArgumentParser(description="change how the script behave by setting a flag")
    parser.add_argument('--start', action='store_true', help='Activate blocking DNS.')
    parser.add_argument('--stop', action='store_true', help='Deactivate blocking DNS.')
    parser.add_argument('--status', action='store_true', help='Check if it\'s active or not')
    parser.add_argument('--update', action='store_true', help='Update the list of DNS to be blocked')
    parser.add_argument('--install', action='store_true', help='install dnsmasq on Mac or check if is installed and properarly configured')
    
    return parser

def download_file(url,ad_server):
    request = requests.get(url, allow_redirects=True)
    with open(ad_server, 'wb') as f:
        f.write(b'## MAZA - List ad blocking\n')
        f.write(request.content)       
        f.write(b'## END MAZA\n')

def create_dnsmasq_conf(ad_server,dns_conf):
    pat = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    with open(ad_server, 'r+') as f, open(dns_conf, 'a') as f2:
        f2.write('## MAZA - List ad blocking\n')
        for line in f.readlines():
            if pat.match(line):
                f2.write('address=/' + line.split()[1] + '/' + line.split()[0] + '\n')
        f2.write('## END MAZA\n')

def update_etc_hosts(ad_server, hostsfile):
    pat = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    with open(ad_server, 'r+') as f, open(hostsfile, 'a') as hostfile:
        hostfile.write('## MAZA - List ad blocking\n')
        for line in  f.readlines():
            if pat.match(line):
                hostfile.write(line)
        hostfile.write('## END MAZA\n')

def empty_dns_conf(dns_conf):
    with open(dns_conf, 'w') as f:
        f.seek(0)
        f.truncate()

def clean_up_etc_hosts(hostsfile, ad_server):
    with open(hostsfile, "r") as hostsfile, open(ad_server, 'r') as ad_file:
        hostfile = hostsfile.readlines()
        adfile = ad_file.readlines()
        hostsfile.close()
        hosts = open('/etc/hosts', "w")
        for line in hostfile:
            if line not in adfile:
                hosts.write(line)

def check_string_in_file(file_to_check, string):
    with open(file_to_check, 'r') as file_to_check:
        for line in file_to_check:
            if string in line:
                return True
    return False

def restart_dnsmasq():
    if sys.platform == 'darwin' and os.path.isfile('/usr/local/bin/brew'):
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

def dns_config_file():
    if sys.platform == 'darwin':
        return '/usr/local/etc/dnsmasq.conf'
    else:
        return '/etc/dnsmasq.conf'

def dnsmasq_exe():
    if sys.platform == 'darwin':
        return '/usr/local/Cellar/dnsmasq'
    else:
        return '/usr/sbin/dnsmasq'

def update(url, ad_server, dns_conf,hostsfile):
    sys.stdout.write('\033[0;32m')
    download_file(url,ad_server)
    print(f"{ad_server} downloaded")
    create_dnsmasq_conf(ad_server,dns_conf)
    print("dnsmasq config created")
    clean_up_etc_hosts(hostsfile, ad_server)
    update_etc_hosts(ad_server, hostsfile)
    restart_dnsmasq()
    sys.stdout.write('\033[0;0m')

def main():
    url = "https://pgl.yoyo.org/adservers/serverlist.php?showintro=0&mimetype=plaintext"
    conf_dir = os.getenv("HOME") + '/.maza' 
    ad_server = os.getenv("HOME") + '/.maza/adserver_list'
    dns_conf = os.getenv("HOME") + '/.maza/dnsmasq.conf'
    hostsfile = '/etc/hosts'
    dnsmasq_config = dns_config_file()
    dnsmasq_executeable = dnsmasq_exe()
    start_tag="## MAZA - List ad blocking"
    RED   = "\033[1;31m"  
    GREEN = "\033[0;32m"
    RESET = "\033[0;0m"

    args = parser().parse_args()

    if args.start:
        if not os.path.isdir(conf_dir):
            os.mkdir(conf_dir)
            update(url, ad_server, dns_conf, hostsfile)
            sys.stdout.write(GREEN)
            print(f"confdir {conf_dir} was created")
            print("enabled")
            sys.stdout.write(RESET)
        else:
            for f_file in os.listdir(conf_dir):
                os.remove(conf_dir + '/' + f_file)
            sys.stdout.write(GREEN)
            update(url, ad_server, dns_conf, hostsfile)
            print("files has been updated")
            sys.stdout.write(RESET)
    elif args.stop:
        clean_up_etc_hosts(hostsfile, ad_server)
        empty_dns_conf(dns_conf)
        restart_dnsmasq()
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
        sys.stdout.write(GREEN)
        update(url, ad_server, dns_conf, hostsfile)
        print("files has been updated, successfully")
        sys.stdout.write(RESET)
    elif args.install:
        if not os.path.isdir(dnsmasq_executeable):
            print(f"{dnsmasq_executeable} missing.")
            if sys.platform == 'darwin':
                print("let's try to install dnsmasq via homebrew")
                if os.path.isfile('/usr/local/bin/brew'):
                    subprocess.run(["brew", "install", "dnsmasq"])
                    with open(dnsmasq_config, 'a') as dnsmasq_conf:
                        dnsmasq_conf.write("conf-file="+ dns_conf)
                    sys.stdout.write(GREEN)
                    print("dnsmasq is configured")
                    sys.stdout.write(RESET)
                else:
                    print("Homebrew not installed please visit: https://docs.brew.sh/Installation")
            else:
                print("Please install dnsmasq via your package manager")
        else:
            if check_string_in_file(dnsmasq_config, dns_conf):
                sys.stdout.write(GREEN)
                print("dnsmasq is configured")
                sys.stdout.write(RESET)
            else:
                with open(dnsmasq_config, 'a') as dnsmasq_conf:
                    dnsmasq_conf.write("conf-file="+ dns_conf)
  

if __name__ == "__main__":
    main()
