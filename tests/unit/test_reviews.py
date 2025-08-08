"""
Unit tests for reviews app functionality.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from reviews.models import Review, Comment
from reviews.forms import ReviewForm, CommentForm
from movies.models import Movie, Genre, Director


class ReviewModelTest(TestCase):
    """Test Review model functionality."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.genre = Genre.objects.create(name="Action")
        self.director = Director.objects.create(name="John Doe")
        self.movie = Movie.objects.create(
            title="Test Movie", release_year=2020, plot="A test movie plot", director=self.director
        )
        self.movie.genres.add(self.genre)
        self.review = Review.objects.create(
            movie=self.movie,
            user=self.user,
            rating=8,
            title="Great Movie",
            content="This is a great movie!",
        )

    def test_review_creation(self):
        """Test review creation and basic fields."""
        self.assertEqual(self.review.movie, self.movie)
        self.assertEqual(self.review.user, self.user)
        self.assertEqual(self.review.rating, 8)
        self.assertEqual(self.review.title, "Great Movie")

    def test_review_str_representation(self):
        """Test review string representation."""
        expected = f"{self.user.username}'s review of {self.movie.title}: 8/10"
        self.assertEqual(str(self.review), expected)

    def test_review_unique_constraint(self):
        """Test review unique constraint (one review per user per movie)."""
        # Try to create another review by the same user for the same movie
        with self.assertRaises(Exception):
            Review.objects.create(
                movie=self.movie,
                user=self.user,
                rating=7,
                title="Another Review",
                content="Another review content",
            )


class CommentModelTest(TestCase):
    """Test Comment model functionality."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.genre = Genre.objects.create(name="Action")
        self.director = Director.objects.create(name="John Doe")
        self.movie = Movie.objects.create(
            title="Test Movie", release_year=2020, plot="A test movie plot", director=self.director
        )
        self.movie.genres.add(self.genre)
        self.review = Review.objects.create(
            movie=self.movie,
            user=self.user,
            rating=8,
            title="Great Movie",
            content="This is a great movie!",
        )
        self.comment = Comment.objects.create(
            review=self.review, user=self.user, content="Great review!"
        )

    def test_comment_creation(self):
        """Test comment creation and basic fields."""
        self.assertEqual(self.comment.review, self.review)
        self.assertEqual(self.comment.user, self.user)
        self.assertEqual(self.comment.content, "Great review!")

    def test_comment_str_representation(self):
        """Test comment string representation."""
        expected = f"Comment by {self.user.username} on {self.review}"
        self.assertEqual(str(self.comment), expected)


class ReviewViewsTest(TestCase):
    """Test review views functionality."""

    def setUp(self):
        self.client = TestCase.client_class()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.genre = Genre.objects.create(name="Action")
        self.director = Director.objects.create(name="John Doe")
        self.movie = Movie.objects.create(
            title="Test Movie", release_year=2020, plot="A test movie plot", director=self.director
        )
        self.movie.genres.add(self.genre)
        self.review = Review.objects.create(
            movie=self.movie,
            user=self.user,
            rating=8,
            title="Great Movie",
            content="This is a great movie!",
        )

    def test_review_create_view_requires_login(self):
        """Test review create view requires authentication."""
        # Test unauthenticated user
        response = self.client.get(
            reverse("reviews:review_create", kwargs={"movie_id": self.movie.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test authenticated user
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(
            reverse("reviews:review_create", kwargs={"movie_id": self.movie.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_movie_reviews_list_view(self):
        """Test movie reviews list view."""
        response = self.client.get(
            reverse("reviews:movie_reviews", kwargs={"movie_id": self.movie.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reviews/movie_reviews.html")
        self.assertContains(response, "Great Movie")

    def test_user_reviews_list_view(self):
        """Test user reviews list view."""
        response = self.client.get(
            reverse("reviews:user_reviews", kwargs={"user_id": self.user.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reviews/user_reviews.html")
        self.assertContains(response, "Great Movie")

    def test_review_update_view_requires_owner(self):
        """Test review update view requires ownership."""  # Test other user trying to edit
        self.client.login(username="otheruser", password="testpass123")
        response = self.client.get(reverse("reviews:review_edit", kwargs={"pk": self.review.pk}))
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Test owner editing
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("reviews:review_edit", kwargs={"pk": self.review.pk}))
        self.assertEqual(response.status_code, 200)

    def test_review_delete_view_requires_owner(self):
        """Test review delete view requires ownership."""  # Test other user trying to delete
        self.client.login(username="otheruser", password="testpass123")
        response = self.client.get(reverse("reviews:review_delete", kwargs={"pk": self.review.pk}))
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Test owner deleting
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("reviews:review_delete", kwargs={"pk": self.review.pk}))
        self.assertEqual(response.status_code, 200)

    def test_review_delete_view_post(self):
        """Test review delete view POST request (actual deletion)."""
        self.client.login(username="testuser", password="testpass123")

        # Store movie ID for verification
        movie_id = self.review.movie.id

        # Perform the deletion
        response = self.client.post(reverse("reviews:review_delete", kwargs={"pk": self.review.pk}))

        # Should redirect to movie detail page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("movies:movie_detail", kwargs={"pk": movie_id}))

        # Verify the review was actually deleted
        self.assertFalse(Review.objects.filter(pk=self.review.pk).exists())


class ReviewFormsTest(TestCase):
    """Test review forms functionality."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.genre = Genre.objects.create(name="Action")
        self.director = Director.objects.create(name="John Doe")
        self.movie = Movie.objects.create(
            title="Test Movie", release_year=2020, plot="A test movie plot", director=self.director
        )
        self.movie.genres.add(self.genre)

    def test_review_form_valid(self):
        """Test valid review form data."""
        form_data = {"rating": 8, "title": "Great Movie", "content": "This is a great movie!"}
        form = ReviewForm(data=form_data, user=self.user, movie=self.movie)
        self.assertTrue(form.is_valid())

    def test_review_form_invalid_rating(self):
        """Test review form with invalid rating."""
        form_data = {
            "rating": 15,  # Invalid rating
            "title": "Great Movie",
            "content": "This is a great movie!",
        }
        form = ReviewForm(data=form_data, user=self.user, movie=self.movie)
        self.assertFalse(form.is_valid())

    def test_review_form_duplicate_review(self):
        """Test review form with duplicate review."""
        # Create first review
        Review.objects.create(
            movie=self.movie,
            user=self.user,
            rating=8,
            title="First Review",
            content="First review content",
        )

        # Try to create duplicate
        form_data = {"rating": 7, "title": "Second Review", "content": "Second review content"}
        form = ReviewForm(data=form_data, user=self.user, movie=self.movie)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_comment_form_valid(self):
        """Test valid comment form data."""
        review = Review.objects.create(
            movie=self.movie,
            user=self.user,
            rating=8,
            title="Great Movie",
            content="This is a great movie!",
        )

        form_data = {"content": "Great review!"}
        form = CommentForm(data=form_data, user=self.user, review=review)
        self.assertTrue(form.is_valid())
