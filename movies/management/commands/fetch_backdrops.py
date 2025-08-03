from django.core.management.base import BaseCommand
from django.conf import settings
from movies.models import Movie
from movies.services import tmdb_service
import time

class Command(BaseCommand):
    help = 'Fetch backdrop images from TMDB for movies that don\'t have them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Limit the number of movies to process (default: 50)'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=0.5,
            help='Delay between API calls in seconds (default: 0.5)'
        )

    def handle(self, *args, **options):
        if not getattr(settings, 'TMDB_API_KEY', None):
            self.stdout.write(
                self.style.ERROR('TMDB_API_KEY not found in settings. Please add it to your settings.py')
            )
            return

        # Get movies without backdrop URLs
        movies = Movie.objects.filter(backdrop_url='')[:options['limit']]
        total_movies = movies.count()

        if total_movies == 0:
            self.stdout.write(
                self.style.SUCCESS('All movies already have backdrop URLs!')
            )
            return

        self.stdout.write(f'Fetching backdrop URLs for {total_movies} movies...')

        success_count = 0
        error_count = 0

        for i, movie in enumerate(movies, 1):
            self.stdout.write(f'Processing {i}/{total_movies}: {movie.title} ({movie.release_year})')
            
            try:
                backdrop_url = tmdb_service.get_backdrop_url(movie.title, movie.release_year)
                
                if backdrop_url:
                    movie.backdrop_url = backdrop_url
                    movie.save()
                    success_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Found backdrop for "{movie.title}"')
                    )
                else:
                    error_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'✗ No backdrop found for "{movie.title}"')
                    )
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Error processing "{movie.title}": {str(e)}')
                )

            # Add delay to avoid hitting API rate limits
            time.sleep(options['delay'])

        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Success: {success_count}, Errors: {error_count}'
            )
        ) 