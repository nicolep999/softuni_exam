from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q, F
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction, IntegrityError
from django.http import Http404
from django.utils.html import strip_tags
import re

from .models import Movie, Genre, Director, Actor, Watchlist
from .forms import MovieForm, MovieSearchForm


def sanitize_input(value):
    """Sanitize user input to prevent XSS and injection attacks"""
    if not value:
        return value
    # Remove HTML tags
    value = strip_tags(str(value))
    # Remove potentially dangerous characters
    value = re.sub(r'[<>"\']', '', value)
    return value.strip()


def validate_movie_id(movie_id):
    """Validate movie_id parameter"""
    try:
        movie_id = int(movie_id)
        if movie_id <= 0:
            raise ValueError("Movie ID must be a positive integer")
        return movie_id
    except (ValueError, TypeError):
        raise ValidationError("Invalid movie ID provided")


def validate_rating(rating_str):
    """Validate rating parameter"""
    try:
        rating = float(rating_str)
        if rating < 0 or rating > 10:
            raise ValueError("Rating must be between 0 and 10")
        return rating
    except (ValueError, TypeError):
        raise ValidationError("Invalid rating provided")


class HomeView(TemplateView):
    template_name = "movies/home.html"

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            
            # Get latest movies - use release_date for accurate sorting
            latest_movies = Movie.objects.order_by("-release_date")[:6]
            
            # Get top rated movies - use IMDB rating instead of user reviews
            top_rated_movies = Movie.objects.exclude(
                imdb_rating__isnull=True
            ).order_by("-imdb_rating")[:6]
            
            # Get movie statistics - optimized queries
            from reviews.models import Review
            total_movies = Movie.objects.count()
            total_genres = Genre.objects.count()
            total_reviews = Review.objects.count()
            
            context.update({
                "latest_movies": latest_movies,
                "top_rated_movies": top_rated_movies,
                "total_movies": total_movies,
                "total_genres": total_genres,
                "total_reviews": total_reviews,
            })
            return context
        except Exception as e:
            messages.error(self.request, f"Error loading home page data: {e}")
            # Return empty context to prevent crashes
            context = super().get_context_data(**kwargs)
            context.update({
                "latest_movies": [],
                "top_rated_movies": [],
                "total_movies": 0,
                "total_genres": 0,
                "total_reviews": 0,
            })
            return context


class MovieListView(ListView):
    model = Movie
    template_name = "movies/movie_list.html"
    context_object_name = "movies"
    paginate_by = 15

    def get_queryset(self):
        try:
            queryset = Movie.objects.all()
            
            # Get search parameters and sanitize them
            title = sanitize_input(self.request.GET.get("title", ""))
            genre = sanitize_input(self.request.GET.get("genre", ""))
            director = sanitize_input(self.request.GET.get("director", ""))
            rating_min = self.request.GET.get("rating_min", "")
            year_min = self.request.GET.get("year_min", "")
            year_max = self.request.GET.get("year_max", "")
            
            # Apply filters
            if title:
                queryset = queryset.filter(title__icontains=title)
            
            if genre:
                queryset = queryset.filter(genres__name__icontains=genre)
            
            if director:
                queryset = queryset.filter(director__name__icontains=director)
            
            if rating_min:
                try:
                    rating = validate_rating(rating_min)
                    queryset = queryset.filter(reviews__rating__gte=rating).distinct()
                except ValidationError:
                    # If rating is invalid, ignore the filter
                    pass
            
            if year_min:
                try:
                    year = int(year_min)
                    if 1888 <= year <= 2030:  # Reasonable year range
                        queryset = queryset.filter(release_year__gte=year)
                except (ValueError, TypeError):
                    # If year is invalid, ignore the filter
                    pass
            
            if year_max:
                try:
                    year = int(year_max)
                    if 1888 <= year <= 2030:  # Reasonable year range
                        queryset = queryset.filter(release_year__lte=year)
                except (ValueError, TypeError):
                    # If year is invalid, ignore the filter
                    pass
            
            return queryset.order_by("-release_year", "title")
        except Exception as e:
            messages.error(self.request, f"Error filtering movies: {e}")
            return Movie.objects.none()

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            
            # Create search form with sanitized data
            search_data = {
                "title": sanitize_input(self.request.GET.get("title", "")),
                "genre": sanitize_input(self.request.GET.get("genre", "")),
                "director": sanitize_input(self.request.GET.get("director", "")),
                "rating_min": self.request.GET.get("rating_min", ""),
                "year_min": self.request.GET.get("year_min", ""),
                "year_max": self.request.GET.get("year_max", ""),
            }
            
            context["search_form"] = MovieSearchForm(data=search_data)
            return context
        except Exception as e:
            messages.error(self.request, f"Error loading search form: {e}")
            context = super().get_context_data(**kwargs)
            context["search_form"] = MovieSearchForm()
            return context


class MovieDetailView(DetailView):
    model = Movie
    template_name = "movies/movie_detail.html"
    context_object_name = "movie"

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            movie = self.get_object()
            
            # Get related movies (same genre or director)
            related_movies = Movie.objects.filter(
                Q(genres__in=movie.genres.all()) | Q(director=movie.director)
            ).exclude(id=movie.id).distinct()[:6]
            
            # Check if movie is in user's watchlist
            in_watchlist = False
            if self.request.user.is_authenticated:
                in_watchlist = Watchlist.objects.filter(
                    user=self.request.user, movie=movie
                ).exists()
            
            # Get user's review if exists
            user_review = None
            if self.request.user.is_authenticated:
                user_review = movie.reviews.filter(user=self.request.user).first()
            
            context.update({
                "related_movies": related_movies,
                "in_watchlist": in_watchlist,
                "user_review": user_review,
            })
            return context
        except Exception as e:
            messages.error(self.request, f"Error loading movie details: {e}")
            raise Http404("Movie not found or error occurred")


class MovieCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Movie
    form_class = MovieForm
    template_name = "movies/movie_form.html"

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return reverse_lazy("movies:movie_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        try:
            # Sanitize form data
            form.instance.title = sanitize_input(form.cleaned_data.get('title'))
            form.instance.plot = sanitize_input(form.cleaned_data.get('plot'))
            
            with transaction.atomic():
                movie = form.save(commit=False)
                movie.save()
                form.save_m2m()  # Save many-to-many relationships
            messages.success(self.request, f"Movie '{movie.title}' was created successfully.")
            return super().form_valid(form)
        except (ValidationError, IntegrityError) as e:
            messages.error(self.request, f"Error creating movie: {e}")
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"An unexpected error occurred: {e}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class MovieUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Movie
    form_class = MovieForm
    template_name = "movies/movie_form.html"

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return reverse_lazy("movies:movie_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        try:
            # Sanitize form data
            form.instance.title = sanitize_input(form.cleaned_data.get('title'))
            form.instance.plot = sanitize_input(form.cleaned_data.get('plot'))
            
            with transaction.atomic():
                movie = form.save(commit=False)
                movie.save()
                form.save_m2m()  # Save many-to-many relationships
            messages.success(self.request, f"Movie '{movie.title}' was updated successfully.")
            return super().form_valid(form)
        except (ValidationError, IntegrityError) as e:
            messages.error(self.request, f"Error updating movie: {e}")
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"An unexpected error occurred: {e}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class MovieDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Movie
    template_name = "movies/movie_confirm_delete.html"
    success_url = reverse_lazy("movies:movie_list")

    def test_func(self):
        return self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        try:
            movie = self.get_object()
            title = movie.title
            with transaction.atomic():
                movie.delete()
            messages.success(request, f"Movie '{title}' was deleted successfully.")
            return super().delete(request, *args, **kwargs)
        except (ValidationError, IntegrityError) as e:
            messages.error(request, f"Error deleting movie: {e}")
            return redirect("movies:movie_detail", pk=self.get_object().pk)
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
            return redirect("movies:movie_detail", pk=self.get_object().pk)


class GenreListView(ListView):
    model = Genre
    template_name = "movies/genre_list.html"
    context_object_name = "genres"


class GenreDetailView(DetailView):
    model = Genre
    template_name = "movies/genre_detail.html"
    context_object_name = "genre"

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            genre = self.get_object()
            context["movies"] = genre.movies.all()
            return context
        except Exception as e:
            messages.error(self.request, f"Error loading genre details: {e}")
            raise Http404("Genre not found or error occurred")


def add_to_watchlist(request, movie_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to add movies to your watchlist.")
        return redirect("accounts:login")

    try:
        # Validate movie_id parameter
        movie_id = validate_movie_id(movie_id)
        movie = get_object_or_404(Movie, id=movie_id)

        # Check if already in watchlist
        if Watchlist.objects.filter(user=request.user, movie=movie).exists():
            messages.info(request, f"'{movie.title}' is already in your watchlist.")
        else:
            with transaction.atomic():
                Watchlist.objects.create(user=request.user, movie=movie)
            messages.success(request, f"'{movie.title}' added to your watchlist.")

        return redirect("movies:movie_detail", pk=movie_id)
    except ValidationError as e:
        messages.error(request, f"Invalid movie ID: {e}")
        return redirect("movies:movie_list")
    except Exception as e:
        messages.error(request, f"An error occurred while adding the movie to your watchlist: {e}")
        return redirect("movies:movie_list")


def remove_from_watchlist(request, movie_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to remove movies from your watchlist.")
        return redirect("accounts:login")

    try:
        # Validate movie_id parameter
        movie_id = validate_movie_id(movie_id)
        movie = get_object_or_404(Movie, id=movie_id)
        
        # Ensure user can only remove from their own watchlist
        watchlist_item = get_object_or_404(Watchlist, user=request.user, movie=movie)
        
        with transaction.atomic():
            watchlist_item.delete()

        messages.success(request, f"'{movie.title}' removed from your watchlist.")

        # Check if we should redirect back to watchlist or movie detail
        next_url = sanitize_input(request.GET.get("next"))
        if next_url == "watchlist":
            return redirect("accounts:profile")
        return redirect("movies:movie_detail", pk=movie_id)
    except ValidationError as e:
        messages.error(request, f"Invalid movie ID: {e}")
        return redirect("movies:movie_list")
    except Exception as e:
        messages.error(request, f"An error occurred while removing the movie from your watchlist: {e}")
        return redirect("movies:movie_list")
