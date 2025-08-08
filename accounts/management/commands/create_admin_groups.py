from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = 'Create admin groups with appropriate permissions'

    def handle(self, *args, **options):
        try:
            # Create Content Managers group
            content_managers, created = Group.objects.get_or_create(name="Content Managers")
            if created:
                movie_permissions = Permission.objects.filter(
                    content_type__app_label="movies",
                    content_type__model__in=["movie", "genre", "director", "actor"],
                )
                content_managers.permissions.add(*movie_permissions)
                self.stdout.write(
                    self.style.SUCCESS('Successfully created Content Managers group')
                )
            else:
                self.stdout.write('Content Managers group already exists')

            # Create Review Managers group
            review_managers, created = Group.objects.get_or_create(name="Review Managers")
            if created:
                review_permissions = Permission.objects.filter(
                    content_type__app_label="reviews", 
                    content_type__model__in=["review", "comment"]
                )
                review_managers.permissions.add(*review_permissions)
                self.stdout.write(
                    self.style.SUCCESS('Successfully created Review Managers group')
                )
            else:
                self.stdout.write('Review Managers group already exists')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating admin groups: {e}')
            )
