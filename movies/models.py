from django.db import models
from django.contrib.auth.models import User

class WatchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_history')
    movie_id = models.IntegerField()
    movie_title = models.CharField(max_length=255)
    poster_path = models.CharField(max_length=255, blank=True, null=True)
    watched_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'movie_id']
        ordering = ['-watched_at']
    
    def __str__(self):
        return f"{self.user.username} watched {self.movie_title}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    movie_id = models.IntegerField()
    movie_title = models.CharField(max_length=255)
    poster_path = models.CharField(max_length=255, blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    watched = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'movie_id']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.username}'s watchlist: {self.movie_title}"

class LikedMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_movies')
    movie_id = models.IntegerField()
    movie_title = models.CharField(max_length=255)
    poster_path = models.CharField(max_length=255, blank=True, null=True)
    liked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'movie_id']
        ordering = ['-liked_at']
    
    def __str__(self):
        return f"{self.user.username} liked {self.movie_title}"
    
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class WatchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_history')
    movie_id = models.IntegerField()
    movie_title = models.CharField(max_length=255)
    poster_path = models.CharField(max_length=255, blank=True, null=True)
    watched_at = models.DateTimeField(auto_now_add=True)
    watch_duration = models.IntegerField(default=0)  # seconds watched
    watch_percentage = models.FloatField(default=0.0)  # percentage of movie watched
    completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'movie_id']
        ordering = ['-watched_at']
    
    def __str__(self):
        return f"{self.user.username} watched {self.movie_title}"

class UserMovieInteraction(models.Model):
    """Track detailed user interactions with movies"""
    INTERACTION_TYPES = [
        ('view', 'View'),
        ('click', 'Click'),
        ('search', 'Search'),
        ('like', 'Like'),
        ('watchlist', 'Watchlist'),
        ('share', 'Share'),
        ('rate', 'Rate'),
        ('watch_time', 'Watch Time'),
        ('complete', 'Complete'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    movie_id = models.IntegerField()
    movie_title = models.CharField(max_length=255)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    value = models.FloatField(default=0.0)  # For ratings, watch time, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'movie_id', 'interaction_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} {self.interaction_type} {self.movie_title}"

class UserBehaviorProfile(models.Model):
    """User behavior profile for recommendation learning"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='behavior_profile')
    
    # Genre preferences (weighted)
    genre_preferences = models.JSONField(default=dict)
    
    # Actor preferences
    actor_preferences = models.JSONField(default=dict)
    
    # Director preferences
    director_preferences = models.JSONField(default=dict)
    
    # Content features (based on NLP analysis)
    content_features = models.JSONField(default=dict)
    
    # Engagement metrics
    avg_watch_time = models.FloatField(default=0.0)
    avg_completion_rate = models.FloatField(default=0.0)
    total_movies_watched = models.IntegerField(default=0)
    total_likes_given = models.IntegerField(default=0)
    total_search_queries = models.IntegerField(default=0)
    
    # Time-based preferences
    preferred_hours = models.JSONField(default=list)  # Hours when user watches most
    preferred_days = models.JSONField(default=list)   # Days when user watches most
    
    # Session information
    last_active = models.DateTimeField(auto_now=True)
    session_count = models.IntegerField(default=0)
    
    # Learning model data
    user_embedding = models.JSONField(default=list)  # Vector representation of user
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Behavior Profile for {self.user.username}"

class MovieFeatureCache(models.Model):
    """Cache for movie features to avoid recomputation"""
    movie_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    features = models.JSONField()  # TF-IDF features
    genres = models.JSONField(default=list)
    actors = models.JSONField(default=list)
    director = models.CharField(max_length=255, blank=True)
    keywords = models.JSONField(default=list)
    avg_rating = models.FloatField(default=0.0)
    popularity_score = models.FloatField(default=0.0)
    freshness_score = models.FloatField(default=0.0)  # How recent is the movie
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-popularity_score']
    
    def __str__(self):
        return f"Features for {self.title}"

class RecommendationFeedback(models.Model):
    """Feedback on recommendations for learning"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie_id = models.IntegerField()
    recommendation_source = models.CharField(max_length=100)  # 'ai', 'trending', 'genre', etc.
    feedback_type = models.CharField(max_length=20)  # 'click', 'view', 'like', 'dislike', 'skip'
    feedback_value = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} {self.feedback_type} {self.movie_id}"