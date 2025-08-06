#!/usr/bin/env python
import os
import django
import requests
import time
import re
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Moodie.settings')
django.setup()

from django.conf import settings
from movies.models import Movie, Director, Actor

# TMDB API Configuration
TMDB_API_KEY = getattr(settings, 'TMDB_API_KEY', None)
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

def normalize_name(name):
    """Normalize a name for comparison (remove special chars, lowercase)"""
    # Remove special characters and convert to lowercase
    normalized = re.sub(r'[^\w\s]', '', name.lower())
    # Replace multiple spaces with single space
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized

def find_matching_file(name, directory, file_type="jpg"):
    """Find a matching file in the directory by comparing normalized names"""
    if not directory.exists():
        return None
    
    normalized_search_name = normalize_name(name)
    
    # Get all files in the directory
    files = list(directory.glob(f"*.{file_type}"))
    
    for file in files:
        # Extract name from filename (remove ID prefix and extension)
        filename = file.stem  # filename without extension
        if '_' in filename:
            # Remove ID prefix (e.g., "123_Name" -> "Name")
            name_part = '_'.join(filename.split('_')[1:])
        else:
            name_part = filename
        
        normalized_filename = normalize_name(name_part)
        
        if normalized_search_name == normalized_filename:
            return file
    
    return None

def check_directors_detailed():
    """Check directors with detailed analysis"""
    print("🎭 DETAILED DIRECTOR CHECK:")
    
    static_dir = Path("static/directors")
    staticfiles_dir = Path("staticfiles/directors")
    
    all_directors = Director.objects.all()
    missing_directors = []
    found_directors = []
    
    for director in all_directors:
        name = director.name
        photo_path = str(director.photo) if director.photo else None
        
        # Check if file exists at the expected path
        file_exists = False
        if photo_path:
            static_file = static_dir / photo_path
            staticfiles_file = staticfiles_dir / photo_path
            file_exists = static_file.exists() or staticfiles_file.exists()
        
        if not file_exists:
            # Try to find a matching file by name
            matching_file = find_matching_file(name, static_dir)
            if matching_file:
                found_directors.append({
                    'director': director,
                    'expected_path': photo_path,
                    'found_file': matching_file.name,
                    'suggestion': f"directors/{matching_file.name}"
                })
            else:
                missing_directors.append({
                    'director': director,
                    'expected_path': photo_path,
                    'issue': 'No matching file found'
                })
    
    print(f"  Total directors: {all_directors.count()}")
    print(f"  Missing photos: {len(missing_directors)}")
    print(f"  Found with mismatched names: {len(found_directors)}")
    
    if found_directors:
        print(f"\n  📝 Directors with mismatched filenames:")
        for item in found_directors[:10]:  # Show first 10
            director = item['director']
            print(f"    Director ID {director.id}: '{director.name}'")
            print(f"      Expected: {item['expected_path']}")
            print(f"      Found: {item['found_file']}")
            print(f"      Suggestion: {item['suggestion']}")
            print()
    
    if missing_directors:
        print(f"\n  ❌ Directors with missing photos:")
        for item in missing_directors[:10]:  # Show first 10
            director = item['director']
            print(f"    Director ID {director.id}: '{director.name}' - {item['issue']}")
    
    return missing_directors, found_directors

def check_actors_detailed():
    """Check actors with detailed analysis"""
    print("\n🎭 DETAILED ACTOR CHECK:")
    
    static_dir = Path("static/actors")
    staticfiles_dir = Path("staticfiles/actors")
    
    all_actors = Actor.objects.all()
    missing_actors = []
    found_actors = []
    
    for actor in all_actors:
        name = actor.name
        photo_path = str(actor.photo) if actor.photo else None
        
        # Check if file exists at the expected path
        file_exists = False
        if photo_path:
            static_file = static_dir / photo_path
            staticfiles_file = staticfiles_dir / photo_path
            file_exists = static_file.exists() or staticfiles_file.exists()
        
        if not file_exists:
            # Try to find a matching file by name
            matching_file = find_matching_file(name, static_dir)
            if matching_file:
                found_actors.append({
                    'actor': actor,
                    'expected_path': photo_path,
                    'found_file': matching_file.name,
                    'suggestion': f"actors/{matching_file.name}"
                })
            else:
                missing_actors.append({
                    'actor': actor,
                    'expected_path': photo_path,
                    'issue': 'No matching file found'
                })
    
    print(f"  Total actors: {all_actors.count()}")
    print(f"  Missing photos: {len(missing_actors)}")
    print(f"  Found with mismatched names: {len(found_actors)}")
    
    if found_actors:
        print(f"\n  📝 Actors with mismatched filenames:")
        for item in found_actors[:10]:  # Show first 10
            actor = item['actor']
            print(f"    Actor ID {actor.id}: '{actor.name}'")
            print(f"      Expected: {item['expected_path']}")
            print(f"      Found: {item['found_file']}")
            print(f"      Suggestion: {item['suggestion']}")
            print()
    
    if missing_actors:
        print(f"\n  ❌ Actors with missing photos:")
        for item in missing_actors[:10]:  # Show first 10
            actor = item['actor']
            print(f"    Actor ID {actor.id}: '{actor.name}' - {item['issue']}")
    
    return missing_actors, found_actors

def search_person_photo(person_name):
    """Search for person photo on TMDB"""
    if not TMDB_API_KEY:
        print("❌ TMDB API key not found in settings")
        return None
    
    search_url = f"{TMDB_BASE_URL}/search/person"
    params = {
        'api_key': TMDB_API_KEY,
        'query': person_name,
        'language': 'en-US',
        'page': 1
    }
    
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data['results']:
            person = data['results'][0]
            profile_path = person.get('profile_path')
            if profile_path:
                return f"{TMDB_IMAGE_BASE_URL}{profile_path}"
        
        return None
    except Exception as e:
        print(f"❌ Error searching for person '{person_name}': {e}")
        return None

def download_image(url, filepath):
    """Download image from URL and save to filepath"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return True
    except Exception as e:
        print(f"❌ Error downloading image: {e}")
        return False

def download_missing_photos(missing_items, item_type):
    """Download missing photos for directors or actors"""
    if not TMDB_API_KEY:
        print("❌ TMDB API key not found in settings!")
        return
    
    print(f"\n🚀 DOWNLOADING MISSING {item_type.upper()} PHOTOS ({len(missing_items)} items):")
    
    static_dir = Path(f"static/{item_type}s")
    downloaded = 0
    failed = 0
    
    for item in missing_items:
        if item_type == 'director':
            person = item['director']
        else:
            person = item['actor']
        
        name = person.name
        photo_path = item.get('suggestion') or f"{item_type}s/{person.id}_{name.replace(' ', '_')}.jpg"
        
        print(f"  Searching for: '{name}' (ID: {person.id})")
        
        # Search for photo on TMDB
        photo_url = search_person_photo(name)
        
        if photo_url:
            # Download the image
            filepath = static_dir / photo_path.split('/')[-1]  # Get just the filename
            if download_image(photo_url, filepath):
                print(f"    ✅ Downloaded: {filepath.name}")
                downloaded += 1
                
                # Update database
                person.photo = photo_path
                person.save()
                print(f"    📝 Updated database with photo path")
            else:
                print(f"    ❌ Failed to download: {filepath.name}")
                failed += 1
        else:
            print(f"    ⚠️  No photo found for: {name}")
            failed += 1
        
        # Rate limiting
        time.sleep(0.5)
    
    print(f"\n📊 {item_type.title()} Photos Summary:")
    print(f"  Downloaded: {downloaded}")
    print(f"  Failed: {failed}")

def main():
    """Main function to check and fix missing photos"""
    print("=== Detailed Missing Photos Check and Fix ===\n")
    
    # Check directors
    missing_directors, found_directors = check_directors_detailed()
    
    # Check actors
    missing_actors, found_actors = check_actors_detailed()
    
    # Summary
    total_missing = len(missing_directors) + len(missing_actors)
    total_found = len(found_directors) + len(found_actors)
    
    print(f"\n📊 OVERALL SUMMARY:")
    print(f"  Missing director photos: {len(missing_directors)}")
    print(f"  Missing actor photos: {len(missing_actors)}")
    print(f"  Directors with mismatched names: {len(found_directors)}")
    print(f"  Actors with mismatched names: {len(found_actors)}")
    print(f"  Total missing: {total_missing}")
    print(f"  Total with name mismatches: {total_found}")
    
    # Ask user if they want to download missing photos
    if total_missing > 0:
        print(f"\n🚀 Would you like to download the missing photos from TMDB?")
        print(f"   This will download {total_missing} photos.")
        
        # For now, let's download them automatically
        if missing_directors:
            download_missing_photos(missing_directors, 'director')
        
        if missing_actors:
            download_missing_photos(missing_actors, 'actor')
    
    print(f"\n🎉 Process completed!")

if __name__ == "__main__":
    main() 