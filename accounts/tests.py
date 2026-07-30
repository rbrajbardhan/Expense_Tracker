from django.test import TestCase
from django.urls import reverse
from accounts.models import CustomUser, UserProfile

class AccountsTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='test@example.com',
            currency='USD',
            monthly_savings_target=100.00
        )

    def test_user_creation_profile_signal(self):
        # Check that profile is created automatically by post_save signal
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())
        self.assertEqual(self.user.profile.user.username, 'testuser')

    def test_signup_view(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

        # Test login post action
        login_response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword123'
        })
        # Successful login redirects to dashboard
        self.assertEqual(login_response.status_code, 302)

    def test_profile_view_requires_login(self):
        # Should redirect to login page
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)

    def test_profile_view_logged_in(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
