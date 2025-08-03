import requests
import os
from django.conf import settings
from typing import Optional, Dict, Any

class TMDBService:
    """Service for interacting with The Movie Database (TMDB) API"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'TMDB_API_KEY', None)
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p"
        
    def search_movie(self, title: str, year: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Search for a movie by title and optionally year"""
        if not self.api_key:
            return None
            
        params = {
            'api_key': self.api_key,
            'query': title,
            'language': 'en-US',
            'page': 1,
            'include_adult': False
        }
        
        if year:
            params['year'] = year
            
        try:
            response = requests.get(f"{self.base_url}/search/movie", params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('results'):
                return data['results'][0]  # Return first (most relevant) result
            return None
            
        except requests.RequestException:
            return None
    
    def get_movie_details(self, tmdb_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed movie information including backdrop images"""
        if not self.api_key:
            return None
            
        params = {
            'api_key': self.api_key,
            'language': 'en-US',
            'append_to_response': 'images'
        }
        
        try:
            response = requests.get(f"{self.base_url}/movie/{tmdb_id}", params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException:
            return None
    
    def get_backdrop_url(self, movie_title: str, release_year: Optional[int] = None) -> Optional[str]:
        """Get high-quality backdrop URL for a movie"""
        # First search for the movie
        movie_data = self.search_movie(movie_title, release_year)
        if not movie_data:
            return None
            
        # Get backdrop path from search results
        backdrop_path = movie_data.get('backdrop_path')
        if backdrop_path:
            # Return high-quality backdrop URL (1920x1080 - optimal for web)
            return f"{self.image_base_url}/w1920{backdrop_path}"
            
        return None
    
    def get_poster_url(self, movie_title: str, release_year: Optional[int] = None) -> Optional[str]:
        """Get high-quality poster URL for a movie"""
        # First search for the movie
        movie_data = self.search_movie(movie_title, release_year)
        if not movie_data:
            return None
            
        # Get poster path from search results
        poster_path = movie_data.get('poster_path')
        if poster_path:
            # Return high-quality poster URL (500x750)
            return f"{self.image_base_url}/w500{poster_path}"
            
        return None

# Global TMDB service instance
tmdb_service = TMDBService() 