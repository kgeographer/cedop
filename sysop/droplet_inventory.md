# DO Droplet Inventory

Run these commands on the droplet (`ssh root@107.170.199.83`) and paste output below each section.

---

## OS / Hardware

```
lsb_release -a
uname -r
nproc
free -h
df -h
```

No LSB modules are available.
Distributor ID:	Ubuntu
Description:	Ubuntu 22.04.4 LTS
Release:	22.04
Codename:	jammy
5.15.0-119-generic
1
               total        used        free      shared  buff/cache   available
Mem:           1.9Gi       421Mi       130Mi        88Mi       1.4Gi       1.2Gi
Swap:          2.0Gi       1.5Gi       483Mi
Filesystem      Size  Used Avail Use% Mounted on
tmpfs           197M  2.3M  195M   2% /run
/dev/vda1        50G   34G   14G  72% /
tmpfs           983M  1.1M  981M   1% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
tmpfs           197M     0  197M   0% /run/user/1000
---

## Apache vhosts

```
ls /etc/apache2/sites-enabled/
apache2ctl -S 2>&1
```

lrwxrwxrwx 1 root root 35 Jan 12 13:14 000-default.conf -> ../sites-available/000-default.conf
lrwxrwxrwx 1 root root 29 Feb  8 18:13 cedop.conf -> ../sites-available/cedop.conf
lrwxrwxrwx 1 root root 46 Feb  9 18:22 cedop-le-ssl.conf -> /etc/apache2/sites-available/cedop-le-ssl.conf
lrwxrwxrwx 1 root root 28 Oct 12  2024 glos.conf -> ../sites-available/glos.conf
lrwxrwxrwx 1 root root 35 Oct  7  2015 kgeographer.conf -> ../sites-available/kgeographer.conf
lrwxrwxrwx 1 root root 35 Aug 13  2020 linkedpaths.conf -> ../sites-available/linkedpaths.conf
lrwxrwxrwx 1 root root 32 Oct  7  2015 topotime.conf -> ../sites-available/topotime.conf
lrwxrwxrwx 1 root root 29 Sep 20  2015 whweb.conf -> ../sites-available/whweb.conf
AH00526: Syntax error on line 34 of /etc/apache2/sites-enabled/cedop-le-ssl.conf:
SSLCertificateFile: file '/etc/letsencrypt/live/cedop.kgeographer.org/fullchain.pem' does not exist or is empty
Action '-S' failed.
The Apache error log may have more information.

## Running services

```
systemctl list-units --type=service --state=running
```

  UNIT                        LOAD   ACTIVE SUB     DESCRIPTION                                      
  accounts-daemon.service     loaded active running Accounts Service
  apache-htcacheclean.service loaded active running Disk Cache Cleaning Daemon for Apache HTTP Server
  apache2.service             loaded active running The Apache HTTP Server
  atd.service                 loaded active running Deferred execution scheduler
  cedop.service               loaded active running CEDOP FastAPI (gunicorn + uvicorn worker)
  containerd.service          loaded active running containerd container runtime
  cron.service                loaded active running Regular background program processing daemon
  dbus.service                loaded active running D-Bus System Message Bus
  do-agent.service            loaded active running The DigitalOcean Monitoring Agent
  droplet-agent.service       loaded active running The DigitalOcean Droplet Agent
  getty@tty1.service          loaded active running Getty on tty1
  kibana.service              loaded active running Kibana
  mysql.service               loaded active running MySQL Community Server
  networkd-dispatcher.service loaded active running Dispatcher daemon for systemd-networkd
  ntp.service                 loaded active running Network Time Service
  packagekit.service          loaded active running PackageKit Daemon
  polkit.service              loaded active running Authorization Manager
  postfix@-.service           loaded active running Postfix Mail Transport Agent (instance -)
  postgresql@15-main.service  loaded active running PostgreSQL Cluster 15-main
  rsyslog.service             loaded active running System Logging Service
  ssh.service                 loaded active running OpenBSD Secure Shell server
  systemd-journald.service    loaded active running Journal Service
  systemd-logind.service      loaded active running User Login Management
  systemd-resolved.service    loaded active running Network Name Resolution
  systemd-udevd.service       loaded active running Rule-based Manager for Device Events and Files
  unattended-upgrades.service loaded active running Unattended Upgrades Shutdown
  user@1000.service           loaded active running User Manager for UID 1000
  uuidd.service               loaded active running Daemon for generating UUIDs
  wpa_supplicant.service      loaded active running WPA supplicant

LOAD   = Reflects whether the unit definition was properly loaded.
ACTIVE = The high-level unit activation state, i.e. generalization of SUB.
SUB    = The low-level unit activation state, values depend on unit type.
29 loaded units listed.

## PostgreSQL

```
psql -U postgres -c "\l"
psql -U postgres -c "SELECT version();"
```
   Name    |  Owner   | Encoding | Locale Provider |   Collate   |    Ctype    | Locale | ICU Rules |   Access privileges   
-----------+----------+----------+-----------------+-------------+-------------+--------+-----------+-----------------------
 cedop     | postgres | UTF8     | libc            | en_US.UTF-8 | en_US.UTF-8 |        |           | 
 glos      | karlg    | UTF8     | libc            | en_US.UTF-8 | en_US.UTF-8 |        |           | 
 postgres  | postgres | UTF8     | libc            | en_US.UTF-8 | en_US.UTF-8 |        |           | 
 template0 | postgres | UTF8     | libc            | en_US.UTF-8 | en_US.UTF-8 |        |           | =c/postgres          +
           |          |          |                 |             |             |        |           | postgres=CTc/postgres
 template1 | postgres | UTF8     | libc            | en_US.UTF-8 | en_US.UTF-8 |        |           | =c/postgres          +
           |          |          |                 |             |             |        |           | postgres=CTc/postgres
(5 rows)

PostgreSQL 15.8 (Ubuntu 15.8-1.pgdg22.04+1) on x86_64-pc-linux-gnu, compiled by gcc (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0, 64-bit

## Python / virtualenvs

```
ls -l ~/envs/
find /var/www -name "*.conf" -o -name "gunicorn*" 2>/dev/null | head -20
```

drwxrwxr-x 6 karlg karlg 4.0K Jan 12 13:33 edop

find has no result

## Web roots

```
ls -l ~/webs/
```

drwxrwxr-x 15 karlg karlg 4096 Feb 20 08:29 cedop
drwxrwxr-x 13 karlg karlg 4096 Jul  7  2025 glos
drwxr-xr-x  2 karlg karlg 4096 Jul 24  2020 html
drwxr-xr-x  8 karlg karlg 4096 Sep 13  2025 kgeographer
drwxr-xr-x  4 karlg karlg 4096 May 10  2017 linkedpaths
drwxrwxr-x  3 karlg karlg 4096 Aug 13  2020 linkedplaces
drwxr-xr-x  3 karlg karlg 4096 Oct  7  2015 topotime
drwxrwxr-x  6 karlg karlg 4096 Feb 27  2017 whweb
drwxr-xr-x  4 karlg karlg 4096 Jun  1  2016 whweb.bak
drwxr-xr-x 11 karlg karlg 4096 Sep 20  2015 whweb_rails

## Crontab

```
crontab -l
```

no crontab for karlg

## Authorized SSH keys (for audit)

```
cat ~/.ssh/authorized_keys
ls -l ~/.ssh/
```
no authorized_keys file

-rw-rw-r-- 1 karlg karlg   64 Aug  6  2024 config
-rw------- 1 karlg karlg 3326 Sep 20  2015 id_rsa
-rw------- 1 karlg karlg 2602 Aug 12  2024 id_rsa_2023
-rw------- 1 karlg karlg 3389 Oct 10  2024 id_rsa_2024
-rw-r--r-- 1 karlg karlg  746 Oct 10  2024 id_rsa_2024.pub
-rw-r--r-- 1 karlg karlg  747 Sep 20  2015 id_rsa.pub
-rw-r--r-- 1 karlg karlg 1250 Apr  5 07:15 known_hosts
-rw-r--r-- 1 karlg karlg 1106 Aug 12  2024 known_hosts.old

## Apache configs for all vhosts

```
cat /etc/apache2/sites-enabled/*.conf
```

see sysop/apache_conf.txt

*Paste command output below each section after running.*
