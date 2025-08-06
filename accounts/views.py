from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
    TemplateView,
    View,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.contrib.auth import get_user_model, logout, login
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction, IntegrityError
from django.http import Http404
from django.utils.html import strip_tags
import re

from .forms import (
    CustomUserCreationForm,
    UserUpdateForm,
    ProfileUpdateForm,
    CustomPasswordChangeForm,
)
from .models import Profile
from movies.models import Watchlist, Genre, Director, Actor

User = get_user_model()


def sanitize_input(value):
    """Sanitize user input to prevent XSS and injection attacks"""
    if not value:
        return value
    # Remove HTML tags
    value = strip_tags(str(value))
    # Remove potentially dangerous characters
    value = re.sub(r'[<>"\']', "", value)
    return value.strip()


def validate_pk(pk):
    """Validate primary key parameter"""
    try:
        pk = int(pk)
        if pk <= 0:
            raise ValueError("Primary key must be a positive integer")
        return pk
    except (ValueError, TypeError):
        raise ValidationError("Invalid primary key provided")


class AdminPermissionMixin:
    """Mixin to ensure only staff/superusers can access admin views"""

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, "You don't have permission to access this page.")
            return redirect("movies:home")
        return super().dispatch(request, *args, **kwargs)


class AdminListView(AdminPermissionMixin, LoginRequiredMixin, ListView):
    """Base class for admin list views"""

    paginate_by = 20


class AdminCreateView(AdminPermissionMixin, LoginRequiredMixin, CreateView):
    """Base class for admin create views"""

    def form_valid(self, form):
        try:
            # Sanitize form data
            for field_name, field_value in form.cleaned_data.items():
                if isinstance(field_value, str):
                    form.instance.__dict__[field_name] = sanitize_input(field_value)

            with transaction.atomic():
                obj = form.save()
            messages.success(self.request, f"{self.model.__name__} was created successfully.")
            return super().form_valid(form)
        except (ValidationError, IntegrityError) as e:
            messages.error(self.request, f"Error creating {self.model.__name__.lower()}: {e}")
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"An unexpected error occurred: {e}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_create"] = True
        return context


class AdminUpdateView(AdminPermissionMixin, LoginRequiredMixin, UpdateView):
    """Base class for admin update views"""

    def form_valid(self, form):
        try:
            # Sanitize form data
            for field_name, field_value in form.cleaned_data.items():
                if isinstance(field_value, str):
                    form.instance.__dict__[field_name] = sanitize_input(field_value)

            with transaction.atomic():
                obj = form.save()
            messages.success(self.request, f"{self.model.__name__} was updated successfully.")
            return super().form_valid(form)
        except (ValidationError, IntegrityError) as e:
            messages.error(self.request, f"Error updating {self.model.__name__.lower()}: {e}")
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"An unexpected error occurred: {e}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_update"] = True
        return context


class AdminDeleteView(AdminPermissionMixin, LoginRequiredMixin, DeleteView):
    """Base class for admin delete views"""

    def delete(self, request, *args, **kwargs):
        try:
            obj = self.get_object()
            obj_name = str(obj)
            with transaction.atomic():
                obj.delete()
            messages.success(
                request, f"{self.model.__name__} '{obj_name}' was deleted successfully."
            )
            return super().delete(request, *args, **kwargs)
        except (ValidationError, IntegrityError) as e:
            messages.error(request, f"Error deleting {self.model.__name__.lower()}: {e}")
            return redirect(self.success_url)
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
            return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_delete"] = True
        return context


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("movies:home")

    def form_valid(self, form):
        try:
            # Sanitize form data before saving (only non-None values)
            cleaned_data = form.cleaned_data
            if cleaned_data.get("username"):
                form.instance.username = sanitize_input(cleaned_data.get("username"))
            if cleaned_data.get("email"):
                form.instance.email = sanitize_input(cleaned_data.get("email"))
            if cleaned_data.get("first_name"):
                form.instance.first_name = sanitize_input(cleaned_data.get("first_name"))
            if cleaned_data.get("last_name"):
                form.instance.last_name = sanitize_input(cleaned_data.get("last_name"))

            with transaction.atomic():
                user = form.save()
                # Profile is automatically created by signal
                
                # Automatically log in the user after successful registration
                login(self.request, user)
                
            messages.success(self.request, f"Account created successfully! Welcome, {user.username}!")
            return super().form_valid(form)
        except (ValidationError, IntegrityError) as e:
            messages.error(self.request, f"Error creating account: {e}")
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"An unexpected error occurred: {e}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in.")
            return redirect("movies:home")
        return super().dispatch(request, *args, **kwargs)


class LogoutView(View):
    def get(self, request):
        # Show confirmation page
        return render(request, "accounts/logout_confirm.html")

    def post(self, request):
        # Perform logout
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect("movies:home")


class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "accounts/profile.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context["watchlist_items"] = Watchlist.objects.filter(
                user=self.request.user
            ).select_related("movie")[:6]
            context["total_watchlist"] = Watchlist.objects.filter(user=self.request.user).count()
            return context
        except Exception as e:
            messages.error(self.request, f"Error loading profile data: {e}")
            context = super().get_context_data(**kwargs)
            context["watchlist_items"] = []
            context["total_watchlist"] = 0
            return context


class ProfileUpdateView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile_edit.html"

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context["user_form"] = UserUpdateForm(instance=self.request.user)
            context["profile_form"] = ProfileUpdateForm(instance=self.request.user.profile)
            return context
        except Exception as e:
            messages.error(self.request, f"Error loading profile forms: {e}")
            context = super().get_context_data(**kwargs)
            context["user_form"] = UserUpdateForm()
            context["profile_form"] = ProfileUpdateForm()
            return context

    def post(self, request, *args, **kwargs):
        try:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            profile_form = ProfileUpdateForm(
                request.POST, request.FILES, instance=request.user.profile
            )

            if user_form.is_valid() and profile_form.is_valid():
                # Sanitize form data
                user_form.instance.username = sanitize_input(user_form.cleaned_data.get("username"))
                user_form.instance.email = sanitize_input(user_form.cleaned_data.get("email"))
                user_form.instance.first_name = sanitize_input(
                    user_form.cleaned_data.get("first_name")
                )
                user_form.instance.last_name = sanitize_input(
                    user_form.cleaned_data.get("last_name")
                )

                with transaction.atomic():
                    user_form.save()
                    profile_form.save()
                messages.success(request, "Your profile has been updated successfully.")
                return redirect("accounts:profile")
            else:
                messages.error(request, "Please correct the errors below.")
                return self.render_to_response(
                    self.get_context_data(user_form=user_form, profile_form=profile_form)
                )
        except (ValidationError, IntegrityError) as e:
            messages.error(request, f"Error updating profile: {e}")
            return self.render_to_response(
                self.get_context_data(user_form=user_form, profile_form=profile_form)
            )
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
            return self.render_to_response(
                self.get_context_data(user_form=user_form, profile_form=profile_form)
            )


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:profile")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Your password has been changed successfully.")
        return response


class WatchlistView(LoginRequiredMixin, ListView):
    template_name = "accounts/watchlist.html"
    context_object_name = "watchlist_items"
    paginate_by = 12

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user).select_related("movie")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_movies"] = self.get_queryset().count()
        return context


class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/admin_dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, "You don't have permission to access the admin dashboard.")
            return redirect("movies:home")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            from movies.models import Movie, Genre, Director, Actor
            from reviews.models import Review

            context["stats"] = {
                "total_movies": Movie.objects.count(),
                "total_genres": Genre.objects.count(),
                "total_directors": Director.objects.count(),
                "total_actors": Actor.objects.count(),
                "total_reviews": Review.objects.count(),
                "total_users": User.objects.count(),
            }
            return context
        except Exception as e:
            messages.error(self.request, f"Error loading admin dashboard: {e}")
            context = super().get_context_data(**kwargs)
            context["stats"] = {
                "total_movies": 0,
                "total_genres": 0,
                "total_directors": 0,
                "total_actors": 0,
                "total_reviews": 0,
                "total_users": 0,
            }
            return context


class AdminMovieListView(AdminListView):
    template_name = "accounts/admin_movies.html"
    context_object_name = "movies"

    def get_queryset(self):
        from movies.models import Movie

        return Movie.objects.all().order_by("-release_year", "title")


class AdminGenreListView(AdminListView):
    template_name = "accounts/admin_genres.html"
    context_object_name = "genres"

    def get_queryset(self):
        from movies.models import Genre

        return Genre.objects.all().order_by("name")


class AdminDirectorListView(AdminListView):
    template_name = "accounts/admin_directors.html"
    context_object_name = "directors"

    def get_queryset(self):
        from movies.models import Director

        return Director.objects.all().order_by("name")


class AdminActorListView(AdminListView):
    template_name = "accounts/admin_actors.html"
    context_object_name = "actors"

    def get_queryset(self):
        from movies.models import Actor

        return Actor.objects.all().order_by("name")


class AdminReviewListView(AdminListView):
    template_name = "accounts/admin_reviews.html"
    context_object_name = "reviews"

    def get_queryset(self):
        from reviews.models import Review

        return Review.objects.all().select_related("user", "movie").order_by("-created_at")

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context["total_reviews"] = self.get_queryset().count()
            return context
        except Exception as e:
            messages.error(self.request, f"Error loading review statistics: {e}")
            context = super().get_context_data(**kwargs)
            context["total_reviews"] = 0
            return context


class AdminUserListView(AdminListView):
    template_name = "accounts/admin_users.html"
    context_object_name = "users"

    def get_queryset(self):
        return User.objects.all().select_related("profile").order_by("-date_joined")

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context["total_users"] = self.get_queryset().count()
            context["staff_users"] = User.objects.filter(is_staff=True).count()
            context["superusers"] = User.objects.filter(is_superuser=True).count()
            return context
        except Exception as e:
            messages.error(self.request, f"Error loading user statistics: {e}")
            context = super().get_context_data(**kwargs)
            context["total_users"] = 0
            context["staff_users"] = 0
            context["superusers"] = 0
            return context


# Admin CRUD Views for Genres
class AdminGenreCreateView(AdminCreateView):
    model = Genre
    fields = ["name", "description"]
    template_name = "accounts/admin_genre_form.html"
    success_url = reverse_lazy("accounts:admin_genres")


class AdminGenreUpdateView(AdminUpdateView):
    model = Genre
    fields = ["name", "description"]
    template_name = "accounts/admin_genre_form.html"
    success_url = reverse_lazy("accounts:admin_genres")


class AdminGenreDeleteView(AdminDeleteView):
    model = Genre
    template_name = "accounts/admin_genre_confirm_delete.html"
    success_url = reverse_lazy("accounts:admin_genres")


# Admin CRUD Views for Directors
class AdminDirectorCreateView(AdminCreateView):
    model = Director
    fields = ["name", "bio", "birth_date", "photo"]
    template_name = "accounts/admin_director_form.html"
    success_url = reverse_lazy("accounts:admin_directors")


class AdminDirectorUpdateView(AdminUpdateView):
    model = Director
    fields = ["name", "bio", "birth_date", "photo"]
    template_name = "accounts/admin_director_form.html"
    success_url = reverse_lazy("accounts:admin_directors")


class AdminDirectorDeleteView(AdminDeleteView):
    model = Director
    template_name = "accounts/admin_director_confirm_delete.html"
    success_url = reverse_lazy("accounts:admin_directors")


# Admin CRUD Views for Actors
class AdminActorCreateView(AdminCreateView):
    model = Actor
    fields = ["name", "bio", "birth_date", "photo"]
    template_name = "accounts/admin_actor_form.html"
    success_url = reverse_lazy("accounts:admin_actors")


class AdminActorUpdateView(AdminUpdateView):
    model = Actor
    fields = ["name", "bio", "birth_date", "photo"]
    template_name = "accounts/admin_actor_form.html"
    success_url = reverse_lazy("accounts:admin_actors")


class AdminActorDeleteView(AdminDeleteView):
    model = Actor
    template_name = "accounts/admin_actor_confirm_delete.html"
    success_url = reverse_lazy("accounts:admin_actors")
