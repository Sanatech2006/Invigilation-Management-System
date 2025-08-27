from django.shortcuts import render
from django.views import View
from apps.staff.models import Staff
from apps.hall.models import Room
from apps.exam_dates.models import ExamDate
from django.db.models import Sum, Count
from django.utils import timezone
import json
from django.shortcuts import redirect
from apps.common.decorators import role_required

class DashboardView(View):
     def get(self, request):
        role = request.session.get('role')
        # Allow roles 1, 2, 3, 4 to access dashboard
        if role not in [1, 2, 3, 4]:
            return redirect('login')

        exam_dates = ExamDate.objects.all().order_by('date')

        category_order = ['AIDED', 'SFM', 'SFW']

        # Staff count chart data
        staff_by_category = Staff.objects.values('dept_category').annotate(count=Count('id'))
        staff_data = {entry['dept_category']: entry['count'] for entry in staff_by_category}
        ordered_staff_categories = [cat for cat in category_order if cat in staff_data]
        ordered_staff_counts = [staff_data[cat] for cat in ordered_staff_categories]

        # Required session chart data
        from apps.hall.models import Room
        session_by_category = Room.objects.values('dept_category').annotate(total=Sum('required_session'))
        session_data = {entry['dept_category']: entry['total'] for entry in session_by_category}
        ordered_session_categories = [cat for cat in category_order if cat in session_data]
        ordered_session_totals = [session_data[cat] for cat in ordered_session_categories]

        context = {
            'total_staff': Staff.objects.count(),
            'total_rooms': Room.objects.count(),
            'total_exam_days': ExamDate.objects.count(),
            'total_sessions': Room.objects.aggregate(total=Sum('required_session'))['total'] or "Not calculated",
            'total_duties_assigned': 120,
            'unassigned_sessions': 2,
            'exam_dates': exam_dates,
            'today': timezone.now().date(),

            'chart_categories': json.dumps(ordered_staff_categories),
            'chart_counts': json.dumps(ordered_staff_counts),
            'chart_session_categories': json.dumps(ordered_session_categories),
            'chart_session_totals': json.dumps(ordered_session_totals),
            'chart_category_with_count': zip(ordered_staff_categories, ordered_staff_counts),
            'chart_session_with_total': zip(ordered_session_categories, ordered_session_totals),
        }
        context['user_role'] = role

        return render(request, 'dashboard/dashboard.html', context)
