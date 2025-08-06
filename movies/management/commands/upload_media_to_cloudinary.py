from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Upload existing media files to Cloudinary'

    def add_arguments(self, parser):
        parser.add_argument(
            '--media-dir',
            type=str,
            default='media',
            help='Directory containing media files to upload'
        )

    def handle(self, *args, **options):
        media_dir = Path(options['media_dir'])
        
        if not media_dir.exists():
            self.stdout.write(
                self.style.ERROR(f'Media directory {media_dir} does not exist')
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f'Starting upload of media files from {media_dir}')
        )

        uploaded_count = 0
        error_count = 0

        # Walk through all files in the media directory
        for root, dirs, files in os.walk(media_dir):
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(media_dir)
                
                try:
                    # Read the file
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                    
                    # Upload to Cloudinary
                    saved_path = default_storage.save(
                        str(relative_path), 
                        ContentFile(file_content)
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Uploaded: {relative_path} -> {saved_path}')
                    )
                    uploaded_count += 1
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error uploading {relative_path}: {str(e)}')
                    )
                    error_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Upload complete! {uploaded_count} files uploaded, {error_count} errors'
            )
        ) 