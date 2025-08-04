import os
import subprocess
import sys

def clear_movie_data():
    """Clear all existing movie data"""
    print("🗑️  Clearing existing movie data...")
    
    try:
        # Use Django shell to clear data
        clear_script = """
from movies.models import Movie, Genre, Director, Actor
from reviews.models import Review
from accounts.models import Watchlist

print(f"Deleting {Movie.objects.count()} movies...")
Movie.objects.all().delete()

print(f"Deleting {Genre.objects.count()} genres...")
Genre.objects.all().delete()

print(f"Deleting {Director.objects.count()} directors...")
Director.objects.all().delete()

print(f"Deleting {Actor.objects.count()} actors...")
Actor.objects.all().delete()

print(f"Deleting {Review.objects.count()} reviews...")
Review.objects.all().delete()

print(f"Deleting {Watchlist.objects.count()} watchlist items...")
Watchlist.objects.all().delete()

print("✅ All movie data cleared successfully!")
"""
        
        result = subprocess.run([
            sys.executable, 'manage.py', 'shell', '-c', clear_script
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"❌ Error clearing data: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def import_new_movies():
    """Import new movies using the import_mixed_movies command"""
    print("\n🎬 Importing new movies...")
    
    try:
        # Import 3 pages of popular movies and 1 page of latest movies
        # We'll use top_rated_pages=3 and new_movies_pages=1
        result = subprocess.run([
            sys.executable, 'manage.py', 'import_mixed_movies',
            '--top-rated-pages', '3',
            '--new-movies-pages', '1'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✅ Movies imported successfully!")
            print(result.stdout)
            return True
        else:
            print(f"❌ Error importing movies: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 Starting movie database reset and import...")
    
    # Check if TMDB API key is set
    tmdb_api_key = os.getenv('TMDB_API_KEY')
    if not tmdb_api_key:
        print("❌ TMDB_API_KEY environment variable not set")
        print("💡 Please set your TMDB API key:")
        print("   export TMDB_API_KEY=your_api_key_here")
        print("   or")
        print("   set TMDB_API_KEY=your_api_key_here (Windows)")
        return False
    
    print(f"🔑 TMDB API key found: {tmdb_api_key[:8]}...")
    
    # Clear existing data
    if not clear_movie_data():
        print("❌ Failed to clear existing data")
        return False
    
    # Import new movies
    if not import_new_movies():
        print("❌ Failed to import new movies")
        return False
    
    print("\n🎉 Movie database reset and import completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 