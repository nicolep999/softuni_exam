from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil
from pathlib import Path


class Command(BaseCommand):
    help = 'Copy media files to staticfiles directory for production'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting media copy to staticfiles...')
        )

        # Source media directory
        source_dir = Path(settings.BASE_DIR) / 'media'
        
        # Destination directory (staticfiles/media)
        dest_dir = Path(settings.STATIC_ROOT) / 'media'
        
        if not source_dir.exists():
            self.stdout.write(
                self.style.ERROR(f'Source directory {source_dir} does not exist!')
            )
            return

        # Create destination directory if it doesn't exist
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Clear destination directory first
        if dest_dir.exists():
            for item in dest_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            self.stdout.write('Cleared existing media files in staticfiles')

        # Copy all files recursively
        copied_count = 0
        
        # Walk through all subdirectories and copy files
        for root, dirs, files in os.walk(source_dir):
            # Get the relative path from source_dir
            rel_path = Path(root).relative_to(source_dir)
            
            # Create corresponding directory in destination
            dest_subdir = dest_dir / rel_path
            dest_subdir.mkdir(parents=True, exist_ok=True)
            
            # Copy all files in this directory
            for file in files:
                src_file = Path(root) / file
                dst_file = dest_subdir / file
                shutil.copy2(src_file, dst_file)
                copied_count += 1
                if copied_count % 100 == 0:  # Log every 100 files
                    self.stdout.write(f'Copied {copied_count} files...')

        self.stdout.write(
            self.style.SUCCESS(f'Media copy completed! {copied_count} files copied to staticfiles.')
        )
        
        # Show summary of what was copied
        self.stdout.write('\nMedia files in staticfiles:')
        for item in dest_dir.iterdir():
            if item.is_dir():
                file_count = len(list(item.rglob('*')))
                self.stdout.write(f'  {item.name}/ - {file_count} files') 