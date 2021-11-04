import misaka
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
# from resource_manager.tasks import get_switch_interfaces
from . import definitions
from ckeditor.fields import RichTextField
# Create your models here.
from django.utils.datetime_safe import datetime
from django.dispatch import receiver
from simple_history.models import HistoricalRecords

# from resource_manager.tasks import generate_ovpn_config


from resource_manager.utils import strfdelta

PORT_CHOISES = (
        ("Gigabit Ethernet", "Gigabit Ethernet"),
        ("10-Gigabit Ethernet", "10 Gigabit Ethernet"),
        ("40-Gigabit Ethernet", "40-Gigabit Ethernet"),
        ("100-Gigabit Ethernet", "40-Gigabit Ethernet"),
)

Xena_chassis_type = [
    ('Valkyrie', 'Valkyrie'),
    ('Vulcan', 'Vulcan'),
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.user.username


class Locations(models.Model):
    localtion_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.localtion_name


class Setup(models.Model):
    setup_name = models.CharField(max_length=50, unique=True)
    setup_location = models.ForeignKey(Locations, on_delete = models.RESTRICT)
    setup_members = models.ManyToManyField(User, through="SetupMember")
    setup_type = models.CharField(choices=definitions.Setup_types, max_length=50)
    setup_description = models.TextField(default='', blank=True)

    def __str__(self):
        return self.setup_name

    def get_absolute_url(self):
        return reverse("resource_manager:setup_detail", kwargs={'pk': self.pk})


class SetupMember(models.Model):
    setup = models.ForeignKey(Setup, related_name="membership", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="user_setups", on_delete=models.CASCADE)

class CPE_HW_Type(models.Model):
    cpe_hw_type = models.CharField(max_length=50, unique=True)
    num_gbe_interfaces = models.IntegerField(blank=True, null=True)
    num_sfp_interfaces = models.IntegerField(blank=True, null=True)
    number_of_rx = models.IntegerField(default=1)

    def __str__(self):
        return self.cpe_hw_type


class VSAT(models.Model):
    # cpe_hw_type = models.CharField(max_length=50)
    # cpe_hw_type = models.ForeignKey(CPE_HW_Type, on_delete=models.CASCADE)
    cpe_hw_type = models.CharField(choices=definitions.cpe_hw_types, max_length=50)
    cpe_mac_address = models.CharField(max_length=50, unique=True)
    cpe_console_ip = models.CharField(max_length=50)
    cpe_console_port = models.CharField(max_length=50)
    cpe_gilat_id = models.CharField(max_length=50, blank=True, null=True)
    cpe_setup = models.ForeignKey(Setup, related_name='cpes', on_delete=models.CASCADE)
    cpe_reserved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reserved_vsats')
    cpe_reserved_since = models.DateTimeField(blank=True, null=True)
    history = HistoricalRecords()


    def get_reserved_time(self):
        timediff = timezone.now() - self.cpe_reserved_since
        return strfdelta(timediff, '{D}d {H}:{M:02}:{S:02}')

    def __str__(self):
        return str(self.cpe_hw_type) + " " + str(self.cpe_mac_address)

    def get_absolute_url(self):
        return reverse("resource_manager:cpe_detail", kwargs={'pk': self.pk})

    def set_reserved(self, user):
        pass

    def release_cpe(self):
        self.cpe_reserved_by = None
        self.cpe_reserved_since = None
        self.save()


class KubePod(models.Model):
    pod_setup = models.ForeignKey(Setup, related_name='kubepods', on_delete=models.CASCADE)
    pod_namespace = models.CharField(max_length=20)
    pod_name = models.CharField(max_length=30)
    pod_image = models.CharField(max_length=30)
    pod_version = models.CharField(max_length=30)
    pod_available_ver = models.CharField(max_length=30, default="Unknown", blank=True, null=True)
    pod_state = models.CharField(max_length=30, default="Unknown", blank=True, null=True)

    def __str__(self):
        return self.pod_name + self.pod_version


class PC(models.Model):
    pc_setup = models.ForeignKey(Setup, related_name='pcs', null=True, blank=True, on_delete=models.SET_NULL)
    pc_role = models.CharField(max_length=300, default="")
    pc_ip_address = models.GenericIPAddressField(null=True, blank=True)
    pc_os = models.CharField(max_length=50)
    pc_username = models.CharField(max_length=30, blank=True, null=True)
    pc_password = models.CharField(max_length=40, blank=True, null=True)
    pc_reserved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reserved_pcs')
    pc_reserved_since = models.DateTimeField(null=True, blank=True)

    def release_pc(self):
        self.pc_reserved_by = None
        self.pc_reserved_since = None
        self.save()

    def get_absolute_url(self):
        return reverse("resource_manager:pc_detail", kwargs={'pk': self.pk})

    def get_reserved_time(self):
        timediff = timezone.now() - self.pc_reserved_since
        return strfdelta(timediff, '{D}d {H}:{M:02}:{S:02}')

    def __str__(self):
        return str(self.pc_setup) + self.pc_role


class DLF(models.Model):
    dlf_setup = models.ForeignKey(Setup, related_name = 'dlfs', blank=True, null=True, on_delete=models.DO_NOTHING)
    connected_to = models.ForeignKey(PC, blank=True, null=True, on_delete=models.SET_NULL)
    dlf_name = models.CharField(max_length=50, default="DLF_1")
    dlf_mgmt_ip = models.GenericIPAddressField(blank=True, null=True)
    dlf_mgmt_port = models.IntegerField(blank=True, null=True)
    dlf_port_num = models.IntegerField(default=8)

    def get_absolute_url(self):
        return reverse("resource_manager:dlf_detail", kwargs={'pk': self.pk})


class DLFPort(models.Model):
    parrent_dlf = models.ForeignKey(DLF, related_name='dlf_ports', on_delete=models.CASCADE)
    dlf_port_number = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.parrent_dlf.dlf_name} - port {self.dlf_port_number}"

    def get_absolute_url(self):
        return reverse("resource_manager:dlf_port_update", kwargs={'pk': self.pk})


class Router(models.Model):
    router_setup = models.ForeignKey(Setup, null=True, blank=True, related_name='routers', on_delete=models.DO_NOTHING)
    router_model = models.CharField(max_length=50, null=True, blank=True)
    router_mgmt_ip = models.GenericIPAddressField()
    router_username = models.CharField(max_length=20, blank=True, null=True)
    router_password = models.CharField(max_length=50, blank=True, null=True)
    router_console_connection = models.CharField(max_length=50, blank=True, null=True)
    gilat_id = models.CharField(max_length=50, blank=True, null=True)

    def get_absolute_url(self):
        return reverse("resource_manager:router_detail", kwargs={'pk': self.pk})

    def __str__(self):
        return f"Router-{self.router_model}"


class Switch(models.Model):
    switch_setup = models.ForeignKey(Setup, null=True, blank=True, related_name='switches', on_delete=models.DO_NOTHING)
    switch_role = models.CharField(max_length=50, default="")
    switch_model = models.CharField(max_length=50, blank=True, null=True, default='')
    switch_mgmt_ip = models.GenericIPAddressField()
    switch_username = models.CharField(max_length=20, default="switch", blank=True, null=True)
    switch_password = models.CharField(max_length=40, default='', blank=True, null=True)
    switch_console_ip = models.GenericIPAddressField(default='0.0.0.0', null=True, blank=True)
    switch_console_port = models.IntegerField(blank=True, null=True)
    switch_gilat_id = models.CharField(max_length=30, null=True, blank=True)

    def get_absolute_url(self):
        return reverse("resource_manager:switch_detail", kwargs={'pk': self.pk})

    # def cereate_interfaces(self):
    #     get_switch_interfaces.delay(self.switch_mgmt_ip, self.switch_username, self.switch_password)

    # @property
    # def get_interfaces_number(self):
    #     return self.switch_ge_ports + self.switch_sfp_ports

    def __str__(self):
        return f'{self.switch_role} {self.switch_model}'


class SwitchPort(models.Model):
    parrent_switch = models.ForeignKey(Switch, related_name='sw_ports', on_delete=models.CASCADE)
    switch_port_index = models.CharField(max_length=30, default="")
    port_description = models.CharField(max_length=200, blank=True, null=True)
    port_mode = models.CharField(max_length=20, choices=[
        ("Access", "Access"),
        ("Trunk", "Trunk")],
        default="Access"
        )
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)

    def __str__(self):
        return f"{self.switch_port_index} ({self.parrent_switch.switch_role})"

    class Meta:
        ordering = ['-created']


class RouterPort(models.Model):
    parent_router = models.ForeignKey(Router, on_delete=models.CASCADE, null=True, blank=True, related_name='router_interfaces')

    interface_index = models.CharField(max_length=20)
    port_description = models.CharField(max_length=100, null=True, blank=True)
    router_interface_switch = models.ForeignKey(Switch, on_delete=models.SET_NULL, blank=True, null=True)
    router_interface_switch_if = models.ForeignKey(SwitchPort, on_delete=models.SET_NULL, blank=True, null=True, related_name='router_interface_switch')

    def __str__(self):
        if self.port_description:
            return str(self.parent_router) + " " + self.interface_index + " " + self.port_description
        return str(self.parent_router) + " " + self.interface_index

class CPEPort(models.Model):
    parrent_cpe = models.ForeignKey(VSAT, on_delete= models.CASCADE, related_name="cpe_ports")
    port_ID = models.IntegerField(default=1)
    port_type = models.CharField(max_length = 50, choices=[("Gigabit Ethernet", "Gigabit Ethernet"),
                                ("SFP", "SFP")])
    port_switch = models.ForeignKey(
            Switch,
            on_delete=models.CASCADE,
            blank=True,
            null=True,
            )
    switch_port_id = models.ForeignKey(SwitchPort, on_delete=models.CASCADE, null=True, blank=True, related_name='cpe_ports_switch')
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)


    def get_absolute_url(self):
        return reverse(
            "resource_manager:cpe_detail",
            kwargs={
                'pk': self.parrent_cpe.id
            }
        )

    def __str__(self):
        return f"{self.parrent_cpe.cpe_hw_type} {self.parrent_cpe.cpe_mac_address[8:]}- Port {self.port_ID}"


    class Meta:
        ordering = ['created']



class CPErxPort(models.Model):
    parent_cpe = models.ForeignKey(VSAT, on_delete=models.CASCADE, related_name='cpe_rx_ports')
    rx_id = models.IntegerField(default=1)
    dlf_port = models.ForeignKey(DLFPort, blank=True, null=True, on_delete=models.SET_NULL, related_name='cpe_rx_port_dlf')

    def get_absolute_url(self):
        return reverse(
            "resource_manager:cpe_detail",
            kwargs={
                'pk': self.parent_cpe.id
            }
        )

    def __str__(self):
        return str(self.parent_cpe.cpe_hw_type) + " " + str(self.parent_cpe.cpe_mac_address) + ", port " + str(self.rx_id)




class Intf_PC(models.Model):
    parrent_pc = models.ForeignKey(PC, related_name = 'pc_nics', default=None, null=True, blank=True, on_delete=models.CASCADE)
    pc_if_name = models.CharField(max_length=10, default="")
    pc_switch = models.ForeignKey(Switch, blank=True, null=True, on_delete=models.SET_NULL)
    pc_switch_if = models.ForeignKey(SwitchPort, blank=True, null=True, on_delete=models.SET_NULL, related_name='pc_ports_switch')

    def get_absolute_url(self):
        return reverse(
            "resource_manager:pc_detail",
            kwargs={
                'pk': self.parrent_pc.id
            }
        )

    def __str__(self):
        return 'PC: ' + str(self.parrent_pc) + ", interface: " + self.pc_if_name


class OpenVPNServer(models.Model):
    ovpn_setup = models.ForeignKey(Setup, related_name="openvpn_servers", default=None, null=True, on_delete=models.DO_NOTHING)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    #management_interface = models.ForeignKey(SwitchPort, null=True, blank=True, on_delete=models.DO_NOTHING, related_name="openvpn_connections")
    #internal_interface = models.ForeignKey(SwitchPort, null=True, blank=True, on_delete=models.DO_NOTHING)
    connection_file = models.CharField(max_length=200,blank=True, null=True)

    def get_absolute_url(self):
        return reverse(
            "resource_manager:ovpnserver_detail",
            kwargs={
                'pk': self.pk
            }
        )
# @receiver(models.signals.post_save, sender=OpenVPNServer)
# def create_openvpn_file(sender, instance, created, *args, **kwargs):
#     if created:
#         generate_ovpn_config(instance.id, instance.ip_address)

class CiscoVPNServer(models.Model):
    cisco_vpn_setup = models.ForeignKey(Setup, related_name="cisco_servers", default=None, null=True, on_delete=models.DO_NOTHING)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    #management_interface = models.ForeignKey(SwitchPort, null=True, blank=True, on_delete=models.DO_NOTHING, related_name="openvpn_connections")
    #internal_interface = models.ForeignKey(SwitchPort, null=True, blank=True, on_delete=models.DO_NOTHING)
    connection_file = models.FileField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse(
            "resource_manager:ciscovpn_detail",
            kwargs={
                'pk': self.pk
            }
        )


class ESXI(models.Model):
    esxi_setup = models.ForeignKey(Setup, related_name='esxis', null=True, blank=True, on_delete=models.SET_NULL)
    esxi_ip_address = models.GenericIPAddressField()
    esxi_username = models.CharField(max_length=50, default='root')
    esxi_password = models.CharField(max_length=50, default="", blank=True, null=True)

    def get_absolute_url(self):
        return reverse(
            "resource_manager:esxi_detail",
            kwargs={
                'pk': self.pk
            }
        )

    def __str__(self):
        return str(self.esxi_setup) + "-" + self.esxi_ip_address

    @property
    def get_total_vms(self):
        '''
        get total number of VMs
        :return:
        '''
        pass
        # return self.related.count()

    @property
    def get_reserved_vms(self):
        '''
        Get number of reserved VMs
        :return:
        '''
        return VM.objects.filter(vm_esxi_id__exact=self.pk, vm_reserved_by__isnull = False).count()




class VM(models.Model):
    vm_esxi = models.ForeignKey(ESXI, related_name='vms', null=True, on_delete=models.CASCADE)
    vm_name = models.CharField(max_length=100)
    vm_guest_FullName = models.CharField(max_length=100, blank=True, null=True)
    vm_numCPU = models.IntegerField(blank=True, null=True)
    vm_cores_socket = models.IntegerField(blank=True, null=True)
    vm_memory = models.IntegerField(blank=True, null=True)
    vm_reserved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reserved_vms')
    vm_reserved_time = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)

    def get_reserved_number(self):
        num_reserved = models.VM.objects.filter(vm_reserved_by="").count()
        return num_reserved

    def get_absolute_url(self):
        return reverse("resource_manager:vm_detail", kwargs={'pk': self.pk})

    def get_reserved_time(self):
        timediff = timezone.now() - self.vm_reserved_time
        return strfdelta(timediff, '{D}d {H}:{M:02}:{S:02}')

    def reserve_vm(self, user):
        self.vm_reserved_by = user
        self.vm_reserved_time = timezone.now()
        self.save()

    def release_vm(self):
        self.vm_reserved_by = None
        self.vm_reserved_time = None
        self.save()

    def __str__(self):
        return f'{self.vm_name} - ESXi {self.vm_esxi.esxi_ip_address}'

    class Meta:
        ordering = ['created']

kontron_node_ids = [
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6),
    (7, 7),
    (8, 8),
    (9, 9),
]

class Kontron(models.Model):
    kontron_setup = models.ForeignKey(Setup, on_delete=models.SET_NULL, null=True, blank=True, related_name='kontrons')
    d_server_id = models.IntegerField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse("resource_manager:kontron_detail", kwargs={'pk': self.pk})

    def __str__(self):
        return f"Kontron-{self.d_server_id}"

kontron_node_types = [
    ('UPM-5', 'UPM-5'),
    ('UPM-6', 'UPM-6'),
    ('UPM-7', 'UPM-7'),
]


class Kontron_node(models.Model):

    # class Meta:
    #     ordering = []
    parent_kontron = models.ForeignKey(Kontron,
                                       on_delete=models.CASCADE,
                                       null=True,
                                       blank=True,
                                       related_name='kontron_nodes')
    node_id = models.IntegerField(choices=kontron_node_ids, null=True, blank=True)
    node_type = models.CharField(max_length=20,
                                 choices=kontron_node_types, default='UPM-6')


    def get_absolute_url(self):
        return reverse("resource_manager:kontron_detail", kwargs={'pk': self.parent_kontron.pk})


class Kontron_interface(models.Model):
    parent_kontron = models.ForeignKey(
        Kontron,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='kontron_interface')
    interface_name = models.CharField(max_length=30)
    interface_description = models.CharField(max_length=50)
    switch = models.ForeignKey(Switch, on_delete=models.SET_NULL, null=True, blank=True)
    switch_interface_id = models.ForeignKey(SwitchPort, on_delete=models.SET_NULL, null=True, blank=True, related_name='kontoron_interfaces')

    def __str__(self):
        return f"{str(self.parent_kontron)}-{self.interface_name}"

class VXGW(models.Model):

    vxgw_model_CHOISES = [
        ('MX204', 'MX204'),
        ('MX5', 'MX5'),
        ('VMX', 'VMX')
    ]
    vxgw_setup = models.ForeignKey(Setup, on_delete=models.SET_NULL, null=True, blank=True, related_name='vxgws')
    vxgw_model = models.CharField(max_length=69, choices=vxgw_model_CHOISES, default='MX204')
    vxgw_sw_version = models.CharField(max_length=50, blank=True, null=True)
    vxgw_management_ip = models.GenericIPAddressField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("resource_manager:vxgw_detail", kwargs={'pk': self.pk})

    def __str__(self):
        return f'VXGW-{self.vxgw_model} '

class VXGW_interface(models.Model):
    parent_vxgw = models.ForeignKey(VXGW, on_delete=models.CASCADE, related_name='vxgwInterfaces')
    interface_index = models.CharField(max_length=20)
    interface_description = models.CharField(max_length=30, null=True, blank=True)
    switch = models.ForeignKey(Switch, on_delete=models.SET_NULL, blank=True, null=True)
    switch_if = models.ForeignKey(SwitchPort, on_delete=models.SET_NULL, blank=True, null=True, related_name='vxgw_if_switch')
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)

    def __str__(self):
        return str(self.parent_vxgw) + self.interface_index + " " + self.interface_description

    class Meta:
        ordering = ['created']

# Spectrum
class SpectrumAnalyzer(models.Model):

    spectrum_setup = models.ForeignKey(Setup, on_delete=models.SET_NULL, null=True, blank=True, related_name='spectrums')
    management_IP = models.GenericIPAddressField(blank=True, null=True)
    management_interface = models.ForeignKey(SwitchPort, on_delete=models.SET_NULL, blank=True, null=True, related_name='spectrum_port')
    username = models.CharField(max_length=30, blank=True, null=True)
    password = models.CharField(max_length=30, blank=True, null=True)
    used_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reserved_spectrum')
    reserved_since = models.DateTimeField(null=True, blank=True)

    def release(self):
        self.used_by = None
        self.reserved_since = None
        self.save()

    def get_reserved_time(self):
        timediff = timezone.now() - self.reserved_since
        return strfdelta(timediff, '{D}d {H}:{M:02}:{S:02}')

    def get_absolute_url(self):
        return reverse("resource_manager:spectrum_detail", kwargs={'pk': self.pk})

    def __str__(self):
        return f'Spectrum-{self.management_IP}'
#Xena
class Xena(models.Model):
    chassis_type = models.CharField(choices=Xena_chassis_type, max_length=30)
    location = models.ForeignKey(Locations, on_delete=models.SET_NULL, null=True, blank=True)
    management_ip = models.GenericIPAddressField()
    password = models.CharField(max_length=40, null=True, blank=True)

    @property
    def count_ports(self):
        return Xena_port.objects.filter(parent_module__module_chassis=self.pk).count

    @property
    def count_reserved_ports(self):
        return Xena_port.objects.filter(parent_module__module_chassis=self.pk, used_by__isnull=False ).count

    def get_absolute_url(self):
        return reverse("resource_manager:xena_detail", kwargs={'pk': self.pk})

class Xena_Module(models.Model):
    module_chassis = models.ForeignKey(Xena, on_delete=models.CASCADE, null=True, blank=True, related_name='xena_module')
    module_id = models.PositiveIntegerField()
    module_num_ports = models.PositiveIntegerField()





class Xena_port(models.Model):
    parent_module = models.ForeignKey(Xena_Module, on_delete=models.CASCADE, blank=True, null=True, related_name='xena_module_port')
    port_index = models.PositiveIntegerField(default=0)
    port_setup = models.ForeignKey(Setup, on_delete=models.SET_NULL, blank=True, null=True, related_name='xena_ports')
    port_switch = models.ForeignKey(Switch, on_delete=models.SET_NULL, blank=True, null=True)
    port_switch_if = models.ForeignKey(SwitchPort, on_delete=models.SET_NULL, blank=True, null=True, related_name='xena_port_switch')
    used_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reserved_xena')
    reserved_since = models.DateTimeField(null=True, blank=True)

    def release(self):
        self.used_by = None
        self.reserved_since = None
        self.save()

    def __str__(self):
        return f"Xena-{self.parent_module.module_chassis.chassis_type}-{self.parent_module.module_id}-{self.port_index}"

    def get_reserved_time(self):
        timediff = timezone.now() - self.reserved_since
        return strfdelta(timediff, '{D}d {H}:{M:02}:{S:02}')


# IXIA
class IXIA(models.Model):
    location = models.ForeignKey(Locations, on_delete=models.SET_NULL, null=True, blank=True)
    management_ip = models.GenericIPAddressField()

    @property
    def count_ports(self):
        return IXIA_port.objects.filter(parent_module__module_chassis=self.pk).count

    @property
    def count_reserved_ports(self):
        return IXIA_port.objects.filter(parent_module__module_chassis=self.pk, used_by__isnull=False ).count

    def get_absolute_url(self):
        return reverse("resource_manager:ixia_detail", kwargs={'pk': self.pk})


class IXIA_Module(models.Model):
    module_chassis = models.ForeignKey(IXIA, on_delete=models.CASCADE, null=True, blank=True, related_name='ixia_module')
    module_id = models.PositiveIntegerField()
    module_num_ports = models.PositiveIntegerField()


class IXIA_port(models.Model):
    parent_module = models.ForeignKey(IXIA_Module, on_delete=models.CASCADE, blank=True, null=True, related_name='ixia_module_port')
    port_index = models.PositiveIntegerField(default=0)
    port_setup = models.ForeignKey(Setup, on_delete=models.SET_NULL, blank=True, null=True, related_name='ixia_ports')
    port_switch = models.ForeignKey(Switch, on_delete=models.SET_NULL, blank=True, null=True)
    port_switch_if = models.ForeignKey(SwitchPort, on_delete=models.SET_NULL, blank=True, null=True, related_name='ixia_port_switch')
    used_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reserved_ixia')
    reserved_since = models.DateTimeField(null=True, blank=True)

    def release(self):
        self.used_by = None
        self.reserved_since = None
        self.save()

    def get_reserved_time(self):
        timediff = timezone.now() - self.reserved_since
        return strfdelta(timediff, '{D}d {H}:{M:02}:{S:02}')

    def __str__(self):
        return f"IXIA port-{self.parent_module.module_id}-{self.port_index}"


class SetupPosts(models.Model):
    user = models.ForeignKey(User, related_name='posts',null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now=True)
    # message = models.TextField()
    message = RichTextField(blank=True, null=True)
    message_title = models.CharField(max_length=50, default="", blank=True, null=True)
    message_html = models.TextField(editable=False)
    setup = models.ForeignKey(Setup, related_name='posts', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.message

    def save(self, *args, **kwargs):
        self.message_html = misaka.html(self.message)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["user", "message"]


class SetupWiki(models.Model):
    body = RichTextField(blank=True, null=True)
    setup = models.ForeignKey(Setup, related_name='wiki', null=True, blank=True, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse("resource_manager:setup_detail", kwargs={'pk': self.setup.pk})