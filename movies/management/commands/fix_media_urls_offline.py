from django.core.management.base import BaseCommand
from django.conf import settings
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Generate SQL statements to fix media URLs for Cloudinary'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='fix_media_urls.sql',
            help='Output SQL file name'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Generating SQL statements to fix media URLs...')
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

        # Generate SQL statements for each model
        sql_statements.extend(self.generate_movie_updates(cloud_name))
        sql_statements.extend(self.generate_actor_updates(cloud_name))
        sql_statements.extend(self.generate_director_updates(cloud_name))
        sql_statements.extend(self.generate_profile_updates(cloud_name))

        # Write SQL file
        with open(output_file, 'w') as f:
            f.write("-- SQL statements to update media URLs for Cloudinary\n")
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
            self.style.SUCCESS('\nTo apply these changes:')
        )
        self.stdout.write('1. Copy the SQL file to your Railway project')
        self.stdout.write('2. Use Railway CLI to run: railway run psql < fix_media_urls.sql')
        self.stdout.write('3. Or manually execute the SQL statements in your database')

    def generate_movie_updates(self, cloud_name):
        statements = []
        statements.append("-- Update Movie posters")
        statements.append("UPDATE movies_movie SET poster = REPLACE(poster, 'posters/', 'https://res.cloudinary.com/" + cloud_name + "/image/upload/posters/') WHERE poster LIKE 'posters/%';")
        return statements

    def generate_actor_updates(self, cloud_name):
        statements = []
        statements.append("-- Update Actor photos")
        statements.append("UPDATE movies_actor SET photo = REPLACE(photo, 'actors/', 'https://res.cloudinary.com/" + cloud_name + "/image/upload/actors/') WHERE photo LIKE 'actors/%';")
        return statements

    def generate_director_updates(self, cloud_name):
        statements = []
        statements.append("-- Update Director photos")
        statements.append("UPDATE movies_director SET photo = REPLACE(photo, 'directors/', 'https://res.cloudinary.com/" + cloud_name + "/image/upload/directors/') WHERE photo LIKE 'directors/%';")
        return statements

    def generate_profile_updates(self, cloud_name):
        statements = []
        statements.append("-- Update Profile avatars")
        statements.append("UPDATE accounts_profile SET avatar = REPLACE(avatar, 'avatars/', 'https://res.cloudinary.com/" + cloud_name + "/image/upload/avatars/') WHERE avatar LIKE 'avatars/%';")
        return statements 