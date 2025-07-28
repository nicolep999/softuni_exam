from django.urls import path
from . import views

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
]