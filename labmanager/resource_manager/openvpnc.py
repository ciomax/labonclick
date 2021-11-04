import os, subprocess, pathlib, signal, time
from resource_manager import definitions
from contextlib import contextmanager

# p = pathlib.Path('/home/max/labmanager/labmanager/ovpn/')
p = pathlib.Path('/home/app/web/ovpn/')
config_path = p.joinpath('Intergration.ovpn')
ca_path = p.joinpath('ca.crt')
cert_path = p.joinpath('client.crt')
key_path = p.joinpath('client.key')

#working on docker
def closeOvpn():
    try:
        for line in os.popen("ps ax | grep openvpn | grep -v grep"):
            if not '--config' in line:
                continue
            else:
                fields = line.split()
                print(fields)
                # Extracting Process ID from the output
                pid = fields[0]

                os.kill(int(pid), signal.SIGILL)
                print("OpenVPN Process Successfully terminated")
    except:
        print("Error encountered while killing OpenVPN process")

# def closeOvpn():
#     try:
#         for line in os.popen("ps ax | grep openvpn | grep -v grep"):
#             if not '--config' in line:
#                 continue
#             else:
#                 fields = line.split()
#                 # Extracting Process ID from the output
#                 pid = fields[0]
#                 subprocess.check_call(["sudo", "kill", str(pid)])
#                 # os.kill(int(pid), signal.SIGILL)
#                 print("OpenVPN Process Successfully terminated")
#     except:
#         print("Error encountered while killing OpenVPN process")

# For docker deployment
def connectOVPN(config_path):
    x = subprocess.Popen(['openvpn', '--data-ciphers','BF-CBC', '--auth-nocache',
                          '--config', config_path,
                          '--ca', definitions.ca_path,
                          '--cert', definitions.cert_path,
                          '--key', definitions.key_path], stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    return x

# def connectOVPN(config_path):
#     x = subprocess.Popen(['sudo', 'openvpn', '--auth-nocache',
#                           '--config', config_path,
#                           '--ca', definitions.ca_path,
#                           '--cert', definitions.cert_path,
#                           '--key', definitions.key_path], stdout=subprocess.PIPE,
#                          stderr=subprocess.STDOUT)
#     return x


