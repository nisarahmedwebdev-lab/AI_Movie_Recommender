from django.core.management.base import BaseCommand
from movies.recommendation_engine import AdvancedMovieRecommender
from movies.tmdb_api import TMDBAPI
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Initialize movie features cache for all users'

    def handle(self, *args, **options):
        self.stdout.write('Initializing movie features...')
        
        # Get popular movies to cache
        popular = TMDBAPI.get_popular_movies()
        if popular and 'results' in popular:
            for movie in popular['results']:
                try:
                    # Get a user (any user) to initialize recommender
                    user = User.objects.first()
                    if user:
                        recommender = AdvancedMovieRecommender(user)
                        recommender.update_movie_features_cache(movie['id'])
                        self.stdout.write(f'Cached features for: {movie.get("title")}')
                except Exception as e:
                    self.stdout.write(f'Error caching {movie.get("title")}: {e}')
        
        self.stdout.write('Feature initialization complete!')