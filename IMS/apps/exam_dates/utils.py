import logging
from django.db import transaction
from apps.exam_dates.models import ExamDate
from apps.invigilation_schedule.models import InvigilationSchedule
from apps.hall.models import Room

logger = logging.getLogger(__name__)


def sync_invigilation_schedule_dates():
    """
    Synchronizes the staff duty schedule (InvigilationSchedule) with the current exam dates table (ExamDate).

    Key behaviors:
    1. Removes all InvigilationSchedule records whose date is no longer in ExamDate.
    2. For any active exam dates in ExamDate that do not yet exist in InvigilationSchedule:
       Creates default unassigned slots for each room across Session 1 and Session 2.
    3. Preserves all existing schedule records and staff assignments on active exam dates.
    """
    with transaction.atomic():
        current_dates = set(ExamDate.objects.values_list('date', flat=True))

        # 1. Delete orphaned/outdated records for dates removed from ExamDate
        deleted_count, _ = InvigilationSchedule.objects.exclude(date__in=current_dates).delete()
        if deleted_count > 0:
            logger.info("Purged %d outdated schedule records not present in ExamDate.", deleted_count)

        # 2. Check for any current exam dates missing from InvigilationSchedule
        existing_schedule_dates = set(
            InvigilationSchedule.objects.filter(date__in=current_dates).values_list('date', flat=True).distinct()
        )
        missing_dates = current_dates - existing_schedule_dates

        # 3. Create slots for missing active exam dates if rooms exist
        if missing_dates:
            rooms = list(Room.objects.all())
            if rooms:
                new_slots = []
                for missing_date in sorted(missing_dates):
                    for room in rooms:
                        staff_required = getattr(room, 'staff_required', 1) or 1
                        total = staff_required * 2
                        for i in range(total):
                            session_number = "1" if i < total // 2 else "2"
                            new_slots.append(
                                InvigilationSchedule(
                                    date=missing_date,
                                    session=session_number,
                                    hall_no=room.hall_no,
                                    hall_department=room.dept_name,
                                    hall_dept_category=room.dept_category,
                                    dept_category=room.dept_category,
                                    staff_id=None,
                                    name=None,
                                    designation=None,
                                    staff_category=None,
                                    double_session=False,
                                )
                            )
                if new_slots:
                    InvigilationSchedule.objects.bulk_create(new_slots)
                    logger.info(
                        "Created %d duty slots for new exam dates: %s",
                        len(new_slots),
                        sorted(missing_dates)
                    )
