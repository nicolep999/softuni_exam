from django.core.management.base import BaseCommand
from django.conf import settings
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Fix media URLs to use Cloudinary URLs'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting to fix media URLs...')
        )

        # Check if Cloudinary is configured
        if not hasattr(settings, 'CLOUDINARY_STORAGE'):
            self.stdout.write(
                self.style.ERROR('Cloudinary is not configured. Please add Cloudinary environment variables.')
            )
            return

        cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME')
        if not cloud_name:
            self.stdout.write(
                self.style.ERROR('Cloudinary cloud name not found in settings.')
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f'Cloudinary cloud name: {cloud_name}')
        )

        # Show example URLs
        self.stdout.write(
            self.style.SUCCESS('Example Cloudinary URLs:')
        )
        self.stdout.write(f'  - https://res.cloudinary.com/{cloud_name}/image/upload/posters/posters/1_War_of_the_Worlds.jpg')
        self.stdout.write(f'  - https://res.cloudinary.com/{cloud_name}/image/upload/actors/actors/1_Ice_Cube.jpg')
        self.stdout.write(f'  - https://res.cloudinary.com/{cloud_name}/image/upload/directors/directors/1_Rich_Lee.jpg')

        self.stdout.write(
            self.style.SUCCESS('\nTo fix the database records, you need to:')
        )
        self.stdout.write('1. Go to Railway dashboard')
        self.stdout.write('2. Find the terminal/console')
        self.stdout.write('3. Run: python manage.py update_media_urls')
        
        self.stdout.write(
            self.style.SUCCESS('\nOr manually update your database records to use Cloudinary URLs.')
        ) 