from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile
from .forms import CustomUserCreationForm, ProfileUpdateForm, UserUpdateForm
from movies.models import Genre

# Create your tests here.

class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.genre = Genre.objects.create(name="Action")

    def test_profile_creation(self):
        # Profile should be automatically created when user is created
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, Profile)

    def test_profile_str_representation(self):
        expected = f"{self.user.username}'s profile"
        self.assertEqual(str(self.user.profile), expected)

    def test_profile_update(self):
        self.user.profile.bio = "Test bio"
        self.user.profile.location = "Test City"
        self.user.profile.save()
        
        self.assertEqual(self.user.profile.bio, "Test bio")
        self.assertEqual(self.user.profile.location, "Test City")

    def test_profile_favorite_genres(self):
        self.user.profile.favorite_genres.add(self.genre)
        self.assertIn(self.genre, self.user.profile.favorite_genres.all())

class AccountViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_register_view(self):
        # Test GET request
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

        # Test POST request with valid data
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        response = self.client.post(reverse('accounts:register'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_view_authenticated_user(self):
        # Test that authenticated users are redirected
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 302)  # Redirect to home

    def test_login_view(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_profile_view_requires_login(self):
        # Test unauthenticated user
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test authenticated user
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_profile_edit_view_requires_login(self):
        # Test unauthenticated user
        response = self.client.get(reverse('accounts:profile_edit'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test authenticated user
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:profile_edit'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile_edit.html')

    def test_profile_edit_post(self):
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'bio': 'Updated bio',
            'location': 'Updated City',
        }
        
        response = self.client.post(reverse('accounts:profile_edit'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        
        # Check that profile was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.profile.bio, 'Updated bio')
        self.assertEqual(self.user.profile.location, 'Updated City')

class AccountFormsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123', email='testuser@example.com')

    def test_custom_user_creation_form_valid(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_custom_user_creation_form_duplicate_email(self):
        form_data = {
            'username': 'newuser',
            'email': 'testuser@example.com',  # Already exists
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_custom_user_creation_form_password_mismatch(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'differentpass',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_profile_update_form_valid(self):
        form_data = {
            'bio': 'Test bio',
            'location': 'Test City',
        }
        form = ProfileUpdateForm(data=form_data, instance=self.user.profile)
        self.assertTrue(form.is_valid())

    def test_user_update_form_valid(self):
        form_data = {
            'username': 'testuser',
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'Name',
        }
        form = UserUpdateForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())

class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_login_logout_flow(self):
        # Test login
        login_data = {
            'username': 'testuser',
            'password': 'testpass123',
        }
        response = self.client.post(reverse('accounts:login'), login_data)
        self.assertEqual(response.status_code, 302)  # Redirect after login
        
        # Check that user is logged in
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        
        # Test logout
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout
        
        # Check that user is logged out
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_invalid_login(self):
        login_data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }
        response = self.client.post(reverse('accounts:login'), login_data)
        self.assertEqual(response.status_code, 200)  # Stay on login page
        
        # Check that user is not logged in
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
