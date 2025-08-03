import requests
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from movies.models import Movie, Genre, Director, Actor


class Command(BaseCommand):
    help = 'Import movies from The Movie Database (TMDB) API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--api-key',
            type=str,
            help='TMDB API key (or set TMDB_API_KEY environment variable)',
        )
        parser.add_argument(
            '--pages',
            type=int,
            default=1,
            help='Number of pages to import (default: 1)',
        )
        parser.add_argument(
            '--category',
            type=str,
            default='popular',
            choices=['popular', 'top_rated', 'now_playing', 'upcoming'],
            help='Movie category to import (default: popular)',
        )

    def handle(self, *args, **options):
        api_key = options['api_key'] or os.getenv('TMDB_API_KEY')
        
        if not api_key:
            self.stdout.write(
                self.style.ERROR(
                    'Please provide TMDB API key via --api-key argument or TMDB_API_KEY environment variable'
                )
            )
            self.stdout.write(
                'Get your API key from: https://www.themoviedb.org/settings/api'
            )
            return

        base_url = 'https://api.themoviedb.org/3'
        image_base_url = 'https://image.tmdb.org/t/p/w500'
        
        # Get category endpoint
        category_endpoints = {
            'popular': '/movie/popular',
            'top_rated': '/movie/top_rated',
            'now_playing': '/movie/now_playing',
            'upcoming': '/movie/upcoming',
        }
        
        endpoint = category_endpoints[options['category']]
        
        movies_created = 0
        movies_skipped = 0
        
        for page in range(1, options['pages'] + 1):
            self.stdout.write(f'Fetching page {page}...')
            
            # Fetch movies
            response = requests.get(
                f'{base_url}{endpoint}',
                params={
                    'api_key': api_key,
                    'page': page,
                    'language': 'en-US'
                }
            )
            
            if response.status_code != 200:
                self.stdout.write(
                    self.style.ERROR(f'Error fetching movies: {response.status_code}')
                )
                continue
            
            movies_data = response.json()['results']
            
            for movie_data in movies_data:
                try:
                    # Check if movie already exists
                    if Movie.objects.filter(title=movie_data['title'], release_year=movie_data['release_date'][:4]).exists():
                        movies_skipped += 1
                        continue
                    
                    # Get detailed movie info
                    detail_response = requests.get(
                        f'{base_url}/movie/{movie_data["id"]}',
                        params={
                            'api_key': api_key,
                            'language': 'en-US',
                            'append_to_response': 'credits'
                        }
                    )
                    
                    if detail_response.status_code != 200:
                        continue
                    
                    detail_data = detail_response.json()
                    
                    # Create or get director
                    director = None
                    if detail_data['credits']['crew']:
                        for crew_member in detail_data['credits']['crew']:
                            if crew_member['job'] == 'Director':
                                director, created = Director.objects.get_or_create(
                                    name=crew_member['name'],
                                    defaults={
                                        'bio': crew_member.get('biography', ''),
                                        'birth_date': self.parse_date(crew_member.get('birthday')),
                                    }
                                )
                                break
                    
                    # Create movie
                    movie = Movie.objects.create(
                        title=movie_data['title'],
                        release_year=int(movie_data['release_date'][:4]) if movie_data['release_date'] else None,
                        plot=movie_data.get('overview', ''),
                        trailer_url='',  # Would need additional API call for trailers
                        director=director,
                    )
                    
                    # Add genres
                    for genre_data in movie_data.get('genre_ids', []):
                        # Get genre name from TMDB
                        genre_response = requests.get(
                            f'{base_url}/genre/movie/list',
                            params={'api_key': api_key}
                        )
                        if genre_response.status_code == 200:
                            genres_data = genre_response.json()['genres']
                            for g in genres_data:
                                if g['id'] == genre_data:
                                    genre, created = Genre.objects.get_or_create(
                                        name=g['name'],
                                        defaults={'description': ''}
                                    )
                                    movie.genres.add(genre)
                                    break
                    
                    # Add actors (top 5)
                    for cast_member in detail_data['credits']['cast'][:5]:
                        actor, created = Actor.objects.get_or_create(
                            name=cast_member['name'],
                            defaults={
                                'bio': '',
                                'birth_date': self.parse_date(cast_member.get('birthday')),
                            }
                        )
                        movie.actors.add(actor)
                    
                    # Download poster if available
                    if movie_data.get('poster_path'):
                        poster_url = f"{image_base_url}{movie_data['poster_path']}"
                        try:
                            poster_response = requests.get(poster_url)
                            if poster_response.status_code == 200:
                                poster_name = f"poster_{movie.id}.jpg"
                                movie.poster.save(poster_name, ContentFile(poster_response.content), save=True)
                        except Exception as e:
                            self.stdout.write(f'Error downloading poster for {movie.title}: {e}')
                    
                    movies_created += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created: {movie.title} ({movie.release_year})')
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing movie {movie_data.get("title", "Unknown")}: {e}')
                    )
                    continue
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Import completed! Created: {movies_created}, Skipped: {movies_skipped}'
            )
        )

    def parse_date(self, date_string):
        """Parse date string from TMDB API"""
        if not date_string:
            return None
        try:
            return datetime.strptime(date_string, '%Y-%m-%d').date()
        except ValueError:
            return None 