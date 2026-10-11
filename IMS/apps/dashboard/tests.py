from datetime import date
from django.test import TestCase, Client
from django.urls import reverse

from apps.staff.models import Staff, Designation
from apps.exam_dates.models import ExamDate
from apps.invigilation_schedule.models import InvigilationSchedule


class StaffAvailabilityCheckerTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.designation = Designation.objects.create(
            name="Assistant Professor",
            category="Teaching"
        )

        # Dynamic exam dates (do not hardcode Oct 12 / Oct 15)
        self.date1 = date(2026, 11, 10)  # Comparison Date
        self.date2 = date(2026, 11, 12)  # Target Selected Date
        self.date3 = date(2026, 11, 14)

        ExamDate.objects.create(date=self.date1)
        ExamDate.objects.create(date=self.date2)
        ExamDate.objects.create(date=self.date3)

        self.date1_str = self.date1.strftime('%Y-%m-%d')
        self.date2_str = self.date2.strftime('%Y-%m-%d')

        # Logged-in Staff (Role 4 = Staff)
        self.logged_staff = Staff.objects.create(
            staff_id="STF_CURRENT",
            name="Logged In Faculty",
            dept_name="Computer Science",
            dept_category="AIDED",
            staff_category="Teaching",
            designation=self.designation,
            mobile="9876543210",
            session=2,
            is_active=True,
            role=4,
            password="password"
        )
        # Logged-in staff has a duty on date1
        InvigilationSchedule.objects.create(
            date=self.date1,
            session="1",
            hall_no="LH-101",
            hall_department="Mathematics",
            hall_dept_category="AIDED",
            staff_id=self.logged_staff.staff_id,
            name=self.logged_staff.name
        )

        # Candidate Staff 1: Has duty on date1; Free in BOTH sessions on date2 (Priority 1)
        self.staff_p1 = Staff.objects.create(
            staff_id="STF_P1",
            name="Dr. Alpha Both",
            dept_name="Physics",
            dept_category="AIDED",
            staff_category="Teaching",
            designation=self.designation,
            mobile="9876543211",
            session=2,
            is_active=True,
            role=4
        )
        InvigilationSchedule.objects.create(
            date=self.date1,
            session="1",
            hall_no="LH-102",
            hall_department="Chemistry",
            hall_dept_category="AIDED",
            staff_id=self.staff_p1.staff_id,
            name=self.staff_p1.name
        )

        # Candidate Staff 2: Has duty on date1; Assigned in Session 2 on date2 -> Free in Session 1 (Priority 2)
        self.staff_s1 = Staff.objects.create(
            staff_id="STF_S1",
            name="Prof. Beta FreeS1",
            dept_name="Physics",
            dept_category="AIDED",
            staff_category="Teaching",
            designation=self.designation,
            mobile="9876543212",
            session=2,
            is_active=True,
            role=4
        )
        InvigilationSchedule.objects.create(
            date=self.date1,
            session="2",
            hall_no="LH-103",
            hall_department="Chemistry",
            hall_dept_category="AIDED",
            staff_id=self.staff_s1.staff_id,
            name=self.staff_s1.name
        )
        InvigilationSchedule.objects.create(
            date=self.date2,
            session="2",  # Busy in session 2, so available in Session 1
            hall_no="LH-104",
            hall_department="Mathematics",
            hall_dept_category="AIDED",
            staff_id=self.staff_s1.staff_id,
            name=self.staff_s1.name
        )

        # Candidate Staff 3: Has duty on date1; Assigned in Session 1 on date2 -> Free in Session 2 (Priority 2)
        self.staff_s2 = Staff.objects.create(
            staff_id="STF_S2",
            name="Dr. Gamma FreeS2",
            dept_name="Mathematics",
            dept_category="AIDED",
            staff_category="Teaching",
            designation=self.designation,
            mobile="9876543213",
            session=2,
            is_active=True,
            role=4
        )
        InvigilationSchedule.objects.create(
            date=self.date1,
            session="1",
            hall_no="LH-105",
            hall_department="Physics",
            hall_dept_category="AIDED",
            staff_id=self.staff_s2.staff_id,
            name=self.staff_s2.name
        )
        InvigilationSchedule.objects.create(
            date=self.date2,
            session="1",  # Busy in session 1, so available in Session 2
            hall_no="LH-106",
            hall_department="Computer Science",
            hall_dept_category="AIDED",
            staff_id=self.staff_s2.staff_id,
            name=self.staff_s2.name
        )

        # Candidate Staff 4: Has duty on date1; Assigned in BOTH sessions on date2 -> NOT available
        self.staff_busy = Staff.objects.create(
            staff_id="STF_BUSY",
            name="Prof. Delta Busy",
            dept_name="Chemistry",
            dept_category="AIDED",
            staff_category="Teaching",
            designation=self.designation,
            mobile="9876543214",
            session=2,
            is_active=True,
            role=4
        )
        InvigilationSchedule.objects.create(
            date=self.date1,
            session="1",
            hall_no="LH-107",
            hall_department="Physics",
            hall_dept_category="AIDED",
            staff_id=self.staff_busy.staff_id,
            name=self.staff_busy.name
        )
        InvigilationSchedule.objects.create(
            date=self.date2,
            session="1",
            hall_no="LH-108",
            hall_department="Physics",
            hall_dept_category="AIDED",
            staff_id=self.staff_busy.staff_id,
            name=self.staff_busy.name
        )
        InvigilationSchedule.objects.create(
            date=self.date2,
            session="2",
            hall_no="LH-109",
            hall_department="Mathematics",
            hall_dept_category="AIDED",
            staff_id=self.staff_busy.staff_id,
            name=self.staff_busy.name
        )

        # Candidate Staff 5: Has NO duty on date1; Free on date2 -> Must NOT be included
        self.staff_no_comp_duty = Staff.objects.create(
            staff_id="STF_NO_COMP",
            name="Dr. Epsilon NoDuty",
            dept_name="Chemistry",
            dept_category="AIDED",
            staff_category="Teaching",
            designation=self.designation,
            mobile="9876543215",
            session=2,
            is_active=True,
            role=4
        )

    def _login_as_staff(self):
        session = self.client.session
        session['staff_id'] = self.logged_staff.staff_id
        session['role'] = 4
        session.save()

    def test_menu_rendered_for_logged_in_staff(self):
        """Requirement 1: Menu named 'Check Staff Availability' must be visible for logged-in staff."""
        self._login_as_staff()
        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        self.assertIn('Check Staff Availability', content)
        self.assertIn(reverse('staff_availability'), content)

    def test_unauthenticated_access_redirects(self):
        """Unauthenticated requests must be redirected to login."""
        response = self.client.get(reverse('staff_availability'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_read_only_access_enforced(self):
        """Requirement 8: Read-Only Access. POST must be rejected with 405 Method Not Allowed."""
        self._login_as_staff()

        # GET is allowed
        get_resp = self.client.get(reverse('staff_availability'))
        self.assertEqual(get_resp.status_code, 200)

        # POST is rejected with 405 Method Not Allowed
        post_resp = self.client.post(reverse('staff_availability'), {'some_data': 'test'})
        self.assertEqual(post_resp.status_code, 405)

    def test_availability_calculation_and_labels(self):
        """
        Requirements 3 & 6:
        - Only staff with duty on comparison date and available on selected date are returned.
        - Labels: 'BOTH SESSIONS', 'SESSION 1', 'SESSION 2'.
        """
        self._login_as_staff()
        response = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date2_str,
                'comparison_date': self.date1_str,
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

        staff_map = {s['staff_id']: s for s in data['staff']}

        # Staff P1 -> BOTH SESSIONS
        self.assertIn(self.staff_p1.staff_id, staff_map)
        self.assertEqual(staff_map[self.staff_p1.staff_id]['availability'], 'BOTH SESSIONS')
        self.assertEqual(staff_map[self.staff_p1.staff_id]['priority'], 1)

        # Staff S1 -> Free in Session 1, busy in Session 2
        self.assertIn(self.staff_s1.staff_id, staff_map)
        self.assertEqual(staff_map[self.staff_s1.staff_id]['availability'], 'SESSION 1')
        self.assertEqual(staff_map[self.staff_s1.staff_id]['priority'], 2)

        # Staff S2 -> Free in Session 2, busy in Session 1
        self.assertIn(self.staff_s2.staff_id, staff_map)
        self.assertEqual(staff_map[self.staff_s2.staff_id]['availability'], 'SESSION 2')
        self.assertEqual(staff_map[self.staff_s2.staff_id]['priority'], 2)

        # Staff Busy -> Assigned in both sessions -> NOT included
        self.assertNotIn(self.staff_busy.staff_id, staff_map)

        # Staff No Comp Duty -> Has no duty on date1 -> NOT included
        self.assertNotIn(self.staff_no_comp_duty.staff_id, staff_map)

    def test_priority_ordering(self):
        """Requirement 4: Priority 1 (Both Sessions) must strictly precede Priority 2 (Single Session)."""
        self._login_as_staff()
        response = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date2_str,
                'comparison_date': self.date1_str,
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        staff_list = response.json()['staff']

        priorities = [s['priority'] for s in staff_list]
        self.assertEqual(priorities, sorted(priorities))

        # Check that the first staff item has Priority 1 and BOTH SESSIONS
        self.assertEqual(staff_list[0]['priority'], 1)
        self.assertEqual(staff_list[0]['availability'], 'BOTH SESSIONS')

        # Check that subsequent staff items have Priority 2
        for s in staff_list[1:]:
            self.assertEqual(s['priority'], 2)
            self.assertIn(s['availability'], ['SESSION 1', 'SESSION 2'])

    def test_display_table_columns_in_html(self):
        """Requirement 5: Table must contain Staff ID, Name, Department, Mobile Number, STAFF AVAILABLE."""
        self._login_as_staff()
        response = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date2_str,
                'comparison_date': self.date1_str,
            }
        )
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Check required table header columns
        self.assertIn('Staff ID', content)
        self.assertIn('Name', content)
        self.assertIn('Department', content)
        self.assertIn('Mobile Number', content)
        self.assertIn('STAFF AVAILABLE', content)

        # Check that staff details appear in table rows
        self.assertIn(self.staff_p1.staff_id, content)
        self.assertIn(self.staff_p1.name, content)
        self.assertIn(self.staff_p1.dept_name, content)
        self.assertIn(self.staff_p1.mobile, content)
        self.assertIn('BOTH SESSIONS', content)

    def test_department_filter(self):
        """Requirement 7: Filter by Department works and maintains priority order."""
        self._login_as_staff()

        # Physics department has staff_p1 (Priority 1) and staff_s1 (Priority 2)
        response = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date2_str,
                'comparison_date': self.date1_str,
                'department': 'Physics',
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        staff_list = response.json()['staff']

        # All returned staff must be from Physics department
        for s in staff_list:
            self.assertEqual(s['department'], 'Physics')

        # Staff S2 (Mathematics) must NOT be in the results
        returned_ids = [s['staff_id'] for s in staff_list]
        self.assertIn(self.staff_p1.staff_id, returned_ids)
        self.assertIn(self.staff_s1.staff_id, returned_ids)
        self.assertNotIn(self.staff_s2.staff_id, returned_ids)

        # Priority order must be preserved: Priority 1 before Priority 2
        self.assertEqual(staff_list[0]['staff_id'], self.staff_p1.staff_id)
        self.assertEqual(staff_list[0]['priority'], 1)
        self.assertEqual(staff_list[1]['staff_id'], self.staff_s1.staff_id)
        self.assertEqual(staff_list[1]['priority'], 2)

    def test_session_availability_filters(self):
        """Requirement 7: Filter by Session Availability works correctly."""
        self._login_as_staff()

        # 1. Filter for BOTH SESSIONS
        resp_both = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date2_str,
                'comparison_date': self.date1_str,
                'session_availability': 'BOTH SESSIONS',
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        both_staff = resp_both.json()['staff']
        self.assertTrue(all(s['availability'] == 'BOTH SESSIONS' for s in both_staff))
        self.assertIn(self.staff_p1.staff_id, [s['staff_id'] for s in both_staff])
        self.assertNotIn(self.staff_s1.staff_id, [s['staff_id'] for s in both_staff])

        # 2. Filter for SESSION 1
        resp_s1 = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date2_str,
                'comparison_date': self.date1_str,
                'session_availability': 'SESSION 1',
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        s1_staff = resp_s1.json()['staff']
        self.assertTrue(all(s['availability'] == 'SESSION 1' for s in s1_staff))
        self.assertIn(self.staff_s1.staff_id, [s['staff_id'] for s in s1_staff])
        self.assertNotIn(self.staff_p1.staff_id, [s['staff_id'] for s in s1_staff])

        # 3. Filter for SESSION 2
        resp_s2 = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date2_str,
                'comparison_date': self.date1_str,
                'session_availability': 'SESSION 2',
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        s2_staff = resp_s2.json()['staff']
        self.assertTrue(all(s['availability'] == 'SESSION 2' for s in s2_staff))
        self.assertIn(self.staff_s2.staff_id, [s['staff_id'] for s in s2_staff])
        self.assertNotIn(self.staff_p1.staff_id, [s['staff_id'] for s in s2_staff])

    def test_combined_filters(self):
        """Requirement 7: Combined filters work together and maintain priority order."""
        self._login_as_staff()

        # Filter Physics + BOTH SESSIONS
        resp = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date2_str,
                'comparison_date': self.date1_str,
                'department': 'Physics',
                'session_availability': 'BOTH SESSIONS',
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        staff_list = resp.json()['staff']
        self.assertEqual(len(staff_list), 1)
        self.assertEqual(staff_list[0]['staff_id'], self.staff_p1.staff_id)
        self.assertEqual(staff_list[0]['department'], 'Physics')
        self.assertEqual(staff_list[0]['availability'], 'BOTH SESSIONS')

    def test_existing_schedule_records_not_modified(self):
        """Requirement 10: Staff Availability Checker must not modify any existing schedule records."""
        self._login_as_staff()

        initial_count = InvigilationSchedule.objects.count()
        initial_records = list(InvigilationSchedule.objects.values('serial_number', 'staff_id', 'date', 'session'))

        # Perform multiple availability queries and filter operations
        self.client.get(reverse('staff_availability'), {'selected_date': self.date2_str, 'comparison_date': self.date1_str})
        self.client.get(reverse('staff_availability'), {'selected_date': self.date2_str, 'department': 'Physics'})
        self.client.get(reverse('staff_availability'), {'selected_date': self.date2_str, 'session_availability': 'SESSION 1'})

        final_count = InvigilationSchedule.objects.count()
        final_records = list(InvigilationSchedule.objects.values('serial_number', 'staff_id', 'date', 'session'))

        self.assertEqual(initial_count, final_count)
        self.assertEqual(initial_records, final_records)

    def test_department_category_restriction_enforced(self):
        """
        User Requirement 1: Staff can only view staff from their own department category.
        Staff from other department categories (e.g. SFM, SFW) must not be returned.
        """
        # Create an SFM candidate with duty on date1 and free on date2
        staff_sfm = Staff.objects.create(
            staff_id="STF_SFM_1",
            name="Prof. SFM Alpha",
            dept_name="SFM Commerce",
            dept_category="SFM",
            staff_category="Teaching",
            designation=self.designation,
            mobile="9876543220",
            session=2,
            is_active=True,
            role=4
        )
        InvigilationSchedule.objects.create(
            date=self.date1,
            session="1",
            hall_no="LH-201",
            hall_department="SFM Commerce",
            hall_dept_category="SFM",
            staff_id=staff_sfm.staff_id,
            name=staff_sfm.name
        )

        # Create an SFW candidate with duty on date1 and free on date2
        staff_sfw = Staff.objects.create(
            staff_id="STF_SFW_1",
            name="Dr. SFW Beta",
            dept_name="SFW English",
            dept_category="SFW",
            staff_category="Teaching",
            designation=self.designation,
            mobile="9876543221",
            session=2,
            is_active=True,
            role=4
        )
        InvigilationSchedule.objects.create(
            date=self.date1,
            session="1",
            hall_no="LH-202",
            hall_department="SFW English",
            hall_dept_category="SFW",
            staff_id=staff_sfw.staff_id,
            name=staff_sfw.name
        )

        # Logged in staff is in AIDED category
        self._login_as_staff()
        response = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date2_str,
                'comparison_date': self.date1_str,
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        returned_ids = [s['staff_id'] for s in data['staff']]

        # AIDED candidates must be returned
        self.assertIn(self.staff_p1.staff_id, returned_ids)
        self.assertIn(self.staff_s1.staff_id, returned_ids)
        self.assertIn(self.staff_s2.staff_id, returned_ids)

        # SFM and SFW candidates must NOT be returned
        self.assertNotIn(staff_sfm.staff_id, returned_ids)
        self.assertNotIn(staff_sfw.staff_id, returned_ids)

        # Department filter dropdown in HTML must only list AIDED departments
        html_resp = self.client.get(
            reverse('staff_availability'),
            {'selected_date': self.date2_str, 'comparison_date': self.date1_str}
        )
        html_content = html_resp.content.decode('utf-8')
        self.assertIn('Physics', html_content)
        self.assertNotIn('SFM Commerce', html_content)
        self.assertNotIn('SFW English', html_content)

        # Now log in as SFM staff and verify only SFM candidate is returned
        staff_sfm_2 = Staff.objects.create(
            staff_id="STF_SFM_2",
            name="Prof. SFM Beta",
            dept_name="SFM Commerce",
            dept_category="SFM",
            staff_category="Teaching",
            designation=self.designation,
            mobile="9876543222",
            session=2,
            is_active=True,
            role=4
        )
        InvigilationSchedule.objects.create(
            date=self.date1,
            session="1",
            hall_no="LH-203",
            hall_department="SFM Commerce",
            hall_dept_category="SFM",
            staff_id=staff_sfm_2.staff_id,
            name=staff_sfm_2.name
        )

        session = self.client.session
        session['staff_id'] = staff_sfm.staff_id
        session['role'] = 4
        session.save()

        sfm_resp = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date2_str,
                'comparison_date': self.date1_str,
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        sfm_data = sfm_resp.json()
        sfm_returned_ids = [s['staff_id'] for s in sfm_data['staff']]
        self.assertIn(staff_sfm_2.staff_id, sfm_returned_ids)
        self.assertNotIn(self.staff_p1.staff_id, sfm_returned_ids)
        self.assertNotIn(staff_sfw.staff_id, sfm_returned_ids)

    def test_dynamic_session_filter_when_assigned_session_1(self):
        """
        User Requirement 3: If logged-in staff is assigned to Session 1 on selected date,
        SESSION 1 and BOTH SESSIONS must not display; only SESSION 2 is available.
        """
        self._login_as_staff()

        # Assign logged-in staff to Session 1 on date2 (selected date)
        duty_s1 = InvigilationSchedule.objects.create(
            date=self.date2,
            session="1",
            hall_no="LH-101",
            hall_department="Computer Science",
            hall_dept_category="AIDED",
            staff_id=self.logged_staff.staff_id,
            name=self.logged_staff.name
        )

        response = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date2_str,
                'comparison_date': self.date1_str,
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        allowed_options = [opt['value'] for opt in data['allowed_session_options']]

        # SESSION 1 and BOTH SESSIONS must not appear
        self.assertNotIn('SESSION 1', allowed_options)
        self.assertNotIn('BOTH SESSIONS', allowed_options)
        # SESSION 2 must appear
        self.assertIn('SESSION 2', allowed_options)

        # In HTML response, option for SESSION 1 must not be inside the sessionFilter select
        html_resp = self.client.get(
            reverse('staff_availability'),
            {'selected_date': self.date2_str, 'comparison_date': self.date1_str}
        )
        content = html_resp.content.decode('utf-8')
        self.assertIn('value="SESSION 2"', content)
        self.assertNotIn('value="SESSION 1"', content)
        self.assertNotIn('value="BOTH SESSIONS"', content)

        # Cleanup
        duty_s1.delete()

    def test_dynamic_session_filter_when_assigned_session_2(self):
        """
        User Requirement 3: If logged-in staff is assigned to Session 2 on selected date,
        SESSION 2 and BOTH SESSIONS must not display; only SESSION 1 is available.
        """
        self._login_as_staff()

        # Assign logged-in staff to Session 2 on date2 (selected date)
        duty_s2 = InvigilationSchedule.objects.create(
            date=self.date2,
            session="2",
            hall_no="LH-101",
            hall_department="Computer Science",
            hall_dept_category="AIDED",
            staff_id=self.logged_staff.staff_id,
            name=self.logged_staff.name
        )

        response = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date2_str,
                'comparison_date': self.date1_str,
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        allowed_options = [opt['value'] for opt in data['allowed_session_options']]

        # SESSION 2 and BOTH SESSIONS must not appear
        self.assertNotIn('SESSION 2', allowed_options)
        self.assertNotIn('BOTH SESSIONS', allowed_options)
        # SESSION 1 must appear
        self.assertIn('SESSION 1', allowed_options)

        # Cleanup
        duty_s2.delete()

    def test_dynamic_session_filter_when_assigned_both_sessions(self):
        """
        User Requirement 3: If logged-in staff is assigned to both sessions on selected date,
        neither SESSION 1, SESSION 2, nor BOTH SESSIONS should appear.
        """
        self._login_as_staff()

        # Assign logged-in staff to Session 1 and Session 2 on date2
        d1 = InvigilationSchedule.objects.create(
            date=self.date2,
            session="1",
            hall_no="LH-101",
            hall_department="Computer Science",
            hall_dept_category="AIDED",
            staff_id=self.logged_staff.staff_id,
            name=self.logged_staff.name
        )
        d2 = InvigilationSchedule.objects.create(
            date=self.date2,
            session="2",
            hall_no="LH-102",
            hall_department="Computer Science",
            hall_dept_category="AIDED",
            staff_id=self.logged_staff.staff_id,
            name=self.logged_staff.name
        )

        response = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date2_str,
                'comparison_date': self.date1_str,
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        allowed_options = [opt['value'] for opt in data['allowed_session_options']]

        # No session filter options should be offered
        self.assertEqual(len(allowed_options), 0)

        html_resp = self.client.get(
            reverse('staff_availability'),
            {'selected_date': self.date2_str, 'comparison_date': self.date1_str}
        )
        content = html_resp.content.decode('utf-8')
        self.assertIn('No Sessions Available (Assigned to Both Sessions)', content)

        # Cleanup
        d1.delete()
        d2.delete()

    def test_vertical_and_horizontal_pagination(self):
        """
        User Requirement 2: Vertical pagination with page navigation controls,
        preserving filters across pages. Horizontal pagination controls present in HTML.
        """
        self._login_as_staff()

        # Create additional AIDED candidates to test multiple pages (say 20 candidates)
        created_staff = []
        created_duties = []
        for i in range(1, 21):
            st = Staff.objects.create(
                staff_id=f"STF_EXTRA_{i}",
                name=f"Extra Staff {i:02d}",
                dept_name="Mathematics",
                dept_category="AIDED",
                staff_category="Teaching",
                designation=self.designation,
                mobile="9876543200",
                session=2,
                is_active=True,
                role=4
            )
            created_staff.append(st)
            d = InvigilationSchedule.objects.create(
                date=self.date1,
                session="1",
                hall_no=f"LH-{300+i}",
                hall_department="Mathematics",
                hall_dept_category="AIDED",
                staff_id=st.staff_id,
                name=st.name
            )
            created_duties.append(d)

        # Request page 1 with page_size=10
        resp_p1 = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date2_str,
                'comparison_date': self.date1_str,
                'page': '1',
                'page_size': '10',
            }
        )
        self.assertEqual(resp_p1.status_code, 200)
        content_p1 = resp_p1.content.decode('utf-8')

        # Check vertical pagination elements
        self.assertIn('Page 1 of', content_p1)
        self.assertIn('Next', content_p1)
        self.assertIn('tableScrollContainer', content_p1)
        self.assertIn('scrollLeftBtn', content_p1)
        self.assertIn('scrollRightBtn', content_p1)

        # Request page 2
        resp_p2 = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date2_str,
                'comparison_date': self.date1_str,
                'page': '2',
                'page_size': '10',
            }
        )
        self.assertEqual(resp_p2.status_code, 200)
        content_p2 = resp_p2.content.decode('utf-8')
        self.assertIn('Page 2 of', content_p2)
        self.assertIn('Prev', content_p2)

        # Check that pagination links preserve date and other parameters
        self.assertIn(f'selected_date={self.date2_str}', content_p2)
        self.assertIn(f'comparison_date={self.date1_str}', content_p2)

        # Cleanup
        for d in created_duties:
            d.delete()
        for st in created_staff:
            st.delete()

    def test_assigned_invigilation_duties_box_ui(self):
        """
        User Requirement 6: Assigned Invigilation Duties box is rendered
        with assigned exam dates, session badge, and hall number.
        """
        self._login_as_staff()

        # Both availability page and dashboard page must render the assigned duty box
        avail_resp = self.client.get(reverse('staff_availability'))
        self.assertEqual(avail_resp.status_code, 200)
        avail_content = avail_resp.content.decode('utf-8')
        self.assertIn('Your Assigned Invigilation Duties', avail_content)
        self.assertIn(self.date1.strftime('%d %b %Y'), avail_content)
        self.assertIn('LH-101', avail_content)

        dash_resp = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(dash_resp.status_code, 200)
        dash_content = dash_resp.content.decode('utf-8')
        self.assertIn('Assigned Invigilation Duties', dash_content)
        self.assertIn(self.date1.strftime('%d %b %Y'), dash_content)
        self.assertIn('LH-101', dash_content)
