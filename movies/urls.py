from django.urls import path
from . import views, api_views

app_name = 'movies'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('movies/', views.MovieListView.as_view(), name='movie_list'),
    path('movies/<int:pk>/', views.MovieDetailView.as_view(), name='movie_detail'),
    path('movies/create/', views.MovieCreateView.as_view(), name='movie_create'),
    path('movies/<int:pk>/update/', views.MovieUpdateView.as_view(), name='movie_update'),
    path('movies/<int:pk>/delete/', views.MovieDeleteView.as_view(), name='movie_delete'),
    path('genres/', views.GenreListView.as_view(), name='genre_list'),
    path('genres/<int:pk>/', views.GenreDetailView.as_view(), name='genre_detail'),
    path('movies/<int:movie_id>/add-to-watchlist/', views.add_to_watchlist, name='add_to_watchlist'),
    path('movies/<int:movie_id>/remove-from-watchlist/', views.remove_from_watchlist, name='remove_from_watchlist'),
    
    # API endpoints
    path('api/movies/', api_views.list_movies_api, name='api_movies_list'),
    path('api/movies/add/', api_views.add_movie_api, name='api_movies_add'),
]
