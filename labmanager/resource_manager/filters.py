import django_filters
from django import forms

from .models import VSAT, Switch, PC, CPE_HW_Type, DLF, OpenVPNServer, ESXI, Router, Kontron, VXGW, Xena, IXIA, \
    CiscoVPNServer


class EmptyStringFilter(django_filters.BooleanFilter):
    def filter(self, qs, value):
        if value in '':
            return qs

        exclude = self.exclude ^ (value is False)
        method = qs.exclude if exclude else qs.filter

        return method(**{self.field_name: ""})



class VSATFilter(django_filters.FilterSet):

    CPE_not_reserved = django_filters.filters.BooleanFilter(field_name='cpe_reserved_by', lookup_expr='isnull')

    class Meta:
        model = VSAT
        fields = {
            'cpe_hw_type': ['exact'],
            'cpe_mac_address': ['contains'],
            'cpe_setup': ['exact'],
        }

        widgets = {
            'cpe_hw_type': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(VSATFilter, self).__init__(*args, **kwargs)
        self.filters['cpe_hw_type'].label = 'HW type'
        self.filters['cpe_mac_address__contains'].label = 'Address'
        self.filters['cpe_setup'].label = 'Setup'
        self.filters['CPE_not_reserved'].label = 'Filter Reserved'


class SwitchesFilter(django_filters.FilterSet):

    class Meta:
        model = Switch
        fields = {
            'switch_setup': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super(SwitchesFilter, self).__init__(*args, **kwargs)
        self.filters['switch_setup'].label = "Setup"


class XenaFilter(django_filters.FilterSet):
    class Meta:
        model = Xena
        fields = {
            'location': ['exact'],
            'chassis_type': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super(XenaFilter, self).__init__(*args, **kwargs)
        self.filters['location'].label = "Chassis Location"
        self.filters['chassis_type'].label = "Chassis Type"


class IxiaFilter(django_filters.FilterSet):
    class Meta:
        model = IXIA
        fields = {
            'location': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super(IxiaFilter, self).__init__(*args, **kwargs)
        self.filters['location'].label = "Chassis Location"


class RouterFilter(django_filters.FilterSet):

    class Meta:
        model = Router
        fields = {
            'router_setup': [
                'exact'
            ],
        }

    def __init__(self, *args, **kwargs):
        super(RouterFilter, self).__init__(*args, **kwargs)
        self.filters['router_setup'].label = "Setup"

class VXGWFilter(django_filters.FilterSet):

    class Meta:
        model = VXGW
        fields = {
            'vxgw_setup': ['exact'],
            'vxgw_model': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super(VXGWFilter, self).__init__(*args, **kwargs)
        self.filters['vxgw_setup'].label = "Setup"
        self.filters['vxgw_model'].label = "Model"


class KontronFilter(django_filters.FilterSet):

    class Meta:
        model = Kontron
        fields = {
            'kontron_setup': [
                'exact'
            ],
        }

    def __init__(self, *args, **kwargs):
        super(KontronFilter, self).__init__(*args, **kwargs)
        self.filters['kontron_setup'].label = "Setup"

class DLFFilter(django_filters.FilterSet):

    class Meta:
        model = DLF
        fields = {
            'dlf_setup': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super(DLFFilter, self).__init__(*args, **kwargs)
        self.filters['dlf_setup'].label = "Setup"


class OVPNFilter(django_filters.FilterSet):
    class Meta:
        model = OpenVPNServer
        fields = {
            'ovpn_setup': ['exact']
        }

    def __init__(self, *args, **kwargs):
        super(OVPNFilter, self).__init__(*args, **kwargs)
        self.filters['ovpn_setup'].label = "Setup"

class CiscoVPNFilter(django_filters.FilterSet):
    class Meta:
        model = CiscoVPNServer
        fields = {
            'cisco_vpn_setup': ['exact']
        }

    def __init__(self, *args, **kwargs):
        super(CiscoVPNFilter, self).__init__(*args, **kwargs)
        self.filters['cisco_vpn_setup'].label = "Setup"


class ESXiFilter(django_filters.FilterSet):
    class Meta:
        model = ESXI
        fields = {
            'esxi_setup': ['exact']
        }

    def __init__(self, *args, **kwargs):
        super(ESXiFilter, self).__init__(*args, **kwargs)
        self.filters['esxi_setup'].label = "Setup"



class PCFilter(django_filters.FilterSet):


    class Meta:
        model = PC
        fields = {
            'pc_setup': ['exact'],
        }

        widgets = {
            'pc_setup': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(PCFilter, self).__init__(*args, **kwargs)
        self.filters['pc_setup'].label = 'Setup'
        # self.filters['cpe_mac_address'].label = 'CPE MAC Address'

