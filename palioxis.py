#!/usr/bin/env python
##
# Palioxis v1.1
# author: ohdae
# Palioxis was the Greek personification of the backrush or retreat from battle.
# It seems fitting in the scenarios that would surround the needed use of this script.
# For use by freedom fighters as needed for self-preservation. 
# Do not operate while under the influence of drugs or alcohol. You might lose data and stuff.
# 
# Running in 'Server' mode:
# usage: ./palioxis.py --mode server --host 127.0.0.1 --port 44524 --key OHSNAP
# This will start Palioxis as a server, meaning it will listen on
# the given host and port for the 'destroy key'. Once received, it
# will proceed to shred the specified files and truecrypt drives.
# Once the server starts, it will run in the background as a daemon
# process until you either reboot or kill the process.
# *It's good idea to run the Palioxis server as system service*
#
# Running in 'Client' mode:
# usage: ./palioxis.py --mode client --list /etc/palioxis/nodes.txt
# This will start Palioxis as the master client. It will read server hosts
# from the file specified with the --list argument and attempt to send the 
# kill signal to each of these hosts. 
# 
# Example server list file:
# # the format for server entries is HOST PORT KEY
# 192.168.56.102 44524 OHSNAP
# 192.168.56.104 44524 FREEDOM
# 192.168.56.105 44524 L33T
##

import os
import sys
import socket
import argparse
import commands

dirs = ['/home/user1/', '/root/', '/home/user2/', '/var/log/', '/var/spool/', '/var/www/', '/usr/share/nginx/www',
    '/tmp/', '/etc/cron.*/']

def start_server(host, port):
    print('\n[*] starting server...')
    print('Host:\t%s' % args.host)
    print('Port:\t%s' % args.port)
    print(' Key:\t%s' % args.key)

    socksize = 4096
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen(5)
    except:
        print('[error] failed to start server.')
        sys.exit(1)

    daemon()
    conn, addr = server.accept()
    conn.send('[*] established.')
    while True:
        cmd = conn.recv(socksize)
        if cmd == key:
            conn.send('[*] received.')
            handle_signal()
            break

    conn.close()

def send_signal(host, port, dkey):
    socksize = 4096
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
    except:
        print('[error] problem connecting to node %s:%s' % (host, port))

    while True:
        c = client.recv(socksize)
        if c == 'established':
            client.sendall(dkey)
        if c == '[*] received.':
            print('[*] signal sent successfully.')
            break

    client.close()

def daemon(stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    try: 
        pid = os.fork() 
        if pid > 0:
            sys.exit(0) 
    except OSError, e: 
        print >>sys.stderr, "[error] fork one failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1)

    os.chdir("/") 
    os.setsid() 
    os.umask(0) 

    try: 
        pid = os.fork() 
        if pid > 0:
            print "[*] Palioxis PID: %d" % pid 
            sys.exit(0) 
    except OSError, e: 
        print >>sys.stderr, "[error] fork two failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1) 

    si = file(stdin, 'r')
    so = file(stdout, 'a+')
    se = file(stderr, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

def destroy_dirs(path):
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)):
            os.popen('shred -n 9 -z -f -u %s' % (os.path.join(path, f)))
        elif os.path.isdir(os.path.join(path, f)):
            destroy_dirs(os.path.join(path, f))

def destroy_tc():
    try:
        drives = commands.getoutput('ls /media').split('\n')
        for d in drives:
            if 'truecrypt' in d:
                destroy_dirs('/media/%s' % d)
                os.popen('truecrypt -d')
    except:
        pass

def handle_signal():
    for p in dirs:
        destroy_dirs(p)
    destroy_tc()
    os.popen('shutdown -h now')


help = """Palioxis: Greek personification of the backrush or retreat from battle. Linux self-destruction utility. Use with caution."""
parser = argparse.ArgumentParser(description=help, prog="palioxis")
parser.add_argument('--mode', help='run as client or server', choices=['client', 'server'], required=True)
parser.add_argument('--host', help='server host')
parser.add_argument('--port', help='server port', type=int)
parser.add_argument('--key', help='destruction key')
parser.add_argument('--list', help='server list [use with client mode]')
args = parser.parse_args()

mode = args.mode
key = args.key

if mode == 'server':
    try:
        h, p = args.host, args.port
        start_server(h, p)
    except:
        print('[error] must specify host and port when running Palioxis in server mode')
        sys.exit(1)
elif mode == 'client':
    if os.path.exists(args.list):
        fin = open(args.list, 'rb')
        for line in fin.readlines():
            if not line.startswith('\n') and not line == '\n':
                try:
                    entry = line.strip('\n').split(' ')
                    print('[*] attempting to signal %s:%s' % (entry[0], entry[1]))
                    send_signal(entry[0], int(entry[1]), entry[2])
                except:
                    continue
            else:
                continue
    else:
        print('[error] host list %s cannot be found.' % args.list)




