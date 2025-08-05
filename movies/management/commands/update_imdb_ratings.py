import requests
from django.core.management.base import BaseCommand
from movies.models import Movie
import time


class Command(BaseCommand):
    help = "Update all existing movies with proper IMDb ratings from OMDB API"

    def add_arguments(self, parser):
        parser.add_argument(
            "--api-key",
            type=str,
            help="TMDB API key (or set TMDB_API_KEY environment variable)",
        )
        parser.add_argument(
            "--omdb-key",
            type=str,
            help="OMDB API key (or set OMDB_API_KEY environment variable)",
        )

    def handle(self, *args, **options):
        tmdb_api_key = options["api_key"] or os.getenv("TMDB_API_KEY")
        omdb_api_key = options["omdb_key"] or os.getenv("OMDB_API_KEY")

        if not tmdb_api_key:
            self.stdout.write(
                self.style.ERROR(
                    "TMDB API key is required. Set TMDB_API_KEY environment variable or use --api-key"
                )
            )
            return

        if not omdb_api_key:
            self.stdout.write(
                self.style.ERROR(
                    "OMDB API key is required. Set OMDB_API_KEY environment variable or use --omdb-key"
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    "You can get a free OMDB API key from: http://www.omdbapi.com/apikey.aspx"
                )
            )
            return

        movies = Movie.objects.all()
        self.stdout.write(f"Updating {movies.count()} movies with proper IMDb ratings...")

        updated_count = 0

        for movie in movies:
            try:
                # Search for movie on TMDB to get IMDb ID
                movie_data = self.search_movie_on_tmdb(
                    tmdb_api_key, movie.title, movie.release_year
                )

                if movie_data:
                    # Get detailed info with external IDs
                    detailed_data = self.get_movie_details(tmdb_api_key, movie_data["id"])

                    if detailed_data and detailed_data.get("external_ids", {}).get("imdb_id"):
                        imdb_id = detailed_data["external_ids"]["imdb_id"]
                        imdb_rating = self.get_imdb_rating(omdb_api_key, imdb_id)

                        if imdb_rating:
                            movie.imdb_rating = imdb_rating
                            movie.save()
                            updated_count += 1
                            self.stdout.write(f"  📊 Updated {movie.title}: {imdb_rating} (IMDb)")
                        else:
                            self.stdout.write(f"  ⚠️  No IMDb rating found for {movie.title}")
                    else:
                        self.stdout.write(f"  ⚠️  No IMDb ID found for {movie.title}")
                else:
                    self.stdout.write(f"  ⚠️  Movie not found on TMDB: {movie.title}")

                time.sleep(0.1)  # Rate limiting

            except Exception:
                self.stdout.write(self.style.ERROR(f"❌ Error updating {movie.title}: {e}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Update completed! Updated {updated_count} movies with proper IMDb ratings"
            )
        )

    def search_movie_on_tmdb(self, api_key, title, year):
        """Search for movie on TMDB"""
        url = "https://api.themoviedb.org/3/search/movie"
        params = {"api_key": api_key, "query": title, "year": year, "language": "en-US"}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])

            if results:
                return results[0]  # Return first (most relevant) result

        except Exception:
            self.stdout.write(f"⚠️  Could not search for {title}: {e}")

        return None

    def get_movie_details(self, api_key, movie_id):
        """Get detailed movie information with external IDs"""
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {"api_key": api_key, "language": "en-US", "append_to_response": "external_ids"}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception:
            self.stdout.write(f"⚠️  Could not get details for movie {movie_id}: {e}")
            return None

    def get_imdb_rating(self, omdb_api_key, imdb_id):
        """Get IMDb rating using OMDB API"""
        if not imdb_id:
            return None

        url = f"http://www.omdbapi.com/"
        params = {"apikey": omdb_api_key, "i": imdb_id, "plot": "short"}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("Response") == "True" and data.get("imdbRating") != "N/A":
                return float(data["imdbRating"])
            else:
                return None

        except Exception:
            self.stdout.write(f"⚠️  Could not get IMDb rating for {imdb_id}: {e}")
            return None
