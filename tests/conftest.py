"""
Pytest configuration and common fixtures for Moodie tests.
"""

import pytest
from django.test import Client
from django.contrib.auth.models import User
from movies.models import Movie, Genre, Director, Actor
from reviews.models import Review


@pytest.fixture
def client():
    """Django test client fixture."""
    return Client()


@pytest.fixture
def user():
    """Create a regular user for testing."""
    user = User.objects.create_user(
        username="testuser", password="testpass123", email="testuser@example.com"
    )
    return user


@pytest.fixture
def staff_user():
    """Create a staff user for testing."""
    user = User.objects.create_user(
        username="staffuser", password="testpass123", email="staff@example.com", is_staff=True
    )
    return user


@pytest.fixture
def superuser():
    """Create a superuser for testing."""
    user = User.objects.create_user(
        username="superuser", password="testpass123", email="admin@example.com", is_superuser=True
    )
    return user


@pytest.fixture
def genre():
    """Create a test genre."""
    return Genre.objects.create(name="Action", description="Action movies")


@pytest.fixture
def director():
    """Create a test director."""
    return Director.objects.create(name="John Doe", bio="Famous director")


@pytest.fixture
def actor():
    """Create a test actor."""
    return Actor.objects.create(name="Jane Smith", bio="Famous actor")


@pytest.fixture
def movie(genre, director, actor):
    """Create a test movie with genre, director, and actor."""
    movie = Movie.objects.create(
        title="Test Movie", release_year=2020, plot="A test movie plot", director=director
    )
    movie.genres.add(genre)
    movie.actors.add(actor)
    return movie


@pytest.fixture
def review(user, movie):
    """Create a test review."""
    return Review.objects.create(
        movie=movie, user=user, rating=8, title="Great Movie", content="This is a great movie!"
    )


@pytest.fixture
def authenticated_client(client, user):
    """Return an authenticated client."""
    client.login(username="testuser", password="testpass123")
    return client


@pytest.fixture
def staff_client(client, staff_user):
    """Return a staff authenticated client."""
    client.login(username="staffuser", password="testpass123")
    return client


@pytest.fixture
def admin_client(client, superuser):
    """Return a superuser authenticated client."""
    client.login(username="superuser", password="testpass123")
    return client
