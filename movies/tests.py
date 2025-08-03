from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Movie, Genre, Director, Actor, Watchlist
from .forms import MovieForm, MovieSearchForm
import tempfile
import os

class MovieModelTest(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Action", description="Action movies")
        self.director = Director.objects.create(name="John Doe", bio="Famous director")
        self.actor = Actor.objects.create(name="Jane Smith", bio="Famous actor")
        self.movie = Movie.objects.create(
            title="Test Movie",
            release_year=2020,
            plot="A test movie plot",
            director=self.director
        )
        self.movie.genres.add(self.genre)
        self.movie.actors.add(self.actor)

    def test_movie_creation(self):
        self.assertEqual(self.movie.title, "Test Movie")
        self.assertEqual(self.movie.release_year, 2020)
        self.assertEqual(self.movie.director, self.director)

    def test_movie_str_representation(self):
        self.assertEqual(str(self.movie), "Test Movie (2020)")

    def test_movie_average_rating(self):
        # Test with no reviews
        self.assertEqual(self.movie.average_rating(), 0)

    def test_genre_str_representation(self):
        self.assertEqual(str(self.genre), "Action")

    def test_director_str_representation(self):
        self.assertEqual(str(self.director), "John Doe")

    def test_actor_str_representation(self):
        self.assertEqual(str(self.actor), "Jane Smith")

class MovieViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.staff_user = User.objects.create_user(username='staffuser', password='testpass123', is_staff=True)
        self.genre = Genre.objects.create(name="Action")
        self.director = Director.objects.create(name="John Doe")
        self.movie = Movie.objects.create(
            title="Test Movie",
            release_year=2020,
            plot="A test movie plot",
            director=self.director
        )
        self.movie.genres.add(self.genre)

    def test_home_view(self):
        response = self.client.get(reverse('movies:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/home.html')

    def test_movie_list_view(self):
        response = self.client.get(reverse('movies:movie_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/movie_list.html')
        self.assertContains(response, "Test Movie")

    def test_movie_detail_view(self):
        response = self.client.get(reverse('movies:movie_detail', kwargs={'pk': self.movie.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/movie_detail.html')
        self.assertContains(response, "Test Movie")

    def test_movie_create_view_requires_staff(self):
        # Test unauthenticated user
        response = self.client.get(reverse('movies:movie_create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test regular user
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('movies:movie_create'))
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Test staff user
        self.client.login(username='staffuser', password='testpass123')
        response = self.client.get(reverse('movies:movie_create'))
        self.assertEqual(response.status_code, 200)

    def test_genre_list_view(self):
        response = self.client.get(reverse('movies:genre_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/genre_list.html')
        self.assertContains(response, "Action")

    def test_genre_detail_view(self):
        response = self.client.get(reverse('movies:genre_detail', kwargs={'pk': self.genre.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/genre_detail.html')
        self.assertContains(response, "Action")

    def test_add_to_watchlist_requires_login(self):
        # Test unauthenticated user
        response = self.client.get(reverse('movies:add_to_watchlist', kwargs={'movie_id': self.movie.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test authenticated user
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('movies:add_to_watchlist', kwargs={'movie_id': self.movie.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect after adding
        self.assertTrue(Watchlist.objects.filter(user=self.user, movie=self.movie).exists())

class MovieFormsTest(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Action")
        self.director = Director.objects.create(name="John Doe")

    def test_movie_form_valid(self):
        form_data = {
            'title': 'Test Movie',
            'release_year': 2020,
            'plot': 'A test movie plot',
            'genres': [self.genre.pk],
            'director': self.director.pk,
        }
        form = MovieForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_movie_form_invalid_year(self):
        form_data = {
            'title': 'Test Movie',
            'release_year': 1800,  # Too early
            'plot': 'A test movie plot',
        }
        form = MovieForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('release_year', form.errors)

    def test_movie_search_form(self):
        form_data = {
            'query': 'test',
            'genre': self.genre.pk,
            'year_from': 2010,
            'year_to': 2020,
        }
        form = MovieSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

class WatchlistTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.movie = Movie.objects.create(
            title="Test Movie",
            release_year=2020,
            plot="A test movie plot"
        )

    def test_watchlist_creation(self):
        watchlist_item = Watchlist.objects.create(user=self.user, movie=self.movie)
        self.assertEqual(watchlist_item.user, self.user)
        self.assertEqual(watchlist_item.movie, self.movie)

    def test_watchlist_unique_constraint(self):
        Watchlist.objects.create(user=self.user, movie=self.movie)
        # Try to create duplicate
        with self.assertRaises(Exception):
            Watchlist.objects.create(user=self.user, movie=self.movie)
