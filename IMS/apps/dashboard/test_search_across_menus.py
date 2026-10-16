from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
import json

from apps.staff.models import Staff, Designation
from apps.hall.models import Room
from apps.exam_dates.models import ExamDate
from apps.invigilation_schedule.models import InvigilationSchedule


class SearchAcrossAllMenusTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.designation = Designation.objects.create(
            name="Assistant Professor",
            category="Teaching"
        )

        self.date1 = date(2026, 10, 12)
        self.date2 = date(2026, 10, 13)
        ExamDate.objects.create(date=self.date1)
        ExamDate.objects.create(date=self.date2)

        # Admin user (role 1)
        self.admin = Staff.objects.create(
            staff_id="ADM001",
            name="Admin User",
            dept_name="Administration",
            dept_category="AIDED",
            staff_category="Non-Teaching",
            designation=self.designation,
            mobile="9876543200",
            session=0,
            is_active=True,
            role=1,
            password="pass"
        )

        # HOD user (role 2)
        self.hod = Staff.objects.create(
            staff_id="HOD001",
            name="Dr. HOD Computer Science",
            dept_name="Computer Science",
            dept_category="AIDED",
            staff_category="Teaching",
            designation=self.designation,
            mobile="9876543201",
            session=2,
            is_active=True,
            role=2,
            password="pass"
        )

        # Staff user (role 4)
        self.staff1 = Staff.objects.create(
            staff_id="STF001",
            name="Alice Smith",
            dept_name="Computer Science",
            dept_category="AIDED",
            staff_category="Teaching",
            designation=self.designation,
            mobile="9876543210",
            email="alice@test.com",
            session=2,
            is_active=True,
            role=4,
            password="pass"
        )

        self.staff2 = Staff.objects.create(
            staff_id="STF002",
            name="Bob Jones",
            dept_name="Mathematics",
            dept_category="AIDED",
            staff_category="Teaching",
            designation=self.designation,
            mobile="9876543220",
            email="bob@test.com",
            session=2,
            is_active=True,
            role=4,
            password="pass"
        )

        self.room1 = Room.objects.create(
            hall_no="LH-101",
            strength=40,
            staff_required=1,
            block="Main Block",
            dept_name="Computer Science",
            dept_category="AIDED"
        )

        self.room2 = Room.objects.create(
            hall_no="LH-201",
            strength=60,
            staff_required=2,
            block="Science Block",
            dept_name="Mathematics",
            dept_category="AIDED"
        )

    def _login(self, user):
        session = self.client.session
        session['staff_id'] = user.staff_id
        session['role'] = user.role
        session['name'] = user.name
        session['dept_name'] = user.dept_name
        session['dept_category'] = user.dept_category
        session.save()

    # 1. View Schedule Search Tests
    def test_view_schedule_search_markup(self):
        self._login(self.admin)
        response = self.client.get(reverse('view_schedule'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('id="searchInput"', content)
        self.assertIn('id="clearSearchBtn"', content)
        self.assertIn('id="showingCount"', content)

    # 2. Staff Management Search & Filter Tests
    def test_staff_management_search_markup_and_query(self):
        self._login(self.admin)
        response = self.client.get(reverse('staff:staff-management'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('id="searchInput"', content)
        self.assertIn('id="clearStaffSearchBtn"', content)
        self.assertIn('id="staffRecordCount"', content)
        self.assertIn('data-dept-name="computer science"', content)
        self.assertIn('data-staff-type="teaching"', content)

        # Test server-side search query
        search_resp = self.client.get(reverse('staff:staff-management'), {'q': 'Alice'})
        self.assertEqual(search_resp.status_code, 200)
        staff_list = search_resp.context['staff_list']
        self.assertTrue(any(s.name == 'Alice Smith' for s in staff_list))
        self.assertFalse(any(s.name == 'Bob Jones' for s in staff_list))
        self.assertEqual(search_resp.context['search_query'], 'Alice')

    # 3. Hall Management Search Tests
    def test_hall_management_search_markup(self):
        self._login(self.admin)
        response = self.client.get(reverse('hall_management'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('id="roomSearch"', content)
        self.assertIn('id="clearRoomSearchBtn"', content)
        self.assertIn('id="roomRecordCount"', content)
        self.assertIn('resetHallFilters()', content)

    # 4. Check Staff Availability Search Tests
    def test_staff_availability_search_functionality(self):
        # Set up duties: staff1 holds duty on date1 (release), staff2 holds duty on date2 (compensation)
        InvigilationSchedule.objects.create(
            date=self.date1,
            session="1",
            hall_no=self.room1.hall_no,
            hall_department=self.room1.dept_name,
            hall_dept_category="AIDED",
            staff_id=self.staff1.staff_id,
            name=self.staff1.name
        )
        InvigilationSchedule.objects.create(
            date=self.date2,
            session="1",
            hall_no=self.room2.hall_no,
            hall_department=self.room2.dept_name,
            hall_dept_category="AIDED",
            staff_id=self.staff2.staff_id,
            name=self.staff2.name
        )

        self._login(self.staff1)
        response = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date1.strftime('%Y-%m-%d'),
                'comparison_date': self.date2.strftime('%Y-%m-%d'),
            }
        )
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('id="staffSearchInput"', content)
        self.assertIn('id="clearStaffSearchBtn"', content)
        self.assertIn('id="staffTotalMatched"', content)
        self.assertIn('id="staffPaginationInfo"', content)
        self.assertIn('id="staffPaginationNavContainer"', content)

        # Context JSON verification
        self.assertIn('all_available_staff_json', response.context)
        all_staff = json.loads(response.context['all_available_staff_json'])
        self.assertIsInstance(all_staff, list)

        # Server-side search filter test
        search_resp = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date1.strftime('%Y-%m-%d'),
                'comparison_date': self.date2.strftime('%Y-%m-%d'),
                'search': 'Bob',
            }
        )
        self.assertEqual(search_resp.status_code, 200)
        filtered_staff = search_resp.context['available_staff']
        self.assertTrue(all('Bob' in s['name'] for s in filtered_staff))

    # 5. Manual Assignment Search Tests
    def test_manual_assignment_search_markup(self):
        self._login(self.admin)
        response = self.client.get(reverse('manual_assignment:manual_assignment'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('id="staffSearch"', content)
        self.assertIn('id="clearStaffSearchBtn"', content)
        self.assertIn('id="staffTotal"', content)
        self.assertIn('id="staffSessionsTotal"', content)
        self.assertIn('id="hallSearch"', content)
        self.assertIn('id="clearHallSearchBtn"', content)
        self.assertIn('id="hallTotal"', content)

    # 6. HOD Reports Search & Filter Tests
    def test_hod_reports_search_and_filters(self):
        self._login(self.hod)
        response = self.client.get(reverse('reports:hod_reports'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('id="globalSearchInput"', content)
        self.assertIn('id="clearGlobalSearchBtn"', content)
        self.assertIn('id="resetReportsFiltersBtn"', content)
        self.assertIn('id="reportsRecordCount"', content)
        self.assertIn('id="staffIdFilter"', content)
        self.assertIn('id="dateFilter"', content)

        # Context options verification
        self.assertIn('staff_id_list', response.context)
        self.assertIn('date_list', response.context)
        self.assertIsInstance(response.context['staff_id_list'], list)
        self.assertIsInstance(response.context['date_list'], list)
