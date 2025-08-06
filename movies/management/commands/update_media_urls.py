from django.core.management.base import BaseCommand
from django.conf import settings
from movies.models import Movie, Director, Actor
from accounts.models import Profile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Update existing media file references to use Cloudinary URLs'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting to update media file references...')
        )

        # Update Movie posters
        movies_updated = 0
        for movie in Movie.objects.all():
            if movie.poster and hasattr(movie.poster, 'name'):
                try:
                    # Get the local file path
                    local_path = os.path.join(settings.MEDIA_ROOT, movie.poster.name)
                    if os.path.exists(local_path):
                        # Read the file and upload to Cloudinary
                        with open(local_path, 'rb') as f:
                            file_content = f.read()
                        
                        # Upload to Cloudinary
                        cloudinary_path = default_storage.save(
                            movie.poster.name, 
                            ContentFile(file_content)
                        )
                        
                        # Update the model
                        movie.poster.name = cloudinary_path
                        movie.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(f'Updated movie poster: {movie.title}')
                        )
                        movies_updated += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error updating movie {movie.title}: {str(e)}')
                    )

        # Update Director photos
        directors_updated = 0
        for director in Director.objects.all():
            if director.photo and hasattr(director.photo, 'name'):
                try:
                    local_path = os.path.join(settings.MEDIA_ROOT, director.photo.name)
                    if os.path.exists(local_path):
                        with open(local_path, 'rb') as f:
                            file_content = f.read()
                        
                        cloudinary_path = default_storage.save(
                            director.photo.name, 
                            ContentFile(file_content)
                        )
                        
                        director.photo.name = cloudinary_path
                        director.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(f'Updated director photo: {director.name}')
                        )
                        directors_updated += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error updating director {director.name}: {str(e)}')
                    )

        # Update Actor photos
        actors_updated = 0
        for actor in Actor.objects.all():
            if actor.photo and hasattr(actor.photo, 'name'):
                try:
                    local_path = os.path.join(settings.MEDIA_ROOT, actor.photo.name)
                    if os.path.exists(local_path):
                        with open(local_path, 'rb') as f:
                            file_content = f.read()
                        
                        cloudinary_path = default_storage.save(
                            actor.photo.name, 
                            ContentFile(file_content)
                        )
                        
                        actor.photo.name = cloudinary_path
                        actor.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(f'Updated actor photo: {actor.name}')
                        )
                        actors_updated += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error updating actor {actor.name}: {str(e)}')
                    )

        # Update Profile avatars
        profiles_updated = 0
        for profile in Profile.objects.all():
            if profile.avatar and hasattr(profile.avatar, 'name'):
                try:
                    local_path = os.path.join(settings.MEDIA_ROOT, profile.avatar.name)
                    if os.path.exists(local_path):
                        with open(local_path, 'rb') as f:
                            file_content = f.read()
                        
                        cloudinary_path = default_storage.save(
                            profile.avatar.name, 
                            ContentFile(file_content)
                        )
                        
                        profile.avatar.name = cloudinary_path
                        profile.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(f'Updated profile avatar: {profile.user.username}')
                        )
                        profiles_updated += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error updating profile {profile.user.username}: {str(e)}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Update complete! {movies_updated} movies, {directors_updated} directors, '
                f'{actors_updated} actors, {profiles_updated} profiles updated'
            )
        ) 