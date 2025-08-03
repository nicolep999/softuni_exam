from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
import json
from .models import Movie, Genre, Director, Actor


def is_staff(user):
    return user.is_staff


@csrf_exempt
@require_http_methods(["POST"])
@login_required
@user_passes_test(is_staff)
def add_movie_api(request):
    """
    API endpoint to add a movie programmatically
    Requires staff permissions
    """
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['title', 'release_year', 'plot']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }, status=400)
        
        # Check if movie already exists
        if Movie.objects.filter(title=data['title'], release_year=data['release_year']).exists():
            return JsonResponse({
                'success': False,
                'error': 'Movie already exists'
            }, status=409)
        
        # Create movie
        movie_data = {
            'title': data['title'],
            'release_year': data['release_year'],
            'plot': data['plot'],
            'trailer_url': data.get('trailer_url', ''),
        }
        
        # Handle director
        if 'director' in data:
            director_name = data['director']
            director, created = Director.objects.get_or_create(
                name=director_name,
                defaults={'bio': ''}
            )
            movie_data['director'] = director
        
        movie = Movie.objects.create(**movie_data)
        
        # Handle genres
        if 'genres' in data:
            for genre_name in data['genres']:
                genre, created = Genre.objects.get_or_create(
                    name=genre_name,
                    defaults={'description': ''}
                )
                movie.genres.add(genre)
        
        # Handle actors
        if 'actors' in data:
            for actor_name in data['actors']:
                actor, created = Actor.objects.get_or_create(
                    name=actor_name,
                    defaults={'bio': ''}
                )
                movie.actors.add(actor)
        
        return JsonResponse({
            'success': True,
            'movie_id': movie.id,
            'message': f'Movie "{movie.title}" created successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def list_movies_api(request):
    """
    API endpoint to list movies
    """
    try:
        movies = Movie.objects.all()
        movies_data = []
        
        for movie in movies:
            movies_data.append({
                'id': movie.id,
                'title': movie.title,
                'release_year': movie.release_year,
                'plot': movie.plot,
                'director': movie.director.name if movie.director else None,
                'genres': [genre.name for genre in movie.genres.all()],
                'actors': [actor.name for actor in movie.actors.all()],
                'average_rating': movie.average_rating(),
            })
        
        return JsonResponse({
            'success': True,
            'movies': movies_data,
            'count': len(movies_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500) 