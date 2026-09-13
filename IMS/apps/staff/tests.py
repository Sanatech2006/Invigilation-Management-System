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
