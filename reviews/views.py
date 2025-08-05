from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.urls import reverse

from .forms import ReviewForm, CommentForm
from .models import Review, Comment
from movies.models import Movie


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "reviews/review_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["movie"] = get_object_or_404(Movie, id=self.kwargs["movie_id"])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["movie"] = get_object_or_404(Movie, id=self.kwargs["movie_id"])
        return context

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

    def get_success_url(self):
        messages.success(self.request, "Your review has been updated successfully.")
        return reverse("movies:movie_detail", kwargs={"pk": self.get_object().movie.id})


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    template_name = "reviews/review_confirm_delete.html"

    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user or self.request.user.is_staff

    def get_success_url(self):
        messages.success(self.request, "Review has been deleted successfully.")
        return reverse("movies:movie_detail", kwargs={"pk": self.get_object().movie.id})


class MovieReviewsListView(ListView):
    model = Review
    template_name = "reviews/movie_reviews.html"
    context_object_name = "reviews"
    paginate_by = 10

    def get_queryset(self):
        self.movie = get_object_or_404(Movie, id=self.kwargs["movie_id"])
        return Review.objects.filter(movie=self.movie)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["movie"] = self.movie

        # Add comment form if user is authenticated
        if self.request.user.is_authenticated:
            context["comment_form"] = CommentForm()

        return context


class UserReviewsListView(ListView):
    model = Review
    template_name = "reviews/user_reviews.html"
    context_object_name = "reviews"
    paginate_by = 10

    def get_queryset(self):
        self.user = get_object_or_404(User, id=self.kwargs["user_id"])
        return Review.objects.filter(user=self.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_user"] = self.user
        return context
