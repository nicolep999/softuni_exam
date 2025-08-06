#!/usr/bin/env python
import os
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Moodie.settings')
django.setup()

from movies.models import Movie, Director, Actor, Genre

def extract_info_from_filename(filename):
    """Extract ID and name from filename like '26_My_Oxford_Year.jpg'"""
    name_without_ext = filename.replace('.jpg', '').replace('.png', '')
    parts = name_without_ext.split('_', 1)
    if len(parts) == 2:
        try:
            item_id = int(parts[0])
            name = parts[1].replace('_', ' ')
            return item_id, name
        except ValueError:
            return None, None
    return None, None

def populate_database():
    """Populate database with movies, directors, and actors from static files"""
    
    static_dir = Path("static")
    
    # Create default genre
    default_genre, created = Genre.objects.get_or_create(
        name="General",
        defaults={'description': 'General movies'}
    )
    
    # Populate movies from posters
    posters_dir = static_dir / "posters"
    if posters_dir.exists():
        poster_files = list(posters_dir.glob("*.jpg")) + list(posters_dir.glob("*.png"))
        print(f"Found {len(poster_files)} poster files")
        
        for poster_file in poster_files:
            filename = poster_file.name
            movie_id, title = extract_info_from_filename(filename)
            
            if movie_id and title:
                movie, created = Movie.objects.get_or_create(
                    id=movie_id,
                    defaults={
                        'title': title,
                        'release_year': 2024,
                        'plot': f"A movie about {title.lower()}. Plot details not available.",
                        'poster': f"posters/{filename}"
                    }
                )
                if created:
                    movie.genres.add(default_genre)
                    print(f"Created Movie ID {movie_id}: {title}")
    
    # Populate directors from photos
    directors_dir = static_dir / "directors"
    if directors_dir.exists():
        director_files = list(directors_dir.glob("*.jpg")) + list(directors_dir.glob("*.png"))
        print(f"Found {len(director_files)} director photo files")
        
        for photo_file in director_files:
            filename = photo_file.name
            director_id, name = extract_info_from_filename(filename)
            
            if director_id and name:
                director, created = Director.objects.get_or_create(
                    id=director_id,
                    defaults={
                        'name': name,
                        'bio': f"Biography for {name} not available.",
                        'photo': f"directors/{filename}"
                    }
                )
                if created:
                    print(f"Created Director ID {director_id}: {name}")
    
    # Populate actors from photos (limit to first 100 to avoid overwhelming)
    actors_dir = static_dir / "actors"
    if actors_dir.exists():
        actor_files = list(actors_dir.glob("*.jpg")) + list(actors_dir.glob("*.png"))
        actor_files = actor_files[:100]  # Limit to first 100
        print(f"Found {len(actor_files)} actor photo files (processing first 100)")
        
        for photo_file in actor_files:
            filename = photo_file.name
            actor_id, name = extract_info_from_filename(filename)
            
            if actor_id and name:
                actor, created = Actor.objects.get_or_create(
                    id=actor_id,
                    defaults={
                        'name': name,
                        'bio': f"Biography for {name} not available.",
                        'photo': f"actors/{filename}"
                    }
                )
                if created:
                    print(f"Created Actor ID {actor_id}: {name}")
    
    print(f"\n🎉 Database population completed!")
    print(f"  Movies: {Movie.objects.count()}")
    print(f"  Directors: {Director.objects.count()}")
    print(f"  Actors: {Actor.objects.count()}")
    print(f"  Genres: {Genre.objects.count()}")

if __name__ == "__main__":
    populate_database() 