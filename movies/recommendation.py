import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .tmdb_api import TMDBAPI
import logging

logger = logging.getLogger(__name__)

class MovieRecommender:
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2)
        )
        self.tfidf_matrix = None
        self.movie_data = None
        self.movie_ids = None
    
    def fetch_movies_for_recommendation(self, movie_ids):
        """Fetch detailed movie data for a list of movie IDs"""
        movies = []
        
        # Get genre mapping
        genre_map = TMDBAPI.get_genre_ids()
        
        for movie_id in movie_ids[:20]:  # Limit to 20 movies for performance
            details = TMDBAPI.get_movie_details(movie_id)
            if details and 'id' in details:
                # Extract genres
                genres = [genre['name'] for genre in details.get('genres', [])]
                
                # Get keywords (simplified - using genres and overview words)
                keywords = ' '.join(genres)
                
                movies.append({
                    'id': details['id'],
                    'title': details['title'],
                    'overview': details.get('overview', ''),
                    'genres': ' '.join(genres),
                    'keywords': keywords,
                    'vote_average': details.get('vote_average', 0),
                    'popularity': details.get('popularity', 0),
                    'release_date': details.get('release_date', ''),
                    'poster_path': details.get('poster_path', '')
                })
        
        return movies
    
    def prepare_data(self, movies):
        """Prepare movie data for recommendation"""
        if not movies:
            return None
        
        # Create DataFrame
        df = pd.DataFrame(movies)
        
        # Create combined features for TF-IDF
        df['combined_features'] = df['overview'] + ' ' + df['genres'] + ' ' + df['keywords']
        
        # Fill NaN values
        df['combined_features'] = df['combined_features'].fillna('')
        
        self.movie_data = df
        self.movie_ids = df['id'].tolist()
        
        return df
    
    def build_tfidf_matrix(self, df):
        """Build TF-IDF matrix from movie features"""
        if df is None or df.empty:
            return None
        
        # Vectorize the combined features
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(df['combined_features'])
        return self.tfidf_matrix
    
    def get_recommendations(self, movie_id, n_recommendations=10):
        """Get movie recommendations based on a single movie"""
        if self.tfidf_matrix is None or self.movie_data is None:
            return []
        
        try:
            # Find the index of the movie
            idx = self.movie_data[self.movie_data['id'] == movie_id].index
            if len(idx) == 0:
                return []
            
            idx = idx[0]
            
            # Calculate similarity scores
            similarity_scores = cosine_similarity(self.tfidf_matrix[idx], self.tfidf_matrix).flatten()
            
            # Get top similar movies (excluding itself)
            similar_indices = similarity_scores.argsort()[::-1][1:n_recommendations+1]
            
            recommendations = []
            for i in similar_indices:
                movie = self.movie_data.iloc[i]
                recommendations.append({
                    'id': movie['id'],
                    'title': movie['title'],
                    'poster_path': movie['poster_path'],
                    'vote_average': movie['vote_average'],
                    'similarity_score': float(similarity_scores[i])
                })
            
            return recommendations
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []
    
    def get_personalized_recommendations(self, user_preferences, n_recommendations=20):
        """Get personalized recommendations based on user preferences"""
        # User preferences: favorite_genres, watch_history, liked_movies, watchlist
        try:
            # Fetch movies based on user's favorite genres
            genre_map = TMDBAPI.get_genre_ids()
            genre_ids = []
            
            for genre in user_preferences.get('favorite_genres', []):
                if genre.lower() in genre_map:
                    genre_ids.append(genre_map[genre.lower()])
            
            # Collect candidate movies
            candidate_movies = []
            
            # If user has favorite genres, get movies from those genres
            if genre_ids:
                for genre_id in genre_ids[:3]:  # Limit to 3 genres for performance
                    movies = TMDBAPI.get_movies_by_genre(genre_id, page=1)
                    if movies and 'results' in movies:
                        for movie in movies['results'][:20]:
                            if movie['id'] not in [m['id'] for m in candidate_movies]:
                                candidate_movies.append(movie)
            
            # If not enough movies, add popular movies
            if len(candidate_movies) < 20:
                popular = TMDBAPI.get_popular_movies()
                if popular and 'results' in popular:
                    for movie in popular['results']:
                        if movie['id'] not in [m['id'] for m in candidate_movies]:
                            candidate_movies.append(movie)
            
            # Get user's watched, liked, and watchlist movies
            watched_ids = user_preferences.get('watched_ids', [])
            liked_ids = user_preferences.get('liked_ids', [])
            watchlist_ids = user_preferences.get('watchlist_ids', [])
            
            # Create scoring system for candidate movies
            movie_scores = {}
            for movie in candidate_movies:
                movie_id = movie['id']
                score = 0
                
                # Boost score based on genres match
                if genre_ids:
                    movie_genres = movie.get('genre_ids', [])
                    genre_match = len(set(movie_genres) & set(genre_ids))
                    score += genre_match * 2
                
                # Boost score based on popularity and rating
                score += movie.get('popularity', 0) / 100
                score += movie.get('vote_average', 0) / 2
                
                movie_scores[movie_id] = score
            
            # Sort movies by score
            sorted_movies = sorted(candidate_movies, key=lambda x: movie_scores.get(x['id'], 0), reverse=True)
            
            # Format recommendations
            recommendations = []
            for movie in sorted_movies[:n_recommendations]:
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
            logger.error(f"Error getting personalized recommendations: {e}")
            return []