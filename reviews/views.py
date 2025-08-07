from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.http import Http404
from django.utils.html import strip_tags
import re

from .models import Review
from .forms import ReviewForm, CommentForm
from movies.models import Movie

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


def validate_movie_id(movie_id):
    """Validate movie_id parameter"""
    try:
        movie_id = int(movie_id)
        if movie_id <= 0:
            raise ValueError("Movie ID must be a positive integer")
        return movie_id
    except (ValueError, TypeError):
        raise ValidationError("Invalid movie ID provided")


def validate_user_id(user_id):
    """Validate user_id parameter"""
    try:
        user_id = int(user_id)
        if user_id <= 0:
            raise ValueError("User ID must be a positive integer")
        return user_id
    except (ValueError, TypeError):
        raise ValidationError("Invalid user ID provided")


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "reviews/review_form.html"

    def get_form_kwargs(self):
        try:
            # Validate and sanitize movie_id
            movie_id = validate_movie_id(self.kwargs.get("movie_id"))
            movie = get_object_or_404(Movie, id=movie_id)

            kwargs = super().get_form_kwargs()
            kwargs["movie"] = movie
            kwargs["user"] = self.request.user
            return kwargs
        except (ValidationError, Http404) as e:
            messages.error(self.request, f"Invalid request: {e}")
            raise Http404("Movie not found")
        except Exception as e:
            messages.error(self.request, f"Error loading review form: {e}")
            raise Http404("Error occurred")

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            movie_id = validate_movie_id(self.kwargs.get("movie_id"))
            context["movie"] = get_object_or_404(Movie, id=movie_id)
            return context
        except (ValidationError, Http404) as e:
            messages.error(self.request, f"Invalid request: {e}")
            raise Http404("Movie not found")
        except Exception as e:
            messages.error(self.request, f"Error loading review context: {e}")
            raise Http404("Error occurred")

    def form_valid(self, form):
        try:
            # Validate movie_id again
            movie_id = validate_movie_id(self.kwargs.get("movie_id"))
            movie = get_object_or_404(Movie, id=movie_id)

            # Check if user already reviewed this movie
            if Review.objects.filter(user=self.request.user, movie=movie).exists():
                messages.error(self.request, "You have already reviewed this movie.")
                return self.form_invalid(form)

            # Sanitize form data
            form.instance.user = self.request.user
            form.instance.movie = movie
            form.instance.title = sanitize_input(form.cleaned_data.get("title"))
            form.instance.content = sanitize_input(form.cleaned_data.get("content"))

            with transaction.atomic():
                form.save()
            messages.success(self.request, "Your review has been posted successfully.")
            return super().form_valid(form)
        except (ValidationError, IntegrityError) as e:
            messages.error(self.request, f"Error creating review: {e}")
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"An unexpected error occurred: {e}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

    def get_success_url(self):
        try:
            movie_id = validate_movie_id(self.kwargs.get("movie_id"))
            return reverse("movies:movie_detail", kwargs={"pk": movie_id})
        except ValidationError:
            return reverse("movies:movie_list")


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = "reviews/review_form.html"

    def test_func(self):
        try:
            review = self.get_object()
            # Only review owner can edit (not admins)
            return self.request.user == review.user
        except Exception:
            return False

    def handle_no_permission(self):
        from django.http import HttpResponseForbidden

        return HttpResponseForbidden("You don't have permission to edit this review.")

    def get_form_kwargs(self):
        try:
            kwargs = super().get_form_kwargs()
            kwargs["user"] = self.request.user
            kwargs["movie"] = self.get_object().movie
            return kwargs
        except Exception as e:
            messages.error(self.request, f"Error loading review form: {e}")
            raise Http404("Review not found")

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context["movie"] = self.get_object().movie
            return context
        except Exception as e:
            messages.error(self.request, f"Error loading review context: {e}")
            raise Http404("Review not found")

    def form_valid(self, form):
        try:
            # Sanitize form data
            form.instance.title = sanitize_input(form.cleaned_data.get("title"))
            form.instance.content = sanitize_input(form.cleaned_data.get("content"))

            with transaction.atomic():
                form.save()
            messages.success(self.request, "Your review has been updated successfully.")
            return super().form_valid(form)
        except (ValidationError, IntegrityError) as e:
            messages.error(self.request, f"Error updating review: {e}")
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"An unexpected error occurred: {e}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

    def get_success_url(self):
        try:
            return reverse("movies:movie_detail", kwargs={"pk": self.get_object().movie.id})
        except Exception:
            return reverse("movies:movie_list")


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    template_name = "reviews/review_confirm_delete.html"

    def test_func(self):
        try:
            review = self.get_object()
            # Review owner or staff can delete
            return self.request.user == review.user or self.request.user.is_staff
        except Exception:
            return False

    def handle_no_permission(self):
        from django.http import HttpResponseForbidden

        return HttpResponseForbidden("You don't have permission to delete this review.")

    def delete(self, request, *args, **kwargs):
        try:
            review = self.get_object()
            with transaction.atomic():
                review.delete()
            messages.success(request, "Review has been deleted successfully.")
            return super().delete(request, *args, **kwargs)
        except (ValidationError, IntegrityError) as e:
            messages.error(request, f"Error deleting review: {e}")
            return redirect("movies:movie_detail", pk=self.get_object().movie.id)
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
            return redirect("movies:movie_detail", pk=self.get_object().movie.id)


class MovieReviewsListView(ListView):
    model = Review
    template_name = "reviews/movie_reviews.html"
    context_object_name = "reviews"
    paginate_by = 10

    def get_queryset(self):
        try:
            # Validate and sanitize movie_id
            movie_id = validate_movie_id(self.kwargs.get("movie_id"))
            # Load movie with all related fields to ensure poster is available
            self.movie = get_object_or_404(
                Movie.objects.select_related('director').prefetch_related('genres', 'actors'), 
                id=movie_id
            )
            return Review.objects.filter(movie=self.movie).select_related("user")
        except (ValidationError, Http404) as e:
            messages.error(self.request, f"Invalid movie ID: {e}")
            raise Http404("Movie not found")
        except Exception as e:
            messages.error(self.request, f"Error loading reviews: {e}")
            raise Http404("Movie not found or error occurred")

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            
            # Ensure movie is properly loaded with all fields
            if hasattr(self, 'movie') and self.movie:
                # Refresh the movie object to ensure all fields are loaded
                self.movie.refresh_from_db()
                context["movie"] = self.movie
            else:
                # Fallback: load movie again if not available
                movie_id = validate_movie_id(self.kwargs.get("movie_id"))
                context["movie"] = get_object_or_404(
                    Movie.objects.select_related('director').prefetch_related('genres', 'actors'), 
                    id=movie_id
                )

            # Add comment form if user is authenticated
            if self.request.user.is_authenticated:
                context["comment_form"] = CommentForm()

            return context
        except Exception as e:
            messages.error(self.request, f"Error loading review context: {e}")
            context = super().get_context_data(**kwargs)
            context["movie"] = None
            context["comment_form"] = CommentForm() if self.request.user.is_authenticated else None
            return context


class UserReviewsListView(ListView):
    model = Review
    template_name = "reviews/user_reviews.html"
    context_object_name = "reviews"
    paginate_by = 10

    def get_queryset(self):
        try:
            # Validate and sanitize user_id
            user_id = validate_user_id(self.kwargs.get("user_id"))
            self.user = get_object_or_404(User, id=user_id)
            return Review.objects.filter(user=self.user).select_related("movie")
        except (ValidationError, Http404) as e:
            messages.error(self.request, f"Invalid user ID: {e}")
            raise Http404("User not found")
        except Exception as e:
            messages.error(self.request, f"Error loading user reviews: {e}")
            raise Http404("User not found or error occurred")

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context["profile_user"] = self.user
            return context
        except Exception as e:
            messages.error(self.request, f"Error loading user review context: {e}")
            context = super().get_context_data(**kwargs)
            context["profile_user"] = None
            return context
