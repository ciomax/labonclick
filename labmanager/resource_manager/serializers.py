# serializers.py

from rest_framework import serializers

from .models import VSAT, Setup, CPEPort, Switch

class VSATSerializer(serializers.ModelSerializer):
    cpe_ports = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = VSAT
        fields = ('cpe_hw_type',
                  'cpe_mac_address',
                  'cpe_console_ip',
                  'cpe_console_port',
                  'cpe_setup',
                  'cpe_reserved_by',
                  'cpe_ports',
                  'pk',
                  )

class SetupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Setup
        fields = ('setup_name',
                  'setup_location',
                  'pk',
                  )

class SwitchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Switch
        fields = ('switch_role',
                  'switch_mgmt_ip',
                  'switch_username',
                  'switch_password',
                  'switch_console_connection',
                  )

class CPEPortSerializer(serializers.ModelSerializer):

    class Meta:
        model = CPEPort
        fields = ('port_ID',
                  'port_switch',
                  'switch_port_id',
                  'pk',
                  )