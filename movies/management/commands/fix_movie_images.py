# management/commands/fix_movie_images.py

from django.core.management.base import BaseCommand
from movies.models import Movie
import os
from django.conf import settings
from pathlib import Path
import re

class Command(BaseCommand):
    help = 'Fix movie poster filenames to match their actual DB IDs'

    def handle(self, *args, **options):
        # Use BASE_DIR / "static" / "posters" instead of STATICFILES_DIRS
        base_dir = Path(settings.BASE_DIR)
        media_dir = base_dir / "static" / "posters"

        # Check if media_dir exists
        if not media_dir.exists():
            self.stdout.write(self.style.ERROR(f"Directory {media_dir} does not exist!"))
            return

        for movie in Movie.objects.all():
            # Find file by name ignoring the old ID
            pattern = re.compile(r'\d+_' + re.escape(movie.title).replace(' ', '_').replace(':', '').replace('/', '') + r'\.jpg')

            found = False
            for filename in media_dir.iterdir():
                if filename.is_file() and pattern.fullmatch(filename.name):
                    new_filename = f"{movie.id}_{movie.title.replace(' ', '_').replace(':', '').replace('/', '')}.jpg"
                    new_path = media_dir / new_filename
                    
                    # Check if target file already exists
                    if new_path.exists():
                        if filename.name == new_filename:
                            self.stdout.write(self.style.SUCCESS(f"File {filename.name} already has correct name"))
                        else:
                            self.stdout.write(self.style.WARNING(f"Target file {new_filename} already exists, skipping {filename.name}"))
                        found = True
                        break
                    else:
                        filename.rename(new_path)
                        self.stdout.write(self.style.SUCCESS(f"Renamed {filename.name} -> {new_filename}"))
                        found = True
                        break

            if not found:
                self.stdout.write(self.style.WARNING(f"No file found for {movie.title}"))
