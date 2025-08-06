from django.core.management.base import BaseCommand
from django.conf import settings
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Generate SQL statements with shorter Cloudinary URLs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='fix_media_urls_short.sql',
            help='Output SQL file name'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Generating SQL statements with shorter URLs...')
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

        output_file = options['output']
        sql_statements = []

        # Generate SQL statements with shorter URLs
        sql_statements.extend(self.generate_movie_updates(cloud_name))
        sql_statements.extend(self.generate_actor_updates(cloud_name))
        sql_statements.extend(self.generate_director_updates(cloud_name))
        sql_statements.extend(self.generate_profile_updates(cloud_name))

        # Write SQL file
        with open(output_file, 'w') as f:
            f.write("-- SQL statements to update media URLs for Cloudinary (short format)\n")
            f.write(f"-- Cloudinary cloud name: {cloud_name}\n\n")
            for statement in sql_statements:
                f.write(statement + "\n")

        self.stdout.write(
            self.style.SUCCESS(f'SQL statements written to {output_file}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Total statements generated: {len(sql_statements)}')
        )
        
        self.stdout.write(
            self.style.SUCCESS('\nThese URLs will be shorter and should fit in your database fields.')
        )

    def generate_movie_updates(self, cloud_name):
        statements = []
        statements.append("-- Update Movie posters (short format)")
        statements.append(f"UPDATE movies_movie SET poster = CONCAT('https://res.cloudinary.com/{cloud_name}/image/upload/', poster) WHERE poster LIKE 'posters/%';")
        return statements

    def generate_actor_updates(self, cloud_name):
        statements = []
        statements.append("-- Update Actor photos (short format)")
        statements.append(f"UPDATE movies_actor SET photo = CONCAT('https://res.cloudinary.com/{cloud_name}/image/upload/', photo) WHERE photo LIKE 'actors/%';")
        return statements

    def generate_director_updates(self, cloud_name):
        statements = []
        statements.append("-- Update Director photos (short format)")
        statements.append(f"UPDATE movies_director SET photo = CONCAT('https://res.cloudinary.com/{cloud_name}/image/upload/', photo) WHERE photo LIKE 'directors/%';")
        return statements

    def generate_profile_updates(self, cloud_name):
        statements = []
        statements.append("-- Update Profile avatars (short format)")
        statements.append(f"UPDATE accounts_profile SET avatar = CONCAT('https://res.cloudinary.com/{cloud_name}/image/upload/', avatar) WHERE avatar LIKE 'avatars/%';")
        return statements 