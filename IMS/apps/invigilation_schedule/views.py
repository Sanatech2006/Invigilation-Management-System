from django.db import transaction
from django.http import JsonResponse
from django.contrib import messages
from .models import InvigilationSchedule
from apps.hall.models import Room
from apps.exam_dates.models import ExamDate
from django.utils.timezone import now
import sys
from django.shortcuts import redirect
from django.shortcuts import render


def generate_schedule(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Debug start
                print("=== STARTING SCHEDULE GENERATION ===", file=sys.stderr)
                
                # 1. Get all required data
                exam_dates = list(ExamDate.objects.filter(date__gte=now().date()))
                rooms = list(Room.objects.all())
                
                if not exam_dates:
                    messages.error(request, "No future exam dates found!")
                    return redirect('generate_schedule')
                
                if not rooms:
                    messages.error(request, "No rooms found!")
                    return redirect('generate_schedule')
                
                # 2. Clear existing data
                deleted_count, _ = InvigilationSchedule.objects.all().delete()
                print(f"Deleted {deleted_count} existing records", file=sys.stderr)
                
                # 3. Create new schedules
                total_created = 0
                for exam_date in exam_dates:
                    for room in rooms:
                        staff_required = getattr(room, 'staff_required', 1)
                        total_slots = staff_required * 2
                        
                        # Create Session 1 slots
                        for _ in range(staff_required):
                            InvigilationSchedule.objects.create(
                                date=exam_date.date,
                                session='Session 1',
                                hall_no=room.hall_no,
                                hall_department=room.dept_name,
                                dept_category=room.dept_category,
                                double_session=False
                            )
                            total_created += 1
                        
                        # Create Session 2 slots
                        for _ in range(staff_required, total_slots):
                            InvigilationSchedule.objects.create(
                                date=exam_date.date,
                                session='Session 2',
                                hall_no=room.hall_no,
                                hall_department=room.dept_name,
                                dept_category=room.dept_category,
                                double_session=False
                            )
                            total_created += 1
                        
                        print(f"Created {total_slots} slots for {room.hall_no} on {exam_date.date}", file=sys.stderr)
                
                # 4. Verify creation
                db_count = InvigilationSchedule.objects.count()
                expected_count = sum(
                    getattr(room, 'staff_required', 1) * 2 * len(exam_dates)
                    for room in rooms
                )
                
                if db_count != expected_count:
                    raise ValueError(f"Created {db_count} records but expected {expected_count}")
                
                messages.success(request, 
                    f"Created {total_created} invigilation slots "
                    f"({len(exam_dates)} dates × {len(rooms)} rooms)"
                )
                return redirect('view_schedule')
                
        except Exception as e:
            messages.error(request, f"Failed to generate schedule: {str(e)}")
            return redirect('generate_schedule')
    
    return render(request, 'generate_schedule.html')

def schedule_api(request):
    try:
        schedules = InvigilationSchedule.objects.all().order_by(
            'date', 'hall_no', 'session'
        ).values(
            'id', 'date', 'session', 'hall_no', 'hall_department',
            'staff_id', 'name', 'designation', 'staff_category',
            'dept_category', 'double_session'
        )
        return JsonResponse({
            'status': 'success',
            'data': list(schedules),
            'count': len(schedules)
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    
def view_schedule(request):  # THIS MUST EXIST
    return render(request, 'view_schedule/view_schedule.html')