import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from accounts.models import Profile
from movies.models import Movie, Genre, Watchlist

class Command(BaseCommand):
    help = 'Create dummy users with profiles and sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of dummy users to create (default: 10)',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Sample usernames and names
        usernames = [
            'moviebuff', 'cinemalover', 'filmfanatic', 'reelreviewer', 'moviegoer',
            'cinemaphile', 'filmcritic', 'movieholic', 'cinemaster', 'filmgeek',
            'moviewatcher', 'cinemaniac', 'filmenthusiast', 'moviecollector', 'cinemafan',
            'filmaddict', 'moviereviewer', 'cinemalover', 'filmfan', 'moviecritic',
            'cinemageek', 'filmwatcher', 'moviemaniac', 'cinemacollector', 'filmholic'
        ]
        
        first_names = [
            'Alex', 'Jordan', 'Casey', 'Taylor', 'Morgan', 'Riley', 'Quinn', 'Avery',
            'Parker', 'Drew', 'Blake', 'Hayden', 'Reese', 'Dakota', 'Emery', 'Rowan',
            'Sage', 'Peyton', 'Kendall', 'Skyler', 'Finley', 'Harper', 'River', 'Phoenix'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
            'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin'
        ]
        
        # Sample favorite genres
        genres = list(Genre.objects.all())
        
        # Sample movies for watchlist
        movies = list(Movie.objects.all())
        
        users_created = 0
        
        for i in range(count):
            try:
                # Generate unique username
                username = f"{random.choice(usernames)}{random.randint(1, 999)}"
                while User.objects.filter(username=username).exists():
                    username = f"{random.choice(usernames)}{random.randint(1, 999)}"
                
                # Generate user data
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                email = f"{username}@example.com"
                
                # Create user
                user = User.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=make_password('password123'),  # All users have same password for testing
                    is_active=True
                )
                
                # Create profile
                profile = Profile.objects.create(
                    user=user,
                    bio=f"I'm {first_name}, a passionate movie lover who enjoys watching films from various genres."
                )
                
                # Add favorite genres
                if genres:
                    favorite_genres = random.sample(genres, min(3, len(genres)))
                    profile.favorite_genres.set(favorite_genres)
                
                # Add some movies to watchlist
                if movies:
                    watchlist_movies = random.sample(movies, min(5, len(movies)))
                    for movie in watchlist_movies:
                        Watchlist.objects.get_or_create(user=user, movie=movie)
                
                users_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created user: {username} ({first_name} {last_name})')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error creating user: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Successfully created {users_created} dummy users!')
        )
        self.stdout.write(
            self.style.WARNING(f'📝 All users have password: password123')
        )
        self.stdout.write(
            self.style.WARNING(f'📧 Email format: username@example.com')
        ) 