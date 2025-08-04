from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.views import View
from django.contrib.auth.views import PasswordChangeView

from .forms import CustomUserCreationForm, ProfileUpdateForm, UserUpdateForm, CustomPasswordChangeForm
from .models import Profile
from movies.models import Watchlist

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('movies:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Log the user in after registration
        login(self.request, self.object)
        messages.success(self.request, f"Welcome to Moodie, {self.object.username}! Your account has been created.")
        return response

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('movies:home')
        return super().dispatch(request, *args, **kwargs)

class LogoutView(View):
    def get(self, request):
        # Show confirmation page
        return render(request, 'accounts/logout_confirm.html')
    
    def post(self, request):
        # Perform logout
        logout(request)
        messages.success(request, "You have been successfully logged out.")
        return redirect('movies:home')

class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'accounts/profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['watchlist'] = Watchlist.objects.filter(user=self.request.user)
        context['reviews'] = self.request.user.reviews.all()
        return context

class ProfileUpdateView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['user_form'] = UserUpdateForm(self.request.POST, instance=self.request.user)
            context['profile_form'] = ProfileUpdateForm(
                self.request.POST, 
                self.request.FILES, 
                instance=self.request.user.profile
            )
        else:
            context['user_form'] = UserUpdateForm(instance=self.request.user)
            context['profile_form'] = ProfileUpdateForm(instance=self.request.user.profile)
        return context

    def post(self, request, *args, **kwargs):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('accounts:profile')

        return self.render_to_response(
            self.get_context_data(
                user_form=user_form,
                profile_form=profile_form
            )
        )

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Your password has been changed successfully.")
        return response

class WatchlistView(LoginRequiredMixin, ListView):
    template_name = 'accounts/watchlist.html'
    context_object_name = 'watchlist_items'
    paginate_by = 12

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user).select_related('movie')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_movies'] = self.get_queryset().count()
        return context

class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/admin_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, "You don't have permission to access the admin dashboard.")
            return redirect('movies:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from movies.models import Movie, Genre, Director, Actor
        from reviews.models import Review
        
        context['stats'] = {
            'total_movies': Movie.objects.count(),
            'total_genres': Genre.objects.count(),
            'total_directors': Director.objects.count(),
            'total_actors': Actor.objects.count(),
            'total_reviews': Review.objects.count(),
            'total_users': User.objects.count(),
        }
        return context

class AdminMovieListView(LoginRequiredMixin, ListView):
    template_name = 'accounts/admin_movies.html'
    context_object_name = 'movies'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, "You don't have permission to access this page.")
            return redirect('movies:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        from movies.models import Movie
        return Movie.objects.all().order_by('-release_year', 'title')

class AdminGenreListView(LoginRequiredMixin, ListView):
    template_name = 'accounts/admin_genres.html'
    context_object_name = 'genres'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, "You don't have permission to access this page.")
            return redirect('movies:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        from movies.models import Genre
        return Genre.objects.all().order_by('name')

class AdminDirectorListView(LoginRequiredMixin, ListView):
    template_name = 'accounts/admin_directors.html'
    context_object_name = 'directors'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, "You don't have permission to access this page.")
            return redirect('movies:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        from movies.models import Director
        return Director.objects.all().order_by('name')

class AdminActorListView(LoginRequiredMixin, ListView):
    template_name = 'accounts/admin_actors.html'
    context_object_name = 'actors'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, "You don't have permission to access this page.")
            return redirect('movies:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        from movies.models import Actor
        return Actor.objects.all().order_by('name')

class AdminReviewListView(LoginRequiredMixin, ListView):
    template_name = 'accounts/admin_reviews.html'
    context_object_name = 'reviews'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, "You don't have permission to access this page.")
            return redirect('movies:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        from reviews.models import Review
        return Review.objects.all().select_related('user', 'movie').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from reviews.models import Review
        from django.contrib.auth.models import User
        
        context['stats'] = {
            'total_reviews': Review.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'movies_reviewed': Review.objects.values('movie').distinct().count(),
        }
        return context

class AdminUserListView(LoginRequiredMixin, ListView):
    template_name = 'accounts/admin_users.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, "You don't have permission to access this page.")
            return redirect('movies:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return User.objects.all().select_related('profile').order_by('-date_joined')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.contrib.auth.models import User
        
        context['stats'] = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'staff_users': User.objects.filter(is_staff=True).count(),
            'superusers': User.objects.filter(is_superuser=True).count(),
        }
        return context
