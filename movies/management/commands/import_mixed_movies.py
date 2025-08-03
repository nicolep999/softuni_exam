import requests
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from movies.models import Movie, Genre, Director, Actor
import time

class Command(BaseCommand):
    help = 'Import a mix of top-rated movies (90%) and newer movies (10%) for latest releases'

    def add_arguments(self, parser):
        parser.add_argument(
            '--api-key',
            type=str,
            help='TMDB API key (or set TMDB_API_KEY environment variable)',
        )
        parser.add_argument(
            '--top-rated-pages',
            type=int,
            default=9,
            help='Number of pages from top-rated movies (default: 9)',
        )
        parser.add_argument(
            '--new-movies-pages',
            type=int,
            default=1,
            help='Number of pages from now_playing/upcoming movies (default: 1)',
        )

    def handle(self, *args, **options):
        api_key = options['api_key'] or os.getenv('TMDB_API_KEY')
        
        if not api_key:
            self.stdout.write(self.style.ERROR('TMDB API key is required. Set TMDB_API_KEY environment variable or use --api-key'))
            return

        top_rated_pages = options['top_rated_pages']
        new_movies_pages = options['new_movies_pages']
        
        self.stdout.write(f'Starting import of {top_rated_pages} pages from top-rated movies and {new_movies_pages} pages from newer movies...')
        
        total_movies_imported = 0
        
        # Import top-rated movies (90% of the collection)
        self.stdout.write(self.style.SUCCESS('=== IMPORTING TOP-RATED MOVIES ==='))
        for page in range(1, top_rated_pages + 1):
            self.stdout.write(f'Importing top-rated page {page}/{top_rated_pages}...')
            
            movies_data = self.get_movies_from_tmdb(api_key, 'top_rated', page)
            
            if not movies_data:
                self.stdout.write(self.style.WARNING(f'No movies found on top-rated page {page}'))
                continue
            
            for movie_data in movies_data:
                try:
                    movie = self.import_movie(api_key, movie_data)
                    if movie:
                        total_movies_imported += 1
                        self.stdout.write(f'✅ Imported: {movie.title} ({movie.release_year})')
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Error importing {movie_data.get("title", "Unknown")}: {e}')
                    )
                
                time.sleep(0.1)  # Rate limiting
            
            time.sleep(0.5)  # Rate limiting between pages
        
        # Import newer movies (10% of the collection) - mix of now_playing and upcoming
        self.stdout.write(self.style.SUCCESS('=== IMPORTING NEWER MOVIES FOR LATEST RELEASES ==='))
        
        # Import some now_playing movies
        for page in range(1, new_movies_pages + 1):
            self.stdout.write(f'Importing now_playing page {page}/{new_movies_pages}...')
            
            movies_data = self.get_movies_from_tmdb(api_key, 'now_playing', page)
            
            if not movies_data:
                self.stdout.write(self.style.WARNING(f'No movies found on now_playing page {page}'))
                continue
            
            for movie_data in movies_data:
                try:
                    movie = self.import_movie(api_key, movie_data)
                    if movie:
                        total_movies_imported += 1
                        self.stdout.write(f'✅ Imported: {movie.title} ({movie.release_year})')
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Error importing {movie_data.get("title", "Unknown")}: {e}')
                    )
                
                time.sleep(0.1)  # Rate limiting
            
            time.sleep(0.5)  # Rate limiting between pages
        
        # Import some upcoming movies
        for page in range(1, new_movies_pages + 1):
            self.stdout.write(f'Importing upcoming page {page}/{new_movies_pages}...')
            
            movies_data = self.get_movies_from_tmdb(api_key, 'upcoming', page)
            
            if not movies_data:
                self.stdout.write(self.style.WARNING(f'No movies found on upcoming page {page}'))
                continue
            
            for movie_data in movies_data:
                try:
                    movie = self.import_movie(api_key, movie_data)
                    if movie:
                        total_movies_imported += 1
                        self.stdout.write(f'✅ Imported: {movie.title} ({movie.release_year})')
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Error importing {movie_data.get("title", "Unknown")}: {e}')
                    )
                
                time.sleep(0.1)  # Rate limiting
            
            time.sleep(0.5)  # Rate limiting between pages
        
        self.stdout.write(
            self.style.SUCCESS(f'Import completed! Successfully imported {total_movies_imported} movies')
        )

    def get_movies_from_tmdb(self, api_key, category, page):
        """Get movies from TMDB API"""
        base_url = 'https://api.themoviedb.org/3'
        
        if category == 'popular':
            url = f'{base_url}/movie/popular'
        elif category == 'top_rated':
            url = f'{base_url}/movie/top_rated'
        elif category == 'now_playing':
            url = f'{base_url}/movie/now_playing'
        elif category == 'upcoming':
            url = f'{base_url}/movie/upcoming'
        
        params = {
            'api_key': api_key,
            'page': page,
            'language': 'en-US'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('results', [])
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error fetching movies from TMDB: {e}'))
            return []

    def import_movie(self, api_key, movie_data):
        """Import a single movie with all its data"""
        # Check if movie already exists
        if Movie.objects.filter(title=movie_data['title'], release_year=movie_data['release_date'][:4]).exists():
            return None
        
        # Parse release date
        release_date = None
        if movie_data.get('release_date'):
            try:
                from datetime import datetime
                release_date = datetime.strptime(movie_data['release_date'], '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Create movie
        movie = Movie.objects.create(
            title=movie_data['title'],
            release_year=int(movie_data['release_date'][:4]),
            release_date=release_date,
            plot=movie_data.get('overview', 'No plot available.'),
            trailer_url=''  # We'll get this later if needed
        )
        
        # Download poster
        if movie_data.get('poster_path'):
            self.download_poster(movie, movie_data['poster_path'])
        
        # Get detailed movie info
        detailed_data = self.get_movie_details(api_key, movie_data['id'])
        if detailed_data:
            # Update plot with more detailed one
            if detailed_data.get('overview'):
                movie.plot = detailed_data['overview']
            
            # Update IMDb rating
            if detailed_data.get('external_ids', {}).get('imdb_id'):
                imdb_id = detailed_data['external_ids']['imdb_id']
                imdb_rating = self.get_imdb_rating(api_key, imdb_id)
                if imdb_rating:
                    movie.imdb_rating = imdb_rating
                    self.stdout.write(f'  📊 Updated IMDb rating for {movie.title}: {imdb_rating}')
            
            # Update release date if we have a more accurate one
            if detailed_data.get('release_date') and not release_date:
                try:
                    movie.release_date = datetime.strptime(detailed_data['release_date'], '%Y-%m-%d').date()
                except ValueError:
                    pass
            
            movie.save()
            
            # Import genres
            self.import_genres(movie, detailed_data.get('genres', []))
            
            # Import cast and crew
            credits_data = self.get_movie_credits(api_key, movie_data['id'])
            if credits_data:
                self.import_cast_and_crew(movie, credits_data)
        
        return movie

    def download_poster(self, movie, poster_path):
        """Download movie poster"""
        try:
            poster_url = f'https://image.tmdb.org/t/p/w500{poster_path}'
            response = requests.get(poster_url, timeout=10)
            response.raise_for_status()
            
            filename = f'posters/{movie.id}_{movie.title.replace(" ", "_")[:30]}.jpg'
            movie.poster.save(filename, ContentFile(response.content), save=True)
        except Exception as e:
            self.stdout.write(f'⚠️  Could not download poster for {movie.title}: {e}')

    def get_movie_details(self, api_key, movie_id):
        """Get detailed movie information"""
        url = f'https://api.themoviedb.org/3/movie/{movie_id}'
        params = {
            'api_key': api_key,
            'language': 'en-US',
            'append_to_response': 'external_ids'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.stdout.write(f'⚠️  Could not get details for movie {movie_id}: {e}')
            return None

    def get_imdb_rating(self, api_key, imdb_id):
        """Get IMDb rating using OMDB API"""
        if not imdb_id:
            return None
            
        # Get OMDB API key from environment
        omdb_api_key = os.getenv('OMDB_API_KEY')
        if not omdb_api_key:
            self.stdout.write(f'⚠️  OMDB_API_KEY not set, skipping IMDb rating for {imdb_id}')
            return None
            
        url = 'http://www.omdbapi.com/'
        params = {
            'apikey': omdb_api_key,
            'i': imdb_id,
            'plot': 'short'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('Response') == 'True' and data.get('imdbRating') != 'N/A':
                return float(data['imdbRating'])
            else:
                return None
                
        except Exception as e:
            self.stdout.write(f'⚠️  Could not get IMDb rating for {imdb_id}: {e}')
            return None

    def get_movie_credits(self, api_key, movie_id):
        """Get movie credits (cast and crew)"""
        url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits'
        params = {
            'api_key': api_key,
            'language': 'en-US'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.stdout.write(f'⚠️  Could not get credits for movie {movie_id}: {e}')
            return None

    def import_genres(self, movie, genres_data):
        """Import genres for the movie"""
        for genre_data in genres_data:
            genre_name = genre_data['name']
            genre, created = Genre.objects.get_or_create(name=genre_name)
            movie.genres.add(genre)
            
            if created:
                self.stdout.write(f'  📝 Created genre: {genre_name}')

    def import_cast_and_crew(self, movie, credits_data):
        """Import cast and crew for the movie"""
        # Import director (first director from crew)
        crew = credits_data.get('crew', [])
        director_data = next((person for person in crew if person['job'] == 'Director'), None)
        
        if director_data:
            director_name = director_data['name']
            director, created = Director.objects.get_or_create(name=director_name)
            
            # Update director with biographical info if newly created
            if created:
                self.update_person_info(director, director_data['id'], 'director')
                self.stdout.write(f'  📝 Created director: {director_name}')
            
            movie.director = director
            movie.save()
        
        # Import top actors (first 10 from cast)
        cast = credits_data.get('cast', [])[:10]
        for actor_data in cast:
            actor_name = actor_data['name']
            actor, created = Actor.objects.get_or_create(name=actor_name)
            
            # Update actor with biographical info if newly created
            if created:
                self.update_person_info(actor, actor_data['id'], 'actor')
                self.stdout.write(f'  📝 Created actor: {actor_name}')
            
            movie.actors.add(actor)

    def update_person_info(self, person, person_id, person_type):
        """Update person (director/actor) with biographical information"""
        api_key = os.getenv('TMDB_API_KEY')
        if not api_key:
            return
            
        # Get person details from TMDB
        url = f'https://api.themoviedb.org/3/person/{person_id}'
        params = {
            'api_key': api_key,
            'language': 'en-US'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            person_data = response.json()
            
            # Update bio
            if person_data.get('biography'):
                person.bio = person_data['biography']
            
            # Update birth date
            if person_data.get('birthday'):
                try:
                    from datetime import datetime
                    birth_date = datetime.strptime(person_data['birthday'], '%Y-%m-%d').date()
                    person.birth_date = birth_date
                except ValueError:
                    pass  # Skip if date format is invalid
            
            # Download photo
            if person_data.get('profile_path'):
                self.download_person_photo(person, person_data['profile_path'], person_type)
            
            person.save()
            
        except Exception as e:
            self.stdout.write(f'⚠️  Could not get details for {person_type} {person.name}: {e}')

    def download_person_photo(self, person, profile_path, person_type):
        """Download person photo"""
        try:
            photo_url = f'https://image.tmdb.org/t/p/w500{profile_path}'
            response = requests.get(photo_url, timeout=10)
            response.raise_for_status()
            
            filename = f'{person_type}s/{person.id}_{person.name.replace(" ", "_")[:30]}.jpg'
            person.photo.save(filename, ContentFile(response.content), save=True)
            
        except Exception as e:
            self.stdout.write(f'⚠️  Could not download photo for {person_type} {person.name}: {e}') 