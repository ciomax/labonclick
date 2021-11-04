from string import Formatter
import pyVmomi
from pyVim.connect import SmartConnect, SmartConnectNoSSL
import ssl
import collections

def get_vms(hostip, username='root', password='$SatCom$'):
    '''
    Function to get list of VMs from ESXi
    :param hostip:
    :param username:
    :param password:
    :return:
    '''
    vmlist = []
    Vmtup = collections.namedtuple('Vmtup', ['vmname', 'vmguestname', 'vmcpunum', 'vmcores', 'vmmem'])

    # s = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    # ssl._create_default_https_context = ssl._create_unverified_context
    # s.verify_mode = ssl.CERT_NONE
    # c = SmartConnect(host=hostip, user=username, pwd=password)
    c = SmartConnectNoSSL(host=hostip, user=username, pwd=password)
    dc = c.content.rootFolder.childEntity[0]
    vms = dc.vmFolder.childEntity
    # print(vms[0].config)
    for vm in vms:
        try:
            instance = Vmtup(vmname=vm.name, vmguestname=vm.config.guestFullName, vmcpunum=vm.config.hardware.numCPU, vmcores=vm.config.hardware.numCoresPerSocket, vmmem=vm.config.hardware.memoryMB)
            # print(instance)
            vmlist.append(instance)
        except:
            continue
    return vmlist



# get_vms(hostip='172.19.1.149')

def strfdelta(tdelta, fmt='{D:02}d {H:02}h {M:02}m {S:02}s', inputtype='timedelta'):
    """Convert a datetime.timedelta object or a regular number to a custom-
    formatted string, just like the stftime() method does for datetime.datetime
    objects.

    The fmt argument allows custom formatting to be specified.  Fields can
    include seconds, minutes, hours, days, and weeks.  Each field is optional.

    Some examples:
        '{D:02}d {H:02}h {M:02}m {S:02}s' --> '05d 08h 04m 02s' (default)
        '{W}w {D}d {H}:{M:02}:{S:02}'     --> '4w 5d 8:04:02'
        '{D:2}d {H:2}:{M:02}:{S:02}'      --> ' 5d  8:04:02'
        '{H}h {S}s'                       --> '72h 800s'

    The inputtype argument allows tdelta to be a regular number instead of the
    default, which is a datetime.timedelta object.  Valid inputtype strings:
        's', 'seconds',
        'm', 'minutes',
        'h', 'hours',
        'd', 'days',
        'w', 'weeks'
    """

    # Convert tdelta to integer seconds.
    if inputtype == 'timedelta':
        remainder = int(tdelta.total_seconds())
    elif inputtype in ['s', 'seconds']:
        remainder = int(tdelta)
    elif inputtype in ['m', 'minutes']:
        remainder = int(tdelta)*60
    elif inputtype in ['h', 'hours']:
        remainder = int(tdelta)*3600
    elif inputtype in ['d', 'days']:
        remainder = int(tdelta)*86400
    elif inputtype in ['w', 'weeks']:
        remainder = int(tdelta)*604800

    f = Formatter()
    desired_fields = [field_tuple[1] for field_tuple in f.parse(fmt)]
    possible_fields = ('W', 'D', 'H', 'M', 'S')
    constants = {'W': 604800, 'D': 86400, 'H': 3600, 'M': 60, 'S': 1}
    values = {}
    for field in possible_fields:
        if field in desired_fields and field in constants:
            values[field], remainder = divmod(remainder, constants[field])
    return f.format(fmt, **values)