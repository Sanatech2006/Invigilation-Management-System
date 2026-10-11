import json
from collections import defaultdict
from datetime import datetime

from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils import timezone

from apps.staff.models import Staff
from apps.hall.models import Room
from apps.exam_dates.models import ExamDate
from apps.invigilation_schedule.models import InvigilationSchedule
from apps.common.decorators import role_required
from django.core.paginator import Paginator


def normalize_date_str(val):
    """Normalize date value/string to YYYY-MM-DD for consistent comparison."""
    if not val:
        return ''
    s = str(val).strip()
    if not s or s.lower() in ('nan', 'none', 'nat'):
        return ''
    if ' ' in s:
        s = s.split(' ')[0]
    for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d', '%m/%d/%Y'):
        try:
            return datetime.strptime(s, fmt).strftime('%Y-%m-%d')
        except ValueError:
            pass
    return s


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
        session_by_category = Room.objects.values('dept_category').annotate(total=Sum('required_session'))
        session_data = {entry['dept_category']: entry['total'] for entry in session_by_category}
        ordered_session_categories = [cat for cat in category_order if cat in session_data]
        ordered_session_totals = [session_data[cat] for cat in ordered_session_categories]
        current_exam_dates = exam_dates.values_list('date', flat=True)
        total_duties_assigned = InvigilationSchedule.objects.filter(
            date__in=current_exam_dates, staff_id__isnull=False
        ).exclude(staff_id='').count()
        unassigned_sessions = InvigilationSchedule.objects.filter(
            date__in=current_exam_dates, staff_id__isnull=True
        ).count()

        staff_id = request.session.get('staff_id')
        logged_in_staff = None
        if staff_id:
            logged_in_staff = Staff.objects.filter(staff_id__iexact=staff_id).first()
        elif request.user.is_authenticated:
            logged_in_staff = (
                Staff.objects.filter(user=request.user).first()
                or Staff.objects.filter(staff_id__iexact=request.user.username).first()
            )

        my_duties = []
        if logged_in_staff:
            my_duties = list(
                InvigilationSchedule.objects.filter(
                    staff_id=logged_in_staff.staff_id,
                    date__in=current_exam_dates
                )
                .values('date', 'session', 'hall_no', 'hall_department')
                .order_by('date', 'session')
            )

        context = {
            'logged_in_staff': logged_in_staff,
            'my_duties': my_duties,
            'total_staff': Staff.objects.count(),
            'total_rooms': Room.objects.count(),
            'total_exam_days': ExamDate.objects.count(),
            'total_sessions': Room.objects.aggregate(total=Sum('required_session'))['total'] or "Not calculated",
            'total_duties_assigned': total_duties_assigned,
            'unassigned_sessions': unassigned_sessions,
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


class StaffAvailabilityView(View):
    """
    Staff Availability Checker
    Strictly read-only view that checks and displays staff members available
    on a selected exam date who have an existing duty on the relevant comparison date.
    
    Priority 1: Free in BOTH sessions (Session 1 and Session 2)
    Priority 2: Free in ONE session (Session 1 or Session 2)
    """
    http_method_names = ['get', 'head', 'options']  # Enforce strict read-only access

    def get(self, request):
        staff_id = request.session.get('staff_id')
        role = request.session.get('role')

        logged_in_staff = None
        if staff_id:
            logged_in_staff = Staff.objects.filter(staff_id__iexact=staff_id).first()
        elif request.user.is_authenticated:
            logged_in_staff = (
                Staff.objects.filter(user=request.user).first()
                or Staff.objects.filter(staff_id__iexact=request.user.username).first()
            )
            if logged_in_staff:
                staff_id = logged_in_staff.staff_id
                role = logged_in_staff.role
                request.session['staff_id'] = staff_id
                request.session['role'] = role

        # Allow roles 1 (Admin), 2 (Squad), 3 (HOD), 4 (Staff)
        if not role or role not in [1, 2, 3, 4]:
            return redirect('login')

        logged_in_dept_category = (logged_in_staff.dept_category or '').strip() if logged_in_staff else ''

        # 1. Fetch all Exam Dates dynamically (no hardcoded dates)
        exam_dates = list(ExamDate.objects.all().order_by('date'))
        exam_date_strs = [d.date.strftime('%Y-%m-%d') for d in exam_dates]

        # 2. Fetch logged-in staff's assigned duties on currently available exam dates only
        my_duties = []
        my_duty_date_strs = []
        my_duties_by_date = defaultdict(list)
        if logged_in_staff:
            my_duties = list(
                InvigilationSchedule.objects.filter(
                    staff_id=logged_in_staff.staff_id,
                    date__in=[d.date for d in exam_dates]
                )
                .values('date', 'session', 'hall_no', 'hall_department')
                .order_by('date', 'session')
            )
            # Distinct duty dates in chronological order
            seen_dates = set()
            for duty in my_duties:
                d_str = duty['date'].strftime('%Y-%m-%d')
                if d_str not in seen_dates:
                    seen_dates.add(d_str)
                    my_duty_date_strs.append(d_str)
                s_val = str(duty['session']).strip().lower()
                if s_val in ('1', 'session 1', 's1', 'forenoon', 'fn'):
                    my_duties_by_date[d_str].append('1')
                elif s_val in ('2', 'session 2', 's2', 'afternoon', 'an'):
                    my_duties_by_date[d_str].append('2')

        # 3. Read input parameters
        selected_date_raw = request.GET.get('selected_date') or request.GET.get('date') or ''
        comparison_date_raw = (
            request.GET.get('comparison_date')
            or request.GET.get('duty_date')
            or request.GET.get('comp_date')
            or ''
        )
        dept_filter = request.GET.get('department', '').strip()
        session_filter = request.GET.get('session_availability') or request.GET.get('session') or ''
        session_filter = session_filter.strip().upper()

        selected_date_str = normalize_date_str(selected_date_raw) if selected_date_raw else ''
        comparison_date_str = normalize_date_str(comparison_date_raw) if comparison_date_raw else ''

        # Dynamic Resolution of Comparison Date if not explicitly passed:
        # Default to the logged-in staff's existing duty date when available,
        # otherwise default to the first available exam date.
        if not comparison_date_str:
            if my_duty_date_strs:
                if selected_date_str and selected_date_str in my_duty_date_strs:
                    diff_duties = [d for d in my_duty_date_strs if d != selected_date_str]
                    comparison_date_str = diff_duties[0] if diff_duties else my_duty_date_strs[0]
                else:
                    comparison_date_str = my_duty_date_strs[0]
            elif exam_date_strs:
                if selected_date_str:
                    diff_exams = [d for d in exam_date_strs if d != selected_date_str]
                    comparison_date_str = diff_exams[0] if diff_exams else exam_date_strs[0]
                else:
                    comparison_date_str = exam_date_strs[0]

        # Dynamic Resolution of Selected Exam Date if not explicitly passed:
        if not selected_date_str:
            if exam_date_strs:
                diff_dates = [d for d in exam_date_strs if d != comparison_date_str]
                selected_date_str = diff_dates[0] if diff_dates else exam_date_strs[0]
            else:
                selected_date_str = ''

        # 4. Determine logged-in staff's schedule on selected_date and dynamically compute allowed session options
        my_s1_assigned = False
        my_s2_assigned = False
        if logged_in_staff and selected_date_str:
            assigned_sessions_on_sel = list(my_duties_by_date.get(selected_date_str, []))
            if not assigned_sessions_on_sel:
                db_sessions = InvigilationSchedule.objects.filter(
                    staff_id=logged_in_staff.staff_id,
                    date=selected_date_str
                ).values_list('session', flat=True)
                for s in db_sessions:
                    s_str = str(s).strip().lower()
                    if s_str in ('1', 'session 1', 's1', 'forenoon', 'fn'):
                        assigned_sessions_on_sel.append('1')
                    elif s_str in ('2', 'session 2', 's2', 'afternoon', 'an'):
                        assigned_sessions_on_sel.append('2')

            if '1' in assigned_sessions_on_sel:
                my_s1_assigned = True
            if '2' in assigned_sessions_on_sel:
                my_s2_assigned = True

        available_session_options = []
        # BOTH SESSIONS is available only when relevant: staff is not assigned to any session on selected date
        if not my_s1_assigned and not my_s2_assigned:
            available_session_options.append({
                'value': 'BOTH SESSIONS',
                'label': 'BOTH SESSIONS (Priority 1)',
            })

        if not my_s1_assigned:
            available_session_options.append({
                'value': 'SESSION 1',
                'label': 'SESSION 1 (Priority 2)',
            })

        if not my_s2_assigned:
            available_session_options.append({
                'value': 'SESSION 2',
                'label': 'SESSION 2 (Priority 2)',
            })

        allowed_session_values = [opt['value'] for opt in available_session_options]
        # Normalize session_filter aliases
        if session_filter in ('1', 'S1'):
            session_filter = 'SESSION 1'
        elif session_filter in ('2', 'S2'):
            session_filter = 'SESSION 2'
        elif session_filter in ('BOTH', 'BOTH_SESSIONS'):
            session_filter = 'BOTH SESSIONS'

        if session_filter and session_filter not in allowed_session_values:
            # Dropdown and backend must not allow/display session if logged-in staff is already assigned to it
            session_filter = ''

        # 5. Fetch distinct departments for filter dropdown (strictly restricted to staff's own dept_category)
        dept_qs = Staff.objects.filter(is_active=True).exclude(dept_name__isnull=True).exclude(dept_name='')
        if logged_in_dept_category:
            dept_qs = dept_qs.filter(dept_category__iexact=logged_in_dept_category)
        departments = list(
            dept_qs.values_list('dept_name', flat=True)
            .distinct()
            .order_by('dept_name')
        )

        available_staff_list = []
        count_both_sessions = 0
        count_session_1 = 0
        count_session_2 = 0

        if comparison_date_str and selected_date_str:
            # Step A: Identify staff members who have an existing duty on the comparison date
            comp_assignments = InvigilationSchedule.objects.filter(
                date=comparison_date_str,
                staff_id__isnull=False
            ).exclude(staff_id='').values('staff_id', 'session', 'hall_no', 'hall_department')

            comp_assigned_ids = set()
            comp_duty_map = defaultdict(list)
            for a in comp_assignments:
                sid = a['staff_id']
                comp_assigned_ids.add(sid)
                s_no = a.get('session')
                h_no = a.get('hall_no')
                if h_no:
                    comp_duty_map[sid].append(f"Session {s_no} (Hall {h_no})")
                else:
                    comp_duty_map[sid].append(f"Session {s_no}")

            # Step B: Fetch active staff details for these candidate staff
            candidates_qs = Staff.objects.filter(
                staff_id__in=comp_assigned_ids,
                is_active=True
            ).select_related('designation')

            # Strictly enforce Department Category restriction in backend
            if logged_in_dept_category:
                candidates_qs = candidates_qs.filter(dept_category__iexact=logged_in_dept_category)

            candidates = list(candidates_qs)
            valid_candidate_ids = {c.staff_id for c in candidates}

            # Step C: Batch fetch existing assignments on the selected date
            sel_assignments = InvigilationSchedule.objects.filter(
                date=selected_date_str,
                staff_id__in=valid_candidate_ids
            ).values_list('staff_id', 'session')

            sel_map = defaultdict(set)
            for sid, sess in sel_assignments:
                if sess:
                    sel_map[sid].add(str(sess).strip().lower())

            include_self = request.GET.get('include_self', '').lower() in ('true', '1', 'yes')

            # Step D: Calculate availability status and priority for each candidate
            for staff in candidates:
                # Exclude the logged-in staff member from candidate results unless include_self is requested
                if not include_self and logged_in_staff and staff.staff_id == logged_in_staff.staff_id:
                    continue

                assigned_sessions = sel_map.get(staff.staff_id, set())

                has_s1 = any(s in ('1', 'session 1', 's1', 'forenoon', 'fn') for s in assigned_sessions)
                has_s2 = any(s in ('2', 'session 2', 's2', 'afternoon', 'an') for s in assigned_sessions)

                # Availability logic:
                if not has_s1 and not has_s2:
                    # Free in both sessions
                    availability_label = 'BOTH SESSIONS'
                    priority = 1
                    count_both_sessions += 1
                elif not has_s1 and has_s2:
                    # Free in Session 1, but assigned in Session 2
                    availability_label = 'SESSION 1'
                    priority = 2
                    count_session_1 += 1
                elif has_s1 and not has_s2:
                    # Free in Session 2, but assigned in Session 1
                    availability_label = 'SESSION 2'
                    priority = 2
                    count_session_2 += 1
                else:
                    # Assigned in both sessions -> Not available on selected date
                    continue

                # Step E: Apply Department Filter
                if dept_filter and dept_filter.upper() not in ('ALL', 'ALL DEPARTMENTS'):
                    staff_dept = (staff.dept_name or '').strip().lower()
                    if staff_dept != dept_filter.lower():
                        continue

                # Step F: Apply Session Availability Filter
                if session_filter and session_filter not in ('ALL', 'ALL SESSIONS', 'ALL AVAILABLE'):
                    if session_filter in ('BOTH', 'BOTH SESSIONS'):
                        if availability_label != 'BOTH SESSIONS':
                            continue
                    elif session_filter in ('1', 'SESSION 1', 'S1'):
                        if availability_label != 'SESSION 1':
                            continue
                    elif session_filter in ('2', 'SESSION 2', 'S2'):
                        if availability_label != 'SESSION 2':
                            continue
                    elif session_filter in ('ANY_S1', 'SESSION 1 AVAILABLE', 'S1 AVAILABLE'):
                        if availability_label not in ('BOTH SESSIONS', 'SESSION 1'):
                            continue
                    elif session_filter in ('ANY_S2', 'SESSION 2 AVAILABLE', 'S2 AVAILABLE'):
                        if availability_label not in ('BOTH SESSIONS', 'SESSION 2'):
                            continue

                dept_display = staff.dept_name or staff.dept_category or '-'
                mobile_display = staff.mobile or '-'
                comp_duty_str = ", ".join(comp_duty_map.get(staff.staff_id, [])) or '-'

                available_staff_list.append({
                    'staff_id': staff.staff_id,
                    'name': staff.name,
                    'department': dept_display,
                    'dept_category': staff.dept_category or '-',
                    'mobile': mobile_display,
                    'availability': availability_label,
                    'priority': priority,
                    'priority_label': f'Priority {priority}',
                    'designation': str(staff.designation.name) if staff.designation else '',
                    'comp_duty': comp_duty_str,
                })

            # Priority 1 (BOTH SESSIONS) comes first, followed by Priority 2 (SESSION 1 & SESSION 2)
            # Secondary sort by name, then staff_id to ensure a deterministic order
            available_staff_list.sort(key=lambda x: (x['priority'], x['name'].lower(), x['staff_id']))

        # Vertical Pagination
        page_size_param = request.GET.get('page_size', '15')
        try:
            page_size = int(page_size_param)
            if page_size not in (10, 15, 25, 50, 100):
                page_size = 15
        except (ValueError, TypeError):
            page_size = 15

        paginator = Paginator(available_staff_list, page_size)
        page_number = request.GET.get('page', 1)
        try:
            page_obj = paginator.get_page(page_number)
        except Exception:
            page_obj = paginator.get_page(1)

        # Build query string for pagination links without 'page'
        query_params = request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        pagination_query_string = query_params.urlencode()

        # JSON response for API or AJAX calls
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
            return JsonResponse({
                'success': True,
                'selected_date': selected_date_str,
                'comparison_date': comparison_date_str,
                'department_filter': dept_filter,
                'session_filter': session_filter,
                'allowed_session_options': available_session_options,
                'logged_in_dept_category': logged_in_dept_category,
                'total_count': len(available_staff_list),
                'total_priority_1': sum(1 for s in available_staff_list if s['priority'] == 1),
                'total_priority_2': sum(1 for s in available_staff_list if s['priority'] == 2),
                'count_both_sessions': count_both_sessions,
                'count_session_1': count_session_1,
                'count_session_2': count_session_2,
                'page': page_obj.number,
                'num_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'staff': available_staff_list,
            })

        context = {
            'logged_in_staff': logged_in_staff,
            'logged_in_dept_category': logged_in_dept_category,
            'my_duties': my_duties,
            'my_duty_date_strs': my_duty_date_strs,
            'my_duties_by_date_json': json.dumps(dict(my_duties_by_date)),
            'my_s1_assigned': my_s1_assigned,
            'my_s2_assigned': my_s2_assigned,
            'available_session_options': available_session_options,
            'exam_dates': exam_dates,
            'exam_date_strs': exam_date_strs,
            'selected_date': selected_date_str,
            'comparison_date': comparison_date_str,
            'departments': departments,
            'dept_filter': dept_filter,
            'session_filter': session_filter,
            'available_staff': available_staff_list,
            'page_obj': page_obj,
            'paginator': paginator,
            'page_size': page_size,
            'pagination_query_string': pagination_query_string,
            'total_available': len(available_staff_list),
            'count_both_sessions': count_both_sessions,
            'count_session_1': count_session_1,
            'count_session_2': count_session_2,
            'user_role': role,
        }
        return render(request, 'dashboard/staff_availability.html', context)

