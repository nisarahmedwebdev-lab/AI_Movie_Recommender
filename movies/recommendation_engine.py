import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
from django.db.models import Q, Count
from django.utils import timezone
from django.core.cache import cache
import logging
from .models import (
    UserBehaviorProfile, UserMovieInteraction, 
    MovieFeatureCache, WatchHistory, LikedMovie,
    Watchlist
)
from .tmdb_api import TMDBAPI

logger = logging.getLogger(__name__)

class AdvancedMovieRecommender:
    """Working recommendation engine"""
    
    def __init__(self, user):
        self.user = user
        self.user_profile = None
        self._load_user_profile()
        
    def _load_user_profile(self):
        """Load or create user profile"""
        try:
            self.user_profile, created = UserBehaviorProfile.objects.get_or_create(user=self.user)
            if created:
                self._initialize_user_profile()
        except Exception as e:
            logger.error(f"Error loading user profile: {e}")
            self.user_profile = None
    
    def _initialize_user_profile(self):
        """Initialize user profile with default preferences"""
        if self.user_profile:
            # Get favorite genres from user profile
            favorite_genres = []
            if hasattr(self.user, 'userprofile'):
                favorite_genres = self.user.userprofile.favorite_genres
            
            if favorite_genres:
                for genre in favorite_genres:
                    self.user_profile.genre_preferences[genre.lower()] = 2.0
            else:
                # Default genres
                default_genres = ['action', 'adventure', 'comedy', 'drama', 'sci-fi', 'thriller']
                for genre in default_genres:
                    self.user_profile.genre_preferences[genre] = 1.0
            
            self.user_profile.save()
            logger.info(f"Initialized profile for user: {self.user.username}")
    
    def get_personalized_recommendations(self, n=20):
        """Get personalized movie recommendations"""
        try:
            # Get user's genre preferences
            genre_preferences = self.user_profile.genre_preferences if self.user_profile else {}
            
            if not genre_preferences:
                # If no preferences, use popular movies
                return self._get_popular_movies(n)
            
            # Get top genres
            top_genres = sorted(genre_preferences.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # Get movies for each genre
            all_movies = []
            genre_map = TMDBAPI.get_genre_ids()
            
            for genre_name, weight in top_genres:
                genre_id = None
                # Find matching genre ID
                for key, value in genre_map.items():
                    if genre_name.lower() in key.lower() or key.lower() in genre_name.lower():
                        genre_id = value
                        break
                
                if genre_id:
                    movies_data = TMDBAPI.get_movies_by_genre(genre_id, page=1)
                    if movies_data and 'results' in movies_data:
                        for movie in movies_data['results'][:20]:
                            movie['genre_weight'] = weight
                            all_movies.append(movie)
            
            # If no movies from genres, get popular movies
            if not all_movies:
                return self._get_popular_movies(n)
            
            # Score and sort movies
            scored_movies = []
            seen_ids = set()
            
            for movie in all_movies:
                if movie['id'] in seen_ids:
                    continue
                seen_ids.add(movie['id'])
                
                # Calculate score
                score = 0
                
                # Genre match
                movie_genres = [g['name'].lower() for g in movie.get('genres', [])]
                for genre in movie_genres:
                    if genre in genre_preferences:
                        score += genre_preferences[genre] * 2
                
                # Popularity
                popularity = movie.get('popularity', 0)
                score += popularity / 1000
                
                # Rating
                rating = movie.get('vote_average', 0)
                score += rating / 10 * 2
                
                scored_movies.append((movie, score))
            
            # Sort by score
            scored_movies.sort(key=lambda x: x[1], reverse=True)
            
            # Return top n movies
            recommendations = [movie for movie, score in scored_movies[:n]]
            
            # If no recommendations, use fallback
            if not recommendations:
                return self._get_popular_movies(n)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return self._get_popular_movies(n)
    
    def _get_popular_movies(self, n=20):
        """Get popular movies as fallback"""
        try:
            popular = TMDBAPI.get_popular_movies()
            if popular and 'results' in popular:
                return popular['results'][:n]
            return []
        except Exception as e:
            logger.error(f"Error getting popular movies: {e}")
            return []
    
    def get_trending_recommendations(self, n=10):
        """Get trending movies"""
        try:
            trending = TMDBAPI.get_trending_movies('day')
            if trending and 'results' in trending:
                return trending['results'][:n]
            return []
        except Exception as e:
            logger.error(f"Error getting trending: {e}")
            return []
    
    def get_explore_recommendations(self, n=10):
        """Get explore recommendations"""
        try:
            # Get all genres
            genre_map = TMDBAPI.get_genre_ids()
            all_genres = list(genre_map.keys())
            
            # Get user's genres
            user_genres = set()
            if self.user_profile and self.user_profile.genre_preferences:
                user_genres = set(self.user_profile.genre_preferences.keys())
            
            # Find genres user hasn't explored
            explore_genres = [g for g in all_genres if g not in user_genres]
            
            if not explore_genres:
                explore_genres = all_genres[:5]
            
            # Get movies from explore genres
            recommendations = []
            for genre in explore_genres[:3]:
                genre_id = genre_map.get(genre)
                if genre_id:
                    movies_data = TMDBAPI.get_movies_by_genre(genre_id, page=1)
                    if movies_data and 'results' in movies_data:
                        for movie in movies_data['results'][:5]:
                            if movie not in recommendations:
                                recommendations.append(movie)
            
            return recommendations[:n]
            
        except Exception as e:
            logger.error(f"Error getting explore: {e}")
            return []
    
    def get_discover_recommendations(self, n=10):
        """Get discover recommendations based on similar users"""
        try:
            # Get movies liked by other users with similar tastes
            if not self.user_profile:
                return []
            
            # Find users with similar genre preferences
            similar_users = []
            from django.contrib.auth.models import User
            
            all_users = User.objects.exclude(id=self.user.id)[:30]
            user_genres = set(self.user_profile.genre_preferences.keys())
            
            for user in all_users:
                try:
                    profile = UserBehaviorProfile.objects.get(user=user)
                    other_genres = set(profile.genre_preferences.keys())
                    
                    # Calculate overlap
                    overlap = len(user_genres & other_genres)
                    if overlap > 0:
                        similar_users.append((user, overlap))
                except:
                    continue
            
            # Sort by overlap
            similar_users.sort(key=lambda x: x[1], reverse=True)
            
            # Get liked movies from similar users
            recommendations = []
            for user, _ in similar_users[:3]:
                liked = LikedMovie.objects.filter(user=user)[:5]
                for movie in liked:
                    if movie.movie_id not in [r.get('id') for r in recommendations if isinstance(r, dict)]:
                        details = TMDBAPI.get_movie_details(movie.movie_id)
                        if details:
                            recommendations.append(details)
            
            return recommendations[:n]
            
        except Exception as e:
            logger.error(f"Error getting discover: {e}")
            return []