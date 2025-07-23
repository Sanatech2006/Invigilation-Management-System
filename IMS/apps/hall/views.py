from django.shortcuts import render
from django.views import View

class HallListView(View):
    def get(self, request):
        return render(request, 'hall/list.html')