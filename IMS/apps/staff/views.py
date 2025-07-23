from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Staff, Department

class StaffListView(ListView):
    model = Staff
    template_name = 'staff/list.html'
    context_object_name = 'staff_members'

class StaffCreateView(CreateView):
    model = Staff
    template_name = 'staff/form.html'
    fields = '__all__'
    success_url = reverse_lazy('staff:list')