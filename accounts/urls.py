from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("session-test/", views.SessionTestView.as_view(), name="session_test"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.ProfileUpdateView.as_view(), name="profile_edit"),
    path("password-change/", views.CustomPasswordChangeView.as_view(), name="password_change"),
    path(
        "password-change-done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="accounts/password_change_done.html"
        ),
        name="password_change_done",
    ),
    path("watchlist/", views.WatchlistView.as_view(), name="watchlist"),
    # Admin URLs
    path("admin-dashboard/", views.AdminDashboardView.as_view(), name="admin_dashboard"),
    path("admin-movies/", views.AdminMovieListView.as_view(), name="admin_movies"),
    path("admin-genres/", views.AdminGenreListView.as_view(), name="admin_genres"),
    path("admin-genres/create/", views.AdminGenreCreateView.as_view(), name="admin_genre_create"),
    path(
        "admin-genres/<int:pk>/edit/", views.AdminGenreUpdateView.as_view(), name="admin_genre_edit"
    ),
    path(
        "admin-genres/<int:pk>/delete/",
        views.AdminGenreDeleteView.as_view(),
        name="admin_genre_delete",
    ),
    path("admin-directors/", views.AdminDirectorListView.as_view(), name="admin_directors"),
    path(
        "admin-directors/create/",
        views.AdminDirectorCreateView.as_view(),
        name="admin_director_create",
    ),
    path(
        "admin-directors/<int:pk>/edit/",
        views.AdminDirectorUpdateView.as_view(),
        name="admin_director_edit",
    ),
    path(
        "admin-directors/<int:pk>/delete/",
        views.AdminDirectorDeleteView.as_view(),
        name="admin_director_delete",
    ),
    path("admin-actors/", views.AdminActorListView.as_view(), name="admin_actors"),
    path("admin-actors/create/", views.AdminActorCreateView.as_view(), name="admin_actor_create"),
    path(
        "admin-actors/<int:pk>/edit/", views.AdminActorUpdateView.as_view(), name="admin_actor_edit"
    ),
    path(
        "admin-actors/<int:pk>/delete/",
        views.AdminActorDeleteView.as_view(),
        name="admin_actor_delete",
    ),
    path("admin-reviews/", views.AdminReviewListView.as_view(), name="admin_reviews"),
    path("admin-users/", views.AdminUserListView.as_view(), name="admin_users"),
]
