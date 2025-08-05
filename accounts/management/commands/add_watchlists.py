from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from movies.models import Movie, Watchlist


class Command(BaseCommand):
    help = "Add watchlist entries to existing users"

    def add_arguments(self, parser):
        parser.add_argument(
            "--movies-per-user",
            type=int,
            default=5,
            help="Number of movies to add per user (default: 5)",
        )

    def handle(self, *args, **options):
        movies_per_user = options["movies_per_user"]

        users = User.objects.all()
        movies = list(Movie.objects.all())

        if not movies:
            self.stdout.write(self.style.ERROR("No movies found in database"))
            return

        if not users:
            self.stdout.write(self.style.ERROR("No users found in database"))
            return

        total_added = 0

        for user in users:
            # Get random movies for this user
            user_movies = random.sample(movies, min(movies_per_user, len(movies)))

            for movie in user_movies:
                watchlist_entry, created = Watchlist.objects.get_or_create(user=user, movie=movie)
                if created:
                    total_added += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Added {len(user_movies)} movies to {user.username}'s watchlist"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(f"\n🎉 Successfully added {total_added} watchlist entries!")
        )
