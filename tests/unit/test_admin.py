"""
Unit tests for admin functionality.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from movies.models import Genre, Director, Actor


class AdminViewsTest(TestCase):
    """Test admin views functionality."""

    def setUp(self):
        self.client = TestCase.client_class()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.staff_user = User.objects.create_user(
            username="staffuser", password="testpass123", is_staff=True
        )
        self.superuser = User.objects.create_user(
            username="superuser", password="testpass123", is_superuser=True
        )
        self.genre = Genre.objects.create(name="Action")
        self.director = Director.objects.create(name="John Doe")
        self.actor = Actor.objects.create(name="Jane Smith")

    def test_admin_dashboard_requires_staff(self):
        """Test admin dashboard requires staff permissions."""
        # Test unauthenticated user
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test regular user
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertEqual(response.status_code, 302)  # Redirect to home

        # Test staff user
        self.client.login(username="staffuser", password="testpass123")
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertEqual(response.status_code, 200)

        # Test superuser
        self.client.login(username="superuser", password="testpass123")
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_admin_genre_views_require_staff(self):
        """Test admin genre views require staff permissions."""
        # Test unauthenticated user
        response = self.client.get(reverse("accounts:admin_genres"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test regular user
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("accounts:admin_genres"))
        self.assertEqual(response.status_code, 302)  # Redirect to home

        # Test staff user
        self.client.login(username="staffuser", password="testpass123")
        response = self.client.get(reverse("accounts:admin_genres"))
        self.assertEqual(response.status_code, 200)

    def test_admin_genre_create_view(self):
        """Test admin genre create view."""
        self.client.login(username="staffuser", password="testpass123")
        response = self.client.get(reverse("accounts:admin_genre_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/admin_genre_form.html")

    def test_admin_genre_update_view(self):
        """Test admin genre update view."""
        self.client.login(username="staffuser", password="testpass123")
        response = self.client.get(
            reverse("accounts:admin_genre_update", kwargs={"pk": self.genre.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/admin_genre_form.html")

    def test_admin_genre_delete_view(self):
        """Test admin genre delete view."""
        self.client.login(username="staffuser", password="testpass123")
        response = self.client.get(
            reverse("accounts:admin_genre_delete", kwargs={"pk": self.genre.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/admin_genre_confirm_delete.html")

    def test_admin_director_views_require_staff(self):
        """Test admin director views require staff permissions."""
        # Test unauthenticated user
        response = self.client.get(reverse("accounts:admin_directors"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test regular user
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("accounts:admin_directors"))
        self.assertEqual(response.status_code, 302)  # Redirect to home

        # Test staff user
        self.client.login(username="staffuser", password="testpass123")
        response = self.client.get(reverse("accounts:admin_directors"))
        self.assertEqual(response.status_code, 200)

    def test_admin_actor_views_require_staff(self):
        """Test admin actor views require staff permissions."""
        # Test unauthenticated user
        response = self.client.get(reverse("accounts:admin_actors"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test regular user
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("accounts:admin_actors"))
        self.assertEqual(response.status_code, 302)  # Redirect to home

        # Test staff user
        self.client.login(username="staffuser", password="testpass123")
        response = self.client.get(reverse("accounts:admin_actors"))
        self.assertEqual(response.status_code, 200)

    def test_admin_reviews_views_require_staff(self):
        """Test admin reviews views require staff permissions."""
        # Test unauthenticated user
        response = self.client.get(reverse("accounts:admin_reviews"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test regular user
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("accounts:admin_reviews"))
        self.assertEqual(response.status_code, 302)  # Redirect to home

        # Test staff user
        self.client.login(username="staffuser", password="testpass123")
        response = self.client.get(reverse("accounts:admin_reviews"))
        self.assertEqual(response.status_code, 200)

    def test_admin_users_views_require_staff(self):
        """Test admin users views require staff permissions."""
        # Test unauthenticated user
        response = self.client.get(reverse("accounts:admin_users"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test regular user
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("accounts:admin_users"))
        self.assertEqual(response.status_code, 302)  # Redirect to home

        # Test staff user
        self.client.login(username="staffuser", password="testpass123")
        response = self.client.get(reverse("accounts:admin_users"))
        self.assertEqual(response.status_code, 200)


# Additional Django TestCase tests for admin functionality
class AdminCRUDTest(TestCase):
    """Test admin CRUD operations using Django TestCase."""

    def setUp(self):
        self.client = TestCase.client_class()
        self.staff_user = User.objects.create_user(
            username="staffuser", password="testpass123", is_staff=True
        )
        self.genre = Genre.objects.create(name="Action")
        self.director = Director.objects.create(name="John Doe")
        self.actor = Actor.objects.create(name="Jane Smith")

    def test_admin_genre_crud_views(self):
        """Test admin genre CRUD views."""
        self.client.login(username="staffuser", password="testpass123")

        # Test list view
        response = self.client.get(reverse("accounts:admin_genres"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/admin_genres.html")

        # Test create view
        response = self.client.get(reverse("accounts:admin_genre_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/admin_genre_form.html")

        # Test update view
        response = self.client.get(
            reverse("accounts:admin_genre_update", kwargs={"pk": self.genre.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/admin_genre_form.html")

        # Test delete view
        response = self.client.get(
            reverse("accounts:admin_genre_delete", kwargs={"pk": self.genre.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/admin_genre_confirm_delete.html")

    def test_admin_director_crud_views(self):
        """Test admin director CRUD views."""
        self.client.login(username="staffuser", password="testpass123")

        # Test list view
        response = self.client.get(reverse("accounts:admin_directors"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/admin_directors.html")

        # Test create view
        response = self.client.get(reverse("accounts:admin_director_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/admin_director_form.html")

        # Test update view
        response = self.client.get(
            reverse("accounts:admin_director_update", kwargs={"pk": self.director.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/admin_director_form.html")

        # Test delete view
        response = self.client.get(
            reverse("accounts:admin_director_delete", kwargs={"pk": self.director.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/admin_director_confirm_delete.html")

    def test_admin_actor_crud_views(self):
        """Test admin actor CRUD views."""
        self.client.login(username="staffuser", password="testpass123")

        # Test list view
        response = self.client.get(reverse("accounts:admin_actors"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/admin_actors.html")

        # Test create view
        response = self.client.get(reverse("accounts:admin_actor_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/admin_actor_form.html")

        # Test update view
        response = self.client.get(
            reverse("accounts:admin_actor_update", kwargs={"pk": self.actor.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/admin_actor_form.html")

        # Test delete view
        response = self.client.get(
            reverse("accounts:admin_actor_delete", kwargs={"pk": self.actor.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/admin_actor_confirm_delete.html")
