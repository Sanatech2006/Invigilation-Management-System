import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password
from apps.staff.models import Staff, Designation


class LoginAndForgotPasswordTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.designation = Designation.objects.create(
            name="Assistant Professor",
            category="Teaching"
        )
        self.staff_legacy = Staff.objects.create(
            staff_id="JMCMTS1001",
            name="Ahmed Khan",
            staff_category="Teaching",
            dept_category="Aided",
            dept_name="Computer Science",
            designation=self.designation,
            mobile="9876543210",
            email="ahmed@jmc.edu",
            date_of_joining="2020-06-15",
            session=2,
            fixed_session=0,
            is_active=True,
            password="oldplainpassword",
            role=4
        )
        self.staff_hashed = Staff.objects.create(
            staff_id="JMCMTS1002",
            name="Fatima Bee",
            staff_category="Teaching",
            dept_category="SFM",
            dept_name="Information Technology",
            designation=self.designation,
            mobile="9876543211",
            email="fatima@jmc.edu",
            date_of_joining="2018-07-01",
            session=3,
            fixed_session=0,
            is_active=True,
            password=make_password("SecretPass123"),
            role=3
        )

    def test_login_page_renders_with_forgot_password_and_correct_tab_order(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Check key elements exist
        self.assertIn('name="staff_id"', content)
        self.assertIn('name="password"', content)
        self.assertIn('Forgot Password?', content)
        self.assertIn('id="forgotPasswordModal"', content)
        self.assertIn('id="supportModal"', content)

        # Tab navigation order test:
        # staff_id input should come BEFORE password input, and the Support link
        # must NOT appear in between staff_id and password!
        staff_id_idx = content.find('id="staff_id"')
        password_idx = content.find('id="password"')
        support_idx = content.find('id="supportBtn"')
        forgot_btn_idx = content.find('id="forgotPasswordBtn"')

        self.assertTrue(staff_id_idx != -1 and password_idx != -1)
        self.assertTrue(staff_id_idx < password_idx, "staff_id input must come before password input")
        
        # Verify Support does not interrupt between staff_id and password
        self.assertTrue(password_idx < support_idx, "password input must come before support button")
        self.assertTrue(password_idx < forgot_btn_idx, "password input must come before forgot password button")

    def test_legacy_plaintext_password_login_success(self):
        response = self.client.post(reverse('login'), {
            'staff_id': 'JMCMTS1001',
            'password': 'oldplainpassword',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard:dashboard'))
        self.assertEqual(self.client.session['staff_id'], 'JMCMTS1001')

    def test_legacy_case_insensitive_staff_id_login(self):
        response = self.client.post(reverse('login'), {
            'staff_id': 'jmcmts1001',
            'password': 'oldplainpassword',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard:dashboard'))

    def test_hashed_password_login_success(self):
        response = self.client.post(reverse('login'), {
            'staff_id': 'JMCMTS1002',
            'password': 'SecretPass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard:dashboard'))
        self.assertEqual(self.client.session['staff_id'], 'JMCMTS1002')

    def test_login_invalid_staff_id(self):
        response = self.client.post(reverse('login'), {
            'staff_id': 'NONEXISTENT999',
            'password': 'anypassword',
        })
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any("Invalid USER ID" in str(m) for m in messages))

    def test_login_wrong_password(self):
        response = self.client.post(reverse('login'), {
            'staff_id': 'JMCMTS1001',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any("Wrong Password" in str(m) for m in messages))

    def test_forgot_password_verify_success(self):
        response = self.client.post(
            reverse('forgot_password_verify'),
            json.dumps({'staff_id': 'JMCMTS1001', 'date_of_joining': '2020-06-15'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['staff_id'], 'JMCMTS1001')
        self.assertEqual(data['name'], 'Ahmed Khan')

    def test_forgot_password_verify_case_insensitive_and_date_format_variations(self):
        # Case insensitive staff id and DD-MM-YYYY date format
        response = self.client.post(
            reverse('forgot_password_verify'),
            json.dumps({'staff_id': 'jmcmts1001', 'date_of_joining': '15-06-2020'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

    def test_forgot_password_verify_wrong_doj(self):
        response = self.client.post(
            reverse('forgot_password_verify'),
            json.dumps({'staff_id': 'JMCMTS1001', 'date_of_joining': '2022-01-01'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('Invalid Staff ID or Date of Joining', data['message'])

    def test_forgot_password_verify_invalid_staff_id(self):
        response = self.client.post(
            reverse('forgot_password_verify'),
            json.dumps({'staff_id': 'INVALID999', 'date_of_joining': '2020-06-15'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])

    def test_forgot_password_verify_missing_fields(self):
        response = self.client.post(
            reverse('forgot_password_verify'),
            json.dumps({'staff_id': '', 'date_of_joining': ''}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])

    def test_forgot_password_reset_success(self):
        new_pwd = "MyBrandNewPassword@2026"
        response = self.client.post(
            reverse('forgot_password_reset'),
            json.dumps({
                'staff_id': 'JMCMTS1001',
                'date_of_joining': '2020-06-15',
                'new_password': new_pwd,
                'confirm_password': new_pwd,
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

        # Verify password in database is hashed securely
        self.staff_legacy.refresh_from_db()
        self.assertNotEqual(self.staff_legacy.password, new_pwd)
        self.assertTrue(self.staff_legacy.password.startswith('pbkdf2_sha256$'))
        self.assertTrue(check_password(new_pwd, self.staff_legacy.password))

        # Verify the user can immediately log in with their Staff ID and new password
        login_res = self.client.post(reverse('login'), {
            'staff_id': 'JMCMTS1001',
            'password': new_pwd,
        })
        self.assertEqual(login_res.status_code, 302)
        self.assertEqual(login_res.url, reverse('dashboard:dashboard'))

    def test_forgot_password_reset_mismatch(self):
        response = self.client.post(
            reverse('forgot_password_reset'),
            json.dumps({
                'staff_id': 'JMCMTS1001',
                'date_of_joining': '2020-06-15',
                'new_password': 'Password123',
                'confirm_password': 'PasswordMismatch',
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('match', data['message'].lower())

    def test_forgot_password_reset_short_password(self):
        response = self.client.post(
            reverse('forgot_password_reset'),
            json.dumps({
                'staff_id': 'JMCMTS1001',
                'date_of_joining': '2020-06-15',
                'new_password': '123',
                'confirm_password': '123',
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('6 characters', data['message'])

    def test_forgot_password_reset_wrong_doj_fails(self):
        response = self.client.post(
            reverse('forgot_password_reset'),
            json.dumps({
                'staff_id': 'JMCMTS1001',
                'date_of_joining': '1999-01-01',
                'new_password': 'ValidPassword123',
                'confirm_password': 'ValidPassword123',
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])

        # Ensure password was NOT modified
        self.staff_legacy.refresh_from_db()
        self.assertEqual(self.staff_legacy.password, 'oldplainpassword')
