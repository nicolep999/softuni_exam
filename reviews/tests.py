from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Review, Comment
from .forms import ReviewForm, CommentForm
from movies.models import Movie, Genre, Director

class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.genre = Genre.objects.create(name="Action")
        self.director = Director.objects.create(name="John Doe")
        self.movie = Movie.objects.create(
            title="Test Movie",
            release_year=2020,
            plot="A test movie plot",
            director=self.director
        )
        self.movie.genres.add(self.genre)
        self.review = Review.objects.create(
            movie=self.movie,
            user=self.user,
            rating=8,
            title="Great Movie",
            content="This is a great movie!"
        )

    def test_review_creation(self):
        self.assertEqual(self.review.movie, self.movie)
        self.assertEqual(self.review.user, self.user)
        self.assertEqual(self.review.rating, 8)
        self.assertEqual(self.review.title, "Great Movie")

    def test_review_str_representation(self):
        expected = f"{self.user.username}'s review of {self.movie.title}: 8/10"
        self.assertEqual(str(self.review), expected)

    def test_review_unique_constraint(self):
        # Try to create another review by the same user for the same movie
        with self.assertRaises(Exception):
            Review.objects.create(
                movie=self.movie,
                user=self.user,
                rating=7,
                title="Another Review",
                content="Another review content"
            )

class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.genre = Genre.objects.create(name="Action")
        self.director = Director.objects.create(name="John Doe")
        self.movie = Movie.objects.create(
            title="Test Movie",
            release_year=2020,
            plot="A test movie plot",
            director=self.director
        )
        self.movie.genres.add(self.genre)
        self.review = Review.objects.create(
            movie=self.movie,
            user=self.user,
            rating=8,
            title="Great Movie",
            content="This is a great movie!"
        )
        self.comment = Comment.objects.create(
            review=self.review,
            user=self.user,
            content="Great review!"
        )

    def test_comment_creation(self):
        self.assertEqual(self.comment.review, self.review)
        self.assertEqual(self.comment.user, self.user)
        self.assertEqual(self.comment.content, "Great review!")

    def test_comment_str_representation(self):
        expected = f"Comment by {self.user.username} on {self.review}"
        self.assertEqual(str(self.comment), expected)

class ReviewViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.genre = Genre.objects.create(name="Action")
        self.director = Director.objects.create(name="John Doe")
        self.movie = Movie.objects.create(
            title="Test Movie",
            release_year=2020,
            plot="A test movie plot",
            director=self.director
        )
        self.movie.genres.add(self.genre)
        self.review = Review.objects.create(
            movie=self.movie,
            user=self.user,
            rating=8,
            title="Great Movie",
            content="This is a great movie!"
        )

    def test_review_create_view_requires_login(self):
        # Test unauthenticated user
        response = self.client.get(reverse('reviews:review_create', kwargs={'movie_id': self.movie.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test authenticated user
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('reviews:review_create', kwargs={'movie_id': self.movie.pk}))
        self.assertEqual(response.status_code, 200)

    def test_movie_reviews_list_view(self):
        response = self.client.get(reverse('reviews:movie_reviews', kwargs={'movie_id': self.movie.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reviews/movie_reviews.html')
        self.assertContains(response, "Great Movie")

    def test_user_reviews_list_view(self):
        response = self.client.get(reverse('reviews:user_reviews', kwargs={'user_id': self.user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reviews/user_reviews.html')
        self.assertContains(response, "Great Movie")

    def test_review_update_view_requires_owner(self):
        other_user = User.objects.create_user(username='otheruser', password='testpass123')
        
        # Test other user trying to edit
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(reverse('reviews:review_edit', kwargs={'pk': self.review.pk}))
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Test owner editing
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('reviews:review_edit', kwargs={'pk': self.review.pk}))
        self.assertEqual(response.status_code, 200)

    def test_review_delete_view_requires_owner(self):
        other_user = User.objects.create_user(username='otheruser', password='testpass123')
        
        # Test other user trying to delete
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(reverse('reviews:review_delete', kwargs={'pk': self.review.pk}))
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Test owner deleting
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('reviews:review_delete', kwargs={'pk': self.review.pk}))
        self.assertEqual(response.status_code, 200)

class ReviewFormsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.genre = Genre.objects.create(name="Action")
        self.director = Director.objects.create(name="John Doe")
        self.movie = Movie.objects.create(
            title="Test Movie",
            release_year=2020,
            plot="A test movie plot",
            director=self.director
        )
        self.movie.genres.add(self.genre)

    def test_review_form_valid(self):
        form_data = {
            'rating': 8,
            'title': 'Great Movie',
            'content': 'This is a great movie!'
        }
        form = ReviewForm(data=form_data, user=self.user, movie=self.movie)
        self.assertTrue(form.is_valid())

    def test_review_form_invalid_rating(self):
        form_data = {
            'rating': 15,  # Invalid rating
            'title': 'Great Movie',
            'content': 'This is a great movie!'
        }
        form = ReviewForm(data=form_data, user=self.user, movie=self.movie)
        self.assertFalse(form.is_valid())

    def test_review_form_duplicate_review(self):
        # Create first review
        Review.objects.create(
            movie=self.movie,
            user=self.user,
            rating=8,
            title="First Review",
            content="First review content"
        )
        
        # Try to create duplicate
        form_data = {
            'rating': 7,
            'title': 'Second Review',
            'content': 'Second review content'
        }
        form = ReviewForm(data=form_data, user=self.user, movie=self.movie)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    def test_comment_form_valid(self):
        review = Review.objects.create(
            movie=self.movie,
            user=self.user,
            rating=8,
            title="Great Movie",
            content="This is a great movie!"
        )
        
        form_data = {
            'content': 'Great review!'
        }
        form = CommentForm(data=form_data, user=self.user, review=review)
        self.assertTrue(form.is_valid())
