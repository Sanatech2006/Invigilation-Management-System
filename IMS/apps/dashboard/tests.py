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

        # Dynamic exam dates
        self.date1 = date(2026, 10, 12)  # Release Date
        self.date2 = date(2026, 10, 13)  # Compensation Date
        self.date3 = date(2026, 10, 14)

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

        # Candidate Staff 1: Free in Session 1 on date1; Assigned in BOTH sessions on date2 (Priority 1)
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
            date=self.date2,
            session="1",
            hall_no="LH-102",
            hall_department="Chemistry",
            hall_dept_category="AIDED",
            staff_id=self.staff_p1.staff_id,
            name=self.staff_p1.name
        )
        InvigilationSchedule.objects.create(
            date=self.date2,
            session="2",
            hall_no="LH-103",
            hall_department="Chemistry",
            hall_dept_category="AIDED",
            staff_id=self.staff_p1.staff_id,
            name=self.staff_p1.name
        )

        # Candidate Staff 2: Has duty in Session 2 on date1 (free in Session 1); Assigned in Session 1 on date2 (Priority 2)
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
            session="2",  # Assigned to Session 2 on release date -> Free in Session 1 (being released)
            hall_no="LH-104",
            hall_department="Chemistry",
            hall_dept_category="AIDED",
            staff_id=self.staff_s1.staff_id,
            name=self.staff_s1.name
        )
        InvigilationSchedule.objects.create(
            date=self.date2,
            session="1",  # Assigned in Session 1 on compensation date
            hall_no="LH-105",
            hall_department="Mathematics",
            hall_dept_category="AIDED",
            staff_id=self.staff_s1.staff_id,
            name=self.staff_s1.name
        )

        # Candidate Staff 3: Assigned to Session 1 on date1 (free in Session 2); Assigned in Session 2 on date2
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
            session="1",  # Assigned to Session 1 on release date -> Free in Session 2
            hall_no="LH-106A",
            hall_department="Mathematics",
            hall_dept_category="AIDED",
            staff_id=self.staff_s2.staff_id,
            name=self.staff_s2.name
        )
        InvigilationSchedule.objects.create(
            date=self.date2,
            session="2",  # Assigned in Session 2 on compensation date
            hall_no="LH-106",
            hall_department="Computer Science",
            hall_dept_category="AIDED",
            staff_id=self.staff_s2.staff_id,
            name=self.staff_s2.name
        )

        # Candidate Staff 4: Already assigned to Session 1 on date1 (Release date) -> Must be EXCLUDED
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
            session="1",  # Busy in Session 1 on release date
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

        # Candidate Staff 5: Free on date1, but has NO duty on date2 (Compensation date) -> Must be EXCLUDED
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
        Requirements 3 & 6 and Spec Section 3:
        When Staff A releases Session 1 on date1 (Oct 12) with compensation date date2 (Oct 13):
        - Candidate P1: Free in both sessions on date1 -> 'BOTH SESSIONS', Priority 1
        - Candidate S1: Free in Session 1 (assigned to Session 2) on date1 -> 'SESSION 1', Priority 2
        - Candidate S2: Assigned to Session 1 on date1 -> EXCLUDED (busy in Session 1)
        - Candidate Busy: Assigned to Session 1 on date1 -> EXCLUDED
        - Candidate No Comp Duty: Free on date1 but has no duty on date2 -> EXCLUDED
        """
        self._login_as_staff()
        response = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date1_str,
                'comparison_date': self.date2_str,
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

        staff_map = {s['staff_id']: s for s in data['staff']}

        # Staff P1 -> Free in both sessions on date1 -> BOTH SESSIONS, Priority 1
        self.assertIn(self.staff_p1.staff_id, staff_map)
        self.assertEqual(staff_map[self.staff_p1.staff_id]['availability'], 'BOTH SESSIONS')
        self.assertEqual(staff_map[self.staff_p1.staff_id]['priority'], 1)

        # Staff S1 -> Free in Session 1 (assigned Session 2) on date1 -> SESSION 1, Priority 2
        self.assertIn(self.staff_s1.staff_id, staff_map)
        self.assertEqual(staff_map[self.staff_s1.staff_id]['availability'], 'SESSION 1')
        self.assertEqual(staff_map[self.staff_s1.staff_id]['priority'], 2)

        # Staff S2 -> Assigned to Session 1 on date1 -> NOT included
        self.assertNotIn(self.staff_s2.staff_id, staff_map)

        # Staff Busy -> Assigned in Session 1 on date1 -> NOT included
        self.assertNotIn(self.staff_busy.staff_id, staff_map)

        # Staff No Comp Duty -> Has no duty on date2 -> NOT included
        self.assertNotIn(self.staff_no_comp_duty.staff_id, staff_map)

    def test_priority_ordering(self):
        """Requirement 4: Priority 1 (Both Sessions) must strictly precede Priority 2 (Single Session)."""
        self._login_as_staff()
        response = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date1_str,
                'comparison_date': self.date2_str,
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
                'selected_date': self.date1_str,
                'comparison_date': self.date2_str,
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
                'selected_date': self.date1_str,
                'comparison_date': self.date2_str,
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
                'selected_date': self.date1_str,
                'comparison_date': self.date2_str,
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
                'selected_date': self.date1_str,
                'comparison_date': self.date2_str,
                'session_availability': 'SESSION 1',
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        s1_staff = resp_s1.json()['staff']
        self.assertTrue(all(s['availability'] == 'SESSION 1' for s in s1_staff))
        self.assertIn(self.staff_s1.staff_id, [s['staff_id'] for s in s1_staff])
        self.assertNotIn(self.staff_p1.staff_id, [s['staff_id'] for s in s1_staff])

        # 3. Filter for SESSION 2 when releasing Session 2
        duty_date3_s2 = InvigilationSchedule.objects.create(
            date=self.date3,
            session="2",
            hall_no="LH-109",
            hall_department="Mathematics",
            hall_dept_category="AIDED",
            staff_id=self.logged_staff.staff_id,
            name=self.logged_staff.name
        )
        duty_s2_cand = InvigilationSchedule.objects.create(
            date=self.date3,
            session="1",  # Assigned to Session 1 on release date -> free in Session 2
            hall_no="LH-110",
            hall_department="Mathematics",
            hall_dept_category="AIDED",
            staff_id=self.staff_s2.staff_id,
            name=self.staff_s2.name
        )
        date3_str = self.date3.strftime('%Y-%m-%d')
        resp_s2 = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': date3_str,
                'comparison_date': self.date2_str,
                'session_availability': 'SESSION 2',
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        s2_staff = resp_s2.json()['staff']
        self.assertTrue(all(s['availability'] == 'SESSION 2' for s in s2_staff))
        self.assertIn(self.staff_s2.staff_id, [s['staff_id'] for s in s2_staff])
        self.assertNotIn(self.staff_s1.staff_id, [s['staff_id'] for s in s2_staff])
        duty_date3_s2.delete()
        duty_s2_cand.delete()

    def test_combined_filters(self):
        """Requirement 7: Combined filters work together and maintain priority order."""
        self._login_as_staff()

        # Filter Physics + BOTH SESSIONS
        resp = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date1_str,
                'comparison_date': self.date2_str,
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
        self.client.get(reverse('staff_availability'), {'selected_date': self.date1_str, 'comparison_date': self.date2_str})
        self.client.get(reverse('staff_availability'), {'selected_date': self.date1_str, 'department': 'Physics'})
        self.client.get(reverse('staff_availability'), {'selected_date': self.date1_str, 'session_availability': 'SESSION 1'})

        final_count = InvigilationSchedule.objects.count()
        final_records = list(InvigilationSchedule.objects.values('serial_number', 'staff_id', 'date', 'session'))

        self.assertEqual(initial_count, final_count)
        self.assertEqual(initial_records, final_records)

    def test_department_category_restriction_enforced(self):
        """
        User Requirement 1: Staff can only view staff from their own department category.
        Staff from other department categories (e.g. SFM, SFW) must not be returned.
        """
        # Create an SFM candidate with duty on date2 (compensation date) and free on date1
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
            date=self.date2,
            session="1",
            hall_no="LH-201",
            hall_department="SFM Commerce",
            hall_dept_category="SFM",
            staff_id=staff_sfm.staff_id,
            name=staff_sfm.name
        )

        # Create an SFW candidate with duty on date2 (compensation date) and free on date1
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
            date=self.date2,
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
                'selected_date': self.date1_str,
                'comparison_date': self.date2_str,
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

        # SFM and SFW candidates must NOT be returned
        self.assertNotIn(staff_sfm.staff_id, returned_ids)
        self.assertNotIn(staff_sfw.staff_id, returned_ids)

        # Department filter dropdown in HTML must only list AIDED departments
        html_resp = self.client.get(
            reverse('staff_availability'),
            {'selected_date': self.date1_str, 'comparison_date': self.date2_str}
        )
        html_content = html_resp.content.decode('utf-8')
        self.assertIn('Physics', html_content)
        self.assertNotIn('SFM Commerce', html_content)
        self.assertNotIn('SFW English', html_content)

        # Now log in as SFM staff and verify only SFM candidate is returned
        sfm_rel = InvigilationSchedule.objects.create(
            date=self.date1,
            session="1",
            hall_no="LH-200",
            hall_department="SFM Commerce",
            hall_dept_category="SFM",
            staff_id=staff_sfm.staff_id,
            name=staff_sfm.name
        )
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
            date=self.date2,
            session="2",
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
                'selected_date': self.date1_str,
                'comparison_date': self.date2_str,
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        sfm_data = sfm_resp.json()
        sfm_returned_ids = [s['staff_id'] for s in sfm_data['staff']]
        self.assertIn(staff_sfm_2.staff_id, sfm_returned_ids)
        self.assertNotIn(self.staff_p1.staff_id, sfm_returned_ids)
        self.assertNotIn(staff_sfw.staff_id, sfm_returned_ids)

        sfm_rel.delete()

    def test_dynamic_session_filter_when_assigned_session_1_on_release_date(self):
        """
        Section 1: The release date and Staff Availability by Session must be treated as a pair.
        The available session options must depend on the session Staff A wants to release on the selected release date.
        When Staff A has Session 1 duty on release date (date1):
        Dropdown options: BOTH SESSIONS, SESSION 1 (SESSION 2 must be hidden).
        """
        self._login_as_staff()

        # Logged-in staff has Session 1 on date1 (from setUp)
        response = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date1_str,
                'comparison_date': self.date2_str,
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        allowed_options = [opt['value'] for opt in data['allowed_session_options']]

        self.assertIn('BOTH SESSIONS', allowed_options)
        self.assertIn('SESSION 1', allowed_options)
        self.assertNotIn('SESSION 2', allowed_options)

        # In HTML response, sessionFilter dropdown reflects these options
        html_resp = self.client.get(
            reverse('staff_availability'),
            {'selected_date': self.date1_str, 'comparison_date': self.date2_str}
        )
        content = html_resp.content.decode('utf-8')
        self.assertIn('value="BOTH SESSIONS"', content)
        self.assertIn('value="SESSION 1"', content)
        self.assertNotIn('value="SESSION 2"', content)

    def test_dynamic_session_filter_when_assigned_session_2_on_release_date(self):
        """
        Section 1: When Staff A has Session 2 duty on release date (date3):
        Dropdown options: BOTH SESSIONS, SESSION 2 (SESSION 1 must be hidden).
        """
        self._login_as_staff()

        # Assign logged-in staff to Session 2 on date3 (release date)
        rel_duty_s2 = InvigilationSchedule.objects.create(
            date=self.date3,
            session="2",
            hall_no="LH-101",
            hall_department="Computer Science",
            hall_dept_category="AIDED",
            staff_id=self.logged_staff.staff_id,
            name=self.logged_staff.name
        )
        date3_str = self.date3.strftime('%Y-%m-%d')

        response = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': date3_str,
                'comparison_date': self.date2_str,
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        allowed_options = [opt['value'] for opt in data['allowed_session_options']]

        self.assertIn('BOTH SESSIONS', allowed_options)
        self.assertIn('SESSION 2', allowed_options)
        self.assertNotIn('SESSION 1', allowed_options)

        html_resp = self.client.get(
            reverse('staff_availability'),
            {'selected_date': date3_str, 'comparison_date': self.date2_str}
        )
        content = html_resp.content.decode('utf-8')
        self.assertIn('value="BOTH SESSIONS"', content)
        self.assertIn('value="SESSION 2"', content)
        self.assertNotIn('value="SESSION 1"', content)

        rel_duty_s2.delete()

    def test_dynamic_session_filter_when_assigned_both_sessions_on_release_date(self):
        """
        Section 1: When Staff A has both sessions on release date:
        Show all 3 options: BOTH SESSIONS, SESSION 1, SESSION 2.
        """
        self._login_as_staff()

        # Assign Staff A to Session 2 on date1 as well (has both sessions on date1)
        d2 = InvigilationSchedule.objects.create(
            date=self.date1,
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
                'selected_date': self.date1_str,
                'comparison_date': self.date2_str,
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        allowed_options = [opt['value'] for opt in data['allowed_session_options']]
        self.assertEqual(allowed_options, ['BOTH SESSIONS', 'SESSION 1', 'SESSION 2'])

        html_resp = self.client.get(
            reverse('staff_availability'),
            {'selected_date': self.date1_str, 'comparison_date': self.date2_str}
        )
        content = html_resp.content.decode('utf-8')
        self.assertIn('value="BOTH SESSIONS"', content)
        self.assertIn('value="SESSION 1"', content)
        self.assertIn('value="SESSION 2"', content)

        d2.delete()

    def test_dynamic_session_filter_when_no_duties_on_release_date(self):
        """
        Section 1: When Staff A has no duties on release date (date2):
        Dropdown options: BOTH SESSIONS, SESSION 1, SESSION 2.
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
        allowed_options = [opt['value'] for opt in data['allowed_session_options']]

        self.assertEqual(allowed_options, ['BOTH SESSIONS', 'SESSION 1', 'SESSION 2'])

    def test_dropdown_updates_when_release_date_changes(self):
        """
        Section 1: Dropdown options must update dynamically when the release date changes.
        Do not base these options on Staff A's compensation-date assignments.
        """
        self._login_as_staff()

        # Date 1 (Staff A has Session 1 duty) -> ['BOTH SESSIONS', 'SESSION 1']
        resp_date1 = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date1_str,
                'comparison_date': self.date2_str,
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        opts_date1 = [opt['value'] for opt in resp_date1.json()['allowed_session_options']]
        self.assertEqual(opts_date1, ['BOTH SESSIONS', 'SESSION 1'])

        # Date 2 (Staff A has NO duty) -> ['BOTH SESSIONS', 'SESSION 1', 'SESSION 2']
        resp_date2 = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date2_str,
                'comparison_date': self.date1_str,
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        opts_date2 = [opt['value'] for opt in resp_date2.json()['allowed_session_options']]
        self.assertEqual(opts_date2, ['BOTH SESSIONS', 'SESSION 1', 'SESSION 2'])

        # Adding a Session 2 duty on the compensation date (date2) does NOT change options for release date (date1)
        comp_duty = InvigilationSchedule.objects.create(
            date=self.date2,
            session="2",
            hall_no="LH-101",
            hall_department="Computer Science",
            hall_dept_category="AIDED",
            staff_id=self.logged_staff.staff_id,
            name=self.logged_staff.name
        )
        resp_date1_again = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date1_str,
                'comparison_date': self.date2_str,
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        opts_date1_again = [opt['value'] for opt in resp_date1_again.json()['allowed_session_options']]
        self.assertEqual(opts_date1_again, ['BOTH SESSIONS', 'SESSION 1'])
        comp_duty.delete()

    def test_stale_session_filter_cleared_on_backend(self):
        """
        Section 4: Clear stale selections when inputs change.
        If a session_availability is passed that is not allowed on the release date,
        the backend clears it to ''.
        """
        self._login_as_staff()

        # On date1, Staff A has Session 1 only -> only BOTH SESSIONS and SESSION 1 allowed.
        # Send session_availability='SESSION 2', which is stale/invalid for date1.
        response = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date1_str,
                'comparison_date': self.date2_str,
                'session_availability': 'SESSION 2',
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['session_filter'], '')

    def test_invalid_exchanges_due_to_staff_a_compensation_duty(self):
        """
        Section 2 (Rule 3): Alternate session filtering on compensation date:
        - When Staff A has Session 1 on compensation date, candidates offering only Session 1
          on compensation date cannot be exchanged and are excluded.
        - Candidates offering Session 2 or Both Sessions can be exchanged.
        - When Staff A has both sessions on compensation date, no exchange is possible.
        """
        self._login_as_staff()

        # Case 1: Staff A has Session 1 on date2 (compensation date)
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
                'selected_date': self.date1_str,
                'comparison_date': self.date2_str,
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        returned_ids = [s['staff_id'] for s in data['staff']]

        # Staff S1 has only Session 1 on compensation date -> Must be EXCLUDED (not alternate session)
        self.assertNotIn(self.staff_s1.staff_id, returned_ids)

        # Staff P1 has both sessions on compensation date (including Session 2) -> Must be INCLUDED
        self.assertIn(self.staff_p1.staff_id, returned_ids)

        duty_s1.delete()

        # Case 2: Staff A has BOTH sessions on compensation date -> No exchange possible (total 0)
        d_both_1 = InvigilationSchedule.objects.create(
            date=self.date2,
            session="1",
            hall_no="LH-101",
            hall_department="Computer Science",
            hall_dept_category="AIDED",
            staff_id=self.logged_staff.staff_id,
            name=self.logged_staff.name
        )
        d_both_2 = InvigilationSchedule.objects.create(
            date=self.date2,
            session="2",
            hall_no="LH-102",
            hall_department="Computer Science",
            hall_dept_category="AIDED",
            staff_id=self.logged_staff.staff_id,
            name=self.logged_staff.name
        )

        resp_both = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date1_str,
                'comparison_date': self.date2_str,
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp_both.status_code, 200)
        self.assertEqual(resp_both.json()['total_count'], 0)

        d_both_1.delete()
        d_both_2.delete()

    def test_availability_based_on_compensation_date_not_release_date(self):
        """
        Section 2 & 3: Candidate Staff Eligibility Verification (Spec Example):
        Staff A releases Session 1 on October 12 and selects October 14 as the compensation date.
        - Candidate B: Free in both sessions on October 12 and assigned to Session 1 on October 14 -> BOTH SESSIONS.
        - Candidate C: Free in Session 1, assigned in Session 2 on October 12, assigned in Session 1 on October 14 -> SESSION 1.
        - Candidate D: Already assigned to Session 1 on October 12 -> exclude.
        - Candidate E: Free in Session 1 on October 12 but has no duty on October 14 -> exclude.
        - Candidate F: Free in Session 1 (assigned to Session 2 on date1), assigned in Session 1 on Oct 14 -> SESSION 1.
        """
        self._login_as_staff()

        # Date 1 = 2026-10-12 (Release Date), Date 3 = 2026-10-14 (Compensation Date)
        date3_str = self.date3.strftime('%Y-%m-%d')

        # Candidate B: Free on date1, assigned Session 1 on date3
        cand_b = Staff.objects.create(
            staff_id="STF_CAND_B",
            name="Candidate B",
            dept_name="Physics",
            dept_category="AIDED",
            staff_category="Teaching",
            designation=self.designation,
            mobile="9876543230",
            session=2,
            is_active=True,
            role=4
        )
        InvigilationSchedule.objects.create(
            date=self.date3,
            session="1",
            hall_no="LH-401",
            hall_department="Physics",
            hall_dept_category="AIDED",
            staff_id=cand_b.staff_id,
            name=cand_b.name
        )

        # Candidate C: Free on date1, assigned Session 2 on date3
        cand_c = Staff.objects.create(
            staff_id="STF_CAND_C",
            name="Candidate C",
            dept_name="Mathematics",
            dept_category="AIDED",
            staff_category="Teaching",
            designation=self.designation,
            mobile="9876543231",
            session=2,
            is_active=True,
            role=4
        )
        InvigilationSchedule.objects.create(
            date=self.date3,
            session="2",
            hall_no="LH-402",
            hall_department="Mathematics",
            hall_dept_category="AIDED",
            staff_id=cand_c.staff_id,
            name=cand_c.name
        )

        # Candidate D: Assigned to Session 1 on date1, assigned Session 1 on date3
        cand_d = Staff.objects.create(
            staff_id="STF_CAND_D",
            name="Candidate D",
            dept_name="Physics",
            dept_category="AIDED",
            staff_category="Teaching",
            designation=self.designation,
            mobile="9876543232",
            session=2,
            is_active=True,
            role=4
        )
        InvigilationSchedule.objects.create(
            date=self.date1,
            session="1",  # Busy in session being released
            hall_no="LH-403",
            hall_department="Physics",
            hall_dept_category="AIDED",
            staff_id=cand_d.staff_id,
            name=cand_d.name
        )
        InvigilationSchedule.objects.create(
            date=self.date3,
            session="1",
            hall_no="LH-404",
            hall_department="Physics",
            hall_dept_category="AIDED",
            staff_id=cand_d.staff_id,
            name=cand_d.name
        )

        # Candidate E: Free in Session 1 on date1, has NO duty on date3
        cand_e = Staff.objects.create(
            staff_id="STF_CAND_E",
            name="Candidate E",
            dept_name="Physics",
            dept_category="AIDED",
            staff_category="Teaching",
            designation=self.designation,
            mobile="9876543233",
            session=2,
            is_active=True,
            role=4
        )

        # Candidate F: Assigned to Session 2 on date1 (free in Session 1!), assigned Session 1 on date3
        cand_f = Staff.objects.create(
            staff_id="STF_CAND_F",
            name="Candidate F",
            dept_name="Chemistry",
            dept_category="AIDED",
            staff_category="Teaching",
            designation=self.designation,
            mobile="9876543234",
            session=2,
            is_active=True,
            role=4
        )
        InvigilationSchedule.objects.create(
            date=self.date1,
            session="2",  # Free in Session 1!
            hall_no="LH-405",
            hall_department="Chemistry",
            hall_dept_category="AIDED",
            staff_id=cand_f.staff_id,
            name=cand_f.name
        )
        InvigilationSchedule.objects.create(
            date=self.date3,
            session="1",
            hall_no="LH-406",
            hall_department="Chemistry",
            hall_dept_category="AIDED",
            staff_id=cand_f.staff_id,
            name=cand_f.name
        )

        response = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date1_str,
                'comparison_date': date3_str,
                'format': 'json',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        staff_map = {s['staff_id']: s for s in data['staff']}

        # Candidate B: Free on date1, assigned Session 1 on date3 -> Eligible, label 'BOTH SESSIONS'
        self.assertIn(cand_b.staff_id, staff_map)
        self.assertEqual(staff_map[cand_b.staff_id]['availability'], 'BOTH SESSIONS')

        # Candidate C: Free on date1, assigned Session 2 on date3 -> Eligible, label 'BOTH SESSIONS'
        self.assertIn(cand_c.staff_id, staff_map)
        self.assertEqual(staff_map[cand_c.staff_id]['availability'], 'BOTH SESSIONS')

        # Candidate D: Assigned to Session 1 on date1 -> Excluded
        self.assertNotIn(cand_d.staff_id, staff_map)

        # Candidate E: Free on date1 but has no duty on date3 -> Excluded
        self.assertNotIn(cand_e.staff_id, staff_map)

        # Candidate F: Assigned to Session 2 on date1 (free in Session 1) -> Eligible, label 'SESSION 1'!
        self.assertIn(cand_f.staff_id, staff_map)
        self.assertEqual(staff_map[cand_f.staff_id]['availability'], 'SESSION 1')

    def test_vertical_and_horizontal_pagination(self):
        """
        User Requirement 2: Vertical pagination with page navigation controls,
        preserving filters across pages. Horizontal pagination controls present in HTML.
        """
        self._login_as_staff()

        # Create additional AIDED candidates with duties on date2 (compensation date) to test multiple pages
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
                date=self.date2,
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
                'selected_date': self.date1_str,
                'comparison_date': self.date2_str,
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
                'selected_date': self.date1_str,
                'comparison_date': self.date2_str,
                'page': '2',
                'page_size': '10',
            }
        )
        self.assertEqual(resp_p2.status_code, 200)
        content_p2 = resp_p2.content.decode('utf-8')
        self.assertIn('Page 2 of', content_p2)
        self.assertIn('Prev', content_p2)

        # Check that pagination links preserve date and other parameters
        self.assertIn(f'selected_date={self.date1_str}', content_p2)
        self.assertIn(f'comparison_date={self.date2_str}', content_p2)

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

    def test_session_dropdown_displays_only_three_values(self):
        """
        Verify that Staff Availability (By Session) dropdown displays only:
        BOTH SESSIONS, SESSION 1, SESSION 2 (or allowed subset based on release date),
        and removes Priority 1, Option 1, etc.
        """
        self._login_as_staff()

        # Date 2 is selected date; Staff A has no duties on date2 -> all 3 options available
        resp = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date2_str,
                'comparison_date': self.date1_str,
            }
        )
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf-8')

        # Check label is "Staff Availability (By Session)"
        self.assertIn('Staff Availability (By Session)', content)

        # Extract options inside select id="sessionFilter"
        import re
        select_match = re.search(r'<select[^>]*id="sessionFilter"[^>]*>(.*?)</select>', content, re.DOTALL)
        self.assertIsNotNone(select_match)
        select_html = select_match.group(1)

        options = re.findall(r'<option[^>]*>(.*?)</option>', select_html, re.DOTALL)
        cleaned_options = [re.sub(r'\s+', ' ', opt).strip() for opt in options if opt.strip()]

        # The dropdown should contain only these three values: BOTH SESSIONS, SESSION 1, SESSION 2
        self.assertEqual(cleaned_options, ['BOTH SESSIONS', 'SESSION 1', 'SESSION 2'])

        # Options must not contain "Priority 1", "Priority 2", "Option 1", or "All Available"
        self.assertNotIn('Priority 1', select_html)
        self.assertNotIn('Priority 2', select_html)
        self.assertNotIn('Option 1', select_html)
        self.assertNotIn('All Available', select_html)

        # On date1 (where Staff A has Session 1), only BOTH SESSIONS and SESSION 1 are available:
        resp_date1 = self.client.get(
            reverse('staff_availability'),
            {
                'selected_date': self.date1_str,
                'comparison_date': self.date2_str,
            }
        )
        self.assertEqual(resp_date1.status_code, 200)
        content_date1 = resp_date1.content.decode('utf-8')
        match_date1 = re.search(r'<select[^>]*id="sessionFilter"[^>]*>(.*?)</select>', content_date1, re.DOTALL)
        self.assertIsNotNone(match_date1)
        opts_date1 = re.findall(r'<option[^>]*>(.*?)</option>', match_date1.group(1), re.DOTALL)
        cleaned_opts_date1 = [re.sub(r'\s+', ' ', opt).strip() for opt in opts_date1 if opt.strip()]
        self.assertEqual(cleaned_opts_date1, ['BOTH SESSIONS', 'SESSION 1'])
