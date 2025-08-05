from django.views.generic import (
    CreateView,
    DetailView,
    UpdateView,
    TemplateView,
    ListView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.views import View
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from .forms import (
    CustomUserCreationForm,
    ProfileUpdateForm,
    UserUpdateForm,
    CustomPasswordChangeForm,
)
from .models import Profile
from movies.models import Watchlist, Genre, Director, Actor


# Base Mixins for Admin Views
class AdminPermissionMixin:
    """Mixin to check admin permissions for all admin views"""

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
            with transaction.atomic():
                response = super().form_valid(form)
                messages.success(self.request, f"{self.model.__name__} created successfully.")
                return response
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
        context["model_name"] = self.model.__name__
        context["model_name_plural"] = self.model.__name__ + "s"
        context["back_url"] = self.success_url
        return context


class AdminUpdateView(AdminPermissionMixin, LoginRequiredMixin, UpdateView):
    """Base class for admin update views"""

    def form_valid(self, form):
        try:
            with transaction.atomic():
                response = super().form_valid(form)
                messages.success(self.request, f"{self.model.__name__} updated successfully.")
                return response
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
        context["model_name"] = self.model.__name__
        context["model_name_plural"] = self.model.__name__ + "s"
        context["back_url"] = self.success_url
        return context


class AdminDeleteView(AdminPermissionMixin, LoginRequiredMixin, DeleteView):
    """Base class for admin delete views"""

    def delete(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                response = super().delete(request, *args, **kwargs)
                messages.success(request, f"{self.model.__name__} deleted successfully.")
                return response
        except (ValidationError, IntegrityError) as e:
            messages.error(request, f"Error deleting {self.model.__name__.lower()}: {e}")
            return redirect(self.success_url)
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
            return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model_name"] = self.model.__name__
        context["model_name_plural"] = self.model.__name__ + "s"
        context["back_url"] = self.success_url
        return context


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("movies:home")

    def form_valid(self, form):
        try:
            with transaction.atomic():
                response = super().form_valid(form)
                # Log the user in after registration
                login(self.request, self.object)
                messages.success(
                    self.request,
                    f"Welcome to Moodie, {self.object.username}! Your account has been created.",
                )
                return response
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
            return redirect("movies:home")
        return super().dispatch(request, *args, **kwargs)


class LogoutView(View):
    def get(self, request):
        # Show confirmation page
        return render(request, "accounts/logout_confirm.html")

    def post(self, request):
        # Perform logout
        logout(request)
        messages.success(request, "You have been successfully logged out.")
        return redirect("movies:home")


class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "accounts/profile.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["watchlist"] = Watchlist.objects.filter(user=self.request.user)
        context["reviews"] = self.request.user.reviews.all()
        return context


class ProfileUpdateView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile_edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == "POST":
            context["user_form"] = UserUpdateForm(self.request.POST, instance=self.request.user)
            context["profile_form"] = ProfileUpdateForm(
                self.request.POST, self.request.FILES, instance=self.request.user.profile
            )
        else:
            context["user_form"] = UserUpdateForm(instance=self.request.user)
            context["profile_form"] = ProfileUpdateForm(instance=self.request.user.profile)
        return context

    def post(self, request, *args, **kwargs):
        try:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

            if user_form.is_valid() and profile_form.is_valid():
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
        context = super().get_context_data(**kwargs)
        from reviews.models import Review
        from django.contrib.auth.models import User

        context["stats"] = {
            "total_reviews": Review.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "movies_reviewed": Review.objects.values("movie").distinct().count(),
        }
        return context


class AdminUserListView(AdminListView):
    template_name = "accounts/admin_users.html"
    context_object_name = "users"

    def get_queryset(self):
        return User.objects.all().select_related("profile").order_by("-date_joined")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.contrib.auth.models import User

        context["stats"] = {
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "staff_users": User.objects.filter(is_staff=True).count(),
            "superusers": User.objects.filter(is_superuser=True).count(),
        }
        return context


# Genre CRUD Views
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


# Director CRUD Views
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


# Actor CRUD Views
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
