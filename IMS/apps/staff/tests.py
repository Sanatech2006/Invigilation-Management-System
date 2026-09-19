import io
import openpyxl
from django.test import TestCase, Client
from django.urls import reverse
from apps.staff.models import Staff, Designation

class BasicStaffExcelUploadTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.designation = Designation.objects.create(
            name="Assistant Professor",
            category="Teaching"
        )
        self.existing_staff = Staff.objects.create(
            staff_id="STF001",
            name="Alice",
            staff_category="Teaching",
            dept_category="Aided",
            dept_name="Computer Science",
            designation=self.designation,
            mobile="9876543210",
            email="alice@test.com",
            date_of_joining="2020-01-01",
            session=2,
            fixed_session=0,
            is_active=True,
            password="pass",
            role=1
        )

    def create_excel_file(self, rows_data, headers=None):
        wb = openpyxl.Workbook()
        ws = wb.active
        if headers is None:
            headers = [
                'staff_id', 'name', 'staff_category', 'designation',
                'dept_category', 'dept_name', 'mobile', 'email',
                'date_of_joining', 'session', 'fixed_session', 'role'
            ]
        ws.append(headers)
        for r in rows_data:
            ws.append(r)

        file_stream = io.BytesIO()
        wb.save(file_stream)
        file_stream.seek(0)
        file_stream.name = 'test_staff.xlsx'
        return file_stream

    def test_basic_excel_upload_creates_and_updates_staff(self):
        """
        Uploading an Excel file directly parses records into database:
        - STF001: existing record is updated with new department
        - STF002: new record is created
        """
        rows = [
            # Existing staff with updated department
            ['STF001', 'Alice', 'Teaching', 'Assistant Professor', 'Aided', 'Information Technology', '9876543210', 'alice@test.com', '2020-01-01', '2', '0', '1'],
            # New staff record
            ['STF002', 'Bob', 'Teaching', 'Assistant Professor', 'Aided', 'Mathematics', '9123456789', 'bob@test.com', '2021-06-01', '2', '0', '1'],
        ]
        excel_file = self.create_excel_file(rows)

        response = self.client.post(
            reverse('staff:staff-management'),
            {'excel_file': excel_file},
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check existing staff was updated
        self.existing_staff.refresh_from_db()
        self.assertEqual(self.existing_staff.dept_name, 'Information Technology')

        # Check new staff was created
        self.assertTrue(Staff.objects.filter(staff_id='STF002').exists())
        bob = Staff.objects.get(staff_id='STF002')
        self.assertEqual(bob.name, 'Bob')

    def test_excel_upload_missing_columns(self):
        """Uploading an Excel file with missing required columns returns error message."""
        incomplete_headers = ['staff_id', 'name', 'mobile']
        rows = [
            ['STF003', 'Charlie', '9998887776'],
        ]
        excel_file = self.create_excel_file(rows, headers=incomplete_headers)

        response = self.client.post(
            reverse('staff:staff-management'),
            {'excel_file': excel_file},
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        messages = list(response.context.get('messages', []))
        self.assertTrue(any('Missing required columns' in str(m) for m in messages))
        self.assertFalse(Staff.objects.filter(staff_id='STF003').exists())

    def test_duplicate_staff_id_handling_and_count_accuracy(self):
        """
        Uploading an Excel file with in-file duplicate staff IDs:
        - First occurrence is processed (created/updated)
        - Second occurrence is flagged as duplicate and skipped
        - Database count equals distinct valid staff IDs
        - Displayed summary clearly separates stored vs duplicate skipped count
        """
        rows = [
            # Row 1: update existing STF001
            ['STF001', 'Alice Updated', 'Teaching', 'Assistant Professor', 'Aided', 'CS', '9876543210', 'alice@test.com', '2020-01-01', '2', '0', '1'],
            # Row 2: duplicate of STF001 with different name
            ['STF001', 'Alice Duplicate', 'Teaching', 'Assistant Professor', 'Aided', 'Math', '9876543210', 'alice2@test.com', '2020-01-01', '2', '0', '1'],
            # Row 3: new staff STF002
            ['STF002', 'Bob New', 'Teaching', 'Assistant Professor', 'Aided', 'Physics', '9123456789', 'bob@test.com', '2021-06-01', '2', '0', '1'],
            # Row 4: duplicate of STF002
            ['STF002', 'Bob Duplicate', 'Teaching', 'Assistant Professor', 'Aided', 'Chemistry', '9123456789', 'bob2@test.com', '2021-06-01', '2', '0', '1'],
        ]
        excel_file = self.create_excel_file(rows)

        response = self.client.post(
            reverse('staff:staff-management'),
            {'excel_file': excel_file},
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        # Only 2 distinct staff records should exist in DB
        self.assertEqual(Staff.objects.count(), 2)

        # STF001 should have the first row's data (Alice Updated), not the duplicate (Alice Duplicate)
        stf001 = Staff.objects.get(staff_id='STF001')
        self.assertEqual(stf001.name, 'Alice Updated')

        # STF002 should have the first row's data (Bob New)
        stf002 = Staff.objects.get(staff_id='STF002')
        self.assertEqual(stf002.name, 'Bob New')

        # Check message accurately reflects 2 stored, 2 duplicates skipped of 4 total
        messages = [str(m) for m in response.context.get('messages', [])]
        self.assertTrue(any('Successfully stored 2 of 4 record(s)' in m for m in messages))
        self.assertTrue(any('2 duplicate record(s) skipped' in m for m in messages))

    def test_preview_and_confirm_import_api(self):
        """
        Tests the 2-step API flow:
        1. Preview returns row classifications (insert, update, duplicate, error)
        2. Confirm commits the records to database
        """
        rows = [
            # Update STF001
            ['STF001', 'Alice API', 'Teaching', 'Assistant Professor', 'Aided', 'CS', '9876543210', 'alice@test.com', '2020-01-01', '2', '0', '1'],
            # New STF003
            ['STF003', 'Charlie', 'Teaching', 'Assistant Professor', 'Aided', 'Bio', '9333344444', 'charlie@test.com', '2022-01-01', '2', '0', '1'],
            # Duplicate STF003
            ['STF003', 'Charlie Dup', 'Teaching', 'Assistant Professor', 'Aided', 'Bio', '9333344444', 'charlie@test.com', '2022-01-01', '2', '0', '1'],
            # Validation Error (invalid email)
            ['STF004', 'David', 'Teaching', 'Assistant Professor', 'Aided', 'Bio', '9444455555', 'not-an-email', '2022-01-01', '2', '0', '1'],
        ]
        excel_file = self.create_excel_file(rows)

        # 1. Preview API
        preview_res = self.client.post(
            reverse('staff:preview_staff_upload'),
            {'excel_file': excel_file}
        )
        self.assertEqual(preview_res.status_code, 200)
        data = preview_res.json()
        self.assertTrue(data['success'])

        summary = data['summary']
        self.assertEqual(summary['total_rows'], 4)
        self.assertEqual(summary['to_update_count'], 1)   # STF001
        self.assertEqual(summary['to_insert_count'], 1)   # STF003
        self.assertEqual(summary['ready_to_store'], 2)
        self.assertEqual(summary['duplicate_count'], 1)   # STF003 duplicate
        self.assertEqual(summary['error_count'], 1)       # STF004 bad email

        # Records array verification
        statuses = [r['status'] for r in data['records']]
        self.assertEqual(statuses, ['update', 'insert', 'duplicate', 'error'])

        # 2. Confirm API
        confirm_res = self.client.post(reverse('staff:confirm_staff_import'))
        self.assertEqual(confirm_res.status_code, 200)
        confirm_data = confirm_res.json()
        self.assertTrue(confirm_data['success'])
        self.assertEqual(confirm_data['summary']['successfully_stored'], 2)

        # DB verification: STF001 updated, STF003 created, STF004 not created
        self.assertEqual(Staff.objects.count(), 2)
        self.assertTrue(Staff.objects.filter(staff_id='STF003').exists())
        self.assertFalse(Staff.objects.filter(staff_id='STF004').exists())
