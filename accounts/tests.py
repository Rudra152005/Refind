from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from accounts.services import generate_verification_url, verify_email_token
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

class AccountsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test.student@campus.edu',
            password='TestPassword123!',
            full_name='Test Student',
            hostel='Hall A'
        )

    def test_user_creation_and_attributes(self):
        self.assertEqual(self.user.email, 'test.student@campus.edu')
        self.assertEqual(self.user.full_name, 'Test Student')
        self.assertFalse(self.user.is_email_verified)
        self.assertTrue(self.user.check_password('TestPassword123!'))

    def test_student_registration_view(self):
        response = self.client.post(reverse('accounts:register'), {
            'full_name': 'New Student',
            'email': 'new.student@campus.edu',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!',
            'hostel': 'Hall B',
            'phone': '1234567890'
        })
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.get(email='new.student@campus.edu')
        self.assertFalse(new_user.is_email_verified)
        self.assertEqual(new_user.full_name, 'New Student')

    def test_email_verification_flow(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        
        # Test verification service directly
        verified_user = verify_email_token(uid, token)
        self.assertIsNotNone(verified_user)
        self.assertTrue(verified_user.is_email_verified)

        # Test verification endpoint
        verify_url = reverse('accounts:verify_email', kwargs={'uidb64': uid, 'token': token})
        response = self.client.get(verify_url)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)

    def test_login_and_logout(self):
        login_res = self.client.post(reverse('accounts:login'), {
            'email': 'test.student@campus.edu',
            'password': 'TestPassword123!'
        })
        self.assertEqual(login_res.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)

        logout_res = self.client.get(reverse('accounts:logout'))
        self.assertEqual(logout_res.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_profile_update(self):
        self.client.login(username='test.student@campus.edu', password='TestPassword123!')
        response = self.client.post(reverse('accounts:profile'), {
            'full_name': 'Updated Name',
            'phone': '9876543210',
            'hostel': 'Hostel 9'
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, 'Updated Name')
        self.assertEqual(self.user.hostel, 'Hostel 9')

    def test_admin_role_registration(self):
        response = self.client.post(reverse('accounts:register'), {
            'full_name': 'Campus Moderator',
            'email': 'moderator@anydomain.org',
            'role': 'admin',
            'password': 'ModPassword123!',
            'confirm_password': 'ModPassword123!',
            'hostel': 'Staff Admin Hall',
            'phone': '1112223333'
        })
        self.assertEqual(response.status_code, 302)
        admin_user = User.objects.get(email='moderator@anydomain.org')
        self.assertEqual(admin_user.role, 'admin')
        self.assertTrue(admin_user.is_staff)

    def test_free_email_domain_registration(self):
        # Users can register with ANY email address
        response = self.client.post(reverse('accounts:register'), {
            'full_name': 'Gmail Student',
            'email': 'student.user@gmail.com',
            'role': 'student',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='student.user@gmail.com').exists())

    def test_password_reset_views(self):
        # Request password reset page
        get_res = self.client.get(reverse('accounts:password_reset'))
        self.assertEqual(get_res.status_code, 200)

        # Submit email for reset
        post_res = self.client.post(reverse('accounts:password_reset'), {
            'email': 'test.student@campus.edu'
        })
        self.assertEqual(post_res.status_code, 302)
        self.assertRedirects(post_res, reverse('accounts:password_reset_done'))
