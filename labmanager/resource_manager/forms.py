from django import forms
from resource_manager.models import VSAT, CPEPort, Switch, SetupMember, PC, SwitchPort, DLF, DLFPort, CPErxPort, \
    OpenVPNServer, ESXI, Intf_PC, Router, Kontron, Kontron_node, Kontron_interface, VXGW, VXGW_interface, RouterPort, \
    Xena, Xena_Module, Xena_port, Setup, IXIA, IXIA_Module, CiscoVPNServer, SpectrumAnalyzer, SetupPosts, SetupWiki
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import get_user_model
# from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext, ugettext_lazy as _


class SetupForm(forms.ModelForm):

    class Meta:
        model = Setup

        exclude = [
            'setup_members',
        ]

        widgets = {
            'setup_name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'setup_location': forms.Select(attrs={
                'class': 'form-control',
            }),
            'setup_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'setup_description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'team or setup usage',
            })
        }

    def __init__(self, *args, **kwargs):
        super(SetupForm, self).__init__(*args, **kwargs)
        self.fields['setup_name'].label = 'Setup Name'
        self.fields['setup_location'].label = 'Setup Location'
        self.fields['setup_description'].label = 'Setup description'


class CPEForm(forms.ModelForm):

    class Meta:
        model = VSAT
        # fields = "__all__"
        exclude = [
            'cpe_reserved_by',
            'cpe_reserved_since',
        ]

        widgets = {
            'cpe_hw_type': forms.Select(attrs={
                'class': 'form-control',
                }),
            'cpe_mac_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00:A0:AC:11:22:33'
            }),
            'cpe_console_ip': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1.2.3.4'
            }),
            'cpe_console_port': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0-65535'
            }),
            'cpe_gilat_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional'
            }),
            'cpe_setup': forms.Select(attrs={
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(CPEForm, self).__init__(*args, **kwargs)
        self.fields['cpe_hw_type'].label = 'CPE HW Type'
        self.fields['cpe_mac_address'].label = 'MAC Address'
        self.fields['cpe_console_ip'].label = 'Console connection IP address'
        self.fields['cpe_console_port'].label = 'Console connection port number'
        self.fields['cpe_gilat_id'].label = 'Gilat Internal ID'
        self.fields['cpe_setup'].label = 'Setup'


class VXGWForm(forms.ModelForm):

    class Meta:
        model = VXGW

        exclude = [
            'vxgw_sw_version',
        ]

        widgets = {
            'vxgw_setup': forms.Select(attrs={
                'class': 'form-control',
            }),
            'vxgw_model': forms.Select(attrs={
                'class': 'form-control',
            }),
            'vxgw_management_ip': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'optional',
            })
        }

    def __init__(self, *args, **kwargs):
        super(VXGWForm, self).__init__(*args, **kwargs)
        self.fields['vxgw_setup'].label = 'Setup'
        self.fields['vxgw_model'].label = 'VXGW Model'
        self.fields['vxgw_management_ip'].label = 'Management IP'


class XenaForm(forms.ModelForm):

    class Meta:
        model = Xena

        fields = '__all__'

        widgets = {
            'chassis_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'location': forms.Select(attrs={
                'class': 'form-control',
            }),
            'management_ip': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'password': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'optional'
            })
        }

    def __init__(self, *args, **kwargs):
        super(XenaForm, self).__init__(*args, **kwargs)
        self.fields['chassis_type'].label = 'Chassis Type'
        self.fields['location'].label = 'Chassis Location'
        self.fields['management_ip'].label = 'Management IP'
        self.fields['password'].label = 'Password'


class XenaModuleForm(forms.ModelForm):

    class Meta:
        model = Xena_Module

        exclude = [
            'module_chassis',
        ]

        widgets = {
            'module_id': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'module_num_ports': forms.TextInput(attrs={
                'class': 'form-control',
            })
        }

    def __init__(self, *args, **kwargs):
        super(XenaModuleForm, self).__init__(*args, **kwargs)
        self.fields['module_id'].label = 'Module ID'
        self.fields['module_num_ports'].label = 'Number of ports'


class XenaPortForm(forms.ModelForm):

    class Meta:
        model = Xena_port

        exclude = [
            'parent_module',
            'port_index',
            'used_by',
            'reserved_since',
        ]

        widgets = {
            'port_setup': forms.Select(attrs={
                'class': 'form-control',
            }),
            'port_switch': forms.Select(attrs={
                'class': 'form-control',
            }),
            'port_switch_if': forms.Select(attrs={
                'class': 'form-control',
            })
        }

    def __init__(self, *args, **kwargs):
        xena_instance = kwargs.pop('par_xena', None)
        super(XenaPortForm, self).__init__(*args, **kwargs)

        self.fields['port_setup'].label = 'Connected to Setup'
        self.fields['port_switch'].label = 'Select Switch'
        self.fields['port_switch_if'].label = 'Select Switch Port'
        self.fields['port_switch'].queryset = Switch.objects.none()
        self.fields['port_switch_if'].queryset = SwitchPort.objects.none()

        if xena_instance:
            # Show only Setups on same Location
            self.fields["port_setup"].queryset = Setup.objects.filter(
                setup_location=xena_instance.location
                )
        if 'port_setup' in self.data:
            try:
                port_setup_id = int(self.data.get('port_setup'))
                self.fields['port_switch'].queryset = Switch.objects.filter(switch_setup_id__exact=port_setup_id)
            except (ValueError, TypeError):
                pass
        if 'port_switch' in self.data:
            try:
                port_switch_id = int(self.data.get('port_switch'))
                self.fields['port_switch_if'].queryset = SwitchPort.objects.filter(parrent_switch_id=port_switch_id)
            except (ValueError, TypeError):
                pass


class VXGWInterfaceForm(forms.ModelForm):

    class Meta:
        model = VXGW_interface

        exclude = [
            'parent_vxgw',
            'interface_index',
        ]

        widgets = {
            'interface_description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'interface description',
            }),
            'switch': forms.Select(attrs={
                'class': 'form-control',
            }),
            'switch_if': forms.Select(attrs={
                'class': 'form-control',
            })
        }

    def __init__(self, *args, **kwargs):
        vxgw_instance = kwargs.pop('par_vxgw', None)
        super(VXGWInterfaceForm, self).__init__(*args, **kwargs)
        setup = vxgw_instance.vxgw_setup
        setup_name = setup.setup_name

        self.fields['interface_description'].label = 'Description'
        self.fields['switch'].label = 'Switch'
        self.fields['switch_if'].label = 'Switch Interface'
        self.fields['switch_if'].queryset = SwitchPort.objects.none()

        if vxgw_instance:
            self.fields['switch'].queryset = Switch.objects.filter(
                switch_setup__setup_name=setup)

        if 'switch' in self.data:
            try:
                port_switch_id = int(self.data.get('switch'))
                self.fields['switch_if'].queryset = SwitchPort.objects.filter(parrent_switch_id=port_switch_id)
            except (ValueError, TypeError):
                pass


class RouterForm(forms.ModelForm):

    class Meta:
        model = Router

        fields = '__all__'

        widgets = {
            'router_setup': forms.Select(attrs={
                'class': 'form-control',
            }),
            'router_model': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'router_mgmt_ip': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'router_username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'optional',
            }),
            'router_password': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'gilat_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional',
            }),
            'router_console_connection': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'x.x.x.x port 1234',
            })
        }

    def __init__(self, *args, **kwargs):
        super(RouterForm, self).__init__(*args, **kwargs)
        self.fields['router_setup'].label = 'Setup'
        self.fields['router_model'].label = 'Model'
        self.fields['router_mgmt_ip'].label = 'Management IP'
        self.fields['router_username'].label = 'Username'
        self.fields['router_password'].label = 'Password'
        self.fields['gilat_id'].label = 'Gilat Internal ID'
        self.fields['router_console_connection'].label = 'Console connection'


class Router_interfaceForm(forms.ModelForm):
    class Meta:
        model = RouterPort

        exclude = [
            'parent_router',
        ]

        widgets = {
            'interface_index': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ge0/1',
            }),
            'port_description': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'router_interface_switch': forms.Select(attrs={
                'class': 'form-control',
            }),
            'router_interface_switch_if': forms.Select(attrs={
                'class': 'form-control',
            })
        }

    def __init__(self, *args, **kwargs):
        router_instance = kwargs.pop('p_router', None)
        super(Router_interfaceForm, self).__init__(*args, **kwargs)
        setup = router_instance.router_setup
        setup_name = setup.setup_name
        self.fields['interface_index'].label = 'Interface Index'
        self.fields['port_description'].label = 'Interface Description'
        self.fields['router_interface_switch'].label = 'Connected to Switch'
        self.fields['router_interface_switch_if'].label = 'Switch Interface'
        self.fields['router_interface_switch_if'].queryset = SwitchPort.objects.none()

        if router_instance:
            # Show only switches on same setup
            self.fields["router_interface_switch"].queryset = Switch.objects.filter(
                switch_setup__setup_name=setup)
        if 'router_interface_switch' in self.data:
            try:
                port_switch_id = int(self.data.get('router_interface_switch'))
                self.fields['router_interface_switch_if'].queryset = SwitchPort.objects.filter(parrent_switch_id=port_switch_id)
            except (ValueError, TypeError):
                pass


class RouterInterfaceUpdateForm(forms.ModelForm):

    class Meta:
        model = RouterPort
        exclude = [
            'parent_router',
        ]

        widgets = {
            'interface_index': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ge0/1',
            }),
            'port_description': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'router_interface_switch': forms.Select(attrs={
                'class': 'form-control',
            }),
            'router_interface_switch_if': forms.Select(attrs={
                'class': 'form-control',
            })
        }

    def __init__(self, *args, **kwargs):
        router_instance = kwargs.pop('p_router', None)
        interface=kwargs.pop('pk', None)
        super(RouterInterfaceUpdateForm, self).__init__(*args, **kwargs)
        setup = router_instance.router_setup
        setup_name = setup.setup_name

        self.fields['interface_index'].label = 'Interface Index'
        self.fields['port_description'].label = 'Interface Description'
        self.fields['router_interface_switch'].label = 'Connected to Switch'
        self.fields['router_interface_switch_if'].label = 'Switch Interface'

        if router_instance:
            self.fields["router_interface_switch"].queryset = Switch.objects.filter(
                switch_setup__setup_name=setup_name)
        if 'router_interface_switch' in self.data:
            try:
                port_switch_id = int(self.data.get('router_interface_switch'))
                self.fields['router_interface_switch_if'].queryset = SwitchPort.objects.filter(parrent_switch_id=port_switch_id)
            except (ValueError, TypeError):
                pass


class KontronForm(forms.ModelForm):

    class Meta:
        model = Kontron

        fields = '__all__'

        widgets = {
            'kontron_setup': forms.Select(attrs={
                'class': 'form-control',
            }),
            'd_server_id': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(KontronForm, self).__init__(*args, **kwargs)
        self.fields['kontron_setup'].label = 'Setup'
        self.fields['d_server_id'].label = 'D-Server-ID'


class KontronNodeForm(forms.ModelForm):

    class Meta:
        model = Kontron_node

        # fields = '__all__'
        exclude = [
            'parent_kontron',
        ]

        widgets = {
            'node_id': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': '1-9',
            }),
            'node_type': forms.Select(attrs={
                'class': 'form-control',
        }),
        }

    def __init__(self, *args, **kwargs):
        super(KontronNodeForm, self).__init__(*args, **kwargs)
        self.fields['node_id'].label = 'Node ID'
        self.fields['node_type'].label = 'Node Type'


class Kontron_interfaceForm(forms.ModelForm):
    class Meta:
        model = Kontron_interface

        exclude = [
            'parent_kontron',
        ]

        widgets = {
            'interface_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1/1/1',
            }),
            'interface_description': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'switch': forms.Select(attrs={
                'class': 'form-control',
            }),
            'switch_interface_id': forms.Select(attrs={
                'class': 'form-control',
            })
        }

    def __init__(self, *args, **kwargs):
        kontron_instance = kwargs.pop('p_kont', None)
        super(Kontron_interfaceForm, self).__init__(*args, **kwargs)
        setup = kontron_instance.kontron_setup
        setup_name = setup.setup_name
        self.fields['interface_name'].label = 'Interface Index'
        self.fields['interface_description'].label = 'Interface Description'
        self.fields['switch'].label = 'Connected to Switch'
        self.fields['switch_interface_id'].label = 'Switch Interface'
        self.fields['switch_interface_id'].queryset = SwitchPort.objects.none()

        if kontron_instance:
            # Show only switches on same setup
            self.fields["switch"].queryset = Switch.objects.filter(
                switch_setup__setup_name=setup)
        if 'switch' in self.data:
            try:
                port_switch_id = int(self.data.get('switch'))
                self.fields['switch_interface_id'].queryset = SwitchPort.objects.filter(parrent_switch_id=port_switch_id)
            except (ValueError, TypeError):
                pass


class KontronInterfaceUpdateForm(forms.ModelForm):

    class Meta:
        model = Kontron_interface
        exclude = [
            'parent_kontron',
        ]

        widgets = {
            'interface_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1/1/1',
            }),
            'interface_description': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'switch': forms.Select(attrs={
                'class': 'form-control',
            }),
            'switch_interface_id': forms.Select(attrs={
                'class': 'form-control',
            })
        }

    def __init__(self, *args, **kwargs):
        kontron_instance = kwargs.pop('p_kont', None)
        interface=kwargs.pop('pk', None)
        super(KontronInterfaceUpdateForm, self).__init__(*args, **kwargs)
        setup = kontron_instance.kontron_setup
        setup_name = setup.setup_name

        self.fields['interface_name'].label = 'Interface Index'
        self.fields['interface_description'].label = 'Interface Description'
        self.fields['switch'].label = 'Connected to Switch'
        self.fields['switch_interface_id'].label = 'Switch Interface'
        self.fields['switch_interface_id'].queryset = SwitchPort.objects.none()

        if kontron_instance:
            # Show only switches on same setup
            self.fields["switch"].queryset = Switch.objects.filter(
                switch_setup__setup_name=setup_name)
        if 'switch' in self.data:
            try:
                port_switch_id = int(self.data.get('switch'))
                self.fields['switch_interface_id'].queryset = SwitchPort.objects.filter(parrent_switch_id=port_switch_id)
            except (ValueError, TypeError):
                pass


class SwitchForm(forms.ModelForm):


    class Meta:
        model = Switch
        fields = '__all__'
        exclude = [
            'switch_model',
        ]

        widgets = {
            'switch_setup': forms.Select(attrs={
                'class': 'form-control',
                }),
            'switch_role': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'switch_mgmt_ip': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'switch_username': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'switch_password': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'switch_console_ip': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'switch_console_port': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'switch_gilat_id': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(SwitchForm, self).__init__(*args, **kwargs)
        self.fields['switch_setup'].label = 'Switch Setup'
        self.fields['switch_role'].label = 'Role (TOR, NMS SW, VSAT, DPS etc.)'
        self.fields['switch_mgmt_ip'].label = 'Management IP'
        self.fields['switch_username'].label = 'Username (optional)'
        self.fields['switch_password'].label = 'Password (optional)'
        self.fields['switch_console_ip'].label = 'Console connection IP'
        self.fields['switch_console_port'].label = 'Console connection port number'
        self.fields['switch_gilat_id'].label = 'Gilat Internal ID (optional)'


class DLFForm(forms.ModelForm):

    class Meta:
        model = DLF
        # fields = '__all__'
        exclude = [
            'dlf_port_num',
                   ]

        widgets = {
            'dlf_setup': forms.Select(attrs={
                'class': 'form-control',
            }),
            'connected_to': forms.Select(attrs={
                'class': 'form-control',
            }),
            'dlf_name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'dlf_mgmt_ip': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'dlf_mgmt_port': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(DLFForm, self).__init__(*args, **kwargs)
        self.fields['dlf_setup'].label = 'Setup'
        self.fields['connected_to'].label = 'Connected to PC'
        self.fields['dlf_name'].label = 'DLF name (to distinguish between DLFs on same setup)'
        self.fields['dlf_mgmt_ip'].label = 'DLF Management IP'
        self.fields['dlf_mgmt_port'].label = 'DLF Management Port'


class PCForm(forms.ModelForm):

    class Meta:
        model = PC
        # fields = "__all__"
        exclude = [
            'pc_reserved_by',
            'pc_reserved_since',
        ]

        widgets = {
            'pc_setup': forms.Select(attrs={'class': 'form-control'}),
            'pc_ip_address': forms.TextInput(attrs={'class': 'form-control'}),
            'pc_role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Monitoring/DLF Management etc'}),
            'pc_os': forms.TextInput(attrs={'class': 'form-control'}),
            'pc_username': forms.TextInput(attrs={'class': 'form-control'}),
            'pc_password': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(PCForm, self).__init__(*args, **kwargs)
        self.fields['pc_setup'].label = 'Select Setup'
        self.fields['pc_ip_address'].label = 'IP address'
        self.fields['pc_role'].label = 'PC Role (serves as)'
        self.fields['pc_os'].label = 'PC Operating System (Windows, Linux)'
        self.fields['pc_username'].label = 'Username (optional)'
        self.fields['pc_password'].label = 'Password (optional)'


class PcInterfaceForm(forms.ModelForm):

    class Meta:
        model = Intf_PC

        exclude = [
            'parrent_pc',
        ]

        widgets = {
            'pc_if_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'eth1',
            }),
            'pc_switch': forms.Select(attrs={
                'class': 'form-control',
            }),
            'pc_switch_if': forms.Select(attrs={
                'class': 'form-control',
            })
        }

    def __init__(self, *args, **kwargs):
        pc_instance = kwargs.pop('par_pc', None)
        super(PcInterfaceForm, self).__init__(*args, **kwargs)
        setup = pc_instance.pc_setup
        setup_name = setup.setup_name

        self.fields['pc_if_name'].label = 'Interface name'
        self.fields['pc_switch'].label = 'Select Switch'
        self.fields['pc_switch_if'].label = 'Select Switch Port'
        self.fields['pc_switch_if'].queryset = SwitchPort.objects.none()

        if pc_instance:
            # Show only switches on same setup
            self.fields["pc_switch"].queryset = Switch.objects.filter(
                switch_setup__setup_name=setup)
        if 'pc_switch' in self.data:
            try:
                port_switch_id = int(self.data.get('pc_switch'))
                self.fields['pc_switch_if'].queryset = SwitchPort.objects.filter(parrent_switch_id=port_switch_id)
            except (ValueError, TypeError):
                pass


class PcInterfaceUpdateForm(forms.ModelForm):

    class Meta:
        model = Intf_PC

        exclude = [
            'parrent_pc',
        ]

        widgets = {
            'pc_if_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'eth1',
            }),
            'pc_switch': forms.Select(attrs={
                'class': 'form-control',
            }),
            'pc_switch_if': forms.Select(attrs={
                'class': 'form-control',
            })
        }

    def __init__(self, *args, **kwargs):
        pc_instance = kwargs.pop('par_pc', None)
        super(PcInterfaceUpdateForm, self).__init__(*args, **kwargs)

        setup = pc_instance.pc_setup
        setup_name = setup.setup_name

        self.fields['pc_if_name'].label = 'Interface name'
        self.fields['pc_switch'].label = 'Select Switch'
        self.fields['pc_switch_if'].label = 'Select Switch Port'
        self.fields['pc_switch_if'].queryset = SwitchPort.objects.none()

        if pc_instance:
            # Show only switches on same setup
            self.fields["pc_switch"].queryset = Switch.objects.filter(
                switch_setup__setup_name=setup)
        if 'pc_switch' in self.data:
            try:
                port_switch_id = int(self.data.get('pc_switch'))
                self.fields['pc_switch_if'].queryset = SwitchPort.objects.filter(parrent_switch_id=port_switch_id)
            except (ValueError, TypeError):
                pass



class UpdateCPEPortForm(forms.ModelForm):

    class Meta:
        model = CPEPort
        # fields = "__all__"
        exclude = [
            'parrent_cpe',
            'port_ID',
            'port_type',
        ]

        widgets = {
            'port_switch': forms.Select(attrs={'class': 'form-control'}),
            'switch_port_id': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(UpdateCPEPortForm, self).__init__(*args, **kwargs)
        # Get setup name from parent cpe
        instance = kwargs.pop("instance", None)
        setup = instance.parrent_cpe.cpe_setup

        self.fields['port_switch'].label = 'Select Switch'
        self.fields['switch_port_id'].label = 'Select Switch Port'
        self.fields["switch_port_id"].queryset = SwitchPort.objects.none() # Don't show any options before switch is chosen
        if instance:
            # Show only switches on same setup
            self.fields["port_switch"].queryset = Switch.objects.filter(
                switch_setup__setup_name=setup)
        if 'port_switch' in self.data:
            try:
                port_switch_id = int(self.data.get('port_switch'))
                self.fields['switch_port_id'].queryset = SwitchPort.objects.filter(parrent_switch_id=port_switch_id)
            except (ValueError, TypeError):
                print("Exceptuioins (((((((((")
                pass


class OVPNForm(forms.ModelForm):

    class Meta:
        model = OpenVPNServer

        exclude = ('connection_file',)

        widgets = {
            'ovpn_setup': forms.Select(attrs={'class': 'form-control'}),
            'ip_address': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(OVPNForm, self).__init__(*args, **kwargs)
        self.fields['ovpn_setup'].label = 'Setup'
        self.fields['ip_address'].label = 'IP address'



class CiscoVPNForm(forms.ModelForm):

    class Meta:
        model = CiscoVPNServer

        fields = '__all__'

        widgets = {
            'cisco_vpn_setup': forms.Select(attrs={'class': 'form-control'}),
            'ip_address': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(CiscoVPNForm, self).__init__(*args, **kwargs)
        self.fields['cisco_vpn_setup'].label = 'Setup'
        self.fields['ip_address'].label = 'IP address'
        self.fields['connection_file'].label = 'Connection File'

class SpectrumForm(forms.ModelForm):

    class Meta:
        model = SpectrumAnalyzer

        exclude = [
            'used_by',
            'reserved_since',
        ]

        widgets = {
            'spectrum_setup': forms.Select(attrs={'class': 'form-control'}),
            'management_IP': forms.TextInput(attrs={'class': 'form-control'}),
            'management_interface': forms.Select(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(SpectrumForm, self).__init__(*args, **kwargs)
        self.fields['spectrum_setup'].label = 'Setup'
        self.fields['management_IP'].label = 'Management IP address'
        self.fields['management_interface'].label = 'Management Interface'
        self.fields['username'].label = 'Username'
        self.fields['password'].label = 'Password'


class UpdateCPERXPortForm(forms.ModelForm):

    class Meta:
        model = CPErxPort

        fields = (
            'dlf_port',
        )

        widgets = {
            'dlf_port': forms.Select(attrs={
                'class': 'form-control col-xs-4',
                'data-width': "50%",

            })
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        setup_name = instance.parent_cpe.cpe_setup
        super(UpdateCPERXPortForm, self).__init__(*args, **kwargs)
        self.fields['dlf_port'].label = 'Select DLF Port'
        if instance:
            self.fields['dlf_port'].queryset = DLFPort.objects.filter(parrent_dlf__dlf_setup__setup_name=setup_name)



class UserForm(forms.ModelForm):

    password = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput)

    class Meta:
        model = User
        # fields = ('username', 'email', 'password')
        fields = ('username', 'first_name', 'last_name', 'email', 'password')


class ESXIForm(forms.ModelForm):

    class Meta:
        model = ESXI

        fields = '__all__'

        widgets = {
            'esxi_setup': forms.Select(attrs={
                'class': 'form-control'
            }),
            'esxi_ip_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1.1.1.1'
            }),
            'esxi_username': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'esxi_password': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'optional'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(ESXIForm, self).__init__(*args, **kwargs)
        self.fields['esxi_setup'].label = 'Setup'
        self.fields['esxi_ip_address'].label = 'IP address'
        self.fields['esxi_username'].label = 'Username'
        self.fields['esxi_password'].label = 'Password'



#IXIA


class IxiaForm(forms.ModelForm):

    class Meta:
        model = IXIA

        fields = '__all__'

        widgets = {
            'location': forms.Select(attrs={
                'class': 'form-control',
            }),
            'management_ip': forms.TextInput(attrs={
                'class': 'form-control',
            })
        }

    def __init__(self, *args, **kwargs):
        super(IxiaForm, self).__init__(*args, **kwargs)
        self.fields['location'].label = 'Chassis Location'
        self.fields['management_ip'].label = 'Management IP'


class IxiaModuleForm(forms.ModelForm):

    class Meta:
        model = IXIA_Module

        exclude = [
            'module_chassis',
        ]

        widgets = {
            'module_id': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'module_num_ports': forms.TextInput(attrs={
                'class': 'form-control',
            })
        }

    def __init__(self, *args, **kwargs):
        super(IxiaModuleForm, self).__init__(*args, **kwargs)
        self.fields['module_id'].label = 'Module ID'
        self.fields['module_num_ports'].label = 'Number of ports'


class IxiaPortForm(forms.ModelForm):

    class Meta:
        model = Xena_port

        exclude = [
            'parent_module',
            'port_index',
            'used_by',
            'reserved_since',
        ]

        widgets = {
            'port_setup': forms.Select(attrs={
                'class': 'form-control',
            }),
            'port_switch': forms.Select(attrs={
                'class': 'form-control',
            }),
            'port_switch_if': forms.Select(attrs={
                'class': 'form-control',
            })
        }

    def __init__(self, *args, **kwargs):
        ixia_instance = kwargs.pop('par_ixia', None)
        super(IxiaPortForm, self).__init__(*args, **kwargs)

        self.fields['port_setup'].label = 'Connected to Setup'
        self.fields['port_switch'].label = 'Select Switch'
        self.fields['port_switch_if'].label = 'Select Switch Port'
        self.fields['port_switch'].queryset = Switch.objects.none()
        self.fields['port_switch_if'].queryset = SwitchPort.objects.none()

        if ixia_instance:
            # Show only Setups on same Location
            self.fields["port_setup"].queryset = Setup.objects.filter(
                setup_location=ixia_instance.location
                )
        if 'port_setup' in self.data:
            try:
                port_setup_id = int(self.data.get('port_setup'))
                self.fields['port_switch'].queryset = Switch.objects.filter(switch_setup_id__exact=port_setup_id)
            except (ValueError, TypeError):
                pass
        if 'port_switch' in self.data:
            try:
                port_switch_id = int(self.data.get('port_switch'))
                self.fields['port_switch_if'].queryset = SwitchPort.objects.filter(parrent_switch_id=port_switch_id)
            except (ValueError, TypeError):
                pass

class PostForm(forms.ModelForm):

    class Meta:
        model = SetupPosts
        fields = ('message',)
        widgets = {
            'message_title': forms.TextInput(attrs={
                # 'class': 'form-control',
                'id': 'msgtitle'
            }),
            'message': forms.TextInput(attrs={
                # 'class': 'form-control',
                'id': 'msg',
            })
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['message'].label = ''


class WikiForm(forms.ModelForm):

    class Meta:
        model = SetupWiki
        fields = ('body',)


    def __init__(self, *args, **kwargs):
        super(WikiForm, self).__init__(*args, **kwargs)
        self.fields['body'].label = ''


