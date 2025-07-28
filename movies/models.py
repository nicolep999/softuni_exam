from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('movies:genre_detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['name']

class Director(models.Model):
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='directors/', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Actor(models.Model):
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='actors/', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Movie(models.Model):
    title = models.CharField(max_length=200)
    release_year = models.IntegerField()
    plot = models.TextField()
    poster = models.ImageField(upload_to='posters/', null=True, blank=True)
    trailer_url = models.URLField(blank=True)
    genres = models.ManyToManyField(Genre, related_name='movies')
    director = models.ForeignKey(Director, on_delete=models.SET_NULL, null=True, blank=True, related_name='movies')
    actors = models.ManyToManyField(Actor, related_name='movies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.release_year})"

    def get_absolute_url(self):
        return reverse('movies:movie_detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['-release_year', 'title']

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='in_watchlists')
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s watchlist: {self.movie.title}"

    class Meta:
        unique_together = ('user', 'movie')
        ordering = ['-added_at']
