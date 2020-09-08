# maza-ad-blocking-python-clone
This is my clone from the famous maza-ad-blocking tool, written in python.

I used 100% basic python3 modules
# Commands
Install
```dotnetcli
maza --install
```

start
```dotnetcli
maza --start
```

stop
```dotnetcli
maza --stop
```

status
```dotnetcli
maza --status
```
udpate

```dotnetcli
maza --update
```

help
```dotnetcli
maza --help or maza -h
```

# Installtion

## Requirements
- curl
- python3
- for mac is also [homebrew(https://docs.brew.sh/Installation)] required 
### Preperation

Optional but recommanded it to backup your /etc/hosts file

```bash
sudo cp -v /etc/hosts /etc/hosts.backup
```

### Download 

To download and install the script just run:
```bash
curl -o maza https://raw.githubusercontent.com/undefynd/maza-ad-blocking-python-clone/master/maza.py && chmod +x maza && sudo mv maza /usr/local/bin
```

### Uninstall

```
rm /usr/local/bin/maza && rm -r ~/.maza
```

### DNSMASQ

Unfortunately the hosts file does not support sub-domains (wildcards), which is necessary to correctly filter all DNS. You will need to install locally a server for that purpose, Maza supports the Dnsmasq format.

#### MAC

##### Install && Configure

```
maza --install
```

With the --install option the script will check if dnsmasq is installed. On Mac it will install dnsmasq via `brew`. Also will this option add the following line to the end of file `/usr/local/etc/dnsmasq.conf
`.

Example:
```
conf-file=/Users/maxmustermann/.maza/dnsmasq.conf
```

##### Tell your OS to use your DNS server

Delete the list of macOS DNS servers and add the 3 addresses. The first one will be your local server, and the other 2 belong to OpenDNS, which you can use any other.

```
127.0.0.1
208.67.222.222
208.67.220.220
```

Refresh DNS cache:

```
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
```

##### Restart/Start Maza

```dotnetcli
sudo maza --start
sudo maza --stop
```
--start will check if the config dir `~/.maza` exists and will if required create it. Followed by downloading and generating the required files and will update `/etc/hosts`. Also will this option restart dnsmasq.

--stop will reverse the changes to `/etc/hosts` empty `~/.maza/dnsmasq.conf`

#### Debian/Ubuntu
##### Install

```dotnetcli
sudo apt update
sudo apt install dnsmasq
``` 
##### Configure

```
maza --install
```

Also will this option add the following line to the end of file `/etc/dnsmasq.conf
`.

Example:
```
conf-file=/home/maxmustermann/.maza/dnsmasq.conf
```

##### Tell your OS to use your DNS server

In Gnome Shell, open Settings->Nework. Click in the sprocket of your connection.

Add your local server (dnsmasq), and the other 2 belong to OpenDNS, which you can use any other.

```127.0.0.1,208.67.222.222,208.67.220.220```

##### Restart/Start Maza

```dotnetcli
sudo maza --start
sudo maza --stop
```
--start will check if the config dir `~/.maza` exists and will if required create it. Followed by downloading and generating the required files and will update `/etc/hosts`. Also will this option restart dnsmasq.

--stop will reverse the changes to `/etc/hosts` empty `~/.maza/dnsmasq.conf`