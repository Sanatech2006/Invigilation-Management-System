from django.test import TestCase, Client
from django.urls import reverse
from datetime import date
from apps.staff.models import Staff, Designation
from apps.invigilation_schedule.models import InvigilationSchedule
from apps.exam_dates.models import ExamDate

class StaffSwapTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.designation = Designation.objects.create(
            name="Assistant Professor",
            category="Teaching"
        )
        self.date1 = date(2026, 9, 1)
        self.date2 = date(2026, 9, 2)
        ExamDate.objects.create(date=self.date1)
        ExamDate.objects.create(date=self.date2)

        # Unallotted Staff A (Computer Science)
        self.staff_a = Staff.objects.create(
            staff_id="STF001",
            name="Staff A",
            staff_category="Teaching",
            dept_category="Aided",
            dept_name="Computer Science",
            designation=self.designation,
            session=2,
            is_active=True,
            password="password"
        )

        # Assigned Staff B (Physics)
        self.staff_b = Staff.objects.create(
            staff_id="STF002",
            name="Staff B",
            staff_category="Teaching",
            dept_category="Aided",
            dept_name="Physics",
            designation=self.designation,
            session=2,
            is_active=True,
            password="password"
        )

        # Unassigned Slot 1 (Mathematics Hall on date1, session 1)
        self.slot1 = InvigilationSchedule.objects.create(
            date=self.date1,
            session="1",
            hall_no="H1",
            hall_department="Mathematics",
            hall_dept_category="Aided",
            staff_id=None
        )

        # Slot 2 assigned to Staff B (Chemistry Hall on date2, session 1)
        self.slot2 = InvigilationSchedule.objects.create(
            date=self.date2,
            session="1",
            hall_no="H2",
            hall_department="Chemistry",
            hall_dept_category="Aided",
            staff_id=self.staff_b.staff_id,
            name=self.staff_b.name,
            designation=str(self.designation),
            staff_category=self.staff_b.staff_category,
            dept_category=self.staff_b.dept_category,
            dept_name=self.staff_b.dept_name
        )

        # Slot 3 unassigned with different dept_category (SFM)
        self.slot3 = InvigilationSchedule.objects.create(
            date=self.date1,
            session="2",
            hall_no="H3",
            hall_department="Biology",
            hall_dept_category="SFM",
            staff_id=None
        )

    def test_staff_swap_view(self):
        response = self.client.get(reverse('manual_assignment:staff_swap'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manual_assignment/staff_swap.html')

    def test_get_swap_unassigned_halls_filtering(self):
        response = self.client.get(reverse('manual_assignment:get_swap_unassigned_halls'), {'staff_id': self.staff_a.staff_id})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['dept_category'], 'Aided')

        serials = [slot['serial_number'] for slot in data['unassigned_slots']]
        self.assertIn(self.slot1.serial_number, serials)
        self.assertNotIn(self.slot3.serial_number, serials)

    def test_get_swap_available_dates(self):
        # When Staff A has no assignments, all exam dates are available
        response = self.client.get(reverse('manual_assignment:get_swap_available_dates'), {'staff_id': self.staff_a.staff_id})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        dates = [d['date_str'] for d in data['available_dates']]
        self.assertIn(self.date1.strftime('%Y-%m-%d'), dates)
        self.assertIn(self.date2.strftime('%Y-%m-%d'), dates)

        # Assign Staff A to date1
        self.slot1.staff_id = self.staff_a.staff_id
        self.slot1.save()

        # Date 1 must now be excluded, only Date 2 should remain
        response2 = self.client.get(reverse('manual_assignment:get_swap_available_dates'), {'staff_id': self.staff_a.staff_id})
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()
        dates2 = [d['date_str'] for d in data2['available_dates']]
        self.assertNotIn(self.date1.strftime('%Y-%m-%d'), dates2)
        self.assertIn(self.date2.strftime('%Y-%m-%d'), dates2)

        # Reset slot1 for subsequent tests
        self.slot1.staff_id = None
        self.slot1.save()

    def test_find_eligible_swap_staff_success(self):
        response = self.client.get(reverse('manual_assignment:find_eligible_swap_staff'), {
            'staff_a_id': self.staff_a.staff_id,
            'slot1_serial': self.slot1.serial_number,
            'selected_date': self.date2.strftime('%Y-%m-%d')
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['eligible_staff']), 1)
        self.assertEqual(data['eligible_staff'][0]['staff_b_id'], self.staff_b.staff_id)

    def test_parent_dept_violation_ineligible(self):
        # Set Slot 2 hall_department to Computer Science (Staff A's parent department)
        self.slot2.hall_department = "Computer Science"
        self.slot2.save()

        response = self.client.get(reverse('manual_assignment:find_eligible_swap_staff'), {
            'staff_a_id': self.staff_a.staff_id,
            'slot1_serial': self.slot1.serial_number,
            'selected_date': self.date2.strftime('%Y-%m-%d')
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['eligible_staff']), 0)
        self.assertEqual(data['message'], "No valid staff swap found.")

    def test_perform_staff_swap_success(self):
        response = self.client.post(reverse('manual_assignment:perform_staff_swap'), {
            'staff_a_id': self.staff_a.staff_id,
            'slot1_serial': self.slot1.serial_number,
            'staff_b_id': self.staff_b.staff_id,
            'slot2_serial': self.slot2.serial_number,
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

        # Verify DB updates
        self.slot1.refresh_from_db()
        self.slot2.refresh_from_db()

        self.assertEqual(self.slot1.staff_id, self.staff_b.staff_id)
        self.assertEqual(self.slot2.staff_id, self.staff_a.staff_id)

    def test_manual_assignment_menu_structure(self):
        session = self.client.session
        session['role'] = 1
        session.save()

        # 1. On staff_swap page (Manual Assignment submenu):
        # Dropdown remains visible (not hidden) so navigating to submenu pages keeps dropdown open
        response = self.client.get(reverse('manual_assignment:staff_swap'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        self.assertIn('id="manualAssignmentToggle"', content)
        self.assertIn('onclick="toggleManualAssignment(event)"', content)
        self.assertIn('function toggleManualAssignment', content)
        self.assertIn('keepManualAssignmentOpen', content)
        self.assertIn('Manual Assignment', content)
        self.assertIn('id="manualAssignmentChevron"', content)

        # On manual assignment pages, submenu is open by default (not hidden)
        self.assertIn('id="manualAssignmentSubmenu"', content)
        self.assertIn('id="manualAssignmentSubmenu" class="pl-6 space-y-1 border-l-2 border-slate-700/50 ml-6 pt-1"', content)

        # Submenu links are present
        self.assertIn('Assign Staff', content)
        self.assertIn('Staff Swap', content)
        self.assertIn(reverse('manual_assignment:manual_assignment'), content)
        self.assertIn(reverse('manual_assignment:staff_swap'), content)

        # 2. On non-manual assignment page (dashboard):
        # Dropdown is hidden by default
        response_dash = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response_dash.status_code, 200)
        dash_content = response_dash.content.decode('utf-8')
        self.assertIn('id="manualAssignmentSubmenu" class="hidden pl-6 space-y-1 border-l-2 border-slate-700/50 ml-6 pt-1"', dash_content)

    def test_staff_swap_workflow_summary_wording(self):
        response = self.client.get(reverse('manual_assignment:staff_swap'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Check title
        self.assertIn('Swap Workflow Summary', content)

        # Step 4 wording
        self.assertIn('Step 4 — Find and Swap Candidates', content)
        self.assertNotIn('Step 4 & 5', content)
        self.assertNotIn('Step 4 and 5', content)
        self.assertNotIn('Step 4 and Step 5', content)

        # Old explanatory labels must be removed
        self.assertNotIn('UNALLOTTED STAFF (STAFF A)', content)
        self.assertNotIn('UNALLOTTED HALL ASSIGNMENT (SLOT 1)', content)
        self.assertNotIn('ASSIGNED CANDIDATE (STAFF B) & SLOT 2', content)

        # Dynamic summary elements exist
        self.assertIn('id="summaryStaffAName"', content)
        self.assertIn('id="summaryStaffADetails"', content)
        self.assertIn('id="summaryStaffBName"', content)
        self.assertIn('id="summarySlot2Details"', content)

        # Section headings
        self.assertIn('UNALLOTTED STAFF', content)
        self.assertIn('SWAPPING STAFF', content)

    def test_manual_assignment_unallotted_staff_badge(self):
        response = self.client.get(reverse('manual_assignment:manual_assignment'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Check Unallotted Staff badge contains staff and session counts
        self.assertIn('id="staffTotalBadge"', content)
        self.assertIn('id="staffTotal"', content)
        self.assertIn('id="staffSessionsTotal"', content)
        self.assertIn('Staff', content)
        self.assertIn('Session', content)

        # Check visual styling is high contrast and matches
        self.assertIn('text-slate-800', content)
        self.assertIn('border-slate-300', content)

    def test_auto_assign_no_further_assignments_message(self):
        # Staff A is Computer Science (cannot take Mathematics hall slot1 if parent dept or capacity rule applies)
        # Make staff_a capacity 0 so no staff are available
        self.staff_a.session = 0
        self.staff_a.save()
        self.staff_b.session = 1  # already has 1 assignment (slot2)
        self.staff_b.save()

        response = self.client.post(reverse('manual_assignment:auto_assign_staff'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['assignments_made'], 0)
        self.assertGreater(data['remaining_unassigned'], 0)

        expected_prefix = "No Further Assignments Possible\n\n"
        expected_suffix = "\n\nClick Staff Swap to find eligible swap candidates and complete the remaining assignments."
        self.assertTrue(data['message'].startswith(expected_prefix))
        self.assertTrue(data['message'].endswith(expected_suffix))
        self.assertIn("remain unassigned.", data['message'])

    def test_manual_assignment_no_further_assignments_modal(self):
        response = self.client.get(reverse('manual_assignment:manual_assignment'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Check modal structure and elements exist
        self.assertIn('id="noFurtherAssignmentsModal"', content)
        self.assertIn('No Further Assignments Possible', content)
        self.assertIn('id="noAssignHallsCount"', content)
        self.assertIn('id="noAssignSessionsCount"', content)
        self.assertIn('Click Staff Swap to find eligible swap candidates and complete the remaining assignments.', content)
        self.assertIn('id="goToStaffSwapBtn"', content)
        self.assertIn('id="closeNoAssignmentsOkBtn"', content)
        self.assertIn('id="closeNoAssignmentsXBtn"', content)
        self.assertIn(reverse('manual_assignment:staff_swap'), content)


