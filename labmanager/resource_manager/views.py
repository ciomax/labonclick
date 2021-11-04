import json

import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
# from resource_manager import models
from . import models
from . import forms
from resource_manager.forms import CPEForm, UserForm, PCForm, UpdateCPEPortForm, UpdateCPERXPortForm, SwitchForm, \
    DLFForm, OVPNForm, ESXIForm, PcInterfaceForm, PcInterfaceUpdateForm, RouterForm, KontronForm, Kontron_interfaceForm, \
    XenaForm, IxiaForm, SetupForm, CiscoVPNForm, PostForm
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (TemplateView,
                                    DetailView,
                                    CreateView,
                                    UpdateView,
                                    DeleteView
                                  )
from django.core.mail import send_mail
from django.views.generic.list import ListView
from django.contrib import messages
from itertools import tee, islice, chain
# Filters import
from .filters import VSATFilter, PCFilter, SwitchesFilter, DLFFilter, OVPNFilter, ESXiFilter, RouterFilter, \
    KontronFilter, VXGWFilter, XenaFilter, IxiaFilter, CiscoVPNFilter
from .models import SwitchPort, Intf_PC, Xena, Switch, IXIA, VSAT, Setup, CPEPort
from .utils import get_vms
from time import sleep
from asgiref.sync import sync_to_async
from django.db import IntegrityError
from resource_manager.definitions import *
from . import tasks
from braces.views import SelectRelatedMixin
from rest_framework import viewsets
from .serializers import VSATSerializer, SetupSerializer, CPEPortSerializer, SwitchSerializer




User = get_user_model()


# Serializer


class VSATViewSet(viewsets.ModelViewSet):
    queryset = VSAT.objects.all().order_by('cpe_hw_type')
    serializer_class = VSATSerializer
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

class CPEPortViewSet(viewsets.ModelViewSet):
    queryset = CPEPort.objects.all()
    serializer_class = CPEPortSerializer
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

class SwitchViewSet(viewsets.ModelViewSet):
    queryset = Switch.objects.all()
    serializer_class = SwitchSerializer
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

class SetupViewSet(viewsets.ModelViewSet):
    queryset = Setup.objects.all()
    serializer_class = SetupSerializer
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

class IndexView(TemplateView):
    template_name = 'resource_manager/index.html'


class HomeView(TemplateView):
    redirect_field_name="resource_manager/homepage.html"
    template_name = 'resource_manager/homepage.html'

class Breathe(TemplateView):
    redirect_field_name="resource_manager/relaxer.html"
    template_name = 'resource_manager/relaxer.html'


# VSAT views
class VsatListView(ListView):
    # contex_object_name = 'vsats'
    # paginate_by = 3
    model = models.VSAT
    template_name = 'resouce_manager/vsat/vsat_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = VSATFilter(self.request.GET, queryset=self.get_queryset())
        return context

def vsat_history(request, pk):
    qry = VSAT.history.filter(id=pk)
    created = qry.last()
    changes = []
    if qry is not None:
        last = qry.first()
        for all_changes in range(qry.count() - 1):
            new_record, old_record = last, last.prev_record
            delta = new_record.diff_against(old_record)
            changes.append(delta)
            if old_record is not None:
                last = old_record


    return render(request, 'resource_manager/vsat/vsat_history.html', {'created': created,
                                                                       'changes': changes})



class VSATDetailView(DetailView):
    contex_object_name = 'vsat_detail'
    model = models.VSAT
    template_name = 'resource_manager/vsat/vsatdetail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qry = VSAT.history.filter(id=self.kwargs['pk'])
        changes = []
        if qry is not None:
            last = qry.first()
            for all_changes in range(qry.count()-1):
                new_record, old_record = last, last.prev_record
                delta = new_record.diff_against(old_record)
                changes.append(delta)
                if old_record is not None:
                    last = old_record



        new_record = qry.first()
        old_record = qry.first().prev_record
        context['created'] = qry.first()
        context['history'] = qry
        if old_record:
            context['history_delta'] = new_record.diff_against(old_record)
        context['changes'] = changes

        return context

    # def historical_changes(qry):
    #     changes = []
    #     if qry is not None:
    #         last = qry.first()
    #     for all_changes in range(qry.count()):
    #         new_record, old_record = last, last.prev_record
    #         if old_record is not None:
    #             delta = new_record.diff_against(old_record)
    #             changes.append(delta)
    #             last = old_record
    #             return changes
    #     changes = historical_changes(qry)
    #     context = {'changes': changes}

class VSATCreateView(CreateView):
    model = models.VSAT
    form_class = CPEForm
    template_name = 'resource_manager/vsat/vsat_form.html'

class VSATUpdateView(UpdateView):
    form_class = CPEForm
    template_name = 'resource_manager/vsat/vsat_form.html'
    model = models.VSAT

class VSATDeleteView(DeleteView):
    model = models.VSAT
    template_name = 'resource_manager/vsat/vsat_confirm_delete.html'
    success_url = reverse_lazy("resource_manager:cpe_list")


class CPEPortUpdateView(UpdateView):
    model = models.CPEPort
    form_class = UpdateCPEPortForm
    template_name = 'resource_manager/vsat/cpeport_form.html'


    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            parrent_cpe__id=self.kwargs.get("cpeid")
        )


class CPERXPortUpdateView(UpdateView):
    model = models.CPErxPort
    form_class = UpdateCPERXPortForm
    template_name = 'resource_manager/vsat/cperxport_form.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            # parent_cpe__id__iexact=self.kwargs.get("cpeid")
            parent_cpe__id=self.kwargs.get("cpeid")
        )


# AJAX
def load_switch_ports(request):
    switch_id = request.GET.get('port_switch_id')
    switch_ports = SwitchPort.objects.filter(parrent_switch_id=switch_id)
    return render(request, 'resource_manager/switch/switch_port_options.html', {'ports': switch_ports})


def load_switch(request):
    setup_id = request.GET.get('setup_id')
    switches = Switch.objects.filter(switch_setup_id=setup_id)
    return render(request, 'resource_manager/switch/switchoptions.html', {'switches': switches})

def load_switches(request):
    setup_id = request.GET.get('setup_id')
    switch_ports = SwitchPort.objects.filter(parrent_switch__switch_setup_id=setup_id)
    return render(request, 'resource_manager/switch/switch_port_options.html', {'ports': switch_ports})


def pc_intfCreateView(request, pk):
    parrent_pc = get_object_or_404(models.PC, pk=pk)
    if request.method == 'POST':
        form = forms.PcInterfaceForm(request.POST, par_pc=parrent_pc)
        if form.is_valid():
            pc_if = form.save(commit=False)
            pc_if.parrent_pc = parrent_pc
            pc_if.save()
            return redirect('resource_manager:pc_detail', pk=pk)
    else:
        form = forms.PcInterfaceForm(par_pc=parrent_pc)
    return render(request, 'resource_manager/pc/intf_pc_form.html', {'form': form})



def pc_intfUpdateView(request, pcid, pk):
    pc = get_object_or_404(models.PC, pk=pcid)
    interface = get_object_or_404(models.Intf_PC, pk=pk)
    form = forms.PcInterfaceUpdateForm(request.POST or None, par_pc=pc, instance=interface)

    if form.is_valid():
        form.save()
        return redirect('resource_manager:pc_detail', pk=pcid)
    return render(request, 'resource_manager/pc/intf_pc_form.html', {'form': form})


class PCInterfaceUpdateView(UpdateView):
    model = Intf_PC
    template_name = 'resource_manager/pc/intf_pc_form.html'
    form_class = PcInterfaceUpdateForm

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            parrent_pc__id__iexact=self.kwargs.get("pcid")
        )


class PCInterfaceDeleteView(DeleteView):
    model = Intf_PC
    template_name = 'resource_manager/pc/intf_pc_confirm_delete.html'

    def get_success_url(self):
        # print(pc){'pk', self.object.parrent_pc}
        return reverse_lazy("resource_manager:pc_detail", args=(self.object.parrent_pc.id,))


def add_cpe_port(request, pk):
    cpe = get_object_or_404(models.VSAT, pk=pk)
    if request.method == 'POST':
        form = forms.CPEPortForm(request.POST)
        if form.is_valid():
            port = form.save(commit=False)
            port.parent_cpe = cpe
            port.save()
            return redirect('resource_manager:cpe_detail', pk=cpe.pk)
    else:
        form = forms.CPEPortForm(cpe=cpe)
    return render(request, 'resource_manager/cpeport_form.html', {'form': form})


def add_switch(request):
    if request.method == "POST":
        form = forms.SwitchForm(request.POST)
        if form.is_valid():
            switch = form.save(commit=False)
            switch.save()
        return redirect('resource_manager:switch_detail', pk=switch.pk)
    else:
        form = forms.SwitchForm()
    return render(request, 'resource_manager/switch/switch_form.html', {'form': form})


def add_router(request):
    if request.method == "POST":
        form = forms.RouterForm(request.POST)
        if form.is_valid():
            router = form.save(commit=False)
            router.save()
        return redirect('resource_manager:router_detail', pk=router.pk)
    else:
        form = forms.RouterForm()
    return render(request, 'resource_manager/router/router_form.html', {'form': form})


class RouterListView(ListView):
    model = models.Router
    template_name = 'resource_manager/router/router_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = RouterFilter(self.request.GET, queryset=self.get_queryset())
        return context


class RouterDetailView(DetailView):
    model = models.Router
    template_name = 'resource_manager/router/router_detail.html'


class RouterUpdateView(UpdateView):
    model = models.Router
    form_class = RouterForm
    template_name = 'resource_manager/router/router_form.html'


class RouterDeleteView(DeleteView):
    model = models.Router
    template_name = 'resource_manager/router/router_confirm_delete.html'
    success_url = reverse_lazy('resource_manager:router_list')


def add_router_interface(request, pk):
    parent_router = get_object_or_404(models.Router, pk=pk)
    if request.method == "POST":
        form = forms.Router_interfaceForm(request.POST, p_router=parent_router)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.parent_router = parent_router
            instance.save()
            return redirect('resource_manager:router_detail', pk=parent_router.pk)
    else:
        form = forms.Router_interfaceForm(p_router=parent_router)
    return render(request, 'resource_manager/router/RouterInterface_form.html', {'form': form})


def routers_interface_UpdateView(request, rid, pk):

    router = get_object_or_404(models.Router, pk=rid)
    interface = get_object_or_404(models.RouterPort, pk=pk)
    form = forms.RouterInterfaceUpdateForm(request.POST or None, p_router=router, instance=interface)

    if form.is_valid():
        form.save()
        return redirect('resource_manager:router_detail', pk=rid)

    return render(request, 'resource_manager/router/RouterInterface_form.html', {'form': form})


class RouterInterfaceDeleteView(DeleteView):
    model = models.RouterPort
    template_name = 'resource_manager/router/RouterInterface_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy("resource_manager:router_detail", args=(self.object.parent_router.pk,))


#Kontron

def add_kontron(request):
    if request.method == "POST":
        form = forms.KontronForm(request.POST)
        if form.is_valid():
            kontron = form.save(commit=False)
            kontron.save()
            return redirect('resource_manager:kontron_detail', pk=kontron.id)
    else:
        form = forms.KontronForm()
    return render(request, 'resource_manager/kontron/kontron_form.html', {'form': form})


class KontronListView(ListView):
    model = models.Kontron
    template_name = 'resource_manager/kontron/kontron_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = KontronFilter(self.request.GET, queryset=self.get_queryset())
        return context


class KontronDetailView(DetailView):
    model = models.Kontron
    template_name = 'resource_manager/kontron/kontron_detail.html'


class KontronUpdateView(UpdateView):
    model = models.Kontron
    form_class = KontronForm
    template_name = 'resource_manager/kontron/kontron_form.html'


class KontronDeleteView(DeleteView):
    model = models.Kontron
    template_name = 'resource_manager/kontron/kontron_confirm_delete.html'
    success_url = reverse_lazy('resource_manager:kontron_list')


def add_kontron_node(request, pk):
    parent_kontron = get_object_or_404(models.Kontron, pk=pk)
    if request.method == "POST":
        form = forms.KontronNodeForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.parent_kontron = parent_kontron
            instance.save()
            return redirect('resource_manager:kontron_detail', pk=parent_kontron.pk)
    else:
        form = forms.KontronNodeForm()
    return render(request, 'resource_manager/kontron/kontronNode_from.html', {'form': form})


class KontronNodeUpdateView(UpdateView):
    model = models.Kontron_node
    form_class = forms.KontronNodeForm
    template_name = 'resource_manager/kontron/kontronNode_from.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            parent_kontron__id__iexact=self.kwargs.get("ktid")
        )


class KontronNodeDeleteView(DeleteView):
    model = models.Kontron_node
    template_name = 'resource_manager/kontron/kontronNode_confirm_delete.html'
    # success_url = reverse_lazy('resource_manager:kontron_detail')

    def get_success_url(self):
        return reverse_lazy("resource_manager:kontron_detail", args=(self.object.parent_kontron.pk,))


def add_kontron_interface(request, pk):
    parent_kontron = get_object_or_404(models.Kontron, pk=pk)
    if request.method == "POST":
        form = forms.Kontron_interfaceForm(request.POST, p_kont = parent_kontron)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.parent_kontron = parent_kontron
            instance.save()
            return redirect('resource_manager:kontron_detail', pk=parent_kontron.pk)
    else:
        form = forms.Kontron_interfaceForm(p_kont = parent_kontron)
    return render(request, 'resource_manager/kontron/kontronInterface_form.html', {'form': form})


def kontron_interface_UpdateView(request, ktid, pk):

    kontron = get_object_or_404(models.Kontron, pk=ktid)
    interface = get_object_or_404(models.Kontron_interface, pk=pk)

    form = forms.KontronInterfaceUpdateForm(request.POST or None, p_kont=kontron, instance=interface)

    if form.is_valid():
        form.save()
        return redirect('resource_manager:kontron_detail', pk=ktid)

    return render(request, 'resource_manager/kontron/kontronInterface_form.html', {'form': form})


class KontronInterfaceUpdateView(UpdateView):
    model = models.Kontron_interface
    template_name = 'resource_manager/kontron/kontronInterface_form.html'
    form_class = Kontron_interfaceForm


class KontronInterfaceDeleteView(DeleteView):
    model = models.Kontron_interface
    template_name = 'resource_manager/kontron/kontronInterface_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy("resource_manager:kontron_detail", args=(self.object.parent_kontron.pk,))

# VXGW

def add_vxgw(request):
    if request.method == "POST":
        form = forms.VXGWForm(request.POST)
        if form.is_valid():
            vxgw = form.save(commit=False)
            vxgw.save()
            if vxgw.vxgw_model == 'MX204':
                for interface in MX204_interface_list:
                    intf = models.VXGW_interface.objects.create(
                        parent_vxgw=vxgw,
                        interface_index=interface,
                        interface_description=None,
                        switch=None,
                        switch_if=None,
                    )
                    intf.save()
            elif vxgw.vxgw_model == 'MX5':
                for interface in MX5_interface_list:
                    intf = models.VXGW_interface.objects.create(
                        parent_vxgw=vxgw,
                        interface_index=interface,
                        interface_description=None,
                        switch=None,
                        switch_if=None,
                    )
                    intf.save()
            elif vxgw.vxgw_model == 'VMX':
                for interface in VMX_interface_list:
                    intf = models.VXGW_interface.objects.create(
                        parent_vxgw=vxgw,
                        interface_index=interface,
                        interface_description=None,
                        switch=None,
                        switch_if=None,
                    )
                    intf.save()
            return redirect('resource_manager:vxgw_detail', pk=vxgw.pk)
    else:
        form = forms.VXGWForm()
    return render(request, 'resource_manager/vxgw/vxgw_form.html', {'form': form})



class VXGWListView(ListView):
    model = models.VXGW
    template_name = 'resource_manager/vxgw/vxgw_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = VXGWFilter(self.request.GET, queryset=self.get_queryset())
        return context


class VXGWDetailView(DetailView):
    model = models.VXGW
    template_name = 'resource_manager/vxgw/vxgw_detail.html'

class VXGWUpdateView(UpdateView):
    model = models.VXGW
    form_class = forms.VXGWForm
    template_name = 'resource_manager/vxgw/vxgw_form.html'

class VXGWDeleteView(DeleteView):
    model = models.VXGW
    template_name = 'resource_manager/vxgw/vxgw_confirm_delete.html'
    success_url = reverse_lazy('resource_manager:vxgw_list')



def vxgw_interface_Update(request, vxgwid, pk):
    vxgw = get_object_or_404(models.VXGW, pk=vxgwid)

    interface = get_object_or_404(models.VXGW_interface, pk=pk)

    form = forms.VXGWInterfaceForm(request.POST or None, par_vxgw=vxgw, instance=interface)

    if form.is_valid():
        form.save()
        return redirect('resource_manager:vxgw_detail', pk=vxgwid)

    return render(request, 'resource_manager/vxgw/vxgw_interfac_form.html', {'form': form})


class VXGWInterfaceDeleteView(DeleteView):
    model = models.VXGW_interface
    template_name = 'resource_manager/vxgw/vxgw_interface_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy("resource_manager:vxgw_detail", args=(self.object.parent_vxgw.pk,))

# Spectrum


def add_spectrum(request):
    if request.method == "POST":
        form = forms.SpectrumForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            return redirect('resource_manager:spectrum_detail', pk=instance.pk)
    else:
        form = forms.SpectrumForm()
    return render(request, 'resource_manager/spectrum/spectrum_form.html', {'form': form})


class SpectrumListView(ListView):
    model = models.SpectrumAnalyzer
    template_name = 'resource_manager/spectrum/spectrum_list.html'


class SpectrumDetailView(DetailView):
    model = models.SpectrumAnalyzer
    template_name = 'resource_manager/spectrum/spectrum_detail.html'


class SpectrumUpdateView(UpdateView):
    model = models.SpectrumAnalyzer
    form_class = forms.SpectrumForm
    template_name = 'resource_manager/spectrum/spectrum_form.html'


class SpectrumDeleteView(DeleteView):
    model = models.SpectrumAnalyzer
    template_name = 'resource_manager/spectrum/spectrum_confirm_delete.html'
    success_url = reverse_lazy('resource_manager:specturm_list')


# Cisco VPN
def add_ciscovpn(request):
    if request.method == "POST":
        form = forms.CiscoVPNForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            return redirect('resource_manager:ciscovpn_detail', pk=instance.pk)
    else:
        form = forms.OVPNForm()
    return render(request, 'resource_manager/ciscovpn/ciscovpnserver_form.html', {'form': form})

class CiscoVPNListView(ListView):
    model = models.CiscoVPNServer
    template_name = 'resource_manager/ciscovpn/ciscovpnserver_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = CiscoVPNFilter(self.request.GET, queryset=self.get_queryset())
        return context

class CiscoVPNDetailView(DetailView):
    model = models.CiscoVPNServer
    context_object_name = 'ciscovpn_detail'
    template_name = 'resource_manager/ciscovpn/ciscovpnserver_detail.html'


class CiscoVPNUpdateView(UpdateView):
    model = models.CiscoVPNServer
    template_name = 'resource_manager/ciscovpn/ciscovpnserver_form.html'
    form_class = CiscoVPNForm


class CiscoVPNDeleteView(DeleteView):
    model = models.CiscoVPNServer
    template_name = 'resource_manager/ciscovpn/ciscovpnserver_confirm_delete.html'
    success_url = reverse_lazy("resource_manager:ciscovpn_list")


# OpenVPN
def add_openvpn(request):
    if request.method == "POST":
        form = forms.OVPNForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            # instance = models.OpenVPNServer(connection_file=request.FILES['connection_file'])
            instance.save()
            return redirect('resource_manager:ovpnserver_detail', pk=instance.pk)
    else:
        form = forms.OVPNForm()
    return render(request, 'resource_manager/ovpn/openvpnserver_form.html', {'form': form})



def add_dlf(request):

    if request.method == "POST":
        form = forms.DLFForm(request.POST)
        if form.is_valid():
            dlf = form.save(commit=False)
            dlf.save()
            for port_num in range(dlf.dlf_port_num):
                dlf_port = models.DLFPort.objects.create(parrent_dlf=dlf, dlf_port_number=port_num + 1)
                dlf_port.save()
            return redirect('resource_manager:dlf_detail', pk=dlf.pk)

    else:
        form = forms.DLFForm()
    return render(request, 'resource_manager/dlf/dlf_form.html', {'form': form})


def add_cpe(request):
    if request.method == "POST":
        form = forms.CPEForm(request.POST)
        if form.is_valid():
            cpe = form.save(commit=False)
            cpe.save()
            # new
            for hw_type in hw_types:
                if hw_type.hw_type == cpe.cpe_hw_type:
                    for gbe_port in range(hw_type.num_gbe):
                        gb_port = models.CPEPort.objects.create(
                            parrent_cpe=cpe,
                            port_ID=gbe_port + 1,
                            port_type="Gigabit Ethernet",
                        )
                        gb_port.save()
                    for sfp_port in range(hw_type.num_sfp):
                        sfp = models.CPEPort.objects.create(
                            parrent_cpe=cpe,
                            port_ID=sfp_port + 1,
                            port_type="SFP",
                        )
                        sfp.save()
                    for rx_port_id in range(hw_type.num_rf):
                        rx = models.CPErxPort.objects.create(
                            parent_cpe=cpe,
                            rx_id=rx_port_id + 1,
                        )
            return redirect('resource_manager:cpe_detail', pk=cpe.pk)

    else:
        form = forms.CPEForm()
    return render(request, 'resource_manager/vsat_form.html', {'form': form})


@login_required(login_url='resource_manager:user_login')
def join_setup(request, pk):
    setup = get_object_or_404(models.Setup, pk=pk)
    user = request.user
    # if request.method == "POST":
    member = models.SetupMember.objects.create(setup=setup, user=user)
    member.save()
    messages.info(request, "Successfully joined!")
    return redirect('resource_manager:setup_detail', pk=setup.pk)


class CPEPortDeleteView(DeleteView):
    model = models.CPEPort
    success_url = reverse_lazy("resource_manager:vsat_list")


# Setup views
class SetupListView(ListView):
    model = models.Setup


class SetupDetailView(DetailView):
    model = models.Setup
    form_class = PostForm
    contex_object_name = 'setup_detail'
    # post_list
    template_name = 'resource_manager/setup_detail.html'


class SetupCreateView(CreateView):
    model = models.Setup
    form_class = SetupForm


class SetupUpdateView(UpdateView):
    model = models.Setup
    form_class = SetupForm


class SetupDeleteView(DeleteView):
    model = models.Setup
    success_url = reverse_lazy("resource_manager:switch_list")


# Switch views
class SwitchListView(ListView):
    model = models.Switch
    template_name = 'resource_manager/switch/switch_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = SwitchesFilter(self.request.GET, queryset=self.get_queryset())
        return context


class SwitchDetailView(DetailView):
    model = models.Switch
    contex_object_name = 'switch_detail'
    template_name = 'resource_manager/switch/switch_detail.html'


class SwitchCreateView(CreateView):
    form_class = SwitchForm
    template_name = 'resource_manager/switch/switch_form.html'
    model = models.Switch


class SwitchUpdateView(UpdateView):
    form_class = SwitchForm
    template_name = 'resource_manager/switch/switch_form.html'
    model = models.Switch


class SwitchDeleteView(DeleteView):
    model = models.Switch
    success_url = reverse_lazy("resource_manager:switch_list")


# DLF views
class DlfListView(ListView):
    model = models.DLF
    template_name = 'resource_manager/dlf/dlf_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = DLFFilter(self.request.GET, queryset=self.get_queryset())
        return context


class DLFDetailView(DetailView):
    model = models.DLF
    contex_object_name = 'dlf_detail'
    template_name = 'resource_manager/dlf/dlf_detail.html'


class DLFCreateView(CreateView):
    model = models.DLF
    template_name = 'resource_manager/dlf/dlf_form.html'
    form_class = DLFForm


class DLFUpdateView(UpdateView):
    model = models.DLF
    template_name = 'resource_manager/dlf/dlf_form.html'
    form_class = DLFForm


class DLFDeleteView(DeleteView):
    model = models.DLF
    template_name = 'resource_manager/dlf/dlf_confirm_delete.html'
    success_url = reverse_lazy("resource_manager:dlf_list")

#Xena Views


def add_xena(request):
    if request.method == "POST":
        form = forms.XenaForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            return redirect('resource_manager:xena_detail', pk=instance.pk)
    else:
        form = forms.XenaForm()
    return render(request, 'resource_manager/xena/xena_form.html', {'form': form})

class XenaListView(ListView):
    model = models.Xena
    template_name = 'resource_manager/xena/xena_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = XenaFilter(self.request.GET, queryset=self.get_queryset())
        return context

class XenaDetailView(DetailView):
    model = models.Xena
    context_object_name = 'xena_detail'
    template_name = 'resource_manager/xena/xena_detail.html'

class XenaUpdateView(UpdateView):
    model = models.Xena
    template_name = 'resource_manager/xena/xena_form.html'
    form_class = XenaForm

class XenaDeleteView(DeleteView):
    model = models.Xena
    template_name = 'resource_manager/xena/xena_confirm_delete.html'

    def get_success_url(self):
        # print(pc){'pk', self.object.parrent_pc}
        return reverse_lazy("resource_manager:xena_list")


def xena_module_add(request, pk):
    chassis = get_object_or_404(Xena, pk=pk)
    if request.method == "POST":
        form = forms.XenaModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.module_chassis = chassis
            module.save()

            for portId in range(module.module_num_ports):
                xena_p = models.Xena_port.objects.create(
                    parent_module=module,
                    port_index=portId,
                )
                xena_p.save()
        return redirect('resource_manager:xena_detail', pk=chassis.pk)
    else:
        form = forms.XenaModuleForm()
    return render(request, 'resource_manager/xena_module_form.html', {'form': form})


def xenaPortUpdate(request, xid, modid, pk):
    xena = get_object_or_404(models.Xena, pk=xid)
    port = get_object_or_404(models.Xena_port, pk=pk)
    form = forms.XenaPortForm(request.POST or None, par_xena=xena, instance=port)
    # form = forms.VXGWInterfaceForm(request.POST or None, par_vxgw=vxgw, instance=interface)

    if form.is_valid():
        form.save()
        return redirect('resource_manager:xena_detail', pk=xid)

    return render(request, 'resource_manager/xena/xena_port_form.html', {'form': form})



#IXIA Views

def add_ixia(request):
    if request.method == "POST":
        form = forms.IxiaForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            return redirect('resource_manager:ixia_detail', pk=instance.pk)
    else:
        form = forms.IxiaForm()
    return render(request, 'resource_manager/ixia/ixia_form.html', {'form': form})


class IxiaListView(ListView):
    model = models.IXIA
    template_name = 'resource_manager/ixia/ixia_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = IxiaFilter(self.request.GET, queryset=self.get_queryset())
        return context

class IxiaDetailView(DetailView):
    model = models.IXIA
    context_object_name = 'ixia_detail'
    template_name = 'resource_manager/ixia/ixia_detail.html'


class IxiaUpdateView(UpdateView):
    model = models.IXIA
    template_name = 'resource_manager/ixia/ixia_form.html'
    form_class = IxiaForm


class IxiaDeleteView(DeleteView):
    model = models.IXIA
    template_name = 'resource_manager/ixia/ixia_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy("resource_manager:ixia_list")


def ixia_module_add(request, pk):
    chassis = get_object_or_404(IXIA, pk=pk)
    if request.method == "POST":
        form = forms.IxiaModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.module_chassis = chassis
            module.save()

            for portId in range(1, module.module_num_ports + 1):
                ixia_p = models.IXIA_port.objects.create(
                    parent_module=module,
                    port_index=portId,
                )
                ixia_p.save()
        return redirect('resource_manager:ixia_detail', pk=chassis.pk)
    else:
        form = forms.IxiaModuleForm()
    return render(request, 'resource_manager/ixia_module_form.html', {'form': form})



def ixiaPortUpdate(request, xid, modid, pk):
    ixia = get_object_or_404(models.IXIA, pk=xid)
    port = get_object_or_404(models.IXIA_port, pk=pk)
    form = forms.IxiaPortForm(request.POST or None, par_ixia=ixia, instance=port)

    if form.is_valid():
        form.save()
        return redirect('resource_manager:ixia_detail', pk=xid)

    return render(request, 'resource_manager/ixia/ixia_port_form.html', {'form': form})

# OpenVPN
class OVPNListView(ListView):
    model = models.OpenVPNServer
    template_name = 'resource_manager/ovpn/openvpnserver_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = OVPNFilter(self.request.GET, queryset=self.get_queryset())
        return context


class OVPNDetailView(DetailView):
    model = models.OpenVPNServer
    context_object_name = 'ovpn_detail'
    template_name = 'resource_manager/ovpn/openvpnserver_detail.html'


class OVPNCreateView(CreateView):
    model = models.OpenVPNServer
    template_name = 'resource_manager/ovpn/openvpnserver_form.html'
    form_class = OVPNForm


class OVPNUpdateView(UpdateView):
    model = models.OpenVPNServer
    template_name = 'resource_manager/ovpn/openvpnserver_form.html'
    form_class = OVPNForm


class OVPNDeleteView(DeleteView):
    model = models.OpenVPNServer
    template_name = 'resource_manager/ovpn/openvpnserver_confirm_delete.html'
    success_url = reverse_lazy("resource_manager:ovpn_list")

# ESXI
class ESXIListView(ListView):
    model = models.ESXI
    template_name = 'resource_manager/esxi/esxi_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = ESXiFilter(self.request.GET, queryset=self.get_queryset())
        return context


class ESXIDetailView(DetailView):
    model = models.ESXI
    context_object_name = 'esxi_detail'
    template_name = 'resource_manager/esxi/esxi_detail.html'


class ESXICreateView(CreateView):
    model = models.ESXI
    template_name = 'resource_manager/esxi/esxi_form.html'
    form_class = ESXIForm


class ESXIUpdateView(UpdateView):
    model = models.ESXI
    template_name = 'resource_manager/esxi/esxi_form.html'
    form_class = ESXIForm


class ESXIDeleteView(DeleteView):
    model = models.ESXI
    template_name = 'resource_manager/esxi/esxi_confirm_delete.html'
    success_url = reverse_lazy("resource_manager:esxi_list")


# PC views
class PCListView(ListView):
    model = models.PC
    template_name = 'resource_manager/pc/pc_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PCFilter(self.request.GET, queryset=self.get_queryset())
        return context


class PCDetailView(DetailView):
    model = models.PC
    contex_object_name = 'pc_detail'
    template_name = 'resource_manager/pc/pc_detail.html'


class PCDeleteView(DeleteView):
    model = models.PC
    template_name = 'resource_manager/pc/pc_confirm_delete.html'
    success_url = reverse_lazy("resource_manager:pc_list")


class PCUpdateView(UpdateView):
    model = models.PC
    template_name = 'resource_manager/pc/pc_form.html'
    form_class = PCForm


class PCCreateView(CreateView):
    model = models.PC
    form_class = PCForm


@login_required(login_url='resource_manager:user_login')
def reserve_cpe(request, pk):
    vsat = get_object_or_404(models.VSAT, pk=pk)
    user = request.user
    vsat.cpe_reserved_by = user
    vsat.cpe_reserved_since = timezone.now()
    vsat.save()
    if vsat.cpe_reserved_by:
        messages.info(request, "CPE reserved. Don't forget to release it when you finish your work!")
    return redirect('resource_manager:cpe_detail', pk=vsat.pk)


@login_required(login_url='resource_manager:user_login')
def reserve_pc(request, pk):
    pc = get_object_or_404(models.PC, pk=pk)
    user = request.user
    pc.pc_reserved_by = user
    pc.pc_reserved_since = timezone.now()
    pc.save()

    if pc.pc_reserved_by:
        messages.info(request, "PC reserved. Don't forget to release it when you finish your work!")

    return redirect('resource_manager:pc_detail', pk=pc.pk)


def reserve_spectrum(request, pk):
    spectrum = get_object_or_404(models.SpectrumAnalyzer, pk=pk)
    user = request.user
    spectrum.reserved_since = timezone.now()
    spectrum.used_by = user
    spectrum.save()
    if spectrum.used_by:
        messages.info(request, "Spectrum reserved. Don't forget to release it when you finish your work!")
    return redirect('resource_manager:spectrum_detail', pk=spectrum.pk)


def release_spectrum(request, pk):
    spectrum=get_object_or_404(models.SpectrumAnalyzer, pk=pk)
    if spectrum.used_by == "":
        messages.error(request, "CPE not reserved!")
    else:
        spectrum.release()
        if spectrum.reserved_since == "":
            messages.info(request, "Successfully released Spectrum!")
    return redirect("resource_manager:spectrum_detail", pk=spectrum.pk)


@login_required(login_url='resource_manager:user_login')
def release_pc(request, pk):
    pc=get_object_or_404(models.PC, pk=pk)
    if pc.pc_reserved_by == "":
        messages.error(request, "CPE not reserved!")
    else:
        pc.release_pc()
        if pc.pc_reserved_by == "":
            messages.info(request, "Successfully released PC!")
    return redirect("resource_manager:pc_detail", pk=pc.pk)

@login_required(login_url='resource_manager:user_login')
def xenaPortReserve(request, xid, modid, pk):
    port = get_object_or_404(models.Xena_port, pk=pk)
    user = request.user
    port.used_by = user
    port.reserved_since = timezone.now()
    port.save()

    if port.used_by:
        messages.info(request, "Port reserved. Don't forget to release it when you finish your work!")

    return redirect('resource_manager:xena_detail', pk=port.parent_module.module_chassis.pk)

@login_required(login_url='resource_manager:user_login')
def xenaPortRelease(request, xid, modid, pk):
    port = get_object_or_404(models.Xena_port, pk=pk)
    port.release()

    if not port.used_by:
        messages.info(request, "Port released successfully!")

    return redirect('resource_manager:xena_detail', pk=port.parent_module.module_chassis.pk)


# IXIA port
@login_required(login_url='resource_manager:user_login')
def ixiaPortReserve(request, xid, modid, pk):
    port = get_object_or_404(models.IXIA_port, pk=pk)
    user = request.user
    port.used_by = user
    port.reserved_since = timezone.now()
    port.save()

    if port.used_by:
        messages.info(request, "Port reserved. Don't forget to release it when you finish your work!")

    return redirect('resource_manager:ixia_detail', pk=port.parent_module.module_chassis.pk)

@login_required(login_url='resource_manager:user_login')
def ixiaPortRelease(request, xid, modid, pk):
    port = get_object_or_404(models.IXIA_port, pk=pk)
    port.release()

    if not port.used_by:
        messages.info(request, "Port released successfully!")

    return redirect('resource_manager:ixia_detail', pk=port.parent_module.module_chassis.pk)



@login_required(login_url='resource_manager:user_login')
def release_cpe(request, pk):
    vsat=get_object_or_404(models.VSAT, pk=pk)
    if vsat.cpe_reserved_by == "":
        messages.error(request, "CPE not reserved!")
    else:
        vsat.release_cpe()
        if vsat.cpe_reserved_by == "":
            messages.info(request, "Successfully released CPE!")
    return redirect("resource_manager:cpe_detail", pk=vsat.pk)

@login_required(login_url='resource_manager:user_login')
def reserve_vm(request, pk):
    vm = get_object_or_404(models.VM, pk=pk)
    user = request.user
    vm.reserve_vm(user=user)
    if vm.vm_reserved_by:
        messages.info(request, f'Successfully reserved VM {vm.vm_name}')
    return redirect("resource_manager:esxi_detail", pk=vm.vm_esxi.pk)

@login_required(login_url='resource_manager:user_login')
def release_vm(request, pk):
    vm = get_object_or_404(models.VM, pk=pk)
    vm.release_vm()
    if not vm.vm_reserved_by:
        messages.info(request, f'Successfully released VM {vm.vm_name}')
    return redirect("resource_manager:esxi_detail", pk=vm.vm_esxi.pk)


@login_required(login_url='resource_manager:user_login')
def leave_setup(request, pk):
    setup = get_object_or_404(models.Setup, pk=pk)
    user = request.user
    member = models.SetupMember.objects.get(user=user, setup=setup)
    member.delete()
    messages.info(request, "Successfully removed from the list of enginners working on the setup. You are free now!")
    return redirect('resource_manager:setup_detail', pk=setup.pk)


def register(request):

    registered = False

    if request.method == "POST":
        user_form = UserForm(data=request.POST)

        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            registered = True

        else:
            print(user_form.errors)

    else:
        user_form = UserForm()

    return render(request, 'resource_manager/registration.html',
                                    {'user_form': user_form,
                                        'registered': registered})


def user_login(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            username=username,
            password=password)

        if user is not None:
            if user.is_active:
                login(user=user, request=request)
                return HttpResponseRedirect(reverse('resource_manager:home'))
            else:
                return HttpResponse("Account not active")
        else:
            messages.error(request, "Login Failed. Wrong username or password")
            print(f"Login failed. {username} - {password}")
            return HttpResponseRedirect(reverse('resource_manager:user_login'))
            # return HttpResponse("Invalid login details supplied!")
    else:
        return render(request, 'resource_manager/user_login.html', {})



def user_logout(request):
    logout(request)
    return redirect('resource_manager:user_login')


@sync_to_async
def esxi_sync_vms(request, pk):
    esxi = get_object_or_404(models.ESXI, pk=pk)

    try:
        vms = get_vms(hostip=esxi.esxi_ip_address, username=esxi.esxi_username, password=esxi.esxi_password)
        vms_instances = []
        existing = []

        print(vms[0])
        for vm in vms:

            instance, created = models.VM.objects.get_or_create(
                vm_esxi=esxi,
                vm_name=vm.vmname,
                vm_guest_FullName=vm.vmguestname,
                vm_cores_socket=vm.vmcores,
                vm_numCPU=vm.vmcpunum,
                vm_memory=vm.vmmem,
            )

            if created:
                vms_instances.append(instance)
            else:
                existing.append(instance)
        # for agf in models.VM.objects.all().values('vm_name', 'vm_esxi'):
        all_instaces = vms_instances + existing
        # for exvm in models.VM.objects.all():
        for exvm in esxi.vms.all():
            vm_exists = False
            print(exvm.vm_name)
            for newvm in all_instaces:
                if exvm.vm_name == newvm.vm_name:
                    vm_exists = True
            if not vm_exists:
                exvm.delete()

        models.VM.objects.bulk_create(vms_instances)

    except IntegrityError as e:
        print(e)
    except Exception as e:
        print(e)
        messages.info(request, "Unable to Sync VMs. Check configured parameters!")
    success_url = reverse_lazy("resource_manager:esxi_detail", pk=esxi.pk)
    return redirect("resource_manager:esxi_detail", pk=esxi.pk)

@login_required(login_url='resource_manager:user_login')
def switch_interface_sync(request, pk):
    task = tasks.get_switch_interfaces.delay(pk)
    messages.info(request, "Will try to sync interfaces from Switch. Please refresh page in few seconds!")
    messages.warning(request, task)
    return redirect("resource_manager:switch_detail", pk=pk)

@login_required(login_url='resource_manager:user_login')
def switch_sync_descriotion(request, swid, pk):
    tasks.sync_interface_description.delay(swid, pk)
    messages.info(request, f"Changing interface description. In order to see changes, please Sync Switch!")
    return redirect("resource_manager:switch_detail", pk=swid)

@login_required(login_url='resource_manager:user_login')
def setup_kuberenetes_sync(request, pk):
    task = tasks.setup_kuberenetes_sync.delay(pk)
    # messages.info(request, "Will try to get kubernetes pods from the node. Please refresh page when task is finished!")
    messages.warning(request, task)
    return redirect("resource_manager:setup_detail", pk)
    # return render(request, "resource_manager:setup_detail", {'pk': pk})

# Posts

@login_required(login_url='resource_manager:user_login')
def create_post(request, pk):
    setup = get_object_or_404(models.Setup, pk=pk)
    if request.method == 'POST':
        form = forms.PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.setup = setup
            post.save()
            # send_mail(
            #     'LabManager Notification',
            #     post.message,
            #     'maximtlc@gmail.com',
            #     ['maximc@gilat.com'],
            # )
            # sleep(5)
            return redirect('resource_manager:setup_detail', pk=setup.pk)
    else:
        form = forms.PostForm()
    return render(request, 'resource_manager/setup/post_form.html', {'form': form})

@login_required(login_url='resource_manager:user_login')
class CreateSetupPost(SelectRelatedMixin, CreateView):
    model = models.SetupPosts
    fields = ('message',)
    select_related=('setup',)
    template_name = 'resource_manager/setup/post_form.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class PostList(SelectRelatedMixin, ListView):
    model = models.SetupPosts
    template_name = 'resource_manager/setup/post_list.html'
    select_related = ("user", "setup")

class PostDeleteView(SelectRelatedMixin, DeleteView):
    model = models.SetupPosts
    select_related = ('user', 'setup')
    template_name = 'resource_manager/setup/setupposts_confirm_delete.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.user.id)

    def delete(self, *args, **kwargs):
        messages.info(self.request, "Post Deleted")
        return super().delete(*args, **kwargs)

    def get_success_url(self):
        # print(pc){'pk', self.object.parrent_pc}
        return reverse_lazy("resource_manager:setup_detail" , args=(self.object.setup.id,))

@login_required(login_url='resource_manager:user_login')
def create_wiki(request, pk):

    setup = get_object_or_404(models.Setup, pk=pk)
    if request.method == 'POST':
        form = forms.WikiForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.setup = setup
            post.save()
            return redirect('resource_manager:setup_detail', pk=setup.pk)
    else:
        form = forms.WikiForm()
    return render(request, 'resource_manager/setup/post_form.html', {'form': form})


class UpdateWiki(UpdateView):
    model = models.SetupWiki
    template_name = 'resource_manager/setup/setup_wiki_form.html'
    form_class = forms.WikiForm

