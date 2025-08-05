from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path("movie/<int:movie_id>/add/", views.ReviewCreateView.as_view(), name="review_create"),
    path(
        "movie/<int:movie_id>/reviews/", views.MovieReviewsListView.as_view(), name="movie_reviews"
    ),
    path("<int:pk>/edit/", views.ReviewUpdateView.as_view(), name="review_edit"),
    path("<int:pk>/delete/", views.ReviewDeleteView.as_view(), name="review_delete"),
    path("user/<int:user_id>/", views.UserReviewsListView.as_view(), name="user_reviews"),
]
