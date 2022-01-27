from __future__ import absolute_import, unicode_literals
import ipaddress
import time

from celery import shared_task
from celery import task
from celery.utils.log import get_task_logger
from celery_progress.backend import ProgressRecorder
import paramiko
from django.shortcuts import get_object_or_404
from time import sleep
import socket
from .models import SwitchPort, Switch, Setup, KubePod, OpenVPNServer
from .switch_operations import SwitchO
from .openvpnc import connectOVPN, closeOvpn
from .node_operations import DockerRepo, Kubernetes
from resource_manager.definitions import docker_catalog, remote_repo, openvpn_files_p
from django.dispatch import receiver
from django.db import models
import subprocess, os, signal
logger = get_task_logger(__name__)


@task(name="sum_numbers")
def testTask(x, y):
    return x + y

@task(name="setup_kuberenetes_sync", bind=True)
def setup_kuberenetes_sync(self, setup_id):
    setup = get_object_or_404(Setup, pk=setup_id)
    progress_recorder = ProgressRecorder(self)
    new_pods = []
    progress_recorder.set_progress(1, 4, f"Establishing OpenVPN  connection to the setup.")
    connectOVPN(f"{openvpn_files_p}/{setup.setup_name}.ovpn")
    time.sleep(2)
    progress_recorder.set_progress(2, 4, f"Request microservices information from Gilat repo: {docker_catalog}")
    my_repo = DockerRepo(catalog=docker_catalog, repo=remote_repo)
    my_repo.get_ms()
    progress_recorder.set_progress(3, 4, "Connecting to NMS node and collecting information from the running pods.")
    kube = Kubernetes('10.16.0.10')
    kube.get_namespaces(my_repo)

    progress_recorder.set_progress(4, 4, "Closing OpenVPN connection.")
    closeOvpn()
    for pod in kube.pods:
        updated_node = KubePod.objects.filter(pod_setup=setup,
                                              pod_namespace=pod.namespace,
                                              pod_name=pod.pod_name)
        if updated_node:
            updated_node.update(pod_version=pod.pod_version,
                                pod_available_ver=pod.available_ver)
        else:
            new_pods.append(KubePod.objects.create(pod_setup=setup,
                                                   pod_namespace=pod.namespace,
                                                   pod_name=pod.pod_name,
                                                   pod_image=pod.pod_image,
                                                   pod_version=pod.pod_version,
                                                   pod_available_ver=pod.available_ver))

    # create all new interfaces
    try:
        KubePod.objects.bulk_create(new_pods)
    except:
        print("Error while creating objects")

@task(name="get_switch_interfaces", bind=True)
def get_switch_interfaces(self, swid):
    sw = get_object_or_404(Switch, pk=swid)

    progress_recorder = ProgressRecorder(self)
    # Create an empty list with interfaces. save bulk later
    new_interfaces = []

    operSwitch = SwitchO(sw.switch_role,
                         sw.switch_mgmt_ip,
                         sw.switch_username,
                         sw.switch_password)

    if operSwitch.require_ovpn():
        progress_recorder.set_progress(1, 4, f"Establishing OpenVPN  connection to the setup.")
        print("Establishing OpenVPN")
        connectOVPN(f"{openvpn_files_p}/{sw.switch_setup.setup_name}.ovpn")
        time.sleep(3)
        progress_recorder.set_progress(2, 4, f"Executing show command on the switch")
        if_desc_output = operSwitch.execute_show_command("show interface description")
        progress_recorder.set_progress(3, 4, f"Parsing the output from the previous command.")
        operSwitch.parse_interfaces(output=if_desc_output)
        progress_recorder.set_progress(4, 4, f"Closing OpenVPN connection.")
        time.sleep(3)
        closeOvpn()
    else:
        print("No VPN required")
        progress_recorder.set_progress(1, 2, f"Connecting to the Switch and executing show command on the switch")
        time.sleep(1)
        if_desc_output = operSwitch.execute_show_command("show interface description")
        progress_recorder.set_progress(2, 2, f"Parsing the output from the previous command.")
        operSwitch.parse_interfaces(output=if_desc_output)

    for interface in operSwitch.interfaces:
        # Check if interface already exists
        updated_interfaces = SwitchPort.objects.filter(parrent_switch=sw,
                                                       switch_port_index=interface.index)
        # If interface exists -> Update description. Else, created new interface and
        # add new instance to the list

        if updated_interfaces:
            updated_interfaces.update(port_description=interface.description)
        else:
            instance = SwitchPort.objects.create(parrent_switch=sw,
                                                 switch_port_index=interface.index,
                                                 port_description=interface.description)
            new_interfaces.append(instance)

    # create all new interfaces
    try:
        SwitchPort.objects.bulk_create(new_interfaces)
    except:
        print("Error while creating interfaces")


@task(name="sync_interface_description")
def sync_interface_description(swid, portid):
    sw = get_object_or_404(Switch, pk=swid)
    port = get_object_or_404(SwitchPort, pk=portid)
    port_index = port.switch_port_index
    connected_devices = []
    for device in list(port.cpe_ports_switch.all()):
        connected_devices.append(device)
    for device in list(port.pc_ports_switch.all()):
        connected_devices.append(device)
    for device in list(port.vxgw_if_switch.all()):
        connected_devices.append(device)
    for device in list(port.router_interface_switch.all()):
        connected_devices.append(device)
    for device in list(port.xena_port_switch.all()):
        connected_devices.append(device)
    for device in list(port.ixia_port_switch.all()):
        connected_devices.append(device)

    pdescription = ' '.join([str(elem) for elem in connected_devices])


    try:
        print("Opening connection")
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        try:
            ssh.connect(sw.switch_mgmt_ip,
                        username=sw.switch_username,
                        password=sw.switch_password,
                        look_for_keys=False)
            print('Connected Successfully.')
            connection = ssh.invoke_shell()
            connection.send('configure terminal\n'.encode())
            sleep(2)
            connection.send(f'interface {port_index}\n'.encode())
            sleep(2)
            # connection.send('no description\n'.encode())
            # sleep(1)
            connection.send(f'description {pdescription}\n'.encode())
            sleep(1)
            connection.send('end\n'.encode())
            connection.close()
            ssh.close()
        except paramiko.AuthenticationException:
            print("Incorrect password")
        except socket.error:
            print("Socket error")
    except:
        print("Something went wrong!")


@receiver(models.signals.post_save, sender=OpenVPNServer)
def create_openvpn_file(sender, instance, created, *args, **kwargs):
    if created:
        generate_ovpn_config(instance.id, instance.ip_address)

@task(name='generate_ovpn_config')
def generate_ovpn_config(ovpn_id, ovpn_ip):
    ovpn_server = get_object_or_404(OpenVPNServer, pk=ovpn_id)

    with open(f"{openvpn_files_p}/Sample.ovpn") as sample:
        lines = sample.readlines()
        lines[42] = f"remote {ovpn_ip} 1194"
        with open(f'{openvpn_files_p}/{ovpn_server.ovpn_setup.setup_name}.ovpn', 'w') as new_file:
            new_file.writelines(lines)
    OpenVPNServer.objects.filter(pk=ovpn_id).update(connection_file=f'{openvpn_files_p}/{ovpn_server.ovpn_setup.setup_name}.ovpn')