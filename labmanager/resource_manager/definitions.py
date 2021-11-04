from dataclasses import dataclass
from pathlib import Path
import ipaddress

cpe_hw_types = [
    ('Capricorn', 'Capricorn'),
    ('Capricorn-4', 'Capricorn-4'),
    ('Capricorn Pro', 'Capricorn Pro'),
    ('Capricorn MEC', 'Capricorn MEC'),
    ('Capricorn-4 S2X', 'Capricorn-4 S2X'),
    ('Aquarius', 'Aquarius'),
    ('Taurus', 'Taurus'),
    ('Capricorn Aero', 'Capricorn Aero'),
    ('Gemini', 'Gemini'),
    ('Gemini-i', 'Gemini-i'),
    ('Gemini-4', 'Gemini-4'),
    ('Aries', 'Aries'),
    ('Gemini-e S2X', 'Gemini-e S2X'),
    ('Libra', 'Libra'),
]


Locations = [
    ('Moldova', 'Moldova'),
    ('Israel', 'Israel'),
]

Setup_types = [
    ('c-HUB', 'c-HUB'),
    ('x-HUB', 'x-HUB'),
    ('mPower', 'mPower'),
]

@dataclass
class VsatHwType:
    hw_type: str
    num_gbe: int = 4
    num_sfp: int = 0
    num_rf: int = 1

hw_types = []

Aquarius = VsatHwType(hw_type='Aquarius', num_gbe=6, num_sfp=2, num_rf=2)
Capricorn = VsatHwType(hw_type='Capricorn', num_gbe=1)
Capricorn_4 = VsatHwType(hw_type='Capricorn-4')
Capricorn_Pro = VsatHwType(hw_type='Capricorn Pro')
Capricorn_MEC = VsatHwType(hw_type='Capricorn MEC', num_gbe=5)
Capricorn_4_S2X = VsatHwType(hw_type='Capricorn-4 S2X')
Taurus = VsatHwType(hw_type='Taurus', num_rf=2)
Capricorn_Aero = VsatHwType(hw_type='Capricorn Aero')
Gemini = VsatHwType(hw_type='Gemini', num_gbe=1)
Gemini_i = VsatHwType(hw_type='Gemini-i', num_gbe=1)
Gemini_4 = VsatHwType(hw_type='Gemini-4')
Aries = VsatHwType(hw_type='Aries', num_gbe=1)
Gemini_e_S2X = VsatHwType(hw_type='Gemini-e S2X', num_gbe=1)
Libra = VsatHwType(hw_type='Libra', num_gbe=1)

hw_types.append(Aquarius)
hw_types.append(Capricorn)
hw_types.append(Capricorn_4)
hw_types.append(Capricorn_Pro)
hw_types.append(Capricorn_MEC)
hw_types.append(Capricorn_4_S2X)
hw_types.append(Taurus)
hw_types.append(Capricorn_Aero)
hw_types.append(Gemini)
hw_types.append(Gemini_i)
hw_types.append(Gemini_4)
hw_types.append(Aries)
hw_types.append(Gemini_e_S2X)
hw_types.append(Libra)


MX204_interface_list = [
    'et-0/0/0',
    'et-0/0/1',
    'et-0/0/2',
    'et-0/0/3',
    'xe-0/1/0',
    'xe-0/1/1',
    'xe-0/1/2',
    'xe-0/1/3',
    'xe-0/1/4',
    'xe-0/1/5',
    'xe-0/1/6',
]

MX5_interface_list = [
    'xe-0/0/0',
    'xe-0/0/1',
    'xe-0/0/2',
    'xe-0/0/3',
    'ge-1/1/0',
    'ge-1/1/1',
    'ge-1/1/2',
    'ge-1/1/3',
    'ge-1/1/4',
    'ge-1/1/5',
    'ge-1/1/6',
    'ge-1/1/7',
    'ge-1/1/8',
    'ge-1/1/9',
]

VMX_interface_list = [
    'management',
    'DPS side',
    'Customer side',
]

# OpenVPN files
openvpn_files_p = Path('/home/app/web/ovpn/')
# p = Path('/home/app/web/ovpn/')
config_path = openvpn_files_p.joinpath('Intergration.ovpn')
ca_path = openvpn_files_p.joinpath('ca.crt')
cert_path = openvpn_files_p.joinpath('client.crt')
key_path = openvpn_files_p.joinpath('client.key')


''' Setup networks
For each task which requires connection to these subnets, OpenVPN connection will pe established'''
setup_subnets = [ipaddress.ip_network('10.64.7.0/24'),
                 ipaddress.ip_network('10.32.7.254')]

# Gilat docker images catalog
docker_catalog = 'http://10.56.51.57:5000/v2/_catalog'
remote_repo = '10.56.51.57:5000'