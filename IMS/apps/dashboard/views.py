from django.shortcuts import render
from django.views import View

class DashboardView(View):
    def get(self, request):
        context = {
            'total_staff': 95,
            'total_rooms': 24,
            'total_exam_days': 6,
            'total_sessions': 12,
            'total_duties_assigned': 120,
            'unassigned_sessions': 2
        }
        return render(request, 'dashboard/dashboard.html', context)