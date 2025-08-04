from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('password-change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password-change-done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'), 
        name='password_change_done'),
    path('watchlist/', views.WatchlistView.as_view(), name='watchlist'),
    
    # Admin URLs
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-movies/', views.AdminMovieListView.as_view(), name='admin_movies'),
    path('admin-genres/', views.AdminGenreListView.as_view(), name='admin_genres'),
    path('admin-directors/', views.AdminDirectorListView.as_view(), name='admin_directors'),
    path('admin-actors/', views.AdminActorListView.as_view(), name='admin_actors'),
    path('admin-reviews/', views.AdminReviewListView.as_view(), name='admin_reviews'),
    path('admin-users/', views.AdminUserListView.as_view(), name='admin_users'),
]