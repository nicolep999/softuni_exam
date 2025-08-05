from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError, transaction
from django.http import Http404

from .forms import ReviewForm, CommentForm
from .models import Review, Comment
from movies.models import Movie


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "reviews/review_form.html"

    def get_form_kwargs(self):
        try:
            kwargs = super().get_form_kwargs()
            kwargs["user"] = self.request.user
            kwargs["movie"] = get_object_or_404(Movie, id=self.kwargs["movie_id"])
            return kwargs
        except Http404:
            messages.error(self.request, "Movie not found.")
            raise
        except Exception as e:
            messages.error(self.request, f"Error loading review form: {e}")
            raise Http404("Movie not found or error occurred")

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context["movie"] = get_object_or_404(Movie, id=self.kwargs["movie_id"])
            return context
        except Http404:
            messages.error(self.request, "Movie not found.")
            raise
        except Exception as e:
            messages.error(self.request, f"Error loading review form: {e}")
            raise Http404("Movie not found or error occurred")

    def form_valid(self, form):
        try:
            with transaction.atomic():
                review = form.save(commit=False)
                review.user = self.request.user
                review.movie = get_object_or_404(Movie, id=self.kwargs["movie_id"])
                review.save()
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
        messages.success(self.request, "Your review has been posted successfully.")
        return reverse("movies:movie_detail", kwargs={"pk": self.kwargs["movie_id"]})


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = "reviews/review_form.html"

    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["movie"] = self.get_object().movie
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["movie"] = self.get_object().movie
        context["is_update"] = True
        return context

    def form_valid(self, form):
        try:
            with transaction.atomic():
                review = form.save(commit=False)
                review.user = self.request.user
                review.movie = self.get_object().movie
                review.save()
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
        messages.success(self.request, "Your review has been updated successfully.")
        return reverse("movies:movie_detail", kwargs={"pk": self.get_object().movie.id})


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    template_name = "reviews/review_confirm_delete.html"

    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user or self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        try:
            review = self.get_object()
            movie_id = review.movie.id
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
            self.movie = get_object_or_404(Movie, id=self.kwargs["movie_id"])
            return Review.objects.filter(movie=self.movie)
        except Http404:
            messages.error(self.request, "Movie not found.")
            raise
        except Exception as e:
            messages.error(self.request, f"Error loading reviews: {e}")
            raise Http404("Movie not found or error occurred")

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context["movie"] = self.movie

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
            self.user = get_object_or_404(User, id=self.kwargs["user_id"])
            return Review.objects.filter(user=self.user)
        except Http404:
            messages.error(self.request, "User not found.")
            raise
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
