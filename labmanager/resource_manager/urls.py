from django.urls import path, re_path, include
from resource_manager import views
from rest_framework import routers

app_name = "resource_manager"
router = routers.DefaultRouter()
router.register(r'vsats', views.VSATViewSet)
router.register(r'setups', views.SetupViewSet)
router.register(r'vsatports', views.CPEPortViewSet)
router.register(r'switches', views.SwitchViewSet)

urlpatterns = [
    path('home/', views.HomeView.as_view(), name='home'),
    path('breathe/', views.Breathe.as_view(), name='breathe'),
    path('login/', views.user_login, name='user_login'),
    path('register/', views.register, name='register'),
    path('api/', include(router.urls)),
    path('api/', include('rest_framework.urls',
                         namespace='rest_framework')),

    # VSAT urls
    path('cpes/', views.VsatListView.as_view(), name='cpe_list'),
    path('cpes/<int:pk>', views.VSATDetailView.as_view(), name='cpe_detail'),
    path('cpes/create/', views.add_cpe, name='cpe_create'),
    path('cpes/<int:pk>/update', views.VSATUpdateView.as_view(), name='cpe_update'),
    path('cpes/<int:pk>/delete', views.VSATDeleteView.as_view(), name='cpe_delete'),
    path('cpes/<int:pk>/reserve', views.reserve_cpe, name='reserve_cpe'),
    path('cpes/<int:pk>/release', views.release_cpe, name='release_cpe'),
    path('cpes/<int:pk>/history', views.vsat_history, name='vsat_history'),

    #CPE Interfaces
    path('cpes/<int:cpeid>/port/<int:pk>/update', views.CPEPortUpdateView.as_view(), name='cpe_port_update'),
    path('ajax/load-interfaces', views.load_switch_ports, name='load_switch_ports'), #AJAX
    path('ajax/load-switches', views.load_switch, name='load_switch'),  # AJAX
    path('ajax/load-switchess', views.load_switches, name='load_switches'),  # AJAX

    #CPE RX Ports
    path('cpes/<int:cpeid>/rxport/<int:pk>/update', views.CPERXPortUpdateView.as_view(), name='cperx_port_update'),

    # Setup urls
    path('setups/', views.SetupListView.as_view(), name='setups'),
    path('setups/<int:pk>', views.SetupDetailView.as_view(), name='setup_detail'),
    path('setups/create/', views.SetupCreateView.as_view(), name='setup_create'),
    path('setups/<int:pk>/update', views.SetupUpdateView.as_view(), name='setup_update'),
    path('setups/<int:pk>/delete', views.SetupDeleteView.as_view(), name='setup_delete'),
    path('setups/<int:pk>/join', views.join_setup, name='join_setup'),
    path('setups/<int:pk>/leave', views.leave_setup, name='leave_setup'),
    path('setups/<int:pk>/posts/create', views.create_post, name='createpost'),
    path('setups/posts/<int:pk>/delete', views.PostDeleteView.as_view(), name='deletepost'),
    path('setups/<int:pk>/wiki/create', views.create_wiki, name='createwiki'),
    path('setups/<int:pk>/wiki/update', views.UpdateWiki.as_view(), name='updatewiki'),
    path('setups/<int:pk>/sync_kube', views.setup_kuberenetes_sync, name='synckube'),

    #Switches
    path('switches/', views.SwitchListView.as_view(), name='switch_list'),
    path('switches/<int:pk>', views.SwitchDetailView.as_view(), name='switch_detail'),
    path('switches/create/', views.add_switch, name='switch_create'),
    path('switches/<int:pk>/update', views.SwitchUpdateView.as_view(), name='switch_update'),
    path('switches/<int:pk>/delete', views.SwitchDeleteView.as_view(), name='switch_delete'),
    path('switches/<int:pk>/sync', views.switch_interface_sync, name='switch_interface_sync'),
    path('switches/<int:swid>/syncdescr/<int:pk>', views.switch_sync_descriotion, name='switch_sync_descr'),

    #Routers
    path('routers/', views.RouterListView.as_view(), name='router_list'),
    path('routers/<int:pk>', views.RouterDetailView.as_view(), name='router_detail'),
    path('routers/create/', views.add_router, name='router_create'),
    path('routers/<int:pk>/update', views.RouterUpdateView.as_view(), name='router_update'),
    path('routers/<int:pk>/delete', views.RouterDeleteView.as_view(), name='router_delete'),

    path('routers/<int:pk>/interface/create', views.add_router_interface, name='routers_interface_create'),
    path('routers/<int:rid>/interface/<int:pk>/update', views.routers_interface_UpdateView,
         name='routers_interface_update'),
    path('routers/<int:rid>/interface/<int:pk>/delete', views.RouterInterfaceDeleteView.as_view(),
         name='routers_interface_delete'),

    # VXGW
    path('vxgw/', views.VXGWListView.as_view(), name='vxgw_list'),
    path('vxgw/<int:pk>', views.VXGWDetailView.as_view(), name='vxgw_detail'),
    path('vxgw/create/', views.add_vxgw, name='vxgw_create'),
    path('vxgw/<int:pk>/update', views.VXGWUpdateView.as_view(), name='vxgw_update'),
    path('vxgw/<int:pk>/delete', views.VXGWDeleteView.as_view(), name='vxgw_delete'),

    # VXGW_interface
    # path('vxgw/<int:pk>/interface/create', views.vxgw_interface_CreateView, name='vxgw_interface_create'),
    path('vxgw/<int:vxgwid>/interface/<int:pk>/update', views.vxgw_interface_Update, name='vxgw_interface_update'),
    path('vxgw/<int:vxgwid>/interface/<int:pk>/delete', views.VXGWInterfaceDeleteView.as_view(), name='vxgw_interface_delete'),

    # Xena
    path('xena/', views.XenaListView.as_view(), name='xena_list'),
    path('xena/<int:pk>', views.XenaDetailView.as_view(), name='xena_detail'),
    path('xena/create/', views.add_xena, name='xena_create'),
    path('xena/<int:pk>/update', views.XenaUpdateView.as_view(), name='xena_update'),
    path('xena/<int:pk>/delete', views.XenaDeleteView.as_view(), name='xena_delete'),
    path('xena/<int:pk>/module/create', views.xena_module_add, name='xena_module_create'),
    path('xena/<int:xid>/module/<int:modid>/interface/<int:pk>/update', views.xenaPortUpdate, name='xena_port_update'),
    path('xena/<int:xid>/module/<int:modid>/interface/<int:pk>/reserve', views.xenaPortReserve, name='xena_port_reserve'),
    path('xena/<int:xid>/module/<int:modid>/interface/<int:pk>/release', views.xenaPortRelease, name='xena_port_release'),

    # IXIA
    path('ixia/', views.IxiaListView.as_view(), name='ixia_list'),
    path('ixia/<int:pk>', views.IxiaDetailView.as_view(), name='ixia_detail'),
    path('ixia/create/', views.add_ixia, name='ixia_create'),
    path('ixia/<int:pk>/update', views.IxiaUpdateView.as_view(), name='ixia_update'),
    path('ixia/<int:pk>/delete', views.IxiaDeleteView.as_view(), name='ixia_delete'),
    path('ixia/<int:pk>/module/create', views.ixia_module_add, name='ixia_module_create'),
    path('ixia/<int:xid>/module/<int:modid>/interface/<int:pk>/update', views.ixiaPortUpdate, name='ixia_port_update'),
    path('ixia/<int:xid>/module/<int:modid>/interface/<int:pk>/reserve', views.ixiaPortReserve,
         name='ixia_port_reserve'),
    path('ixia/<int:xid>/module/<int:modid>/interface/<int:pk>/release', views.ixiaPortRelease,
         name='ixia_port_release'),


    # Kontron
    path('kontron/', views.KontronListView.as_view(), name='kontron_list'),
    path('kontron/<int:pk>', views.KontronDetailView.as_view(), name='kontron_detail'),
    path('kontron/create/', views.add_kontron, name='kontron_create'),
    path('kontron/<int:pk>/update', views.KontronUpdateView.as_view(), name='kontron_update'),
    path('kontron/<int:pk>/delete', views.KontronDeleteView.as_view(), name='kontron_delete'),

    path('kontron/<int:pk>/node/create', views.add_kontron_node, name='kontron_node_create'),
    path('kontron/<int:ktid>/node/<int:pk>/update', views.KontronNodeUpdateView.as_view(), name='kontron_node_update'),
    path('kontron/<int:ktid>/node/<int:pk>/delete', views.KontronNodeDeleteView.as_view(), name='kontron_node_delete'),

    path('kontron/<int:pk>/interface/create', views.add_kontron_interface, name='kontron_interface_create'),
    path('kontron/<int:ktid>/interface/<int:pk>/update', views.kontron_interface_UpdateView, name='kontron_interface_update'),
    path('kontron/<int:ktid>/interface/<int:pk>/delete', views.KontronInterfaceDeleteView.as_view(), name='kontron_interface_delete'),

    # DLF
    path('dlfs/', views.DlfListView.as_view(), name='dlf_list'),
    path('dlfs/<int:pk>', views.DLFDetailView.as_view(), name='dlf_detail'),
    path('dlfs/create/', views.add_dlf, name='dlf_create'),
    path('dlfs/<int:pk>/update', views.DLFUpdateView.as_view(), name='dlf_update'),
    path('dlfs/<int:pk>/delete', views.DLFDeleteView.as_view(), name='dlf_delete'),

    # Spectrum
    path('specturm/', views.SpectrumListView.as_view(), name='specturm_list'),
    path('specturm/<int:pk>', views.SpectrumDetailView.as_view(), name='spectrum_detail'),
    path('specturm/create/', views.add_spectrum, name='specturm_create'),
    path('specturm/<int:pk>/update', views.SpectrumUpdateView.as_view(), name='specturm_update'),
    path('specturm/<int:pk>/delete', views.SpectrumDeleteView.as_view(), name='spectrum_delete'),
    path('specturm/<int:pk>/reserve', views.reserve_spectrum, name='reserve_spectrum'),
    path('specturm/<int:pk>/release', views.release_spectrum, name='release_spectrum'),

    #PCs
    path('pc/', views.PCListView.as_view(), name='pc_list'),
    path('pc/<int:pk>', views.PCDetailView.as_view(), name='pc_detail'),
    path('pc/create/', views.PCCreateView.as_view(), name='pc_create'),
    path('pc/<int:pk>/update', views.PCUpdateView.as_view(), name='pc_update'),
    path('pc/<int:pk>/delete', views.PCDeleteView.as_view(), name='pc_delete'),
    path('pc/<int:pk>/reserve', views.reserve_pc, name='reserve_pc'),
    path('pc/<int:pk>/release', views.release_pc, name='release_pc'),

    #PC_interface
    path('pc/<int:pk>/interface/create', views.pc_intfCreateView, name='pc_interface_create'),
    path('pc/<int:pcid>/interface/<int:pk>/update', views.pc_intfUpdateView, name='pc_port_update'),
    path('pc/<int:pcid>/interface/<int:pk>/delete', views.PCInterfaceDeleteView.as_view(), name='interface_delete'),
    # path('pc/<int:pcid>/interface/<int:pk>/delete', views.PCInterfaceDeleteView.as_view(), name='pc_port_delete'),

    # OpenVPN
    path('ovpn/', views.OVPNListView.as_view(), name='ovpn_list'),
    path('ovpn/<int:pk>', views.OVPNDetailView.as_view(), name='ovpnserver_detail'),
    path('ovpn/create', views.add_openvpn, name='ovpn_create'),
    path('ovpn/<int:pk>/update', views.OVPNUpdateView.as_view(), name='ovpn_update'),
    path('ovpn/<int:pk>/delete', views.OVPNDeleteView.as_view(), name='ovpn_delete'),

    # CiscoVPN
    path('ciscovpn/', views.CiscoVPNListView.as_view(), name='ciscovpn_list'),
    path('ciscovpn/<int:pk>', views.CiscoVPNDetailView.as_view(), name='ciscovpn_detail'),
    path('ciscovpn/create', views.add_ciscovpn, name='ciscovpn_create'),
    path('ciscovpn/<int:pk>/update', views.CiscoVPNUpdateView.as_view(), name='ciscovpn_update'),
    path('ciscovpn/<int:pk>/delete', views.CiscoVPNDeleteView.as_view(), name='ciscovpn_delete'),

    #ESXI
    path('esxi/', views.ESXIListView.as_view(), name='esxi_list'),
    path('esxi/<int:pk>', views.ESXIDetailView.as_view(), name='esxi_detail'),
    path('esxi/create', views.ESXICreateView.as_view(), name='esxi_create'),
    path('esxi/<int:pk>/update', views.ESXIUpdateView.as_view(), name='esxi_update'),
    path('esxi/<int:pk>/delete', views.ESXIDeleteView.as_view(), name='esxi_delete'),
    path('esxi/<int:pk>/syncvms', views.esxi_sync_vms, name='sync_vms'),

    #VM
    path('esxi/vm/<int:pk>/reserve', views.reserve_vm, name='reserve_vm'),
    path('esxi/vm/<int:pk>/release', views.release_vm, name='release_vm'),
]
