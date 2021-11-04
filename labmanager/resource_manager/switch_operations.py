import paramiko, re, ipaddress
# from .definitions import setup_subnets
from resource_manager.definitions import setup_subnets


class SSHCom(object):
    def __init__(self, ip_addr, username, passwd):
        self.ip_addr = ip_addr
        self.username = username
        self.passwd = passwd
        self.ssh = paramiko.SSHClient()

    def __enter__(self):
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        self.ssh.connect(str(self.ip_addr),
                         username=self.username,
                         password=self.passwd,
                         look_for_keys=False)

        return self.ssh

    def execute_command(self, command):
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(command=command)
        return ssh_stdout

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ssh.close()


class SwitchO:
    def __init__(self, name, ip_addr, username, password):
        self.name = name
        self.ip_addr = ipaddress.IPv4Address(ip_addr)
        self.username = username
        self.password = password
        self.interfaces = []

    def _add_interface(self, interface):
        self.interfaces.append(interface)

    def __str__(self):
        return "{0}: {1}".format(self.name, str(self.ip_addr))

    def require_ovpn(self):
        for net in setup_subnets:
            if self.ip_addr in net:
                return True
        return False

    def parse_interfaces(self, output):
        '''

        :param output: output of "show interface description" command
        :return:
        '''
        switchInterfaces = list(
            filter(lambda x: x.startswith('Gi') or x.startswith('Te') or x.startswith('Eth'), output))
        for i in range(len(switchInterfaces)):
            # print(switchInterfaces[i])
            if_split = re.split(" +", switchInterfaces[i])
            interface_index = if_split[0]
            interface_description = if_split[-1]
            self._add_interface(SwitchInterface(interface_index, interface_description))

    def execute_show_command(self, command):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh.connect(str(self.ip_addr),
                    username=self.username,
                    password=self.password,
                    look_for_keys=False)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command=command)
        output = ssh_stdout.readlines()
        ssh.close()

        return output


class SwitchInterface:
    def __init__(self, index, description, **kwargs):
        '''

        :param index: interface index eg. Eth1/1
        :param description:  port description
        :param kwargs: mode: access, trunk ;
                        access_vlan: vlan_id
                        allowed_vlans: list
        '''
        self.index = index
        self.description = description
        self.mode = kwargs.get('mode', None)
        self.access_vlan = kwargs.get('access_vlan', None)
        self.access_vlan = kwargs.get('allowed_vlans', [])

    def __str__(self):
        return self.index + " " + self.description