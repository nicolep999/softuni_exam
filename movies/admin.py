from django.contrib import admin
from django.utils.html import format_html
from .models import Movie, Genre, Director, Actor, Watchlist

class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'display_genres', 'director', 'display_poster', 'average_rating', 'created_at')
    list_filter = ('release_year', 'genres', 'director')
    search_fields = ('title', 'plot', 'director__name', 'actors__name')
    filter_horizontal = ('genres', 'actors')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_per_page = 20

    def display_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genres.all()[:3]])
    display_genres.short_description = 'Genres'

    def display_poster(self, obj):
        if obj.poster:
            return format_html('<img src="{}" width="50" height="70" />', obj.poster.url)
        return "No Poster"
    display_poster.short_description = 'Poster'

class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'movie_count', 'display_poster')
    search_fields = ('name', 'description')
    fields = ('name', 'description', 'poster')

    def movie_count(self, obj):
        return obj.movies.count()
    movie_count.short_description = 'Number of Movies'

    def display_poster(self, obj):
        if obj.poster:
            return format_html('<img src="{}" width="60" height="40" style="object-fit: cover; border-radius: 4px;" />', obj.poster)
        return "No Poster"
    display_poster.short_description = 'Poster'

class DirectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'birth_date', 'movie_count', 'display_photo')
    list_filter = ('birth_date',)
    search_fields = ('name', 'bio')

    def movie_count(self, obj):
        return obj.movies.count()
    movie_count.short_description = 'Number of Movies'

    def display_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.photo.url)
        return "No Photo"
    display_photo.short_description = 'Photo'

class ActorAdmin(admin.ModelAdmin):
    list_display = ('name', 'birth_date', 'movie_count', 'display_photo')
    list_filter = ('birth_date',)
    search_fields = ('name', 'bio')

    def movie_count(self, obj):
        return obj.movies.count()
    movie_count.short_description = 'Number of Movies'

    def display_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.photo.url)
        return "No Photo"
    display_photo.short_description = 'Photo'

class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'added_at')
    list_filter = ('added_at', 'user')
    search_fields = ('user__username', 'movie__title')
    date_hierarchy = 'added_at'

# Register models
admin.site.register(Movie, MovieAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Director, DirectorAdmin)
admin.site.register(Actor, ActorAdmin)
admin.site.register(Watchlist, WatchlistAdmin)
