from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Avg
from django.contrib import messages

from .models import Movie, Genre, Director, Actor, Watchlist
from .forms import MovieForm, GenreForm, DirectorForm, ActorForm, MovieSearchForm

class HomeView(TemplateView):
    template_name = 'movies/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_movies'] = Movie.objects.all().order_by('-created_at')[:6]
        context['top_rated_movies'] = Movie.objects.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')[:6]
        return context

class MovieListView(ListView):
    model = Movie
    template_name = 'movies/movie_list.html'
    context_object_name = 'movies'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        form = MovieSearchForm(self.request.GET)

        if form.is_valid():
            query = form.cleaned_data.get('query')
            genre = form.cleaned_data.get('genre')
            year_from = form.cleaned_data.get('year_from')
            year_to = form.cleaned_data.get('year_to')

            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) | 
                    Q(plot__icontains=query) |
                    Q(director__name__icontains=query) |
                    Q(actors__name__icontains=query)
                ).distinct()

            if genre:
                queryset = queryset.filter(genres=genre)

            if year_from:
                queryset = queryset.filter(release_year__gte=year_from)

            if year_to:
                queryset = queryset.filter(release_year__lte=year_to)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = MovieSearchForm(self.request.GET)
        return context

class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies/movie_detail.html'
    context_object_name = 'movie'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = self.get_object()

        # Check if movie is in user's watchlist
        if self.request.user.is_authenticated:
            context['in_watchlist'] = Watchlist.objects.filter(
                user=self.request.user, 
                movie=movie
            ).exists()

        # Get reviews for this movie
        context['reviews'] = movie.reviews.all()[:5]

        # Get similar movies (same genres)
        movie_genres = movie.genres.all()
        similar_movies = Movie.objects.filter(genres__in=movie_genres).exclude(id=movie.id).distinct()
        context['similar_movies'] = similar_movies[:6]

        return context

class MovieCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Movie
    form_class = MovieForm
    template_name = 'movies/movie_form.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        messages.success(self.request, f"Movie '{self.object.title}' was created successfully.")
        return reverse_lazy('movies:movie_detail', kwargs={'pk': self.object.pk})

class MovieUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Movie
    form_class = MovieForm
    template_name = 'movies/movie_form.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        messages.success(self.request, f"Movie '{self.object.title}' was updated successfully.")
        return reverse_lazy('movies:movie_detail', kwargs={'pk': self.object.pk})

class MovieDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Movie
    template_name = 'movies/movie_confirm_delete.html'
    success_url = reverse_lazy('movies:movie_list')

    def test_func(self):
        return self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        movie = self.get_object()
        messages.success(request, f"Movie '{movie.title}' was deleted successfully.")
        return super().delete(request, *args, **kwargs)

class GenreListView(ListView):
    model = Genre
    template_name = 'movies/genre_list.html'
    context_object_name = 'genres'

class GenreDetailView(DetailView):
    model = Genre
    template_name = 'movies/genre_detail.html'
    context_object_name = 'genre'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        genre = self.get_object()
        context['movies'] = genre.movies.all()
        return context

def add_to_watchlist(request, movie_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to add movies to your watchlist.")
        return redirect('accounts:login')

    movie = get_object_or_404(Movie, id=movie_id)

    # Check if already in watchlist
    if Watchlist.objects.filter(user=request.user, movie=movie).exists():
        messages.info(request, f"'{movie.title}' is already in your watchlist.")
    else:
        Watchlist.objects.create(user=request.user, movie=movie)
        messages.success(request, f"'{movie.title}' added to your watchlist.")

    return redirect('movies:movie_detail', pk=movie_id)

def remove_from_watchlist(request, movie_id):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    movie = get_object_or_404(Movie, id=movie_id)
    watchlist_item = get_object_or_404(Watchlist, user=request.user, movie=movie)
    watchlist_item.delete()

    messages.success(request, f"'{movie.title}' removed from your watchlist.")

    # Check if we should redirect back to watchlist or movie detail
    next_url = request.GET.get('next')
    if next_url == 'watchlist':
        return redirect('accounts:profile')
    return redirect('movies:movie_detail', pk=movie_id)
