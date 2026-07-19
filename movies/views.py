from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .tmdb_api import TMDBAPI
from .models import WatchHistory, Watchlist, LikedMovie, UserMovieInteraction
from .services import get_movie_recommendations, get_movie_details_with_recommendations, get_user_preferences
from .recommendation_engine import AdvancedMovieRecommender
import json
import logging

logger = logging.getLogger(__name__)

@login_required
def dashboard(request):
    """Home dashboard with AI recommendations"""
    try:
        # Initialize recommender
        recommender = AdvancedMovieRecommender(request.user)
        
        # Get personalized recommendations
        ai_recommendations = recommender.get_personalized_recommendations(20)
        
        # Get trending recommendations
        trending_recommendations = recommender.get_trending_recommendations(10)
        
        # Get explore recommendations (new genres)
        explore_recommendations = recommender.get_explore_recommendations(10)
        
        # Get discover recommendations (similar users)
        discover_recommendations = recommender.get_discover_recommendations(10)
        
        # Get user preferences
        user_prefs = get_user_preferences(request.user)
        
        # Get popular movies
        popular = TMDBAPI.get_popular_movies()
        popular_movies = popular.get('results', [])[:10] if popular else []
        
        # Get top rated movies
        top_rated = TMDBAPI.get_top_rated_movies()
        top_rated_movies = top_rated.get('results', [])[:10] if top_rated else []
        
        # Get upcoming movies
        upcoming = TMDBAPI.get_upcoming_movies()
        upcoming_movies = upcoming.get('results', [])[:10] if upcoming else []
        
        # Get featured movie (first trending)
        featured_movie = trending_recommendations[0] if trending_recommendations else None
        
        # Get genre-based recommendations
        genre_recommendations = {}
        if user_prefs['favorite_genres']:
            genre_map = TMDBAPI.get_genre_ids()
            for genre in user_prefs['favorite_genres'][:3]:
                if genre.lower() in genre_map:
                    genre_id = genre_map[genre.lower()]
                    movies = TMDBAPI.get_movies_by_genre(genre_id, page=1)
                    if movies and 'results' in movies:
                        genre_recommendations[genre] = movies['results'][:6]
        
        context = {
            'featured_movie': featured_movie,
            'ai_recommendations': ai_recommendations,
            'trending_recommendations': trending_recommendations,
            'explore_recommendations': explore_recommendations,
            'discover_recommendations': discover_recommendations,
            'popular_movies': popular_movies,
            'top_rated_movies': top_rated_movies,
            'upcoming_movies': upcoming_movies,
            'genre_recommendations': genre_recommendations,
            'user_prefs': user_prefs,
            'api_error': False
        }
        
        return render(request, 'movies/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return render(request, 'movies/dashboard.html', {'api_error': True})

@login_required
def movie_detail(request, movie_id):
    """Movie detail page with AI recommendations"""
    try:
        # Initialize recommender
        recommender = AdvancedMovieRecommender(request.user)
        
        # Record view interaction
        recommender.learn_from_interaction(movie_id, 'view')
        
        # Get movie details
        movie_data = get_movie_details_with_recommendations(movie_id, request.user)
        
        if not movie_data:
            messages.error(request, 'Movie not found.')
            return redirect('movies:dashboard')
        
        # Get similar movies
        similar_movies = recommender.get_similar_movies(movie_id, 10)
        
        # Check if movie is in user's watchlist
        in_watchlist = Watchlist.objects.filter(user=request.user, movie_id=movie_id).exists()
        
        # Check if movie is liked
        is_liked = LikedMovie.objects.filter(user=request.user, movie_id=movie_id).exists()
        
        # Add to watch history
        WatchHistory.objects.get_or_create(
            user=request.user,
            movie_id=movie_id,
            defaults={
                'movie_title': movie_data['title'],
                'poster_path': movie_data['poster_path']
            }
        )
        
        context = {
            'movie': movie_data,
            'similar_movies': similar_movies,
            'in_watchlist': in_watchlist,
            'is_liked': is_liked
        }
        
        return render(request, 'movies/movie_detail.html', context)
        
    except Exception as e:
        logger.error(f"Movie detail error: {e}")
        messages.error(request, 'Error loading movie details.')
        return redirect('movies:dashboard')

@login_required
def trending_movies(request):
    """Trending movies page with personalization"""
    try:
        # Initialize recommender
        recommender = AdvancedMovieRecommender(request.user)
        
        # Get personalized trending recommendations
        trending_recommendations = recommender.get_trending_recommendations(20)
        
        # Also get regular trending for comparison
        trending = TMDBAPI.get_trending_movies()
        regular_trending = trending.get('results', []) if trending else []
        
        context = {
            'title': 'Trending Movies',
            'movies': regular_trending,
            'personalized_trending': trending_recommendations,
            'show_personalized': True
        }
        
        return render(request, 'movies/trending.html', context)
        
    except Exception as e:
        logger.error(f"Trending view error: {e}")
        messages.error(request, 'Error loading trending movies.')
        return render(request, 'movies/trending.html', {
            'title': 'Trending Movies',
            'movies': [],
            'show_personalized': False
        })

@login_required
@require_POST
def toggle_watchlist(request, movie_id):
    """Add or remove movie from watchlist"""
    try:
        data = json.loads(request.body)
        movie_title = data.get('movie_title', 'Unknown Movie')
        poster_path = data.get('poster_path', '')
        
        # Initialize recommender for learning
        recommender = AdvancedMovieRecommender(request.user)
        
        watchlist_item = Watchlist.objects.filter(user=request.user, movie_id=movie_id)
        
        if watchlist_item.exists():
            watchlist_item.delete()
            return JsonResponse({
                'status': 'removed', 
                'message': 'Removed from watchlist',
                'in_watchlist': False
            })
        else:
            Watchlist.objects.create(
                user=request.user,
                movie_id=movie_id,
                movie_title=movie_title,
                poster_path=poster_path
            )
            # Learn from watchlist addition
            recommender.learn_from_interaction(movie_id, 'watchlist')
            
            return JsonResponse({
                'status': 'added', 
                'message': 'Added to watchlist',
                'in_watchlist': True
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Toggle watchlist error: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@require_POST
def toggle_like(request, movie_id):
    """Like or unlike a movie"""
    try:
        data = json.loads(request.body)
        movie_title = data.get('movie_title', 'Unknown Movie')
        poster_path = data.get('poster_path', '')
        
        # Initialize recommender for learning
        recommender = AdvancedMovieRecommender(request.user)
        
        liked_movie = LikedMovie.objects.filter(user=request.user, movie_id=movie_id)
        
        if liked_movie.exists():
            liked_movie.delete()
            return JsonResponse({
                'status': 'unliked', 
                'message': 'Movie unliked',
                'is_liked': False
            })
        else:
            LikedMovie.objects.create(
                user=request.user,
                movie_id=movie_id,
                movie_title=movie_title,
                poster_path=poster_path
            )
            # Learn from like
            recommender.learn_from_interaction(movie_id, 'like')
            
            return JsonResponse({
                'status': 'liked', 
                'message': 'Movie liked',
                'is_liked': True
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Toggle like error: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def watch_time_tracking(request, movie_id):
    """Track watch time for learning"""
    try:
        data = json.loads(request.body)
        watch_duration = data.get('duration', 0)
        percentage = data.get('percentage', 0)
        
        # Initialize recommender
        recommender = AdvancedMovieRecommender(request.user)
        
        # Update watch history
        watch_entry = WatchHistory.objects.filter(user=request.user, movie_id=movie_id).first()
        if watch_entry:
            watch_entry.watch_duration = watch_duration
            watch_entry.watch_percentage = percentage
            if percentage >= 90:  # Consider as completed
                watch_entry.completed = True
                recommender.learn_from_interaction(movie_id, 'complete')
            watch_entry.save()
        
        # Track watch time interaction
        if watch_duration > 0:
            recommender.learn_from_interaction(movie_id, 'watch_time', watch_duration / 60)  # Convert to minutes
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Watch time tracking error: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def search_movies(request):
    """Search movies with learning"""
    query = request.GET.get('q', '')
    if not query:
        return render(request, 'movies/search.html', {'query': query, 'results': []})
    
    try:
        # Record search interaction
        recommender = AdvancedMovieRecommender(request.user)
        recommender.learn_from_interaction(0, 'search', 0)  # 0 is a placeholder
        
        results = TMDBAPI.search_movies(query)
        movies = results.get('results', []) if results else []
        
        context = {
            'query': query,
            'results': movies,
            'total_results': results.get('total_results', 0) if results else 0
        }
        
        return render(request, 'movies/search.html', context)
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        messages.error(request, 'Error searching movies.')
        return render(request, 'movies/search.html', {'query': query, 'results': []})

@login_required
def recommendations_view(request):
    """Recommendations page"""
    try:
        # Initialize recommender
        recommender = AdvancedMovieRecommender(request.user)
        
        # Get all types of recommendations
        personalized = recommender.get_personalized_recommendations(20)
        trending = recommender.get_trending_recommendations(10)
        explore = recommender.get_explore_recommendations(10)
        discover = recommender.get_discover_recommendations(10)
        
        # Get popular movies as fallback
        popular = []
        popular_data = TMDBAPI.get_popular_movies()
        if popular_data and 'results' in popular_data:
            popular = popular_data['results'][:10]
        
        # Get user preferences
        user_prefs = get_user_preferences(request.user)
        
        # Log what we found
        logger.info(f"Recommendations for {request.user.username}: Personalized: {len(personalized)}, Trending: {len(trending)}, Explore: {len(explore)}, Discover: {len(discover)}")
        
        context = {
            'personalized_recommendations': personalized,
            'trending_recommendations': trending,
            'explore_recommendations': explore,
            'discover_recommendations': discover,
            'popular_movies': popular,
            'user_prefs': user_prefs
        }
        
        return render(request, 'movies/recommendations.html', context)
        
    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        # Return with empty data
        return render(request, 'movies/recommendations.html', {
            'personalized_recommendations': [],
            'trending_recommendations': [],
            'explore_recommendations': [],
            'discover_recommendations': [],
            'popular_movies': [],
            'user_prefs': {}
        })
@login_required
def watchlist_view(request):
    """User watchlist page"""
    try:
        watchlist = Watchlist.objects.filter(user=request.user)
        
        context = {
            'watchlist': watchlist
        }
        
        return render(request, 'movies/watchlist.html', context)
        
    except Exception as e:
        logger.error(f"Watchlist view error: {e}")
        messages.error(request, 'Error loading watchlist.')
        return render(request, 'movies/watchlist.html', {'watchlist': []})

@login_required
def genres_view(request, genre_name):
    """Movies by genre"""
    try:
        genre_map = TMDBAPI.get_genre_ids()
        genre_id = genre_map.get(genre_name.lower())
        
        if not genre_id:
            messages.error(request, f'Genre "{genre_name}" not found.')
            return redirect('movies:dashboard')
        
        movies = TMDBAPI.get_movies_by_genre(genre_id)
        movie_list = movies.get('results', []) if movies else []
        
        context = {
            'genre_name': genre_name.title(),
            'movies': movie_list
        }
        
        return render(request, 'movies/genre_movies.html', context)
        
    except Exception as e:
        logger.error(f"Genre view error: {e}")
        messages.error(request, 'Error loading genre movies.')
        return render(request, 'movies/genre_movies.html', {'genre_name': genre_name, 'movies': []})

@login_required
def refresh_recommendations(request):
    """AJAX endpoint to refresh recommendations"""
    try:
        recommender = AdvancedMovieRecommender(request.user)
        
        # Update user embedding
        recommender._update_user_embedding()
        
        # Get fresh recommendations
        recommendations = recommender.get_personalized_recommendations(20)
        
        # Format recommendations for JSON response
        formatted_recommendations = []
        for movie in recommendations:
            formatted_recommendations.append({
                'id': movie.get('id'),
                'title': movie.get('title'),
                'poster_path': movie.get('poster_path'),
                'vote_average': movie.get('vote_average', 0),
                'overview': movie.get('overview', ''),
                'release_date': movie.get('release_date', '')
            })
        
        return JsonResponse({
            'status': 'success',
            'recommendations': formatted_recommendations
        })
        
    except Exception as e:
        logger.error(f"Refresh recommendations error: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)