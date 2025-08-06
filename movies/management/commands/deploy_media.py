from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil
from pathlib import Path


class Command(BaseCommand):
    help = 'Deploy media files to Railway volume'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting media deployment...')
        )

        # Source media directory (local)
        source_dir = Path(settings.BASE_DIR) / 'media'
        
        # Destination directory (Railway volume)
        dest_dir = Path('/app/media')
        
        if not source_dir.exists():
            self.stdout.write(
                self.style.ERROR(f'Source directory {source_dir} does not exist!')
            )
            return

        # Create destination directory if it doesn't exist
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Copy all files and directories
        copied_count = 0
        for item in source_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, dest_dir / item.name)
                copied_count += 1
                self.stdout.write(f'Copied file: {item.name}')
            elif item.is_dir():
                shutil.copytree(item, dest_dir / item.name, dirs_exist_ok=True)
                copied_count += 1
                self.stdout.write(f'Copied directory: {item.name}')

        self.stdout.write(
            self.style.SUCCESS(f'Media deployment completed! {copied_count} items copied.')
        )
        
        # List what's in the destination
        self.stdout.write('\nContents of /app/media:')
        for item in dest_dir.iterdir():
            if item.is_file():
                self.stdout.write(f'  File: {item.name}')
            else:
                self.stdout.write(f'  Directory: {item.name}/')
                for subitem in item.iterdir():
                    self.stdout.write(f'    - {subitem.name}') 