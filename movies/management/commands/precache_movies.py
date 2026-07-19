from django.core.management.base import BaseCommand
from django.core.cache import cache
from movies.tmdb_api import TMDBAPI
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Pre-cache movie data for faster loading'

    def handle(self, *args, **options):
        self.stdout.write('Pre-caching movie data...')
        
        # Cache genres
        genres = TMDBAPI.get_genres()
        if genres and 'genres' in genres:
            cache.set('tmdb_genres', genres['genres'], 86400)
            self.stdout.write('Genres cached')
        
        # Cache popular movies
        popular = TMDBAPI.get_popular_movies()
        if popular and 'results' in popular:
            cache.set('popular_movies', popular['results'], 3600)
            cache.set('popular_movies_limited', popular['results'][:10], 3600)
            self.stdout.write('Popular movies cached')
        
        # Cache trending movies
        trending = TMDBAPI.get_trending_movies()
        if trending and 'results' in trending:
            cache.set('trending_movies', trending['results'], 1800)
            self.stdout.write('Trending movies cached')
        
        # Cache genre map
        genre_map = TMDBAPI.get_genre_ids()
        if genre_map:
            cache.set('tmdb_genre_map', genre_map, 86400)
            self.stdout.write('Genre map cached')
        
        self.stdout.write('Pre-caching complete!')