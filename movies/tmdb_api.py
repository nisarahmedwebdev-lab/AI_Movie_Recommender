import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class TMDBAPI:
    BASE_URL = settings.TMDB_BASE_URL
    API_KEY = settings.TMDB_API_KEY
    IMAGE_BASE_URL = settings.TMDB_IMAGE_BASE_URL
    
    @classmethod
    def _make_request(cls, endpoint, params=None):
        """Make a request to TMDB API"""
        if params is None:
            params = {}
        
        # Check if API key exists
        if not cls.API_KEY:
            logger.error("TMDB API Key is missing! Please set TMDB_API_KEY in .env file")
            return None
        
        params['api_key'] = cls.API_KEY
        url = f"{cls.BASE_URL}{endpoint}"
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            # Log the request URL (without API key for security)
            log_url = url + "?" + "&".join([f"{k}={v}" for k, v in params.items() if k != 'api_key'])
            logger.debug(f"Requesting: {log_url}")
            logger.debug(f"Response status: {response.status_code}")
            
            if response.status_code == 401:
                logger.error("Invalid TMDB API Key. Please check your API key.")
                return None
            elif response.status_code == 404:
                logger.error(f"Endpoint not found: {endpoint}")
                return None
            elif response.status_code != 200:
                logger.error(f"TMDB API error: {response.status_code} - {response.text}")
                return None
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"TMDB API request error: {e}")
            return None
    
    @classmethod
    def get_movie_details(cls, movie_id):
        """Get movie details by ID"""
        endpoint = f"/movie/{movie_id}"
        params = {'append_to_response': 'credits,videos,similar'}
        return cls._make_request(endpoint, params)
    
    @classmethod
    def get_popular_movies(cls, page=1):
        """Get popular movies"""
        return cls._make_request('/movie/popular', {'page': page})
    
    @classmethod
    def get_top_rated_movies(cls, page=1):
        """Get top rated movies"""
        return cls._make_request('/movie/top_rated', {'page': page})
    
    @classmethod
    def get_upcoming_movies(cls, page=1):
        """Get upcoming movies"""
        return cls._make_request('/movie/upcoming', {'page': page})
    
    @classmethod
    def get_trending_movies(cls, time_window='week'):
        """Get trending movies"""
        return cls._make_request(f'/trending/movie/{time_window}')
    
    @classmethod
    def search_movies(cls, query, page=1):
        """Search for movies"""
        return cls._make_request('/search/movie', {'query': query, 'page': page})
    
    @classmethod
    def get_movies_by_genre(cls, genre_id, page=1):
        """Get movies by genre"""
        return cls._make_request('/discover/movie', {'with_genres': genre_id, 'page': page})
    
    @classmethod
    def get_genres(cls):
        """Get list of movie genres"""
        return cls._make_request('/genre/movie/list')
    
    @classmethod
    def get_image_url(cls, path, size='w500'):
        """Get full image URL"""
        if path:
            return f"{cls.IMAGE_BASE_URL}/{size}{path}"
        return None
    
    @classmethod
    def get_genre_ids(cls):
        """Get mapping of genre names to IDs"""
        genres_response = cls.get_genres()
        if genres_response and 'genres' in genres_response:
            return {genre['name'].lower(): genre['id'] for genre in genres_response['genres']}
        return {}
    
    @classmethod
    def get_genre_name(cls, genre_id):
        """Get genre name from ID"""
        genres = cls.get_genres()
        if genres and 'genres' in genres:
            for genre in genres['genres']:
                if genre['id'] == genre_id:
                    return genre['name']
        return None

# Test function to verify API key
def test_tmdb_api():
    """Test if TMDB API is working"""
    print("Testing TMDB API connection...")
    print(f"API Key present: {bool(TMDBAPI.API_KEY)}")
    
    if not TMDBAPI.API_KEY:
        print("ERROR: No API key found. Please set TMDB_API_KEY in .env file")
        return False
    
    # Try to get genres (simple API call)
    result = TMDBAPI.get_genres()
    if result and 'genres' in result:
        print(f"SUCCESS: Connected to TMDB API! Found {len(result['genres'])} genres")
        return True
    else:
        print("ERROR: Failed to connect to TMDB API")
        print(f"Response: {result}")
        return False