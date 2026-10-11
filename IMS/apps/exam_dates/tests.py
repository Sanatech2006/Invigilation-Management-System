import json
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse

from apps.exam_dates.models import ExamDate
from apps.hall.models import Room
from apps.invigilation_schedule.models import InvigilationSchedule
from apps.staff.models import Staff
from apps.exam_dates.utils import sync_invigilation_schedule_dates


class ExamDateSynchronizationTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a test room
        self.room = Room.objects.create(
            hall_no='H101',
            dept_name='COMPUTER SCIENCE',
            dept_category='AIDED',
            strength=40,
            staff_required=1
        )
        from apps.staff.models import Designation
        self.designation = Designation.objects.create(name='Assistant Professor', category='AIDED')
        # Create a test staff member
        self.staff = Staff.objects.create(
            staff_id='STAFF001',
            name='Prof. Test',
            designation=self.designation,
            dept_name='COMPUTER SCIENCE',
            dept_category='AIDED',
            staff_category='AIDED',
            session=5,
            is_active=True
        )

    def test_sync_removes_outdated_dates_and_keeps_current_dates(self):
        """
        When August dates are deleted from ExamDate and October dates are in ExamDate,
        sync removes all August duties and keeps October duties with staff assignments.
        """
        aug_date = date(2026, 8, 22)
        oct_date = date(2026, 10, 12)

        # Create duty schedule for both dates
        InvigilationSchedule.objects.create(
            date=aug_date,
            session='1',
            hall_no='H101',
            hall_department='COMPUTER SCIENCE',
            hall_dept_category='AIDED',
            dept_category='AIDED',
            staff_id=self.staff.staff_id,
            name=self.staff.name
        )
        InvigilationSchedule.objects.create(
            date=oct_date,
            session='1',
            hall_no='H101',
            hall_department='COMPUTER SCIENCE',
            hall_dept_category='AIDED',
            dept_category='AIDED',
            staff_id=self.staff.staff_id,
            name=self.staff.name
        )

        # Only October is in ExamDate
        ExamDate.objects.create(day_no=1, date=oct_date)

        # Run sync
        sync_invigilation_schedule_dates()

        # August duties must be gone
        self.assertFalse(InvigilationSchedule.objects.filter(date=aug_date).exists())
        # October duties must remain with staff assignment intact
        oct_duty = InvigilationSchedule.objects.filter(date=oct_date).first()
        self.assertIsNotNone(oct_duty)
        self.assertEqual(oct_duty.staff_id, self.staff.staff_id)
        self.assertEqual(oct_duty.name, self.staff.name)

    def test_adding_exam_date_creates_schedule_slots(self):
        """
        When a new exam date is added via save_exam_date, schedule slots are created.
        """
        response = self.client.post(
            reverse('exam_dates:save'),
            data=json.dumps({'date': '2026-10-12', 'day_number': 1}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

        # Check ExamDate created
        self.assertTrue(ExamDate.objects.filter(date=date(2026, 10, 12)).exists())
        # Check schedule slots automatically generated for the room
        slots = InvigilationSchedule.objects.filter(date=date(2026, 10, 12))
        self.assertEqual(slots.count(), 2)  # staff_required (1) * 2 sessions

    def test_deleting_exam_date_removes_duties(self):
        """
        When an exam date is deleted via delete_exam_date, its duties are removed.
        """
        oct_date = date(2026, 10, 12)
        ed = ExamDate.objects.create(day_no=1, date=oct_date)
        sync_invigilation_schedule_dates()
        self.assertTrue(InvigilationSchedule.objects.filter(date=oct_date).exists())

        # Delete the exam date
        response = self.client.delete(reverse('exam_dates:delete', args=[ed.day_no]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

        # Duties for that date must be gone
        self.assertFalse(ExamDate.objects.filter(pk=ed.day_no).exists())
        self.assertFalse(InvigilationSchedule.objects.filter(date=oct_date).exists())

    def test_updating_exam_date_updates_schedule(self):
        """
        When an exam date is updated via update_exam_date, duties are moved to the new date.
        """
        old_date = date(2026, 10, 12)
        new_date = date(2026, 10, 13)
        ed = ExamDate.objects.create(day_no=1, date=old_date)
        sync_invigilation_schedule_dates()

        response = self.client.post(
            reverse('exam_dates:update', args=[ed.day_no]),
            data=json.dumps({'date': '2026-10-13', 'day_number': 1}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

        # Old date should have 0 duties, new date should have duties
        self.assertFalse(InvigilationSchedule.objects.filter(date=old_date).exists())
        self.assertTrue(InvigilationSchedule.objects.filter(date=new_date).exists())

    def test_view_schedule_displays_only_current_exam_dates(self):
        """
        The view_schedule page displays duties only for currently active exam dates.
        """
        aug_date = date(2026, 8, 22)
        oct_date = date(2026, 10, 12)

        # Create schedule for both dates directly
        InvigilationSchedule.objects.create(
            date=aug_date,
            session='1',
            hall_no='H101',
            hall_department='COMPUTER SCIENCE',
            hall_dept_category='AIDED',
            dept_category='AIDED',
            staff_id=self.staff.staff_id,
            name=self.staff.name
        )
        InvigilationSchedule.objects.create(
            date=oct_date,
            session='1',
            hall_no='H101',
            hall_department='COMPUTER SCIENCE',
            hall_dept_category='AIDED',
            dept_category='AIDED',
            staff_id=self.staff.staff_id,
            name=self.staff.name
        )

        # Only October is in ExamDate
        ExamDate.objects.create(day_no=1, date=oct_date)

        response = self.client.get(reverse('view_schedule'))
        self.assertEqual(response.status_code, 200)

        # Context schedules should only contain October
        schedules = list(response.context['schedules'])
        self.assertEqual(len(schedules), 1)
        self.assertEqual(schedules[0].date, oct_date)

        # August must not be in context dates
        context_dates = response.context['dates']
        self.assertIn('Oct. 12, 2026', context_dates)
        self.assertNotIn('Aug. 22, 2026', context_dates)

    def test_filter_options_returns_only_current_dates(self):
        """
        filter-options endpoint returns only dates present in ExamDate.
        """
        oct_date = date(2026, 10, 12)
        ExamDate.objects.create(day_no=1, date=oct_date)
        sync_invigilation_schedule_dates()

        response = self.client.get(reverse('filter_options'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['dates'], ['2026-10-12'])
