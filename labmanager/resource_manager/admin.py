from django.contrib import admin
from resource_manager.models import VSAT, UserProfile, Setup, Locations, CPE_HW_Type, SetupMember, DLF, DLFPort, \
    CPErxPort, CPEPort, PC, \
    OpenVPNServer, VM, ESXI, Intf_PC, VXGW, VXGW_interface, Xena, Xena_port, Switch, SwitchPort, SetupPosts, \
    KubePod

from simple_history.admin import SimpleHistoryAdmin
class SetupMemberInLine(admin.TabularInline):
    model = SetupMember

# Register your models here.
# admin.site.register(VSAT)
admin.site.register(Setup)
admin.site.register(SetupMember)
admin.site.register(UserProfile)
admin.site.register(Locations)
admin.site.register(CPE_HW_Type)
admin.site.register(DLF)
admin.site.register(DLFPort)
admin.site.register(CPErxPort)
admin.site.register(CPEPort)
admin.site.register(PC)
admin.site.register(OpenVPNServer)
admin.site.register(ESXI)
admin.site.register(VM)
admin.site.register(Intf_PC)
admin.site.register(VXGW)
admin.site.register(VXGW_interface)
admin.site.register(Xena)
admin.site.register(Xena_port)
admin.site.register(Switch)
admin.site.register(SwitchPort)
admin.site.register(SetupPosts)
admin.site.register(KubePod)

#history
admin.site.register(VSAT, SimpleHistoryAdmin)

