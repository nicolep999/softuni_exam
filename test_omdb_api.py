import requests
import os

def test_omdb_api():
    """Test OMDB API with a known movie"""
    
    # Get API key from environment or use a test key
    omdb_api_key = os.getenv('OMDB_API_KEY')
    
    if not omdb_api_key:
        print("❌ OMDB_API_KEY environment variable not set")
        print("💡 You can get a free OMDB API key from: http://www.omdbapi.com/apikey.aspx")
        print("💡 Set it with: export OMDB_API_KEY=your_key_here")
        return False
    
    # Test with a well-known movie
    test_movie = "The Shawshank Redemption"
    test_year = 1994
    
    print(f"🎬 Testing OMDB API with: {test_movie} ({test_year})")
    print(f"🔑 Using API key: {omdb_api_key[:8]}...")
    
    # Search for the movie
    search_url = 'http://www.omdbapi.com/'
    search_params = {
        'apikey': omdb_api_key,
        's': test_movie,
        'y': test_year,
        'type': 'movie'
    }
    
    try:
        print("\n🔍 Searching for movie...")
        response = requests.get(search_url, params=search_params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📄 Response: {data}")
        
        if data.get('Response') == 'True':
            search_results = data.get('Search', [])
            if search_results:
                movie = search_results[0]
                imdb_id = movie.get('imdbID')
                title = movie.get('Title')
                year = movie.get('Year')
                
                print(f"\n✅ Found movie: {title} ({year})")
                print(f"🆔 IMDb ID: {imdb_id}")
                
                # Get detailed info including rating
                detail_params = {
                    'apikey': omdb_api_key,
                    'i': imdb_id,
                    'plot': 'short'
                }
                
                print("\n📊 Getting detailed info...")
                detail_response = requests.get(search_url, params=detail_params, timeout=10)
                detail_response.raise_for_status()
                detail_data = detail_response.json()
                
                print(f"📡 Detail response status: {detail_response.status_code}")
                print(f"📄 Detail response: {detail_data}")
                
                if detail_data.get('Response') == 'True':
                    imdb_rating = detail_data.get('imdbRating')
                    plot = detail_data.get('Plot')
                    director = detail_data.get('Director')
                    
                    print(f"\n🎯 Success! Movie details:")
                    print(f"   Title: {detail_data.get('Title')}")
                    print(f"   Year: {detail_data.get('Year')}")
                    print(f"   Director: {director}")
                    print(f"   IMDb Rating: {imdb_rating}")
                    print(f"   Plot: {plot[:100]}..." if plot else "   Plot: N/A")
                    
                    return True
                else:
                    print(f"❌ Failed to get detailed info: {detail_data.get('Error', 'Unknown error')}")
                    return False
            else:
                print("❌ No search results found")
                return False
        else:
            print(f"❌ Search failed: {data.get('Error', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing OMDB API...")
    success = test_omdb_api()
    
    if success:
        print("\n🎉 OMDB API test successful!")
    else:
        print("\n💥 OMDB API test failed!") 