from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from movies.models import Movie


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 11)]

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(
        choices=RATING_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s review of {self.movie.title}: {self.rating}/10"

    def get_absolute_url(self):
        return reverse("reviews:movie_reviews", kwargs={"movie_id": self.movie.id})

    class Meta:
        unique_together = ("movie", "user")
        ordering = ["-created_at"]


class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.review}"

    class Meta:
        ordering = ["created_at"]
