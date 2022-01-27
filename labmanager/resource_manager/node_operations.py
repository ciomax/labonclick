from pprint import pprint

import paramiko, yaml, requests, re
from resource_manager.switch_operations import SSHCom
from resource_manager import definitions

pod_list = []

class KubePod():
    def __init__(self,namespace, pod_name, pod_version, pod_image, availabe_ver=None):
        self.namespace = namespace
        self.pod_name = pod_name
        self.pod_image = pod_image
        self.pod_version = pod_version
        self.available_ver = availabe_ver

    def set_latest(self, latest):
        self.available_ver = latest

    def __str__(self):
        return "NS: {}, name: {}, version: {}, latest: {}".format(self.namespace, self.pod_name, self.pod_version, self.available_ver)


class Kubernetes(object):
    def __init__(self, node_ip):
        self.node_ip = node_ip
        self.namespaces = []
        self.pods = []

    def get_namespaces(self, repo_list):
        with SSHCom(self.node_ip, 'root', '$SatCom$') as node_ssh:
            ssh_stdin, ssh_stdout, ssh_stderr = node_ssh.exec_command(command='kubectl get namespaces')
            namespaces = ssh_stdout.readlines()
            for line in namespaces:
                if 'nms' in line:
                    ns = line.split()[0]
                    self.namespaces.append(ns)
            for ns in self.namespaces:
                if ns == 'nms-postgres':
                    continue
                ssh_stdin, ssh_stdout, ssh_stderr = node_ssh.exec_command(command=f'kubectl -n {ns} get pods -o yaml')
                output = ssh_stdout.read()
                parsed_yaml = yaml.safe_load(output)
                for pod in parsed_yaml['items']:
                    if not 'app' in pod['metadata']['labels'].keys():
                        continue
                    pod_name = pod['metadata']['labels']['app']
                    #if ns == 'nms-kafka':
					#	print(pod['spec']['containers']
                    #    pod_version = pod['spec']['containers'][1]['image']
                    #else:
                    pod_version = pod['spec']['containers'][0]['image']
                    pod_image = pod_version.split(':')[-2].split('/')[-1]
                    latest_ver = repo_list.ms.get(pod_image, None)
                    r = re.compile("^100.\d{1,3}.\d{1,3}.\d{1,3}$") #salut2
                    off_list = []
                    if latest_ver:
                        off_list = list(filter(r.match, latest_ver))
                    if latest_ver is not None and len(latest_ver) >=1:
                        if off_list:
                            latest_ver = off_list[-1] + "_test_ver3"
                        else:
                            latest_ver = latest_ver[-1]
                    self.pods.append(KubePod(namespace=ns,
                                             pod_name=pod_name,
                                             pod_image=pod_image,
                                             pod_version=pod_version.split(':')[-1],
                                             availabe_ver=latest_ver))

class DockerRepo(object):
    def __init__(self, catalog, repo):
        self.catalog = catalog
        self.repo = repo
        self.ms = {}

    def get_ms(self):
        try:
            response = requests.get(self.catalog)
            ms_list =response.json()['repositories']
            for ms in ms_list:
                # print(ms)
                self.ms[ms] = self.__get_ms_ver(ms)
            return response.json()['repositories']
        except Exception as err:
            print(err)

    def __get_ms_ver(self, ms_name):
        ''' Get available versions for specific microservice'''
        try:
            response = requests.get(f"http://{self.repo}/v2/{ms_name}/tags/list")
            if response.status_code == 200:
                return response.json()['tags']
            else:
                print("Unable to get container versions.")
                return []
        except Exception as err:
            print(err)






