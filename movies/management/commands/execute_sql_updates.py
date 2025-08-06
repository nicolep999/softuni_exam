from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings


class Command(BaseCommand):
    help = 'Execute SQL updates to fix media URLs for Cloudinary'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Executing SQL updates to fix media URLs...')
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

        # SQL statements to execute
        sql_statements = [
            f"UPDATE movies_movie SET poster = REPLACE(poster, 'posters/', 'https://res.cloudinary.com/{cloud_name}/image/upload/posters/') WHERE poster LIKE 'posters/%';",
            f"UPDATE movies_actor SET photo = REPLACE(photo, 'actors/', 'https://res.cloudinary.com/{cloud_name}/image/upload/actors/') WHERE photo LIKE 'actors/%';",
            f"UPDATE movies_director SET photo = REPLACE(photo, 'directors/', 'https://res.cloudinary.com/{cloud_name}/image/upload/directors/') WHERE photo LIKE 'directors/%';",
            f"UPDATE accounts_profile SET avatar = REPLACE(avatar, 'avatars/', 'https://res.cloudinary.com/{cloud_name}/image/upload/avatars/') WHERE avatar LIKE 'avatars/%';",
        ]

        with connection.cursor() as cursor:
            for i, statement in enumerate(sql_statements, 1):
                try:
                    self.stdout.write(f"Executing statement {i}...")
                    cursor.execute(statement)
                    rows_affected = cursor.rowcount
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Statement {i} executed successfully. Rows affected: {rows_affected}")
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"✗ Error executing statement {i}: {e}")
                    )

        self.stdout.write(
            self.style.SUCCESS('All SQL updates completed!')
        ) 