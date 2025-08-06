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

        # Clear destination directory first to avoid conflicts
        if dest_dir.exists():
            for item in dest_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            self.stdout.write('Cleared existing media files in destination')

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
            self.style.SUCCESS(f'Media deployment completed! {copied_count} files copied.')
        )
        
        # Show summary of what was copied
        self.stdout.write('\nMedia files deployed:')
        for item in dest_dir.iterdir():
            if item.is_dir():
                file_count = len(list(item.rglob('*')))
                self.stdout.write(f'  {item.name}/ - {file_count} files') 