from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q, F
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError, transaction
from django.http import Http404
from .models import Movie, Genre, Director, Actor, Watchlist
from .forms import MovieForm, MovieSearchForm


class HomeView(TemplateView):
    template_name = "movies/home.html"

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            # Get latest movies with IMDB ratings, sorted by release date
            context["latest_movies"] = (
                Movie.objects.exclude(release_date__isnull=True)
                .exclude(imdb_rating__isnull=True)
                .order_by("-release_date")[:6]
            )

            # Get top rated movies sorted by IMDB rating (not average rating)
            context["top_rated_movies"] = Movie.objects.exclude(imdb_rating__isnull=True).order_by(
                "-imdb_rating"
            )[:6]
            return context
        except Exception as e:
            messages.error(self.request, f"Error loading home page: {e}")
            # Return empty context to prevent crashes
            context = super().get_context_data(**kwargs)
            context["latest_movies"] = []
            context["top_rated_movies"] = []
            return context


class MovieListView(ListView):
    model = Movie
    template_name = "movies/movie_list.html"
    context_object_name = "movies"
    paginate_by = 15

    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            form = MovieSearchForm(self.request.GET)

            if form.is_valid():
                query = form.cleaned_data.get("query")
                genre = form.cleaned_data.get("genre")
                year_from = form.cleaned_data.get("year_from")
                year_to = form.cleaned_data.get("year_to")

                if query:
                    queryset = queryset.filter(
                        Q(title__icontains=query)
                        | Q(plot__icontains=query)
                        | Q(director__name__icontains=query)
                        | Q(actors__name__icontains=query)
                    ).distinct()

                if genre:
                    queryset = queryset.filter(genres=genre)

                if year_from:
                    queryset = queryset.filter(release_year__gte=year_from)

                if year_to:
                    queryset = queryset.filter(release_year__lte=year_to)

            # Additional filters from GET parameters
            rating_min = self.request.GET.get("rating_min")
            has_rating = self.request.GET.get("has_rating")
            has_poster = self.request.GET.get("has_poster")
            sort_by = self.request.GET.get("sort_by", "-release_year")  # Default sort

            # Rating minimum filter
            if rating_min:
                try:
                    rating_value = float(rating_min)
                    queryset = queryset.filter(imdb_rating__gte=rating_value)
                except (ValueError, TypeError):
                    messages.warning(self.request, "Invalid rating value provided.")

            # Has rating filter
            if has_rating == "yes":
                queryset = queryset.exclude(imdb_rating__isnull=True)
            elif has_rating == "no":
                queryset = queryset.filter(imdb_rating__isnull=True)

            # Has poster filter
            if has_poster == "yes":
                queryset = queryset.exclude(poster="")
            elif has_poster == "no":
                queryset = queryset.filter(poster="")

            # Sorting
            if sort_by:
                if sort_by == "-imdb_rating":
                    # For highest rated, put NULL ratings last
                    queryset = queryset.order_by(F("imdb_rating").desc(nulls_last=True))
                elif sort_by == "imdb_rating":
                    # For lowest rated, put NULL ratings last
                    queryset = queryset.order_by(F("imdb_rating").asc(nulls_last=True))
                else:
                    queryset = queryset.order_by(sort_by)

            return queryset
        except Exception as e:
            messages.error(self.request, f"Error loading movies: {e}")
            return Movie.objects.none()

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context["search_form"] = MovieSearchForm(self.request.GET)
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

            # Check if movie is in user's watchlist
            if self.request.user.is_authenticated:
                context["in_watchlist"] = Watchlist.objects.filter(
                    user=self.request.user, movie=movie
                ).exists()

            # Get reviews for this movie
            context["reviews"] = movie.reviews.all()[:5]

            # Get similar movies (same genres)
            movie_genres = movie.genres.all()
            similar_movies = (
                Movie.objects.filter(genres__in=movie_genres).exclude(id=movie.id).distinct()
            )
            context["similar_movies"] = similar_movies[:6]

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
        messages.success(self.request, f"Movie '{self.object.title}' was created successfully.")
        return reverse_lazy("movies:movie_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        try:
            with transaction.atomic():
                movie = form.save(commit=False)
                movie.save()
                # Handle genres, directors, actors
                form.save_m2m()
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
        messages.success(self.request, f"Movie '{self.object.title}' was updated successfully.")
        return reverse_lazy("movies:movie_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        try:
            with transaction.atomic():
                movie = form.save(commit=False)
                movie.save()
                # Handle genres, directors, actors
                form.save_m2m()
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
        movie = get_object_or_404(Movie, id=movie_id)

        # Check if already in watchlist
        if Watchlist.objects.filter(user=request.user, movie=movie).exists():
            messages.info(request, f"'{movie.title}' is already in your watchlist.")
        else:
            Watchlist.objects.create(user=request.user, movie=movie)
            messages.success(request, f"'{movie.title}' added to your watchlist.")

        return redirect("movies:movie_detail", pk=movie_id)
    except Exception:
        messages.error(request, "An error occurred while adding the movie to your watchlist.")
        return redirect("movies:movie_list")


def remove_from_watchlist(request, movie_id):
    if not request.user.is_authenticated:
        return redirect("accounts:login")

    try:
        movie = get_object_or_404(Movie, id=movie_id)
        watchlist_item = get_object_or_404(Watchlist, user=request.user, movie=movie)
        watchlist_item.delete()

        messages.success(request, f"'{movie.title}' removed from your watchlist.")

        # Check if we should redirect back to watchlist or movie detail
        next_url = request.GET.get("next")
        if next_url == "watchlist":
            return redirect("accounts:profile")
        return redirect("movies:movie_detail", pk=movie_id)
    except Exception:
        messages.error(request, "An error occurred while removing the movie from your watchlist.")
        return redirect("movies:movie_list")
