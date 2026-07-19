from .models import WatchHistory, Watchlist, LikedMovie
from .tmdb_api import TMDBAPI
from .recommendation import MovieRecommender
import logging

logger = logging.getLogger(__name__)

def get_user_preferences(user):
    """Get user preferences for recommendation engine"""
    try:
        # Get favorite genres
        favorite_genres = user.userprofile.favorite_genres if hasattr(user, 'userprofile') else []
        
        # Get watched movies
        watch_history = WatchHistory.objects.filter(user=user)
        watched_ids = [entry.movie_id for entry in watch_history]
        
        # Get liked movies
        liked_movies = LikedMovie.objects.filter(user=user)
        liked_ids = [movie.movie_id for movie in liked_movies]
        
        # Get watchlist
        watchlist = Watchlist.objects.filter(user=user)
        watchlist_ids = [entry.movie_id for entry in watchlist]
        
        return {
            'favorite_genres': favorite_genres,
            'watched_ids': watched_ids,
            'liked_ids': liked_ids,
            'watchlist_ids': watchlist_ids,
            'watch_history': watch_history,
            'liked_movies': liked_movies,
            'watchlist': watchlist
        }
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        return {
            'favorite_genres': [],
            'watched_ids': [],
            'liked_ids': [],
            'watchlist_ids': [],
            'watch_history': [],
            'liked_movies': [],
            'watchlist': []
        }

def get_movie_recommendations(user, movie_id=None, n_recommendations=20):
    """Get movie recommendations for a user"""
    try:
        recommender = MovieRecommender()
        
        if movie_id:
            # Get similar movies for a specific movie
            movie_details = TMDBAPI.get_movie_details(movie_id)
            if movie_details:
                movies = recommender.fetch_movies_for_recommendation([movie_id])
                df = recommender.prepare_data(movies)
                if df is not None:
                    recommender.build_tfidf_matrix(df)
                    return recommender.get_recommendations(movie_id, n_recommendations)
        
        # Get personalized recommendations
        user_prefs = get_user_preferences(user)
        
        # If user has favorites, watch history, or liked movies, use them for recommendations
        if user_prefs['favorite_genres'] or user_prefs['watched_ids'] or user_prefs['liked_ids']:
            # If user has liked movies, use those as seed
            if user_prefs['liked_ids']:
                seed_movies = user_prefs['liked_ids'][:5]
                # Get recommendations based on liked movies
                all_recommendations = []
                for seed_id in seed_movies:
                    movie_details = TMDBAPI.get_movie_details(seed_id)
                    if movie_details:
                        movies = recommender.fetch_movies_for_recommendation([seed_id])
                        df = recommender.prepare_data(movies)
                        if df is not None:
                            recommender.build_tfidf_matrix(df)
                            recs = recommender.get_recommendations(seed_id, 5)
                            all_recommendations.extend(recs)
                
                # Remove duplicates
                seen_ids = set()
                unique_recommendations = []
                for rec in all_recommendations:
                    if rec['id'] not in seen_ids:
                        seen_ids.add(rec['id'])
                        unique_recommendations.append(rec)
                
                return unique_recommendations[:n_recommendations]
            
            # Use personalized recommendations based on genres
            return recommender.get_personalized_recommendations(user_prefs, n_recommendations)
        
        # Fallback to popular movies
        popular = TMDBAPI.get_popular_movies()
        recommendations = []
        if popular and 'results' in popular:
            for movie in popular['results'][:n_recommendations]:
                recommendations.append({
                    'id': movie['id'],
                    'title': movie['title'],
                    'poster_path': movie.get('poster_path', ''),
                    'vote_average': movie.get('vote_average', 0),
                    'overview': movie.get('overview', ''),
                    'release_date': movie.get('release_date', ''),
                    'genre_ids': movie.get('genre_ids', [])
                })
        return recommendations
    except Exception as e:
        logger.error(f"Error getting movie recommendations: {e}")
        return []

def get_movie_details_with_recommendations(movie_id, user=None):
    """Get movie details with AI recommendations"""
    try:
        # Get movie details
        details = TMDBAPI.get_movie_details(movie_id)
        if not details:
            return None
        
        # Get similar movies using AI
        similar_movies = []
        if user:
            similar_movies = get_movie_recommendations(user, movie_id, 10)
        else:
            # Get similar movies without user context
            recommender = MovieRecommender()
            movies = recommender.fetch_movies_for_recommendation([movie_id])
            df = recommender.prepare_data(movies)
            if df is not None:
                recommender.build_tfidf_matrix(df)
                similar_movies = recommender.get_recommendations(movie_id, 10)
        
        # Format movie details
        movie_data = {
            'id': details['id'],
            'title': details['title'],
            'overview': details.get('overview', ''),
            'tagline': details.get('tagline', ''),
            'poster_path': details.get('poster_path', ''),
            'backdrop_path': details.get('backdrop_path', ''),
            'release_date': details.get('release_date', ''),
            'vote_average': details.get('vote_average', 0),
            'vote_count': details.get('vote_count', 0),
            'popularity': details.get('popularity', 0),
            'runtime': details.get('runtime', 0),
            'genres': details.get('genres', []),
            'production_companies': details.get('production_companies', []),
            'cast': details.get('credits', {}).get('cast', [])[:10],
            'videos': details.get('videos', {}).get('results', []),
            'similar_movies': similar_movies
        }
        
        return movie_data
    except Exception as e:
        logger.error(f"Error getting movie details: {e}")
        return None