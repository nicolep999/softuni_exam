from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    poster = models.URLField(max_length=500, blank=True, help_text="Genre poster image URL")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("movies:genre_detail", kwargs={"pk": self.pk})

    class Meta:
        ordering = ["name"]


class Director(models.Model):
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to="directors/", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Actor(models.Model):
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to="actors/", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Movie(models.Model):
    title = models.CharField(max_length=200)
    release_year = models.IntegerField()
    release_date = models.DateField(null=True, blank=True)  # Full release date for latest releases
    plot = models.TextField()
    poster = models.ImageField(upload_to="posters/", null=True, blank=True)
    backdrop_url = models.URLField(
        blank=True, help_text="High-quality backdrop image URL from TMDB"
    )
    trailer_url = models.URLField(blank=True)
    imdb_rating = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True
    )  # IMDb rating (e.g., 8.5)
    genres = models.ManyToManyField(Genre, related_name="movies")
    director = models.ForeignKey(
        Director, on_delete=models.SET_NULL, null=True, blank=True, related_name="movies"
    )
    actors = models.ManyToManyField(Actor, related_name="movies", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.release_year})"

    def get_absolute_url(self):
        return reverse("movies:movie_detail", kwargs={"pk": self.pk})

    class Meta:
        ordering = ["-release_year", "title"]

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

    @classmethod
    def get_latest_releases(cls, limit=10):
        """Get the most recently released movies"""
        from datetime import date, timedelta

        # Get movies released in the last 2 years
        recent_date = date.today() - timedelta(days=730)
        return (
            cls.objects.filter(release_date__gte=recent_date)
            .exclude(release_date__isnull=True)
            .order_by("-release_date")[:limit]
        )

    @classmethod
    def get_highest_rated(cls, limit=10):
        """Get the highest rated movies"""
        return cls.objects.exclude(imdb_rating__isnull=True).order_by("-imdb_rating")[:limit]

    @classmethod
    def get_classic_movies(cls, limit=10):
        """Get classic movies (highly rated older movies)"""
        from datetime import date

        # Movies older than 20 years with high ratings
        cutoff_date = date.today().replace(year=date.today().year - 20)
        return (
            cls.objects.filter(release_date__lt=cutoff_date, imdb_rating__gte=8.0)
            .exclude(release_date__isnull=True, imdb_rating__isnull=True)
            .order_by("-imdb_rating")[:limit]
        )


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="in_watchlists")
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s watchlist: {self.movie.title}"

    class Meta:
        unique_together = ("user", "movie")
        ordering = ["-added_at"]
