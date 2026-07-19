import os
import django
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from movies.tmdb_api import test_tmdb_api, TMDBAPI

if __name__ == "__main__":
    print("=" * 50)
    print("Testing TMDB API Connection")
    print("=" * 50)
    
    # Test the API
    test_tmdb_api()
    
    # Try to get popular movies
    print("\nFetching popular movies...")
    popular = TMDBAPI.get_popular_movies()
    if popular and 'results' in popular:
        print(f"SUCCESS: Found {len(popular['results'])} popular movies")
        if popular['results']:
            first_movie = popular['results'][0]
            print(f"First movie: {first_movie.get('title')} ({first_movie.get('release_date', 'N/A')})")
    else:
        print("ERROR: Failed to fetch popular movies")
        print(f"Response: {popular}")